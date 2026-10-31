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
uv run python scripts/update_indexes.py

# Python — uv only, never bare python3 / pip / venv
uv venv && uv pip install -r requirements.txt   # create or repair .venv
uv run python scripts/<script>.py               # run anything

# Convert the source PDFs in input/ into a markdown vault
uv run python scripts/pdf2md/convert.py <PDF> <OUTDIR>
```

`input/` is a staging area for raw source material (sourcebook PDFs, the `pdf2md` vault, files to import into the wiki). Sessions never go there: they come only from rpgnotes, through `/import-session` (see below).

## Private repo (`private/`)

`input/`, `build/`, `content/99-DM-Corner/` and the per-session working files (`private/sessions/{NNN}/`) are **not** part of this public repo. They live in the private repo `karpiq24/OotD-private`, cloned into `private/` (gitignored), and are reached through gitignored symlinks: `input → private/input`, `build → private/build`, `content/99-DM-Corner → ../private/DM-Corner`. Commit changes to anything under those paths from inside `private/` (`git -C private ...`), never from the public repo. Anything copyrighted (sourcebook text, Nowa Era PDF build) or DM-only goes there. The two sourcebook PDFs in `input/` are local only (over GitHub's 100 MB limit). Setup on a fresh machine is in `private/README.md`.

## Foundry VTT

The campaign runs on Foundry at https://dnd.klima-kar.pl (world `odyssey-of-the-dragonlords`, files mounted at `/mnt/beholder/appdata/Foundry/Data/worlds/odyssey-of-the-dragonlords/`). To create or update actors (stat blocks, art, tokens), follow `build/foundry-import/README.md`: stat blocks go in through Plutonium's API in the browser, never by editing the world's LevelDB.

## rpgnotes and this wiki

The sibling repo `../rpgnotes` turns a game's audio and Foundry log into a session draft. The two repos touch through exactly two files, each with a `schema_version` that both sides check:

- **Session package** (rpgnotes → wiki): `../rpgnotes/output/{NNN}/` with `manifest.json` (override the location with `RPGNOTES_OUTBOX`). `scripts/import_session.py` copies the `publish` files into `content/assets/sessions/{NNN}/` and the `working` files (`draft0.md`, `details.json`, `validation_report.json`) into `private/sessions/{NNN}/`, then fills `templates/Session.md`. rpgnotes never writes into this repo.
- **Campaign context** (wiki → rpgnotes): `campaign/campaign_context.json`, written by `scripts/export_context.py` (gitignored, regenerate any time). It carries the party (from `content/02-People/Bohaterowie/`), entity names and aliases, `Campaign_Context.md`, the timeline, and the hand-kept files in `campaign/`: `phonetic_corrections.md`, `learned_rules.md`, `whisper_hotwords.txt`, and the summary sections of `proza.md` (the campaign's prose rules, sent as `prose_rules` and appended to rpgnotes' summary style prompt). rpgnotes reads nothing else from the wiki.

Draft quality is rpgnotes' job: there is no summarizer here. Corrections flow back through `campaign/` (`/harvest-corrections`) and reach rpgnotes on the next export.

## The `.agents/` directory

This is the AI automation layer, shared between Antigravity (native `.agents/rules`, `.agents/skills` support) and Claude Code. `.agents/` is the single source of truth; `.claude/skills` is a symlink into it (`.claude/skills → ../.agents/skills`), so Claude Code's native Skill tool (e.g. `/finalize-session-recap`) picks up the exact same files Antigravity uses — nothing is duplicated. There is no `workflows/` directory: multi-step pipelines are skills too (both agents resolve `/<skill-name>` for any skill), distinguished only by role below. It contains two subdirectories:

### `rules/` — always-on constraints

Imported below so their full text is always in context for Claude Code too (mirrors Antigravity's `trigger: always_on`):

@.agents/rules/indexes.md
@.agents/rules/wikilinks.md
@.agents/rules/use_venv.md
@.agents/rules/proza.md

### `skills/` — capabilities and pipelines

Two kinds of skill live side by side here. **Capability skills** do one focused job and are invoked by pipeline skills (with an explicit mode parameter where noted) or directly:

| Skill | Purpose |
|---|---|
| `rpg-illustrator` | Generates image prompts and renders images. Modes: `Session Recap - Prompts Only`, `Session Recap - Generate Images`, `Single Image`, `Prompt Generation`. |
| `rpg-wiki-manager` | Extracts and creates/updates entity files (NPCs, locations, items, lore) from session text, inserts wikilinks. |
| `rpg-timeline-manager` | Appends key events to `content/Timeline.md` and updates `content/Campaign_Context.md`. |
| `rpg-video-scripter` | Generates a paste-ready, per-clip Google Flow video script from a session recap. Invoked on-demand via `generate-video-script`, never automatically. |
| `rpg-chatlog-analyst` | Answers precise mechanics questions (exact damage, who cast what, hit/miss) by grepping the session's `chat_events.txt` / `chat_log.json` (imported from rpgnotes into `content/assets/sessions/{NNN}/`). All timeline sources share one clock: seconds since the Craig recording start. Never loads whole logs into context. |

**Pipeline skills** are the multi-step, user-facing entry points — invoked explicitly as `/<skill-name>` (Claude Code) or from the Antigravity Skills panel. Two main ones for processing a new session, plus three on-demand:

**`import-session`** (Part 1; the only way a new session enters the wiki):
1. Ask for the session number; run `scripts/import_session.py {N}`: checks the package's manifest, copies its files (published / private), assembles `content/01-Sessions/Sesja {N} - {Title}.md` from `templates/Session.md` + `draft0.md` + `details.json` + `quotes.json`. Stops on a missing or incomplete package, an unknown schema version, or an existing note (`--force` only with the user's consent).
2. **Interactive verification** — open `validation_report.json` findings, ambiguous identities and abandoned actions, each checked with targeted greps of the transcript, become ≤10 pick-one questions in one message; mechanics questions are first answered from `chat_events.txt` via `rpg-chatlog-analyst`; answers are applied to the note, skipped ones marked `<!-- UNVERIFIED: ... -->`.
3. Fix evident ASR mishearings in `## Cytaty` (never rephrase).
4. `scripts/import_session.py {N} --snapshot` saves the note to `private/sessions/{000}/draft_pre_edit.md` for the learning loop; report unresolved findings and UNVERIFIED markers.

