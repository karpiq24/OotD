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

## Step 3: Finalization (Wikilinks & Visuals)
1.  **Link Entities**:
    *   Activate skill `rpg-wiki-manager`.
    *   Search for entity names in the text.
    *   Replace with `[[wikilinks]]`.
    *   Save the file.
2.  **Visuals**:
    *   Activate skill `rpg-illustrator`.
    *   Generate prompts (prioritizing `image_prompt` frontmatter from linked entities).
    *   Generate Images -> Insert into file -> Move to `content/assets/sessions/{000}/`.
3.  **Timeline & Context**:
    *   Activate skill `rpg-timeline-manager`.
    *   Append Key Events to `content/Timeline.md`.
    *   Update concise summary in `content/Campaign_Context.md`.
4.  **Video Scripts**:
    *   Activate skill `rpg-video-scripter`.
    *   Generate video prompts to `content/06-Video-Scripts/`.

## Step 4: Completion
1.  **Notify User**: "Session {number} recap finalized! Verified wikilinks, images generated, timeline updated, and video scripts created."
