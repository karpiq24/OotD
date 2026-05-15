# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A campaign wiki for the **Odyssey of the Dragonlords** D&D campaign, built with [Quartz](https://quartz.jzhao.xyz/) (static site generator). All campaign content lives in `content/` as Markdown. The site is published to GitHub Pages.

## Commands

```bash
# Local dev server (http://localhost:8080)
npx quartz build --serve

# Type-check + formatting check
npm run check

# Auto-format
npm run format

# Regenerate all index.md files after adding/moving/deleting content
python3 update_indexes.py

# Python deps (Pillow, tqdm) — use the local venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python <script>.py   # always use venv, never bare python3
```

The `input/` directory is a staging area (gitignored except `.gitkeep`). Drop new session files there before processing.

## The `.agent/` directory

This is the AI automation layer — Claude's instructions for working in this repo. It is **not** a standard Claude Code directory; it contains three subdirectories:

### `rules/` — always-on constraints

These apply automatically to every task:

- **`read_transcript.md`** — When summarizing a transcript, read the full file before generating output. **Exception**: when `rpg-summarizer` is active (chunked subagent mode), the orchestrating agent must NOT pre-load the full transcript — only get the line count and scan for names. Each chunk subagent reads its own slice.
- **`indexes.md`** — After any content file is created, moved, or renamed, run `python3 update_indexes.py`.
- **`wikilinks.md`** — All internal links use simplified Obsidian format: `[[Name]]` or `[[Name|Alias]]`. No paths, no `.md` extension. PC hero names always link to the full filename: `[[Felicjan Janus Twardowski|Felicjan]]`.
- **`use_venv.md`** — Always use `.venv/bin/python`, never `python3` directly.

### `skills/` — reusable capabilities

Skills are invoked by workflows or directly, with an explicit mode parameter:

| Skill | Purpose |
|---|---|
| `rpg-summarizer` | Converts a transcript to a narrative recap using sequential chunk subagents. Each subagent gets ~800 lines + a rolling summary from the previous chunk. |
| `rpg-illustrator` | Generates image prompts and renders images. Modes: `Session Recap - Prompts Only`, `Session Recap - Generate Images`, `Single Image`, `Prompt Generation`. |
| `rpg-wiki-manager` | Extracts and creates/updates entity files (NPCs, locations, items, lore) from session text, inserts wikilinks. |
| `rpg-timeline-manager` | Appends key events to `content/Timeline.md` and updates `content/Campaign_Context.md`. |
| `rpg-video-scripter` | Generates video prompt scripts to `content/06-Video-Scripts/`. |

### `workflows/` — multi-step pipelines

Two main workflows for processing a new session:

**`generate-session-recap-draft`** (Part 1):
1. Ask for session number → move files from `input/` to `content/assets/sessions/{000}/`.
2. Get transcript line count, scan for names, load entity context, read last 3 session files.
3. Activate `rpg-summarizer` (chunk subagent mode) → generates draft.
4. Save to `content/01-Sessions/Sesja {N} - {Title}.md`.

**`finalize-session-recap`** (Part 2, after user edits the draft):
1. Activate `rpg-wiki-manager` → apply wikilinks, update/create entity files.
2. Activate `rpg-illustrator` (`Session Recap - Prompts Only`) → save `.txt` prompt files + insert placeholder image links into the session file.
3. Activate `rpg-timeline-manager` and `rpg-video-scripter`.
4. **Pause** — notify user to review `.txt` prompt files in `content/assets/sessions/{000}/`.
5. After user confirms → activate `rpg-illustrator` (`Session Recap - Generate Images`).

## Content structure

```
content/
  01-Sessions/      # Session recap Markdown files + index.md
  02-People/        # PCs, NPCs, Factions
  03-Locations/     # Places and geography
  04-Items-and-Loot/
  05-Lore/
  assets/sessions/{000}/  # Per-session: transcript, images, prompt .txt files
  Timeline.md       # Chronological campaign events
  Campaign_Context.md  # Running concise campaign summary
```

Templates for new entity files: `templates/Session.md`, `NPC.md`, `Location.md`, `Item.md`, `Faction.md`, `Handout.md`.

Entity files may have an `image_prompt` frontmatter field — `rpg-illustrator` uses this verbatim (never paraphrase it) when the entity appears in a scene.

## Python utility scripts (root-level)

- `update_indexes.py` — regenerates all `index.md` files under `content/`
- `fix_image_paths.py` — repairs broken image paths in Markdown
- `convert_assets.py`, `get_prompts.py`, `replace_script.py` — one-off maintenance utilities
