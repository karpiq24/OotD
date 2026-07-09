---
name: rpg-timeline-manager
description: Appends session events to the campaign timeline.
---

# RPG Timeline Manager

Use this skill to keep the `content/Timeline.md` and `content/Campaign_Context.md` updated.

## Instructions

1.  **Input:**
    *   List of "Key Events" from the session recap.
    *   Session Number and Date.
    *   A concise, one-sentence summary for the campaign context.

2.  **Action 1: Update Detailed Timeline:**
    *   Read `content/Timeline.md`.
    *   Append a new section:
        ```markdown
        ## Sesja {number} - {Title} ({Date})
        * {Event 1}
        * {Event 2}
        ...
        ```
    *   Save the file.

3.  **Action 2: Update Campaign Context:**
    *   Read `content/Campaign_Context.md`.
    *   Locate the "Oś Czasu i Kluczowe Wydarzenia" section.
    *   Find the appropriate chapter (e.g., "Wojna o Thyleę").
    *   If the session fits an existing group (e.g., "S69-S71"), update that line.
    *   Otherwise, add a new bullet point:
        `* **{Topic} (S{number}):** {Summary}`
    *   Ensure the session range in the chapter header is up to date (e.g., update `(Sesje 56-68)` to `(Sesje 56-72)` if applicable).
    *   Save the file.
