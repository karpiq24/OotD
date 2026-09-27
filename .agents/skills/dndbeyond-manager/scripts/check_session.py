#!/usr/bin/env python3
"""Check whether the persistent D&D Beyond session is valid."""
import os
import sys
from pathlib import Path

PROFILE_DIR = os.path.expanduser("~/.gemini/antigravity-cli/dndbeyond_profile")

def check_session():
    if not Path(PROFILE_DIR).exists():
        print(f"[ERROR] Profile directory not found at: {PROFILE_DIR}")
        print("Run `reauth.py` to sign in and initialize the profile.")
        sys.exit(1)

    from playwright.sync_api import sync_playwright

    print(f"Checking session in: {PROFILE_DIR}...")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        cookies = ctx.cookies()
        has_cobalt = any(c.get("name") == "CobaltSession" for c in cookies)

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.dndbeyond.com/", wait_until="domcontentloaded")
        user_el = page.locator(".user-bttn, .user-profile, .site-user, a[href*='/my-characters']").count()

        ctx.close()

        if has_cobalt or user_el > 0:
            print("[SUCCESS] D&D Beyond session is active and authenticated!")
            sys.exit(0)
        else:
            print("[EXPIRED] Session cookie missing or expired. Run `reauth.py` to sign in again.")
            sys.exit(2)

if __name__ == "__main__":
    check_session()
