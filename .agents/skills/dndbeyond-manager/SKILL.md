---
name: dndbeyond-manager
description: Automates D&D Beyond operations using a persistent authenticated browser session. Creates and updates homebrew feats, species/races, spells, items, backgrounds, monsters, and validates session status.
---

# D&D Beyond Manager

Use this skill whenever you need to interact with D&D Beyond to create, update, or manage homebrew content (Feats, Species/Races, Spells, Magic Items, Backgrounds, Monsters) or inspect user campaign assets.

---

## 1. Architecture & Authentication

D&D Beyond employs Cloudflare bot mitigation and multi-provider SSO (Google, Wizards, Apple, Twitch). To automate tasks reliably without triggering anti-bot flags:

* **Persistent Profile Location:** `~/.gemini/antigravity-cli/dndbeyond_profile`
* **Session Persistence:** Once authenticated, the browser profile stores all `CobaltSession`, `UserToken`, and authorization cookies permanently across conversations.
* **Storage State Export (Concurrent Subagents):** `~/.gemini/antigravity-cli/dndbeyond_storage_state.json` allows multiple headless browser contexts to run concurrently without Chromium lockfile collisions (`SingletonLock`).
* **Execution Engine:** Playwright scripts executed via `uv run --with playwright python`.

---

## 2. Master Homebrew Creation Endpoints & Reference Guides

D&D Beyond separates homebrew creations into distinct engines with dedicated entity models, subforms, and URL structures:

