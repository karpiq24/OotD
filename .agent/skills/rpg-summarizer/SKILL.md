---
name: rpg-summarizer
description: Generates a narrative session recap from a transcript, using campaign context.
---

# RPG Summarizer

Use this skill to convert a raw transcript into a narrative story based on the campaign's specific writing style.

## Instructions

1.  **Context Loading (Smart Search):**
    *   **Scan** the transcript for proper names (People, Locations).
    *   **Search** the `content/` directory for files matching these names.
    *   **Read** the matched files to understand who they are (Bio, History).
    *   **Read** the last 3 session files in `content/01-Sessions/` to understand recent events.

2.  **Load System Prompt:**
    *   Read `.agent/skills/rpg-summarizer/resources/summary_prompt.txt`.
    *   Follow the tone, structure, and formatting rules (flowery language, specific headers).

3.  **Generation:**
    *   Convert the transcript into a narrative summary.
    *   **Constraint**: Do NOT generate `[[wiki links]]` yet. Plain text only.
    *   **Constraint**: Use the structure defined in `templates/Session.md`.

4.  **Output:**
    *   Return the generated Markdown content. Do not save to a file yet (the workflow handles that).
