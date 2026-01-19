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
Always update the corresponding `index.md` file in the same directory (and potentially parent directories if necessary) to reflect the correct state of the content.

### Details
1. **Creation**: Add a link to the new file in the `index.md` of the directory.
2. **Deletion**: Remove the link to the deleted file from `index.md`.
3. **Move**: Remove from old `index.md`, add to new `index.md`.
4. **Rename**: Update the link text and target in `index.md`.
