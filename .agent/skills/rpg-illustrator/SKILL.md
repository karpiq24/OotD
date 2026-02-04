---
name: rpg-illustrator
description: Generates detailed image prompts and renders images using Nano Banana Pro. Supports Session Recaps, Single Images, and Prompt Generation modes.
---

# RPG Illustrator

Use this skill as the central visual engine for the campaign. It handles prompt engineering, style consistency, and image generation, prioritizing defined `image_prompt` frontmatter from entity files.

## API / Modes
This skill accepts the following parameters:
- **Mode**: One of `["Session Recap", "Single Image", "Prompt Generation"]`.
- **Input Data**:
    - For `Session Recap`: Path to the **Edited** markdown file to process.
    - For `Single Image`: A description string of what to draw.
    - For `Prompt Generation`: A description string of the scene.

## Core Logic (APPLIES TO ALL MODES)

### 1. Context Loading & No Proper Names
- **CRITICAL**: The AI image generator does NOT know who "Versir", "Kyrah", or "Estor" is.
- **Action**: You MUST replace every proper name with its **FULL physical description**.
- **Source Priority**:
    1.  **Check Frontmatter**: If the entity has an `image_prompt` field in its file, USE IT EXACTLY.
    2.  **Fallback**: If no `image_prompt`, read the entity's file (bio/description) and synthesize a physical description.
    3.  **Last Resort**: Generate a generic description based on context.

### 2. Visual Styles
- **Requirement**: Use a defined art style for every image.
- **Allowed Styles**: *High quality digital fantasy art, Dark Fantasy Oil Painting (Frazetta style), Watercolor and Ink, Vibrant Comic Book Style, Stained Glass illustration, Woodcut print, Tarot Card aesthetic, Abstract Ethereal Concept Art, 80s Dark Fantasy Anime, Nouveau Art Style.*
- **Variation**:
    - **Session Recap**: Vary the style between images to keep it visually interesting.
    - **Video/Single**: Stick to the style requested by the caller, or default to *High quality digital fantasy art*.

### 3. Prompt Structure
Every prompt must follow this structure:
`[Detailed Subject Description (No Names)] [Action/Pose]. [Detailed Environment/Setting]. [Lighting/Atmosphere]. [Art Style].`

---

## Workflow 1: Session Recap Mode
**Input**: `Input Data` = Absolute path to the session recap markdown file.

1.  **Read & Parse**: Read the content of the markdown file.
2.  **Scan for Entities**: Identify `[[wikilinks]]` in the text to find relevant entity files for descriptions.
3.  **Generate Prompts**:
    -   **Main Header**: Create 3 distinct prompts representing the overall session themes/events.
    -   **Section Headers**: For *each* `### Header` in the body, create 2 distinct prompts representing that specific section.
4.  **Update File**:
    -   Insert image blocks into the markdown file *immediately* after the headers (Main and Sections).
    -   **Format**:
        ```markdown
        ![The FULL text of the prompt you generated](../assets/sessions/{000}/{filename}.png)
        ```
    -   **Crucial**: The Alt Text (`![...]`) MUST be the **exact, full prompt**. Do NOT shorten it.
    -   **Path**: Use `../assets/sessions/{000}/` relative path.
5.  **Generate Images**:
    -   Call `generate_image` for each prompt.
    -   **Target File**: `content/assets/sessions/{000}/{filename}.png` (Ensure it matches the link).
    -   **Error Handling**: If generation fails, do NOT revert the markdown. The placeholders are valuable.

## Workflow 2: Single Image Mode
**Input**: `Input Data` = Description string.

1.  **Refine Prompt**: Apply Core Logic (No Names -> `image_prompt` or bio, added Style, detailed setting).
2.  **Generate Image**: Call `generate_image`.
3.  **Result**: Return the path to the generated image.

## Workflow 3: Prompt Generation Mode
**Input**: `Input Data` = Description description.

1.  **Refine Prompt**: Apply Core Logic (No Names -> `image_prompt` or bio, detailed setting).
2.  **Result**: Return the **Refined Text Prompt** only.
