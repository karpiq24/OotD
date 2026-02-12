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
    1.  **Check Frontmatter**: If the entity has an `image_prompt` field in its file, **COPY IT VERBATIM**. 
        -   **CRITICAL RULE**: Do **NOT** summarize, shorten, paraphrase, or "optimize" this text. 
        -   **IGNORE LENGTH**: Even if the description is very long, you MUST include the ENTIRE text. Consistency depends on this specific phrasing.
        -   **ONLY ADAPT**: You may only add specific action verbs or held items (e.g., "holding a sword" or "casting a spell") to the end or beginning of the description, but do NOT remove any physical details.
    2.  **Fallback**: If no `image_prompt`, read the entity's file (bio/description) and synthesize a **detailed** physical description including: race, build, facial features, hair color/style, eye color, clothing, armor, weapons, accessories, and any distinguishing marks.
    3.  **Last Resort**: Generate a detailed description based on context, but include at least 5 specific visual attributes.

#### Example - WRONG vs CORRECT:
- ❌ WRONG: "a human wizard", "an aasimar paladin"
- ✅ CORRECT: "a young adult male human wizard with a lean, rugged build...", "a pale male with blonde hair and piercing cyan eyes..."

### 2.1. Forbidden Terms
- **Do NOT use**: "Aasimar", "Tiefling", "Genasi", or other D&D-specific race names that models might misconstrue.
- **Instead**: Describe the visual traits (e.g., "pale skin, glowing eyes" instead of "Aasimar").

#### Quick Reference - Main PCs:
Before generating any prompt with PCs, **READ** their entity files and copy the `image_prompt` field exactly.

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
4.  **Save Prompt**:
    -   Save the **Full Refined Prompt** to a text file: `content/assets/sessions/{000}/{filename}.txt`.
5.  **Update File**:
    -   Insert image blocks into the markdown file *immediately* after the headers (Main and Sections).
    -   **Format**:
        ```markdown
        ![{Short Description of Scene}](../assets/sessions/{000}/{filename}.png)
        [Prompt](../assets/sessions/{000}/{filename}.txt)
        ```
    -   **Alt Text**: Use a short, readable description in **Polish** (e.g., "Bitwa na Arenie", "Spotkanie z Zarządcą"). Do NOT put the full prompt here.
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
