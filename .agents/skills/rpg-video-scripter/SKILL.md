---
name: rpg-video-scripter
description: Generates a paste-ready, per-clip video script for Google Flow (Gemini Omni/Veo) from a session recap. Each clip prompt is fully self-contained — no cross-references, no assembly required.
---

# RPG Video Scripter

Use this skill to translate a D&D session recap into a video script the user can copy-paste, clip by clip, straight into Google Flow. Every clip prompt is **self-contained**: full physical descriptions, location, action, camera, lighting, and art style are all inlined into the one block. There is no "asset setup" step, no `@Tags`, and no cross-referencing between clips — Flow takes one prompt at a time and each one must stand on its own.

## Input Parameters
- **Session Recap File**: Absolute path to the session recap markdown file (e.g. `content/01-Sessions/Sesja 74 - Matka Smoków.md`).
- **Mode Selection**: Decided interactively with the user:
  - **Highlights Mode**: Capture 3 to 10 of the most memorable clips spanning the entire session's events.
  - **Single Event Mode**: Capture a sequence of 3 to 10 shots mapping a specific dramatic scene or battle from beginning to end.
- **Art Style Selection**: Decided interactively with the user from 3 curated suggestions.

---

## Step 1: Parse the Session Recap, Character, & Location Lists
1. Read the session recap file. Extract key sections (using `###` headers) and dramatic event candidates (e.g., specific battles, discoveries, or deaths).
2. Identify all characters (Bohaterowie/NPCs) and locations featured in the recap or sections.
3. For each identified character, locate their markdown file in the wiki (e.g., in `content/02-People/Bohaterowie/` or `content/02-People/NPCs/`). Read their frontmatter to extract `image_prompt`, `character_personality`, and `voice_characteristics`.
4. For each identified location, locate their markdown file in the wiki (e.g., under `content/03-Locations/`). Read their frontmatter to extract `image_prompt`.
5. **Fallback Generation Rules**:
   - If any character or location fields are missing or empty in their wiki frontmatter:
     - **Thoroughly search session recaps** (using grep or file searches on files in `content/01-Sessions/`) to harvest additional context about how they were described, what actions occurred there, key atmosphere traits, and quotes.
     - Combine the findings from the wiki entity file with these harvested details.
     - **Character Image Prompt Fallback**: Synthesize a detailed, long physical description (at least 5 distinct visual attributes) based on their bio, race, gender, role, and any physical descriptions or action contexts harvested from the session recaps.
     - **Character Personality Fallback**: Synthesize a detailed paragraph describing their traits, behavior, motivations, and temperament, enriched with their key decisions found in the session recaps.
     - **Character Voice Characteristics Fallback**: Deduce and write a highly specific voice profile (tone, speed, pitch, accent) informed by their dialogue style and quotes found in session recaps.
     - **Location Image Prompt Fallback**: Synthesize a detailed, long environmental description (at least 5 distinct visual attributes) detailing the architecture, landscape, color palette, lighting (e.g. dramatic, dark, bioluminescent), mood, and materials, drawing directly from the wiki bio and harvested session recap contexts.
6. These resolved (or fallback-synthesized) descriptions are the raw material you will inline verbatim into clip prompts in Step 4 — do not paraphrase a real `image_prompt`.

---

## Step 2: Interactive Prompting (User Decision Gate)

This skill asks **exactly two questions**, then generates the script. No other interactive gates.

### Question 1: Script Focus Mode
List the extracted key event candidates in chat, then ask:
- "Should the script be a **Highlights** video of memorable moments across the entire session, or should it focus on **One Specific Event**?"
- Provide the list of extracted sections/events. If the user selects a specific event, focus the entire script on detailing that event sequentially, beginning to end.

### Question 2: Video Art Style
Analyze the session's thematic context, environments, and overall emotional tone. Present exactly **3 curated art style options** plus a free-text option:
- **Option 1 (always)**: **Arcane (League of Legends / Fortiche Studio style)**: Masterful mix of 3D rendering and hand-painted 2D textures, dramatic theatrical lighting, sharp graphic outlines, highly stylized anatomy, and rich, dynamic brushstrokes.
- **Options 2–3**: Two distinct art styles fitted specifically to this session's narrative and mood (e.g. a grimdark painterly style for a tragedy-heavy session, a vibrant storybook style for a whimsical one). For each, give a catchy name and a one- or two-sentence description of its visual attributes.
- **Free-text option**: "Or describe your own art style."

Do not generate more than 3 curated options — this is a quick choice, not a research exercise.

---

## Step 3: Clip Physics (Hard Constraints)

Every clip must obey these limits, because they map to how Flow/Veo actually generates:

