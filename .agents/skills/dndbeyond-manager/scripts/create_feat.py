#!/usr/bin/env python3
"""Create or update a homebrew feat on D&D Beyond with Modifiers, Actions, and Limited Use trackers."""
import argparse
import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.expanduser("~/.gemini/antigravity-cli/dndbeyond_profile")

def add_modifier(page, feat_edit_url, mod_type, mod_subtype, fixed_val=None, ability_stat=None):
    print(f"  -> Adding Modifier [{mod_type} -> {mod_subtype}]...")
    page.goto(feat_edit_url, wait_until="networkidle")
    time.sleep(2)

    page.evaluate("() => document.querySelectorAll('.vex, .vex-overlay, .vex-content').forEach(el => el.remove())")

    mod_btn = page.locator("a:has-text('ADD A MODIFIER'), a:has-text('Add a Modifier')").first
    if mod_btn.count() == 0:
        print("     [ERROR] 'ADD A MODIFIER' button not found.")
        return False

    href = mod_btn.get_attribute("href")
    target_url = "https://www.dndbeyond.com" + href if href.startswith("/") else href
    page.goto(target_url, wait_until="networkidle")
    time.sleep(2)

    # 1. Select Modifier Type (Select2)
    page.locator("#s2id_field-spell-modifier-type").click()
    time.sleep(1)
    page.get_by_role("option", name=mod_type, exact=True).click()
    time.sleep(2)

    # 2. Select Modifier Subtype (Select2)
    page.locator("#s2id_field-spell-modifier-sub-type").click()
    time.sleep(1)
    page.get_by_role("option", name=mod_subtype, exact=True).click()
    time.sleep(2)

    # 3. Ability Stat (native select)
    if ability_stat:
        page.select_option("#field-rpg-stat", value=ability_stat)
        time.sleep(1)

    # 4. Fixed Value
    if fixed_val is not None:
        page.fill("#field-fixed-value", str(fixed_val))
        time.sleep(1)

    # 5. Save
    save_btn = page.locator("button:has-text('SAVE'), button:has-text('Save'), input[value='Save']").first
    save_btn.click()
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    print(f"     [SUCCESS] Modifier [{mod_type} -> {mod_subtype}] saved.")
    return True

def add_action(page, feat_edit_url, name, action_type="General", activation="Special", reset_type="Long Rest", dice_count=None, die_type=None, snippet="", uses=1):
    print(f"  -> Adding Action '{name}'...")
    page.goto(feat_edit_url, wait_until="networkidle")
    time.sleep(2)

    page.evaluate("() => document.querySelectorAll('.vex, .vex-overlay, .vex-content').forEach(el => el.remove())")

    act_btn = page.locator("a:has-text('ADD ACTION'), a:has-text('Add Action')").first
    if act_btn.count() == 0:
        print("     [ERROR] 'ADD ACTION' button not found.")
        return False

    href = act_btn.get_attribute("href")
    target_url = "https://www.dndbeyond.com" + href if href.startswith("/") else href
    page.goto(target_url, wait_until="networkidle")
    time.sleep(2)

    # 1. Action Type FIRST
    page.select_option("#field-action-type", label=action_type)
    time.sleep(2)

    # 2. Name
    page.fill("#field-name-field", name)

    # 3. Activation & Reset
    page.select_option("#field-activation", label=activation)
    page.select_option("#field-reset-type", label=reset_type)

    # 4. Dice
    if dice_count:
        page.fill("#field-dice-count", str(dice_count))
    if die_type:
        page.select_option("#field-die-type", label=die_type)

    # 5. Snippet
    if snippet:
        page.fill("#field-snippet-field", snippet)

    # 6. Save Base Action
    save_btn = page.locator("button:has-text('SAVE'), button:has-text('Save')").first
    save_btn.click()
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    action_edit_url = page.url
    print(f"     [SUCCESS] Action '{name}' saved at: {action_edit_url}")

    # 7. Add Limited Use Checkboxes (Level Scale)
    if uses:
        print(f"     -> Configuring {uses} Limited Use checkmark(s)...")
        level_scale_btn = page.locator("a:has-text('ADD LIMITED USE DATA'), a:has-text('Add Limited Use Data')").first
        if level_scale_btn.count() > 0:
            scale_href = level_scale_btn.get_attribute("href")
            scale_target = "https://www.dndbeyond.com" + scale_href if scale_href.startswith("/") else scale_href
            page.goto(scale_target, wait_until="networkidle")
            time.sleep(2)

            page.fill("#field-number-of-uses", str(uses))
            save_scale_btn = page.locator("button[type='submit']:has-text('SAVE'), button:has-text('Save'), input[value='Save']").first
            save_scale_btn.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            print(f"     [SUCCESS] Limited Use count ({uses}) active.")
        else:
            print("     [WARNING] 'ADD LIMITED USE DATA' button not found.")

    return True