**`finalize-session-recap`** (Part 2, after user edits the draft):
0. **Harvest corrections** (non-blocking) → run `/harvest-corrections`; skips silently if there is nothing to harvest.
1. Activate `rpg-wiki-manager` → apply wikilinks, update/create entity files.
2. Activate `rpg-illustrator` (`Session Recap - Prompts Only`) → save `.txt` prompt files + insert placeholder image links into the session file.
3. Activate `rpg-timeline-manager`, then run `scripts/export_context.py` so the next rpgnotes run sees the new entities, timeline and harvested corrections.
4. **Pause** — notify user to review `.txt` prompt files in `content/assets/sessions/{000}/`.
5. After user confirms → activate `rpg-illustrator` (`Session Recap - Generate Images`).

**`generate-video-script`** (on-demand only, invoked explicitly — not part of finalization):
1. Ask for session number → locate the recap file.
2. Activate `rpg-video-scripter` → interactively pick focus mode + art style, then generate the script.
3. Save to `content/assets/sessions/{000}/video_script.md` (auto-listed under **Metadane** by the `SessionAssets` transformer — no frontmatter link needed), run `update_indexes.py`, and echo clips in chat.

**`harvest-corrections`** (learning loop; auto-runs as `finalize-session-recap` Step 0, or on-demand):
1. Diff `private/sessions/{000}/draft_pre_edit.md` against the user-edited session file. Skip gracefully if the pre-edit snapshot is missing.
2. Classify each change: name correction → `campaign/phonetic_corrections.md`; deleted claim → candidate rule (propose a bullet for `campaign/learned_rules.md` if the pattern repeats across ≥2 sessions); entity fact fix → propose the same fix to the wiki entity file; pure style edit → propose a style bullet for `learned_rules.md` if consistent.
3. Present all proposed writes to the user for confirmation; write only what is approved.

**`iterate-recap`** (on-demand, tool-agnostic — usable from Antigravity):
1. Input: session number + free-form complaint.
2. Grep the transcript for the complaint's names/keywords (expand through `campaign/phonetic_corrections.md`), re-read only those slices.
3. Rewrite only the affected `###` section(s); never touch the rest of the file. Uses only read/grep/edit — no Claude-specific tooling.

## Content structure

```
content/
  01-Sessions/      # Session recap Markdown files + index.md
  02-People/        # Bohaterowie (PCs), Factions, NPCs/<group folder>/, Katalog postaci.md
  03-Locations/     # Kontynent Thylea/, the seas, Zaświaty i Plany/, Statki i Ruchome Wyspy/
  04-Items-and-Loot/
  05-Lore/
  assets/sessions/{000}/  # Per-session: transcript, chat log, quotes, images, prompt .txt files
  Timeline.md       # Chronological campaign events
  Campaign_Context.md  # Running concise campaign summary
```

**Look and navigation ("Brąz i Patyna").** Palette and fonts (Cinzel headers, Alegreya Sans body) are in `quartz.config.ts`; extra tokens, the meander band and page-wide rules in `quartz/styles/custom.scss`; component styles in `quartz/components/styles/ootd.scss`. Our own components, all built at build time from the content:

- `HomePage` (home only): banner hero with live counts, latest session with an excerpt, hero portraits, section tiles.
- `pages/CardFolderContent` (every folder page): an image card per page, each with its first image and its italic lead line as the subtitle; a live filter box on folders with more than 8 cards. The `index.md` bullet list that `update_indexes.py` writes stays for Obsidian and is hidden on the site. The sessions folder groups cards by the story arcs, read from the `### Name: subtitle (Sesje X-Y)` headings of `Campaign_Context.md`, so those headings must keep that form.
- `RelatedPeople` (faction and location pages): a "Postacie" section with the people of the NPC folder of the same name (`Factions/Kult Węża.md` ↔ `NPCs/Kult Węża/`, `Mytros.md` ↔ `NPCs/Mytros/`).
- `PeopleCatalog` (a page with `catalog: true`, i.e. `02-People/Katalog postaci.md`): every person in one grid with search and folder/group filter chips.

