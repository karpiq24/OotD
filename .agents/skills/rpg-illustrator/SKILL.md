---
name: rpg-illustrator
description: Generates detailed image prompts and renders images using Nano Banana Pro. Supports Session Recaps, Single Images, and Prompt Generation modes.
---

# RPG Illustrator

Use this skill as the central visual engine for the campaign. It handles prompt engineering, style consistency, and image generation, prioritizing defined `image_prompt` frontmatter from entity files.

## API / Modes
This skill accepts the following parameters:
- **Mode**: One of `["Session Recap - Prompts Only", "Session Recap - Generate Images", "Single Image", "Prompt Generation"]`.
- **Input Data**:
    - For `Session Recap - Prompts Only`: Path to the **Edited** markdown file to process.
    - For `Session Recap - Generate Images`: Path to the session assets folder (`content/assets/sessions/{000}/`).
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

### 2. Prompt Construction & Style
**The prompt must be long and detailed.**

#### Structure
Follow this structure for complex scenes with multiple characters:

```
[General Scene Description: Action, Atmosphere, Lighting]

[Character 1 Description (No Name)]
[Character 2 Description (No Name)]
...

[Background/Environment/Secondary Elements]

[Style/Quality Tags]
```

#### Example of a High-Quality Prompt
```
A chaotic battle scene. In the center, a massive ancient copper dragon with metallic scales and bat-like wings roars, ridden by a spectral figure in obsidian armor conducting with a baton. Facing them are five heroes:
1. young adult male elf with a slender build. He has an angular face with high cheekbones, a sharp jawline, intense dark eyes, and long pointed ears. His shoulder-length, wavy dark brown hair frames his face. He wears layered brown leather armor with intricate silver filigree details over a dark, high-collared tunic. He is equipped with black fingerless leather gloves, an ornate silver pendant with a large cracked dark gemstone, and a single silver diamond-shaped earring.
2. young adult male human wizard with a lean, rugged build. He has intense blue-grey eyes, a strong jawline, a weathered complexion, and a prominent scar across his right cheek. His short, messy dark brown hair is complemented by a full dark brown beard. He wears layered medieval clothing, a rust-brown hooded tunic over a coarse off-white linen shirt, with a thick brown leather shoulder strap and buckle. Two bronze circular geometric star emblems are visible on his chest.
3. powerful male minotaur with a muscular build, broad shoulders, and brown fur. His bovine head features large, curved dark grey horns, piercing glowing blue eyes, and a bull snout. He has stylish, thick blonde hair swept back and a well-groomed blonde fur beard. He is dressed in a draped white toga with an ornate red sash featuring carved patterns and a textured grey shoulder strap.
4. male fantasy warrior with an athletic build and elven features. He wears highly ornate golden plate armor with intricate filigree in a Greco-Roman spartan style. His head is covered by a full golden Corinthian helmet with a large yellow and black plume, from which his glowing orange eyes peer out. He wears a dark blue cloth hood and cape over layered golden pauldrons. His attire is completed by a leather belt with multiple pouches, a gold ornamental bird-head buckle, a blue loincloth with white embroidered patterns, a quiver of arrows, and a round wooden shield.
5. young adult male with a dark fantasy aesthetic. He has a slender build, pale alabaster skin, and short blonde hair styled in a messy quiff. His face is defined by a strong jawline, high cheekbones, and piercing cyan eyes, often held in a confident smirk. large, jagged scar runs along the side of his neck and jaw. He wears a dark blue or black high-collared jacket and a single black leather glove.

In the background, a powerful lizardfolk with a lightning staff and a medusa archer can be seen. The background is filled with cheering spectral spectators. Dramatic lighting, magical effects, intense action. High quality digital fantasy art.
```

### 3. Visual Styles
- **Allowed Styles**: *High quality digital fantasy art, Dark Fantasy Oil Painting (Frazetta style), Watercolor and Ink, Vibrant Comic Book Style, Stained Glass illustration, Woodcut print, Tarot Card aesthetic, Abstract Ethereal Concept Art, 80s Dark Fantasy Anime, Nouveau Art Style.*

### 4. Character Inclusion & Context (CRITICAL)
- **Do NOT Include Everyone**: Only include characters that are *essential* to the specific scene. If a scene focuses on 2 characters, do not list all 5 party members just because they exist.
- **Mandatory Context**: If you include a character, you **MUST** specify where they are and what they are doing in the scene.
    - ❌ WRONG: `1. hero (Versir): [description]`
    - ✅ CORRECT: `1. hero (Versir): kneeling on the floor, screaming in anger. [description]`
    - ✅ CORRECT: `2. hero (Felicjan): standing in the background, observing silently with crossed arms. [description]`

---

## Workflow 1a: Session Recap - Prompts Only
**Input**: `Input Data` = Absolute path to the session recap markdown file.

Use this mode to generate and save all image prompts without rendering any images yet. Intended as the first phase before user review.

1.  **Read & Parse**: Read the content of the markdown file.
2.  **Scan for Entities**: Identify `[[wikilinks]]` in the text to find relevant entity files for descriptions.
3.  **Generate Prompts**:
    -   **Main Header**: Create 3 distinct prompts representing the overall session themes/events.
    -   **Section Headers**: For *each* `### Header` in the body, create 1 prompt representing that specific section.
4.  **Save Prompts**:
    -   Save each **Full Refined Prompt** to a text file: `content/assets/sessions/{000}/{filename}.txt`.
5.  **Update File**:
    -   Insert image placeholder blocks into the markdown file *immediately* after the headers (Main and Sections).
    -   **Format**:
        ```markdown
        ![{Short Description of Scene}](../assets/sessions/{000}/{filename}.png)
        [Prompt](../assets/sessions/{000}/{filename}.txt)
        ```
    -   **Alt Text**: Use a short, readable description in **Polish** (e.g., "Bitwa na Arenie", "Spotkanie z Zarządcą"). Do NOT put the full prompt here.
    -   **Path**: Use `../assets/sessions/{000}/` relative path.
6.  **Stop here.** Do NOT call `generate_image`. Return a summary of all saved `.txt` file paths so the user knows what to review.

## Workflow 1b: Session Recap - Generate Images
**Input**: `Input Data` = Path to the session assets folder (`content/assets/sessions/{000}/`).

Use this mode after the user has reviewed and approved the prompts. It reads every `.txt` file in the assets folder and renders the corresponding image.

1.  **Find Prompts**: List all `.txt` files in the given assets folder.
2.  **Generate Images**:
    -   For each `.txt` file, read its content and call `generate_image`.
    -   **Target File**: Same path as the `.txt` file but with `.png` extension.
    -   **Error Handling**: If generation fails, do NOT revert the markdown. The placeholders remain valuable — skip the failed image and continue.

## Workflow 2: Single Image Mode
**Input**: `Input Data` = Description string.

1.  **Refine Prompt**: Apply Core Logic (No Names -> `image_prompt` or bio, added Style, detailed setting, SOTA structure).
2.  **Generate Image**: Call `generate_image`.
3.  **Result**: Return the path to the generated image.

## Workflow 3: Prompt Generation Mode
**Input**: `Input Data` = Description description.

1.  **Refine Prompt**: Apply Core Logic (No Names -> `image_prompt` or bio, detailed setting, SOTA structure).
2.  **Result**: Return the **Refined Text Prompt** only.
