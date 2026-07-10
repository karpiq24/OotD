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

## The `.agents/` directory

This is the AI automation layer, shared between Antigravity (native `.agents/rules`, `.agents/skills`, `.agents/workflows` support) and Claude Code. `.agents/` is the single source of truth; `.claude/skills` and `.claude/commands` are symlinks into it (`.claude/skills → ../.agents/skills`, `.claude/commands → ../.agents/workflows`), so Claude Code's native Skill tool and slash commands (e.g. `/finalize-session-recap`) pick up the exact same files Antigravity uses — nothing is duplicated. It contains three subdirectories:

### `rules/` — always-on constraints

Imported below so their full text is always in context for Claude Code too (mirrors Antigravity's `trigger: always_on`):

@.agents/rules/read_transcript.md
@.agents/rules/indexes.md
@.agents/rules/wikilinks.md
@.agents/rules/use_venv.md

### `skills/` — reusable capabilities

Skills are invoked by workflows or directly, with an explicit mode parameter:

| Skill | Purpose |
|---|---|
| `rpg-summarizer` | Converts a transcript to a narrative recap using sequential chunk subagents. Each subagent gets ~800 lines + a rolling summary from the previous chunk. Chunks against `transcript_enriched.txt` when present (transcript with `[VISUAL]` scene-truth and `[CZAT]` mechanics-truth lines merged in — fact anchors, never quotable as dialogue), falling back to `transcript.txt`. Two modes: `from-scratch` (default) or `refine` (corrects an `rpgnotes` draft-0 instead of writing from scratch). |
| `rpg-illustrator` | Generates image prompts and renders images. Modes: `Session Recap - Prompts Only`, `Session Recap - Generate Images`, `Single Image`, `Prompt Generation`. |
| `rpg-wiki-manager` | Extracts and creates/updates entity files (NPCs, locations, items, lore) from session text, inserts wikilinks. |
| `rpg-timeline-manager` | Appends key events to `content/Timeline.md` and updates `content/Campaign_Context.md`. |
| `rpg-video-scripter` | Generates a paste-ready, per-clip Google Flow video script from a session recap. Invoked on-demand via `generate-video-script`, never automatically. |
| `rpg-chatlog-analyst` | Answers precise mechanics questions (exact damage, who cast what, hit/miss) by grepping the session's `chat_events.txt` / `chat_log.json` (written by rpgnotes into `content/assets/sessions/{NNN}/`). All timeline sources share one clock: seconds since the Craig recording start. Never loads whole logs into context. |

### `workflows/` — multi-step pipelines

Two main workflows for processing a new session, plus one on-demand workflow:

**`generate-session-recap-draft`** (Part 1):
1. Ask for session number; check `content/assets/sessions/{000}/` for what rpgnotes has already written there (`OUTPUT_DIR` points straight at this repo's `content/`, so no copy/move step is needed). `draft0.md` present → **refine mode**; otherwise **from-scratch mode**.
2. Get transcript line count (`transcript_enriched.txt` preferred, else `transcript.txt`), scan for names, load entity context, read last 3 session files; in refine mode also read `draft0.md`/`validation_report.md`.
3. Activate `rpg-summarizer` (chunk subagent mode, `refine` or `from-scratch`) → generates the narrative draft.
4. Save the narrative draft (provisional title) to `content/01-Sessions/Sesja {N} - {Title}.md`.
4.5. **Interactive verification** — collect open findings (fact-checker, `validation_report.md`, ambiguous identities, abandoned actions, chunk-boundary chronology) into ≤10 pick-one questions asked in one message; mechanics questions are first answered from `chat_events.txt` via `rpg-chatlog-analyst` and only reach the user if the chat log can't settle them; apply answers to the draft immediately, mark skipped sentences with `<!-- UNVERIFIED: ... -->`.
4.7. **Generate session details** — from the final refined draft, derive the structured sections per `templates/Session.md` (final title → filename, `Kluczowe wydarzenia`, `Postacie`, `Lokacje`, `Przedmioty`, and `Cytaty` from the bundle's `quotes.json`, verbatim), then assemble the **complete** session file (frontmatter — just `title`; asset links are not written by hand, the `SessionAssets` transformer lists them under **Metadane** at build time — plus details + narrative under `## Podsumowanie`) — rpgnotes no longer pre-renders any of it. Finally save the pristine copy to `content/assets/sessions/{000}/draft_pre_edit.md` for the learning loop.
5. In refine mode, surface any still-unresolved `validation_report.md` findings (not the ones answered in 4.5) plus any UNVERIFIED-marker count alongside the review notice.

**`finalize-session-recap`** (Part 2, after user edits the draft):
0. **Harvest corrections** (non-blocking) → run `/harvest-corrections`; skips silently if there is nothing to harvest.
1. Activate `rpg-wiki-manager` → apply wikilinks, update/create entity files.
2. Activate `rpg-illustrator` (`Session Recap - Prompts Only`) → save `.txt` prompt files + insert placeholder image links into the session file.
3. Activate `rpg-timeline-manager`.
4. **Pause** — notify user to review `.txt` prompt files in `content/assets/sessions/{000}/`.
5. After user confirms → activate `rpg-illustrator` (`Session Recap - Generate Images`).

**`generate-video-script`** (on-demand only, invoked explicitly — not part of finalization):
1. Ask for session number → locate the recap file.
2. Activate `rpg-video-scripter` → interactively pick focus mode + art style, then generate the script.
3. Save to `content/assets/sessions/{000}/video_script.md` (auto-listed under **Metadane** by the `SessionAssets` transformer — no frontmatter link needed), run `update_indexes.py`, and echo clips in chat.

**`harvest-corrections`** (learning loop; auto-runs as `finalize-session-recap` Step 0, or on-demand):
1. Diff `content/assets/sessions/{000}/draft_pre_edit.md` against the user-edited session file. Skip gracefully if the pre-edit snapshot is missing.
2. Classify each change: name correction → `phonetic_corrections.md`; deleted claim → anti-hallucination example (propose a new ZAKAZY rule if the pattern repeats across ≥2 sessions); entity fact fix → propose the same fix to the wiki entity file; pure style edit → propose a style-rule amendment if consistent.
3. Present all proposed writes to the user for confirmation; write only what is approved.

**`iterate-recap`** (on-demand, tool-agnostic — usable from Antigravity):
1. Input: session number + free-form complaint.
2. Grep the transcript for the complaint's names/keywords (expand through `phonetic_corrections.md`), re-read only those slices.
3. Rewrite only the affected `###` section(s); never touch the rest of the file. Uses only read/grep/edit — no Claude-specific tooling.

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

**Session "Metadane" list.** The `SessionAssets` transformer (`quartz/plugins/transformers/sessionAssets.ts`) scans `content/assets/sessions/{000}/` at build time for any recap file named `Sesja {N} - …` and lists **every** file in that directory — grouped into categories (Transkrypty, Logi czatu, Dane, Raporty, Wideo, Obrazki, Prompty) — under the **Metadane** section rendered by `quartz/components/FrontmatterTable.tsx`. Do **not** add `transcript_*` / `chat_log` / `video_script` links to session frontmatter by hand; drop a file in the asset directory and it appears automatically.

Templates for new entity files: `templates/Session.md`, `NPC.md`, `Location.md`, `Item.md`, `Faction.md`, `Handout.md`.

Entity files may have an `image_prompt` frontmatter field — `rpg-illustrator` uses this verbatim (never paraphrase it) when the entity appears in a scene.

## Python utility scripts (root-level)

- `update_indexes.py` — regenerates all `index.md` files under `content/`
- `fix_image_paths.py` — repairs broken image paths in Markdown
- `convert_assets.py`, `get_prompts.py`, `replace_script.py` — one-off maintenance utilities