1. **Duration**: target ~8 seconds per clip. One continuous action per clip — no scene cuts, no montage, no "then" transitions inside a single prompt.
2. **Cast size**: at most 2 fully-described characters per clip. More than 2 degrades generation quality. If a moment involves more people, pick the 1–2 focal characters and reduce everyone else to unnamed background description (e.g. "a cluster of soldiers in the background") — never fully describe a third named character.
3. **Length budget**: keep each clip prompt under ~150 words, not counting the trailing art-style descriptor block.
4. **Trimming rule**: when a verbatim `image_prompt` is too long to fit the budget, trim detail from *background* characters or secondary description first. Never trim the focal character's description — if a cut must come from the focal character, shorten adjectives, not the identifying features (species/race, key silhouette elements, signature colors/props).
5. **Self-containment**: a clip prompt must never assume information from another clip. If the same character reappears in clip 5 as in clip 1, restate their full description in clip 5's prompt too.

---

## Step 4: Prompt Composition Rules

Compose each clip prompt as a single paragraph containing, in this order:
1. Camera/shot type (e.g. "Low-angle tracking shot", "Slow push-in", "Static wide shot").
2. Full physical description of each focal character (verbatim `image_prompt` text where available, trimmed per Step 3 rule 4), inlined directly — no `@Tags`, no "see [File.md]" references, no pointers to an external asset list.
3. Location/environment description (verbatim location `image_prompt` where available), inlined the same way.
4. The action itself — what happens during the ~8 seconds, described as one continuous motion.
5. Lighting and atmosphere.
6. Dialogue or key sound, if any, **quoted in Polish** inline in the prompt (e.g. `He roars in Polish: "Za Mytros!"`). Sound effects/music can be described in English (e.g. "Deep rumbling percussion swells.").
7. The selected art style's descriptor block, appended at the end.

**Language rule**: all prompt text is in English, except quoted spoken dialogue, which stays in Polish exactly as it would be said in-game.

**No preamble, no cross-references**: do not emit a "Project Assets Setup" section, do not use `@CharacterName`/`@LocationName` tags, and do not split a clip into separate "Visual Prompt" / "Ingredients" / "Audio" fields. Everything lives in one prose block per clip.

**Optional appendix**: if useful, you may add an appendix *after* all clip blocks suggesting Flow "ingredient" reference-image descriptions per character/location. This is optional and must never be required to understand or use a clip prompt — every clip prompt must remain independently paste-ready without it.

### Clip block template

Format each clip exactly like this:

```
## Clip {N} — {Short scene title} (~8s)

### PROMPT (paste into Flow):
{Camera/shot type}: {full inlined character description(s)}, {inlined location description}, {the continuous action}. {Lighting/atmosphere}. {Dialogue quoted in Polish, if any}. {SFX/music description, if any}. {Art style descriptor block.}
```

Example:

```
## Clip 3 — Orestes charges the colossus (~8s)

### PROMPT (paste into Flow):
Low-angle tracking shot: a powerful male minotaur with a muscular build,
broad shoulders and brown fur, large curved dark grey horns, glowing blue
eyes, dressed in a white toga with an ornate red sash, sprints across a
shattered marble plaza toward a towering bronze colossus wreathed in storm
clouds. Debris and sparks fly as he closes the distance in one unbroken
sprint. Dramatic rim lighting, slow-motion dust catching the light.
He roars in Polish: "Za Mytros!" Deep rumbling footsteps, orchestral
percussion swelling. Arcane (Fortiche Studio) style: painterly 3D/2D hybrid
rendering, sharp graphic outlines, dramatic theatrical lighting, stylized
anatomy, rich dynamic brushstrokes.
```

---

## Step 5: Save & Attach to Recap

1. Assemble all clip blocks (in order) under a single markdown document, prefixed with a header:
   ```
   # Skrypt wideo: Sesja {NNN} - {Session Title} ({Mode})
   Art Style: {Selected Art Style Name}

   {clip blocks...}

   {optional ingredients appendix, if produced}
   ```
2. Save the document as markdown to `content/assets/sessions/{NNN}/video_script.md`.
3. Open the session recap markdown file (`content/01-Sessions/Sesja {NNN} - *.md`).
4. Add or update the following field in the YAML frontmatter:
   ```yaml
   video_script: "[Skrypt wideo](../assets/sessions/{NNN}/video_script.md)"
   ```
5. Run the index auto-updater script to update the Obsidian-compatible navigation and links:
   ```bash
   python3 scripts/update_indexes.py
   ```
6. **Echo every clip block in chat**, in order, exactly as saved to the file, so the user can copy any single clip directly without opening the file.
