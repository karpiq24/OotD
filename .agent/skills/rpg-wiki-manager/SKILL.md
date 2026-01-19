---
name: rpg-wiki-manager
description: Extracts entities (NPCs, Locations, Items, Lore, Handouts) from RPG session recaps and input files, updating the wiki structure.
---

# RPG Wiki Manager Skill

This skill allows the agent to process session recaps and raw input files to update the D&D Campaign Wiki.

## 1. Input Processing
The agent should look for content in two places:
1.  **Direct Text**: Provided by the user in the chat.
2.  **Input Directory**: Files located in `input/`.

### File Type Handling
Check file extensions in `input/` and handle accordingly:

-   **`.md` (Markdown)**:
    -   **Session Logs**: If filename contains "Sesja" (e.g., `Sesja 64 - Tytuł.md`), move directly to `content/01-Sessions/`. Update the Session Index.
    -   **Handouts**: If content looks like a letter/note, move to `content/07-Handouts/`.
    -   **Source Content**: Otherwise, parse text to extract entities.

-   **`.txt` (Text)**:
    -   **Handouts**: Can be letters, riddles, or notes. Convert to `.md` in `content/07-Handouts/`.
    -   **Raw Notes**: Parse for entities (NPCs, Locations) to update the Wiki.

-   **`.pdf` (PDF)**:
    -   **Campaign Books**: Treat as large source material. Structure might be complex.
    -   **Action**: Extract text. Identify sections (Headers).
    -   **Parsing**: Break down into individual entities:
        -   Characters -> `content/02-People/`
        -   Locations -> `content/03-Locations/`
        -   Lore/Rules -> `content/05-Lore/` or `content/06-Rules/`

-   **`.png` / `.jpg` / `.webp` / `.mp4`**:
    -   **Visual Handouts**: Move to `content/assets/`.
    -   Create a reference file in `content/07-Handouts/`.

## 2. Entity Parsing
**Goal**: Identify content for:
-   **People** (NPCs, PCs, Factions) -> `content/02-People/`
-   **Locations** (Cities, Dungeons, Kingdoms) -> `content/03-Locations/`
-   **Items** (Artifacts, Magic Items, Loot) -> `content/04-Items-and-Loot/`
-   **Lore** (Gods, History, events) -> `content/05-Lore/`
-   **Rules** (House rules mentioned) -> `content/06-Rules/`
-   **Handouts** (Visuals, Documents) -> `content/07-Handouts/`

## 3. File Management Rules
For each identified entity:
1.  **Search**: Check existence (`find_by_name`).
2.  **Create (if new)**:
    -   Create markdown file in correct subdirectory.
    -   Use the standard Frontmatter template.
    -   **Important**: If the input was a file in `input/`, **delete or archive** the input file after successful processing to keep the staging area clean.
3.  **Update (if exists)**:
    -   Append new info to "Notes" or "History".

## 4. Templates
When creating new files, you MUST use the templates located in the `resources/` directory of this skill.
Read the template file using `view_file`, then populate it with extracted data.

### Available Templates:
- **NPCs**: `resources/NPC.md` (for Non-Player Characters)
- **PCs**: `resources/PC.md` (for Player Characters)
- **Locations**: `resources/Location.md` (for Cities, Dungeons, etc.)
- **Items**: `resources/Item.md` (for Magic Items, Loot, etc.)

- **Handouts**: `resources/Handout.md` (for Maps, Letters, Images)

## 5. Execution Flow
1.  **Scan Input**: List files in `input/`.
2.  **Process Files**: For each file, determine type and extract content.
3.  **Parse & Link**: Identify entities and create wiki links.
4.  **Update Wiki**: Write files to `content/`.
5.  **Cleanup**: Remove processed files from `input/`.
