---
name: rpg-video-scripter
description: Generates video script PROMPTS only (no images) tailored for Google Flow workflows.
---

# RPG Video Scripter (Google Flow Edition)

Use this skill to create a highly structured video script file. This script is designed so the User can easily copy and paste prompts directly into Google Flow, step-by-step, utilizing Flow's specific UI features (First Frame, Veo Video Generation, Expand, Camera, Ingredients, Scene Creator).

## Instructions

1.  **Input:**
    *   Session Recap file (markdown).
    *   List of "Key Events" (or select top 3-6 dramatic moments).

2.  **Prompt Generation (DELEGATED via `rpg-illustrator`):**
    *   **Action**: For every major key event, you MUST call the `rpg-illustrator` skill in **"Prompt Generation" Mode** to create the foundation for a **Clip**.
    *   **Input**: Provide a description of the event to the skill.
    *   **Output**: The skill returns a fully refined image prompt (NO proper names, uses physical descriptions, consistent style, verbatium `image_prompt`).
    *   **Do NOT** manually reconstruct character descriptions or styles here. Trust the `rpg-illustrator` output. We will use this output as the "First Frame" (Rozpocznij) image prompt.

3.  **Select Art Style (CONSISTENCY REQUIRED):**
    *   **Choose ONE art style** for the entire script. All clips MUST adhere to it.
    *   **Allowed Styles**: *High quality digital fantasy art, Dark Fantasy Oil Painting (Frazetta style), Watercolor and Ink, Vibrant Comic Book Style, Stained Glass illustration, Woodcut print, Tarot Card aesthetic, Abstract Ethereal Concept Art, 80s Dark Fantasy Anime, Nouveau Art Style, Cinematic photorealistic fantasy.*

4.  **Google Flow Workflow Structure:**
    *   Google Flow uses a specific pipeline: Generate Image -> Use as First Frame -> Generate Video Clip -> Expand/Edit -> Combine Clips in Scene Creator into a final **Scene**.
    *   Structure the script so the user can easily copy/paste prompts for each step of this pipeline.

    *   **Phase A: First Frame Generation (Image)**
        - Shows the **BEGINNING STATE** of the clip, **BEFORE** the main action occurs.
        - The user will generate this using models *Nano Banana 2*.
        - The prompt is exactly what `rpg-illustrator` gave you (environment + lighting + character states).
    
    *   **Phase B: Base Video (Action)**
        - Describes the **TRANSFORMATION/ACTION** occurring in the clip perfectly hooked to the Start Frame.
        - Create a cinematic Veo prompt describing exactly what moves. **Crucially, Veo clips are exactly 8 seconds long by default**, so pace the action to fit this timeframe.
        - **Camera Instructions**: Provide an explicit Google Flow Camera Suggestion (e.g., *Pan: Left, Tilt: High, Motion: Orbit, Dolly Zoom / Najazd kamerą*).
        - **Audio & Dialogue**: Veo clips generate embedded audio automatically. Provide descriptions for consistent background sounds. If needed, include **Polish dialogue** and a description of the voice tone (e.g., "Męski, chropowaty głos...").
        - **Transitions**: NEVER use "cut to". Videos are continuous shots.

    *   **Phase C: Flow Refinement (Optional per clip)**
        - **Expand (Rozszerz)**: If the action is too complex/long for one 8s generation, provide a secondary prompt for the "What next? (Co dalej?)" text field in the video editor.
        - **Ingredients (Składniki)**: If a specific character must remain perfectly consistent across clips, suggest saving them as an Ingredient to attach using `@`.

5.  **Output Format:**
    *   Create a file: `content/assets/sessions/{000}/video_script.txt` (where `{000}` is the 3-digit session number).
    *   Format structure:

        ```markdown
        # Video Script: Sesja {number}
        
        **Art Style Set**: {Selected Art Style}
        **Global Ingredients** (Składniki): {Suggest any characters or recurring items that should be saved as 'Składniki' in Flow for consistency}
        
        ---
        
        ## Clip 1: {Event Name}
        
        ### Step 1: First Frame (Static Image)
        *Model Suggestion: Nano Banana 2*
        **Prompt (Copy this)**:
        > [Insert the EXACT, detailed output from rpg-illustrator here. High quality, full character descriptions, lighting, environment, etc.]
        
        ### Step 2: Base Video (Action & Audio)
        *Model: Veo 3.1 - Fast | Tool: Set Video 'Rozpocznij' frame using image from Step 1*
        *Camera Suggestion: [e.g., Static / Najazd kamerą (Zoom In) / Orbituj]*
        **Action Prompt (Copy this)**:
        > [Describe the cinematic action and movement based on the first frame. Remember it's an 8-second continuous shot. E.g., The man in armor stands up and slowly raises his glowing sword. Dust particles swirl in the air.]
        
        **Audio & Dialogue Prompt (Optional)**:
        > [Background sounds: e.g., Mroźny wiatr i wycie wilków. / Dialogue (Polish): e.g., Kobieta o delikatnym, zimnym głosie szepcze: "Zima nadeszła."]
        
        ### Step 3: Expand / Rozszerz (Optional)
        *Use when in the video player/editor after generating Step 2*
        **Action Continuation Prompt (Co dalej?)**:
        > [E.g., An explosive blue shockwave ripples out from the raised sword, shattering the ground around him.]

        ---
        
        ## Clip 2: ...
        ```
    *   **Constraint**: Do NOT generate actual images or videos. Process text only. At the end, remind the user to load these **Clips** into the "Kreator Scen" (Scene Creator) timeline to combine them into the final **Scene**!
