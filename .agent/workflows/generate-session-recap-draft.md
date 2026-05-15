---
description: Generates a session recap draft from a transcript (Part 1 of 2).
---

# Generate Session Recap Draft Workflow

This workflow processes a raw transcript into a markdown draft.

## Step 1: Initialization
1.  Ask the user for the `session_number`.
2.  Confirm the input files exist:
    *   `input/transcript.txt` (Required)
    *   `input/chat_log.json` (Optional)
    *   `input/transcript.json` (Optional)

## Step 2: Asset Management
1.  **Directory**: Create `content/assets/sessions/{000}/` (padded 3 digits).
2.  **Move Files**:
    *   Move `input/transcript.txt` -> `content/assets/sessions/{000}/transcript.txt`
    *   If present, move `input/chat_log.json` -> `content/assets/sessions/{000}/chat_log.json`
    *   If present, move `input/transcript.json` -> `content/assets/sessions/{000}/transcript.json`

## Step 3: Context Loading & Analysis
1.  **Line Count**: Run `wc -l content/assets/sessions/{000}/transcript.txt` to get the total line count — the skill needs this to plan chunks.
2.  **Build canonical glossary**: Run `.venv/bin/python scripts/extract_glossary.py content/assets/sessions/{000}/transcript.txt`. The stdout is the session-specific canonical-names list (filtered to names that appear in this transcript). Pass it verbatim into every chunk subagent prompt.
3.  **Read phonetic corrections**: `.agent/skills/rpg-summarizer/resources/phonetic_corrections.md` — list of known ASR misspellings. Pass verbatim into every chunk subagent prompt too.
4.  **Read** the last 3 session files in `content/01-Sessions/` to understand the current narrative arc. Do NOT load all transcript dialogue into your context — the rpg-summarizer skill handles the full text via chunk subagents.

## Step 4: Draft Generation (Text Only)
1.  **Activate** skill `rpg-summarizer`.
2.  **Generate** the draft using `templates/Session.md`.
    *   Fill `title`, `number`, `Date`.
    *   Fill frontmatter links (files are now in assets).
    *   Fill `Narrative Summary` and Lists.
    *   **NO** Wikilinks at this stage.
    *   **NO** Images at this stage.
3.  **Save** the draft to `content/01-Sessions/Sesja {number} - {Title}.md`.

## Step 5: Completion & Review Reminder
1.  **Notify User**: "Draft created at `content/01-Sessions/Sesja {number} - {Title}.md`. Please review the text, make edits as needed, and then run `/finalize-session-recap` to generate wikilinks, images, and other assets."