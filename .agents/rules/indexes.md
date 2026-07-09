---
trigger: always_on
---

# Rule: Auto-update Index Files

## Trigger
This rule applies whenever any content file (Markdown, etc.) is:
- Created
- Deleted
- Moved
- Renamed
- Changed (if the change affects the title/link representation)

## Action
Instead of manually updating `index.md` files, run the update script:
```bash
python3 scripts/update_indexes.py
```
This script will recurse through the `content/` directory and update/regenerate all `index.md` files with correct links and titles, preserving existing descriptions and non-list content.
