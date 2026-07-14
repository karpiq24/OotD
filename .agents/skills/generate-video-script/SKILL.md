---
name: generate-video-script
description: On-demand generation of a paste-ready Google Flow video script from an existing session recap. Invoke explicitly as /generate-video-script — never runs automatically as part of the recap pipeline.
---

# Generate Video Script

This skill is invoked explicitly (`/generate-video-script`), never automatically. It owns the entire interaction with the user; no other skill calls it.

## Step 1: Initialization
1.  Ask the user for the `session_number`.
2.  **Locate** the recap file: `content/01-Sessions/Sesja {number} - *.md`.
    *   If multiple files match, ask the user to clarify.
    *   If no file matches, error out.

## Step 2: Context Loading
1.  **Read** the session recap file in full.
2.  **Verify** content is loaded.

## Step 3: Generate the Script
1.  Activate skill `rpg-video-scripter`.
2.  Input: path to the session recap markdown file.
3.  The skill interactively asks the user the two design questions (script focus mode, art style), then generates the script.
4.  The skill saves the output to `content/assets/sessions/{NNN}/video_script.md` (surfaced automatically under **Metadane** by the `SessionAssets` transformer — no frontmatter link needed), runs `python3 scripts/update_indexes.py`, and echoes the clip prompts in chat.

## Step 4: Completion
1.  **Notify User**: "Video script for Session {number} generated at `content/assets/sessions/{NNN}/video_script.md` (auto-listed under Metadane on the recap). Clips are echoed above — copy any block directly into Google Flow."
