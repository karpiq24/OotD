---
name: rpg-video-scripter
description: Generates video script PROMPTS only (no images) for session events.
---

# RPG Video Scripter

Use this skill to create a video script file with prompts for Google Veo, based on session events.

## Instructions

1.  **Input:**
    *   Session Recap file (markdown).
    *   List of "Key Events" (or select top 3 dramatic moments).

2.  **Generation:**
    *   For each selected event, create a **Script Entry**.
    *   **Start Frame Image Prompt**: Use `rpg-illustrator` logic (resolve `image_prompt` frontmatter) to create a detailed static image description.
    *   **Veo Video Prompt**: create a cinematic prompt for the video generation (e.g., "Cinematic wide shot of [Description] [Action]...").

3.  **Output:**
    *   Create a file: `content/06-Video-Scripts/Sesja_{number}_Script.md`.
    *   Format:
        ```markdown
        # Video Script: Sesja {number}
        
        ## Scene 1: {Event Name}
        **Start Frame Prompt**: {Detailed Image Prompt}
        **Video Prompt**: {Veo Video Prompt}
        
        ## Scene 2...
        ```
    *   **Constraint**: Do NOT generate actual images or videos. Text only.
