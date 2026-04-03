---
name: rpg-video-scripter
description: Generates a structured video script with integrated prompts for Google Flow (Veo/Nano).
---

# RPG Video Scripter (Google Flow Edition)

Use this skill to create a highly structured video script file (`video_script.txt`). This script is optimized for Google Flow, allowing the user to quickly copy-paste prompts for high-quality AI video generation.

## Core Rules

1.  **Single Video Prompt**: Combine all scene information into one single English text block.
    *   **Include**: Action descriptions, Camera movement instructions (e.g., "The camera orbits clockwise..."), Lighting, Atmosphere, and Sound descriptions.
    *   **Dialogue**: Use **Polish** ONLY for actual character speech (e.g., "...as the knight yells: 'Za Thyleę!' while charging..."). All other descriptions must be in English.
    *   **Pacing**: Veo clips are exactly **8 seconds**, so describe actions that fit this duration. Avoid "cut to"; describe continuous motion.

2.  **Clip Methods (Mutually Exclusive)**: For each clip, you must propose exactly ONE method:
    *   **Method A: First Frame (Image-to-Video)**: Generate a static image first (using `rpg-illustrator`), then set it as the `Start Frame` in Veo. This is best for complex character details or specific starting compositions.
    *   **Method B: Ingredients (Text-to-Video with @refs)**: Generate the video directly from text. Reference saved characters/items using `@IngredientName`. This is best for dynamic movement or when characters are already defined in the user's Flow library.

3.  **Visual Prompting (DELEGATED)**:
    *   **Action**: For every clip, you MUST call the `rpg-illustrator` skill in **"Prompt Generation" Mode** to get character and environment descriptions.
    *   **First Frame (Method A)**: Use the `rpg-illustrator` output verbatim for the image prompt.
    *   **Ingredients (Method B)**: Use the `rpg-illustrator` output but replace character names with `@IngredientName` tags in the consolidated video prompt.

4.  **Ingredient Generation Rules**:
    *   When the output asks to define an Ingredient (`@Name`), provide a **full image prompt** for that ingredient in the `Global Ingredients` section:
    *   **Character Ingredients**: Prompt = [Character Description] + "isolated on a simple one color background (grey or white background), no environment".
    *   **Place/Environment Ingredients**: Prompt = [Environment Description] + "empty, no characters, no people".
    *   **Style**: Always include the session's art style in these ingredient prompts.

5.  **Art Style Consistency**: Choose ONE art style for the entire session (e.g., *Arcane Studio Fortiche style*, *80s Dark Fantasy Anime*, *Dark Fantasy Oil Painting (Frazetta style)*) and apply it to every prompt. Never choose photorealistic style.

## Output Format

Create the file: `content/assets/sessions/{000}/video_script.txt` (where `{000}` is the 3-digit session number).

### Template Structure:

```markdown
# Video Script: Sesja {number} - {Title}

**Art Style**: {Selected Style}

**Global Ingredients (Składniki)**:
*   **@IngredientName**:
    *   *Role*: {Character/Location}
    *   *Prompt (Copy and paste to create ingredient)*:
{Full refined prompt based on Rule 4}

---

## CLIP 1: {Event Name}
**Method**: {Method A: First Frame | Method B: Ingredients}

### STEP 1: {Setup - e.g., Generate First Frame}
**Prompt to copy (for Step 1 image)**:
[Refined prompt from rpg-illustrator - used for Image Generation in Method A, or as the character baseline for Method B]

### STEP 2: VIDEO GENERATION (8 Seconds)
*Model: Veo 3.1 - Fast | Motion: 5 | [Set Image from Step 1 as Start Frame (Method A only)]*

**Consolidated Video Prompt to copy (for Step 2 video)**:
[One single block containing: Action + Camera Movement + Atmosphere + Sound + Polish Dialogue. English only, except for Polish speech. Use @IngredientName markers if Method B.]

### STEP 3: EXPAND / ROZSZERZ (Optional)
**Continuation Prompt to copy (for Expand/Co dalej?)**:
[Brief 8-second follow-up action for the Expand tool if the scene needs more time.]

---
```

## Instructions for the Agent

1.  **Identify or Receive Scenes**:
    *   **Case A (Default)**: Identify 3-6 key dramatic moments from the session recap.
    *   **Case B (User-Specified)**: If the user provides a specific scene description, prompt, or list of moments, **use those instead**.
2.  **Propose a Clip Method** (A or B) for each, balancing visual detail (Method A) with fluid character movement (Method B).
3.  **Call `rpg-illustrator`** in "Prompt Generation" Mode for each clip to get high-quality descriptions.
4.  **Write the Consolidated Video Prompt** ensuring it hits all requirements (Camera, Audio, Polish Dialog).
5.  **Save the file** and remind the user to load these into the "Kreator Scen" (Scene Creator) timeline to build the final scene.