| Category | DDB Endpoint | Entity Type ID | Comprehensive Reference Guide |
| :--- | :--- | :--- | :--- |
| **Backgrounds** | `/homebrew/creations/create-background` | `1669830167` | [references/backgrounds.md](file:///home/karpiq/Code/OotD/.agents/skills/dndbeyond-manager/references/backgrounds.md) |
| **Feats** | `/homebrew/creations/create-feat` | `1088940854` | [references/feats.md](file:///home/karpiq/Code/OotD/.agents/skills/dndbeyond-manager/references/feats.md) |
| **Magic Items** | `/homebrew/creations/create-magic-item` | `112130694` | [references/magic-items.md](file:///home/karpiq/Code/OotD/.agents/skills/dndbeyond-manager/references/magic-items.md) |
| **Monsters** | `/homebrew/creations/create-monster` | `779871897` | [references/monsters.md](file:///home/karpiq/Code/OotD/.agents/skills/dndbeyond-manager/references/monsters.md) |
| **Species / Races** | `/homebrew/creations/create-species` | `1743923279` | [references/races.md](file:///home/karpiq/Code/OotD/.agents/skills/dndbeyond-manager/references/races.md) |
| **Spells** | `/homebrew/creations/create-spell` | `1118725998` | [references/spells.md](file:///home/karpiq/Code/OotD/.agents/skills/dndbeyond-manager/references/spells.md) |
| **Subclasses** | `/homebrew/creations/create-subclass` | *(Class-specific)* | *In development* |

*Note: In the 2024 update, D&D Beyond renamed Races to **Species** (`create-species`). Visiting `create-race` returns a 404.*

---

## 3. Universal D&D Beyond Homebrew Architecture

Across all entity types, D&D Beyond follows a **Three-Tier Architecture**:

### Tier 1: Presentation & Rich Text (TinyMCE + Tooltips)
* **Rules Text:** Formatted 5e mechanics via TinyMCE textareas. Always write in standard 5e English phrasing.
* **D&D Beyond BBCode Tooltip Tags:** Embed interactive tooltip links:
  * Spells: `[spell]darkness[/spell]`
  * Magic Items: `[magicitem]flame tongue[/magicitem]` or `[item]rope of climbing[/item]`
  * Conditions: `[condition]poisoned[/condition]`
  * Senses: `[sense]darkvision[/sense]`
  * Actions: `[action]dash[/action]`
  * Skills: `[skill]athletics[/skill]`
  * Monsters: `[monster]red dragon[/monster]`
  * Digital Dice Rollers (Monsters): `[rollable]+7;{"diceNotation":"1d20+7","rollType":"to hit","rollAction":"Bite"}[/rollable]`
* **Snippets:** Short summaries (< 250 characters) displayed on character sheet tooltips. Supports dynamic handlebars math:
  * Ability Modifiers: `{{modifier:wis}}`, `{{modifier:con#unsigned}}`
  * Proficiency Bonus: `{{proficiency}}`, `{{proficiency#unsigned}}`
  * Save DCs: `{{savedc:int}}`
  * Scaling Calculations: `{{rounddown(characterlevel/2)}}`, `{{(modifier:con*2)#unsigned}}`

### Tier 2: Mechanical Modifiers & Subforms
Text descriptions alone do **not** adjust character sheet calculations. Modifiers must be explicitly added to update scores, AC, saves, proficiencies, or dice pools:
* **Select2 Cascading Dropdowns:** Selecting a `Modifier Type` (e.g., `Bonus`, `Advantage`, `Resistance`, `Language`, `Immunity`) triggers an AJAX call to load hundreds of `Modifier Subtypes`.
* **Stat Increases & Maximum Caps:** Raising an ability score beyond 20 requires **two** modifiers:
  1. `Bonus` ➔ `[Stat] Score` (Fixed Value: `X`)
  2. `Bonus` ➔ `Ability Score Maximum` ➔ Ability: `[STAT]` (Fixed Value: `X`)
* **Magic Enchantments:** For magic armor/weapons, use `Bonus` ➔ `Magic` (+1/+2/+3) rather than `Bonus` ➔ `Weapon Attack Rolls` (which fails to apply to damage).

### Tier 3: Action Trackers & Limited Uses
For abilities with activation economies or finite uses per rest:
1. **Base Action Form:** Select Action Type (`General`, `Spell`, `Weapon`) to reveal fields, then set Activation (`Action`, `Bonus Action`, `Reaction`, `Special`) and Reset Type (`Long Rest`, `Short Rest`).
2. **Limited Use Data (`/level-scale/create`):**
   * **CRITICAL STEP:** Saving the base action does **NOT** generate checkbox trackers on character sheets!
   * You must navigate to `/entity/limited-use/{id}/level-scale/create` and set `number-of-uses` (e.g. `1` or proficiency bonus). This renders interactive checkboxes on the character sheet.

---

## 4. Universal Automation Patterns & Traps (Playwright)

1. **Handling Select2 Dropdowns:**
   Never attempt a raw `.fill()` on Select2 elements. Use:
   ```python
   # Click the Select2 container
   page.locator("#s2id_field-spell-modifier-type").click()
   page.wait_for_selector(".select2-drop-active")
   # Select the option
   page.get_by_role("option", name=mod_type, exact=True).click()
   page.wait_for_timeout(1500)  # Wait for AJAX cascade
   ```
   Or update via jQuery:
   ```javascript
   window.jQuery('#field-id').val(['val1', 'val2']).trigger('change');
   ```

2. **Suppressing Vex Overlays:**
   D&D Beyond modals inject `.vex-overlay` and `.vex` backdrops that intercept clicks. Suppress them before interacting:
   ```python
   page.evaluate("() => document.querySelectorAll('.vex, .vex-overlay, .vex-content').forEach(el => el.remove())")
   ```

3. **TinyMCE Editors:**
   Always sync before submitting forms:
   ```javascript
   if (typeof tinymce !== 'undefined') {
       tinymce.triggerSave();
   }
   ```

4. **Homebrew Deletion Protocol:**
   Deleting a homebrew item via UI requires confirming an AJAX modal:
   ```python
   # Trigger delete modal link
   page.locator("a[href*='/homebrew/creations/delete?entityTypeId=']").first.click()
   page.wait_for_selector(".ddb-modal a.ajax-post")
   page.locator(".ddb-modal a.ajax-post:has-text('Yes')").click()
   ```

---

## 5. Helper Scripts

All scripts reside in `.agents/skills/dndbeyond-manager/scripts/`:

### 1. Check Session Validity
```bash
uv run --with playwright python .agents/skills/dndbeyond-manager/scripts/check_session.py
```
* Returns exit code `0` if authenticated and active.
* Returns exit code `2` if expired.

### 2. Re-Authenticate / Login
```bash
uv run --with playwright python .agents/skills/dndbeyond-manager/scripts/reauth.py
```
* Opens a visible Chromium window on the user's desktop.
* Monitors for sign-in completion.
* Saves refreshed session into `~/.gemini/antigravity-cli/dndbeyond_profile`.

### 3. Create Homebrew Feats (with Modifiers, Actions & Uses)
```bash
uv run --with playwright python .agents/skills/dndbeyond-manager/scripts/create_feat.py \
  --json-file path/to/feats.json
```
Creates base feats, adds Select2 modifiers, actions, and configures level-scale checkbox trackers automatically.
