---
description: Process a single RPG session recap markdown file from input/ to content/01-Sessions/.
---

# Process Session Recap

This workflow guides the agent through manually processing a single session recap file.

## Prequisites
-   The user must have specified a FILE to process.
-   The file should be in `input/` or a subdirectory.
-   **Skill**: `rpg-wiki-manager` (Agent must read `SKILL.md`).

## Workflow Steps

1.  **Read the content** of the session file using `view_file`.
    -   *Goal*: Understand the plot, identify key entities (People, Locations, Items).

2.  **Extract Metadata**:
    -   Identify the Session Number and Title.
    -   Identify the Date.

3.  **Handle Assets (Images/Videos)**:
    -   **Scan**: Look for image links `![Alt](path/to/image)` and video mentions.
    -   **Prepare Directory**: Create a directory: `content/assets/sessions/<000>/` (using 3 digit session number).
    -   **Move Assets**: Move the actual image/video files from `input/...` to the new directory.
    -   **Update Links**: Update the markdown in the session file to point to the new location relative to `content/01-Sessions/`.
        -   *Path*: `../assets/sessions/<000>/image.png`

4.  **Research & Entity Linking Loop**:
    -   **Constraint**: Do NOT change the narrative text of the summary, only add wikilinks.
    -   **Book Source Check (CRITICAL)**: For every entity (NPC, Location, Item) identified, search `input/Book Source/` (using `grep_search`) to find official lore. Use this information to populate or enhance entity files.
    -   For each **Person/NPC** mentioned:
        -   **Search Wiki** (`find_by_name`) to see if they exist in `content/02-People/`.
        -   **Search Book Source**: Grep `input/Book Source/` for lore.
        -   **If Exists**: Link it `[[Name]]`. If the current page is missing details found in the Book Source, enhance it.
        -   **If New**: Create a file in `content/02-People/` using `resources/NPC.md`. Populate with Research. Then Link it.
    -   For each **Location** mentioned:
        -   **Search Wiki** -> Search Book Source -> Link or Create (`resources/Location.md`) -> Link.
    -   For each **Item/Artifact** mentioned:
        -   **Search Wiki** -> Search Book Source -> Link or Create (`resources/Item.md`) -> Link.

5.  **Final Polish**:
    -   Ensure frontmatter is correct.
    -   Verify image links work.

6.  **Move File**:
    -   Move the session file to `content/01-Sessions/`.

7.  **Cleanup**:
    -   Delete original input file if needed.