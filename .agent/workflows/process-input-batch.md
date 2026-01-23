---
description: Process all files in the input/ directory using the appropriate workflow for each file type.
---

# Process Input Batch

This workflow guides the agent through processing the entire backlog of files in `input/`.

## Prerequisites
-   **Skill**: `rpg-wiki-manager` (Agent must read `SKILL.md`).
-   **Workflow**: `process-session.md` (for session recaps).

## Workflow Steps

1.  **List Files**:
    -   Run `ls -R input/` to see all pending files.

2.  **Iterate**:
    -   Pick the first file in the list.
    -   **Identify Type**:
        -   Start with "Sesja..."? -> It's a Session Recap.
        -   Looks like a letter/note? -> It's a Handout.
        -   Other? -> Check content.

3.  **Execute Specific Workflow**:
    -   If **Session Recap**:
        -   Execute the instructions in `.agent/workflows/process-session.md` for this file.
    -   If **Handout**:
        -   (Future workflow) For now, manual process: Read -> Link Entities -> Move to `content/07-Handouts/`.
    -   If **Image/Video**:
        -   Move to `content/assets/` (or `content/07-Handouts/assets/` if preferred).
        -   Create a container markdown file in `content/07-Handouts/` if it represents a document.

4.  **Repeat**:
    -   Pick the next file.
    -   Repeat until `input/` is empty (or only contains directories).

5.  **Final Cleanup**:
    -   Remove empty directories in `input/`.
