---
name: rpg-video-scripter
description: Generates video script PROMPTS only (no images) for session events.
---

# RPG Video Scripter

Use this skill to create a video script file with prompts for Google Veo, based on session events.

## Instructions

1.  **Input:**
    *   Session Recap file (markdown).
    *   List of "Key Events" (or select top 3-6 dramatic moments).

2.  **Pre-Generation (CRITICAL):**
    *   **Read entity files**: For EVERY character that will appear in the prompts, read their wiki file and extract the `image_prompt` field from frontmatter.
    *   **Copy verbatim**: Do NOT summarize or shorten these descriptions. Use them exactly as written.
    *   **No proper names**: The video generator does not know who "Versir" or "Felicjan" is. Replace all names with their full visual descriptions.

3.  **Select Art Style (CONSISTENCY REQUIRED):**
    *   **Choose ONE art style** for the entire script. All scenes MUST use the same style.
    *   Select a style that best fits the session's mood and themes.
    *   **Allowed Styles**: *High quality digital fantasy art, Dark Fantasy Oil Painting (Frazetta style), Watercolor and Ink, Vibrant Comic Book Style, Stained Glass illustration, Woodcut print, Tarot Card aesthetic, Abstract Ethereal Concept Art, 80s Dark Fantasy Anime, Nouveau Art Style, Cinematic photorealistic fantasy.*
    *   Note: Different sessions may use different styles, but within a single script all scenes must be consistent.

4.  **Generation:**
    *   For each selected event, create a **Script Entry**.
    *   **Start Frame Image Prompt**: 
        - Shows the **BEGINNING STATE** of the scene, **BEFORE** the main action occurs.
        - Include the FULL `image_prompt` for each character **already present** at the start.
        - Do NOT include characters/elements that appear DURING the video action.
        - Combine with scene description, environment, lighting, and the **selected art style**.
        - Example: If scene is "Lutheria arrives", Start Frame shows arena WITHOUT Lutheria, maybe with rift forming.
    *   **Veo Video Prompt**: 
        - Describes the **ACTION** that transforms the scene from Start Frame to end state.
        - Create a cinematic prompt (e.g., "Cinematic wide shot of [FULL Description] [Action]...").
        - **TRANSITIONS (CRITICAL)**: **NEVER use "cut to"**. The camera must **transition smoothly** (pan, tilt, zoom, dolly, track) between subjects or angles. The video is a continuous shot.
        - **DURATION**: Do NOT include specific durations (e.g., "10 seconds") in the prompt text.

5.  **Output:**
    *   Create a file: `content/assets/sessions/{000}/video_script.md` (where `{000}` is the 3-digit session number).
    *   Format:
        ```markdown
        # Video Script: Sesja {number}
        
        **Art Style**: {Selected Art Style}
        
        ## Scene 1: {Event Name}
        **Start Frame Prompt**: {Detailed Image Prompt with FULL character descriptions and art style}
        **Video Prompt**: {Veo Video Prompt with FULL character descriptions}
        
        ## Scene 2...
        ```
    *   **Constraint**: Do NOT generate actual images or videos. Text only.

## Example Character Description (DO NOT SHORTEN):
Instead of: "a pale young man in a dark jacket"
Use: "young adult male with a dark fantasy aesthetic, slender build, pale alabaster skin, short blonde hair styled in a messy quiff, face defined by a strong jawline, high cheekbones, and piercing cyan eyes, often held in a confident smirk, large jagged scar runs along the side of his neck and jaw, wearing a dark blue high-collared jacket and a single black leather glove"