def create_full_feat(feat_data):
    name = feat_data["name"]
    snippet = feat_data.get("snippet", "")
    description = feat_data.get("description", "")
    version = feat_data.get("version", "1")
    modifiers = feat_data.get("modifiers", [])
    actions = feat_data.get("actions", [])

    print(f"\n==========================================")
    print(f"Creating Feat: {name} (Version {version})")
    print(f"==========================================")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Step 1: Base Feat Creation
        page.goto("https://www.dndbeyond.com/homebrew/creations/create-feat/create", wait_until="networkidle")
        time.sleep(2)

        page.evaluate("() => document.querySelectorAll('.vex, .vex-overlay, .vex-content').forEach(el => el.remove())")

        page.fill("#field-name", name)
        page.fill("#field-version", str(version))
        page.fill("#field-snippet", snippet)

        page.evaluate("""(html) => {
            if (typeof tinymce !== 'undefined' && tinymce.get('field-item-description-wysiwyg')) {
                tinymce.get('field-item-description-wysiwyg').setContent(html);
                tinymce.triggerSave();
            } else {
                const ta = document.getElementById('field-item-description-wysiwyg') || document.getElementById('field-item-description');
                if (ta) ta.value = html;
            }
        }""", description)

        submit_btn = page.locator("button[type='submit']:has-text('CREATE FEAT'), button:has-text('Create Feat')").first
        submit_btn.click(force=True)
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        edit_url = page.url
        print(f"[SUCCESS] Base feat created! Edit URL: {edit_url}")

        # Step 2: Add Modifiers
        for m in modifiers:
            add_modifier(
                page, edit_url,
                mod_type=m["type"],
                mod_subtype=m["subtype"],
                fixed_val=m.get("fixed_val") or m.get("value"),
                ability_stat=m.get("ability") or m.get("ability_stat")
            )

        # Step 3: Add Actions with Limited Uses
        for a in actions:
            add_action(
                page, edit_url,
                name=a["name"],
                action_type=a.get("action_type", "General"),
                activation=a.get("activation", "Special"),
                reset_type=a.get("reset_type", "Long Rest"),
                dice_count=a.get("dice_count"),
                die_type=a.get("die_type"),
                snippet=a.get("snippet", ""),
                uses=a.get("uses", 1)
            )

        ctx.close()
        print(f"[COMPLETED] Feat '{name}' fully configured at: {edit_url}\n")
        return edit_url

def main():
    parser = argparse.ArgumentParser(description="Full mechanical creation of D&D Beyond homebrew feats.")
    parser.add_argument("--json-file", help="Path to JSON file containing feat or list of feats with modifiers and actions")
    parser.add_argument("--name", help="Feat name")
    parser.add_argument("--snippet", help="Feat tooltip snippet")
    parser.add_argument("--description", help="Feat rules HTML description")
    parser.add_argument("--version", default="1", help="Version")

    args = parser.parse_args()

    if args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        feats = data if isinstance(data, list) else [data]
        for f in feats:
            create_full_feat(f)
    elif args.name and args.snippet and args.description:
        create_full_feat({
            "name": args.name,
            "snippet": args.snippet,
            "description": args.description,
            "version": args.version
        })
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
