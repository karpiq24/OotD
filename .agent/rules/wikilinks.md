---
trigger: always_on
---

# Rule: Standardize Wikilinks

## Trigger
This rule applies whenever creating or editing markdown files that contain internal links (wikilinks).

## Action
Always use the simplified wikilink format compatible with Obsidian/modern wiki software.

1. **No Paths**: Do NOT include the directory path in the link.
   - **Incorrect**: `[[content/02-People/NPCs/Zephyrus.md|Zephyrus]]`
   - **Correct**: `[[Zephyrus]]` or `[[Zephyrus|Alias]]`

2. **No Extensions**: Do NOT include the `.md` file extension.
   - **Incorrect**: `[[Lutheria.md]]`
   - **Correct**: `[[Lutheria]]`

3. **Anchors**: You may responsibly use anchors if pointing to a specific section.
   - **Correct**: `[[History of Thylea#The First War]]`

4. **Consistency**: Ensure all new and edited links follow this pattern to maintain a clean and portable graph structure.
