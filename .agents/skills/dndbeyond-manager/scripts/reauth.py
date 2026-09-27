#!/usr/bin/env python3
"""Launch headful browser for interactive D&D Beyond sign-in and persist session."""
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.expanduser("~/.gemini/antigravity-cli/dndbeyond_profile")

def reauth():
    Path(PROFILE_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Opening browser using profile: {PROFILE_DIR}...")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--no-default-browser-check"
            ],
            viewport={"width": 1280, "height": 900}
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.dndbeyond.com/homebrew/creations/create-feat", wait_until="domcontentloaded")

        print("\n" + "="*60)
        print(">>> Browser window is open.")
        print(">>> Please sign into D&D Beyond in the window.")
        print(">>> Waiting for authentication to complete...")
        print("="*60 + "\n")

        start = time.time()
        authenticated = False
        while time.time() - start < 600:
            time.sleep(3)
            cookies = ctx.cookies()
            has_cobalt = any(c.get("name") in ["CobaltSession", "UserToken"] for c in cookies)
            url = page.url
            if has_cobalt or ("sign-in" not in url and "login" not in url and "homebrew" in url):
                print(f"[SUCCESS] Login detected! Current URL: {url}")
                authenticated = True
                break

        if not authenticated:
            print("[TIMEOUT] Login was not completed within 10 minutes.")
            ctx.close()
            sys.exit(1)

        time.sleep(2)
        ctx.close()
        print(f"[DONE] Session saved to {PROFILE_DIR}.")

if __name__ == "__main__":
    reauth()
