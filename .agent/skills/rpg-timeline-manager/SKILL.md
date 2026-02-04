---
name: rpg-timeline-manager
description: Appends session events to the campaign timeline.
---

# RPG Timeline Manager

Use this skill to keep the `content/Timeline.md` updated.

## Instructions

1.  **Input:**
    *   List of "Key Events" from the session recap.
    *   Session Number and Date.

2.  **Action:**
    *   Read `content/Timeline.md`.
    *   Append a new section:
        ```markdown
        ## Sesja {number} ({Date})
        * {Event 1}
        * {Event 2}
        ...
        ```
    *   Save the file.
