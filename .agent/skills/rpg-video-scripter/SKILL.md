---
name: rpg-video-scripter
description: Generates a structured, multi-scene video script optimized for Google Flow (Gemini Omni) from a session recap, maintaining character and location visual continuity via rpg-illustrator prompts.
---

# RPG Video Scripter

Use this skill to translate a D&D session recap into a high-quality, structured video script that the user can copy-paste directly into Google Flow (Gemini Omni). The skill ensures character and location visual continuity, matches physical description prompts from `rpg-illustrator`, and outputs the exact tag format that Flow expects.

## Input Parameters
- **Session Recap File**: Absolute path to the session recap markdown file (e.g. `content/01-Sessions/Sesja 74 - Matka Smoków.md`).
- **Mode Selection**: Decided interactively with the user:
  - **Highlights Mode**: Capture 3 to 10 of the most memorable clips spanning the entire session's events.
  - **Single Event Mode**: Capture a sequence of 3 to 10 shots mapping a specific dramatic scene or battle from beginning to end.
- **Art Style Selection**: Decided interactively with the user from 10 dynamic presets generated on the fly.

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

---

## Step 2: Interactive Prompting (User Decision Gate)
Before generating the script, list the extracted key event candidates to the user in chat. Ask the user two key design questions:

### 1. Script Focus Mode
- "Should the script be a **Highlights** video of memorable moments across the entire session, or should it focus on **One Specific Event**?"
- Provide a list of the extracted sections/events. If they select a specific event, focus the entire script on detailing that event sequentially.

### 2. Video Art Style (Dynamic Generation)
Analyze the parsed session recap's thematic context, environments (e.g. celestial tower, dark oceans, ancient temples), and overall emotional tone. Present the user with **10 unique visual art style options generated on the fly**:
- **Mandatory Option 1**: **Arcane (League of Legends / Fortiche Studio style)**: Masterful mix of 3D rendering and hand-painted 2D textures, dramatic theatrical lighting, sharp graphic outlines, highly stylized anatomy, and rich, dynamic brushstrokes.
- **Options 2–10 (On-The-Fly Generation)**: Dynamically conceive **9 distinct art styles** tailored specifically to the narrative and themes of this particular session recap. 
  - For each dynamic style, provide a catchy title and a clear, descriptive summary of its visual attributes and guidelines so the user can easily visualize the final aesthetic.

---

## Step 3: Script Writing Rules & Prompt Refinement (Reusing rpg-illustrator)

When drafting the script, follow these rules:

1. **Scene Layout**: The script must be broken down into individual 4-to-10 second shots.
2. **Visual Prompts (English)**: 
   - Must be written in **English** for maximum compatibility with Gemini Omni in Flow.
   - Describe subject, camera angle, action, lighting, and apply the selected **Video Art Style** prompt descriptors at the end.
   - Use `@CharacterName` (e.g. `@Orestes`) and `@LocationName` (e.g. `@Praxys`) within the prompt to track characters and environments. Include their resolved physical/environmental descriptions in the text to maintain visual and scene consistency.
3. **Ingredients to Assign in Flow**:
   - List each character and location tracked in the visual prompt using `@CharacterName` and `@LocationName` tags.
   - Format: `@Name (Reference image of the [role/location], see [File.md]: [Verbatim Physical/Environmental Description])`.
4. **Audio/Dialogue (Polish)**:
   - Must be in **Polish** to preserve exact in-game quotes, narration, and tone.
   - Format: `@Voice: CharacterName — "Dialogue line"` or `None (Sound effect/music description)`.

---

## Step 4: Google Flow Script Structure

Format the final script output file exactly like this:

```
# Skrypt wideo: Sesja {NNN} - {Session Title} ({Mode})
Art Style: {Selected Art Style Name}

## 1. Google Flow Project Assets Setup
Before generating the scenes, set up these character and location assets in your Google Flow project:

### Characters

#### @CharacterName
- **Image Prompt**: {The long physical description from frontmatter/fallback}
- **Character Personality**: {Personality description from frontmatter/fallback}
- **Voice Characteristics**: {Voice characteristics from frontmatter/fallback}

### Locations

#### @LocationName
- **Image Prompt**: {The long environmental description from frontmatter/fallback}

---

## 2. Scenes Timeline

Scene 1: {Scene Title/Action}
Visual Prompt: {Detailed English prompt including camera shot type, mood, actions, and character tags like @CharacterName, within the environment tagged @LocationName. Conclude with the selected art style guidelines.}
Ingredients to Assign in Flow:
- @CharacterName
- @LocationName
Audio/Dialogue:
- @Voice: CharacterName — "Polish dialogue or narration line"

Scene 2: {Scene Title/Action}
Visual Prompt: {Detailed English prompt...}
...
```

---

## Step 5: Save & Attach to Recap

1. Save the generated script as a plain text file to `content/assets/sessions/{NNN}/video_script.txt`.
2. Open the session recap markdown file (`content/01-Sessions/Sesja {NNN} - *.md`).
3. Add or update the following field in the YAML frontmatter:
   ```yaml
   video_script: "[Skrypt wideo](../assets/sessions/{NNN}/video_script.txt)"
   ```
4. Run the index auto-updater script to update the Obsidian-compatible navigation and links:
   ```bash
   python3 scripts/update_indexes.py
   ```
