---
name: rpg-wiki-manager
description: Extracts entities (NPCs, Locations, Items, Lore, Handouts) from RPG session recaps and input files, updating the wiki structure.
---

# RPG Wiki Manager Skill

This skill allows the agent to process session recaps and raw input files to update the D&D Campaign Wiki.

## 1. Input Processing Strategy (Manual Agentic Workflow)

The agent must manually read, analyze, and process each file. **Do not rely on scripts for content extraction** due to inconsistent formats.

### Core Loop
For each target file in `input/`:
1.  **READ**: Read the full content of the file.
2.  **IDENTIFY**: Determine the type (Session Recap, Handout, Source Material).
3.  **PARSE**: Go through the content section by section (or paragraph by paragraph).
4.  **LINK/CREATE**: For every proper noun (Person, Place, Item), check if it exists in the wiki. Link it or create it.
5.  **HANDLE ASSETS**: Move linked images/videos to appropriate asset folders and update links.
6.  **MOVE**: Move the processed file to its final destination in `content/`.

## 2. File Type Handling

-   **Session Recaps** (e.g., "Sesja 64..."):
    -   **Destination**: `content/01-Sessions/`
    -   **Assets**: Create a subdirectory `content/assets/sessions/<Session Name>/`. Move all images/videos used in the recap there.
    -   **Action**: Extract entities (NPCs, Locations) mentioned. Update the "Session Index" if one exists.
-   **Handouts** (Letters, Notes, Images):
    -   **Destination**: `content/07-Handouts/`
    -   **Action**: Ensure it has a meaningful title. If it's an image, create a wrapper Markdown file.
-   **Source Material** (Lore, Rulebooks):
    -   **Destination**: `content/` (appropriate subfolder)

## 3. Entity Linking and Creation Rules (CRITICAL)

**Goal**: Every significant entity mentioned in the text must be wikilinked: `[[Entity Name]]`.
**Constraint**: Do NOT modify the narrative content of the summary itself, only add wikilinks.

### The "Search First" Rule
Before creating ANY new file or link:
1.  **SEARCH**: Use `find_by_name` to see if the entity already exists.
    -   *Example*: Input says "Kyrah the Goddess". Search for "Kyrah". Found `content/02-People/Kyrah.md`. Acknowledge existence.
2.  **LINK**: In the text, replace "Kyrah the Goddess" with `[[Kyrah|Kyrah the Goddess]]`.
    -   *Rule*: Always alias to the existing filename if the text differs.

### The "Create with Template" Rule
If the entity does **NOT** exist:
1.  **DETERMINE TYPE**: Is it an NPC, Location, Item, or Handout?
2.  **READ TEMPLATE**: Use `view_file` on the appropriate template in `.agent/skills/rpg-wiki-manager/resources/`.
3.  **CREATE**: Create the new file in the correct directory using the template content.
4.  **LINK**: Update the source text to link to this new file: `[[New Entity Name]]`.

## 4. Inconsistency Handling

-   **Ambiguous Names**: If "The Captain" is mentioned and you know who it is, link it: `[[Orestes|The Captain]]`.
-   **Variant Spellings**: Fix spelling only if it's clearly a typo of a known name, and link it.
-   **Missing Data**: If creating an NPC and you only know their name, fill the template with known info and leave others as "TBD" or empty. Do NOT invent information.

## 5. Templates

You MUST use these templates for new files:
-   **NPCs**: `resources/NPC.md`
-   **Locations**: `resources/Location.md`
-   **Items**: `resources/Item.md`
-   **Handouts**: `resources/Handout.md`
-   **Factions**: `resources/Faction.md`
