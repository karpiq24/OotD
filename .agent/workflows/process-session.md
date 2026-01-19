---
description: Process a new RPG session recap or raw input files to update the wiki.
---

# Process Session & Inputs

Use this workflow to process session recaps and any files staged in the `input/` directory.

## 1. Prepare Content
-   Place any raw files (images, PDFs, text logs) into the `input/` directory.
-   Have any additional text ready to paste.

## 2. Load Skill
Read the instructions for the Wiki Manager.
// turbo
```bash
cat /home/karpiq/Code/OotD/.agent/skills/rpg-wiki-manager/SKILL.md
```

## 3. Check Input Directory
List files to be processed.
// turbo
```bash
ls -F input/
```

## 4. Execution
Perform the following steps using the `rpg-wiki-manager` logic:
1.  **Ingest**: Read text from chat and files from `input/`.
2.  **Move Assets**: Move images/videos to `content/assets/` and reference them.
3.  **Parse**: Identify NPCs, Locations, Items, and Handouts.
4.  **Update Wiki**: Create/Update markdown files in `content/`.
5.  **Session Log**: If a session recap exists, compile it into `content/01-Sessions/`.
6.  **Cleanup**: Delete processed files from `input/`.

## 5. Build & Verify
// turbo
```bash
npx quartz build
```
