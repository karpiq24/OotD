---
description: Generates wikilinks, images, timeline events, and video scripts for a session recap draft.
---

# Finalize Session Recap Workflow

This workflow processes a user-reviewed session recap draft, adding wikilinks, images, and other assets.

## Step 1: Initialization
1.  Ask the user for the `session_number`.
2.  **Locate** the draft file: `content/01-Sessions/Sesja {number} - *.md`.
    *   If multiple files match, ask the user to clarify.
    *   If no file matches, error out.

## Step 2: Context Loading
1.  **Read** the *User-Edited* file: `content/01-Sessions/Sesja {number} - ... .md`.
2.  **Verify** content is loaded.

## Step 3: Finalization (Wikilinks, Prompts, Timeline, Scripts)
1.  **Link, Update and Create Entities**:
    *   Activate skill `rpg-wiki-manager`.
    *   Search for entity names in the text.
    *   Replace with `[[wikilinks]]`.
    *   Update any target entities with new information.
    *   Create any new characters, locations etc.
    *   Save the file.
2.  **Generate Image Prompts**:
    *   Activate skill `rpg-illustrator` with mode `Session Recap - Prompts Only`.
    *   Input: path to the session markdown file.
    *   The skill generates prompts, saves them as `.txt` files in `content/assets/sessions/{000}/`, and inserts placeholder image links into the markdown.
3.  **Timeline & Context**:
    *   Activate skill `rpg-timeline-manager`.
    *   Append Key Events to `content/Timeline.md`.
    *   Update concise summary in `content/Campaign_Context.md`.
4.  **Video Scripts**:
    *   Activate skill `rpg-video-scripter`.
    *   Generate video prompts to `content/06-Video-Scripts/`.

## Step 4: Prompt Review (User Gate)
1.  **Notify User**: "Image prompts are ready for review in `content/assets/sessions/{000}/`. Open the `.txt` files and check each scene description. Edit any you want changed, then reply to generate the actual images."
2.  **Wait** for explicit user confirmation before proceeding.

## Step 5: Image Generation
1.  **Generate Images**:
    *   Activate skill `rpg-illustrator` with mode `Session Recap - Generate Images`.
    *   Input: `content/assets/sessions/{000}/`.
    *   The skill renders a `.png` for every `.txt` prompt file in that folder.

## Step 6: Completion
1.  **Notify User**: "Session {number} recap finalized! Wikilinks applied, images generated, timeline updated, and video scripts created."