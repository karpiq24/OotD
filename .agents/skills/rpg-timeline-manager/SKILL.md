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
    *   **Style** (matches the audited timeline): 3–7 bullets per session, only the events that matter later (deaths, alliances, artefacts won or lost, major reveals, changes of ruler); no blow-by-blow battle detail and no bold walls of text. `* ` bullets, Polish nominal phrases ("Pokonanie…", "Odkrycie…", "Śmierć…"), wikilinks to existing pages, heroes by full file name with alias. Every bullet must come from the recap, with the right actor (who killed whom). Prose by `campaign/proza.md` section A (no epithets such as „potężny”, no commentary).
    *   **Date**: take it from the recap's `**Data:**`. When `content/assets/sessions/{000}/chat_log.json` exists, its message timestamps give the real play date — if the two disagree, tell the user (in the audit, S44 and S47 had wrong years and S20's chat log turned out to be a copy of S19's).

3.  **Action 2: Update Campaign Context:**
    *   Read `content/Campaign_Context.md`.
    *   Locate the "Oś Czasu i Kluczowe Wydarzenia" section.
    *   Find the appropriate chapter (e.g., "Wojna o Thyleę").
    *   If the session fits an existing group (e.g., "S69-S71"), update that line.
    *   Otherwise, add a new bullet point:
        `* **{Topic} (S{number}):** {Summary}`
    *   Ensure the session range in the chapter header is up to date (e.g., update `(Sesje 56-68)` to `(Sesje 56-72)` if applicable). These `### Name: subtitle (Sesje X-Y)` headings are the story arcs the wiki's Sessions page groups its cards by, so keep exactly that form (a one-session arc is `(Sesja 84)`); a session outside every range lands under "Pozostałe sesje". Start a new arc heading when the story clearly moves to a new chapter, and tell the user.
    *   **Keep the character and faction entries current**: if the session killed, crowned, freed, imprisoned or turned someone listed under "Ważne Postacie" / "Frakcje", update that entry too (present tense = state now; finished goals in past tense). The file is the summary rpgnotes reads, so a stale entry ("obecnie więzień drużyny" for someone already dead) misleads the next draft.
    *   Save the file.