Frontmatter fields they read (all hidden from the Metadane table):

| Field | Where | Effect |
|---|---|---|
| `description`, `cover` | folder `index.md` | tile subtitle and image on the home page and in folder listings (`cover` is also the link-preview image) |
| `group` | NPC folder `index.md` | the section the folder appears under (Bogowie i Tytani, Miasta i krainy, Wyspy i wieże, Zakony i kulty, Załogi i statki, Istoty, Inne) |
| `groups` | `02-People/NPCs/index.md` | order of those sections |
| `expand` | `02-People/index.md` | lists the subfolders (Bohaterowie, Factions, NPCs) shown inline on that page |
| `also_in` | any person page | other folders (by folder name, same section) where the person also appears, under "Również tutaj"; e.g. Astra lives in `Kult Węża/` with `also_in: [Mytros, Bohaterowie]`. A person has one home folder; never copy a page into a second folder |
| `also_label` | folder `index.md` | heading for that section (`Bohaterowie` uses "Rodzina i towarzysze") |
| `people` | faction/location page | the NPC folder to show when its name differs (`Orestessos Zythikē` → `Orestessos`) |

The site icon is `quartz/static/icon.svg` (also used for the favicon and the generated preview images).

**Quartz version.** We run the latest Quartz **v4** (upstream `jackyzha0/quartz`, branch `v4`) with local patches: the components above, the `SessionAssets` and `OgImageExtractor` transformers, `FrontmatterTable`, relative-link resolution in `util/path.ts`, the GitHub Pages trailing-slash fix in `spa.inline.ts`, og-image path resolution, and the svg icon. To pick up upstream v4 fixes, diff the upstream commit range over `quartz/` and apply it, keeping those patches. Quartz 5 replaces the plugin system (plugins as separate git packages); moving there means rewriting all of the above as plugins, so it has not been done.

**Session "Metadane" list.** The `SessionAssets` transformer (`quartz/plugins/transformers/sessionAssets.ts`) scans `content/assets/sessions/{000}/` at build time for any recap file named `Sesja {N} - …` and lists every file in that directory — grouped into categories (Transkrypty, Logi czatu, Dane, Wideo, Obrazki, Prompty) — under the **Metadane** section rendered by `quartz/components/FrontmatterTable.tsx`. Do **not** add `transcript_*` / `chat_log` / `video_script` links to session frontmatter by hand; drop a file in the asset directory and it appears automatically. rpgnotes' working files (`draft*`, `validation_report*`, `details.json`, `manifest.json`) are never listed, and `quartz.config.ts`'s `ignorePatterns` keep them off the site; they belong in `private/sessions/{000}/`.

Templates for new entity files: `templates/Session.md`, `NPC.md`, `Location.md`, `Item.md`, `Faction.md`, `Handout.md`.

Entity files may have an `image_prompt` frontmatter field — `rpg-illustrator` uses this verbatim (never paraphrase it) when the entity appears in a scene.

## Python utility scripts

Everything lives under `scripts/` (run via `uv run python scripts/...`):

- `update_indexes.py` — regenerates all `index.md` files under `content/`
- `import_session.py` — imports an rpgnotes session package and assembles the note (`--snapshot` saves the pre-edit baseline)
- `export_context.py` — writes `campaign/campaign_context.json` for rpgnotes
- `check_wikilinks.py` — reports broken wikilinks and alias collisions in `content/`
- `fix_image_paths.py` — repairs broken image paths in Markdown
- `convert_assets.py` (compress images/videos), `get_prompts.py` (collect `image_prompt` fields), `find_and_zip.py` (zip the files mentioning given names) — maintenance utilities
- `pdf2md/` — PDF → markdown-vault pipeline (see below)

## `scripts/pdf2md/` — sourcebook PDF → markdown vault

Converts the *Odyssey of the Dragonlords* / *The Great Labors* PDFs into a
navigable markdown tree: one directory per chapter, one file per
table-of-contents section, illustrations cropped into a per-chapter `images/`.

```bash
uv run python scripts/pdf2md/convert.py input/<book>.pdf input/vault/<Book>
```

- `pdfmd.py` — page → element stream: headings, paragraphs, statblocks, tables,
  sidebars, multi-column reflow, hyphenation re-joining.
- `images.py` — every page is one flattened raster with live text on top, so
  illustrations are found by masking non-parchment regions and cropping them.
- `split.py` — maps the PDF table of contents onto the element stream to decide
  chapter directories and section files.
- `convert.py` — the entry point tying the three together.

Output currently lands in `input/vault/` (tracked in the private repo), with an
`index.md` in every directory describing each file.
