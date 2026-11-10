# OotD wiki

A campaign wiki for the **Odyssey of the Dragonlords** D&D campaign (in Polish), built with [Quartz](https://quartz.jzhao.xyz/) (static site generator). All campaign content lives in `content/` as Markdown. The site is published to GitHub Pages. This repo is **public**: nothing copyrighted, DM-only or private goes in here.

## Commands

```bash
npx quartz build --serve           # local dev server (http://localhost:8080)
npm run check                      # type-check + formatting check
npm run format                     # auto-format

rpg-tools wiki update-indexes      # regenerate every index.md after adding/moving/deleting content
rpg-tools wiki status              # where each rpgnotes session stands (staged / draft / rendering)
rpg-tools wiki import-session N    # import an rpgnotes package and assemble the note (--snapshot, --force, --stage --push)
rpg-tools wiki export-context      # write the campaign context rpgnotes reads
rpg-tools wiki render-images N     # render a session's {000}_*.txt prompts with agy into .webp
rpg-tools wiki check-links         # broken wikilinks and alias collisions in content/
rpg-tools wiki fix-image-paths     # repair broken image paths in Markdown
rpg-tools wiki convert-assets      # compress images/videos (--dry-run, --target all|images|videos)
rpg-tools wiki find STR... [--merge]   # zip the files that mention given names
rpg-tools wiki image-prompts       # collect the image_prompt fields
```

The wiki tools live in the rpg-tools repo. If `rpg-tools` is not on PATH, run `uv run --project ~/Code/rpg-tools rpg-tools …`; it finds the campaign from the cwd. `rpg-tools campaign show` prints the campaign's settings and the paths of its campaign files.

## The campaign's other half

The campaign settings (players, Foundry, prep), the tools' campaign files (ASR corrections, learned rules, Whisper hotwords, the prose rules, the skills' wiki rules) and everything DM-only or copyrighted live outside this repo; `rpg-tools campaign show --json` gives their paths (`files.*`). Nothing from there is ever copied into this repo or linked from it. Sessions come only from rpgnotes, through `import-session` (below).

## rpgnotes and this wiki

rpgnotes (part of rpg-tools) turns a game's audio and Foundry log into a session draft. The two touch through exactly two files, each with a `schema_version` that both sides check:

- **Session package** (rpgnotes → wiki): rpgnotes' outbox `{NNN}/` with `manifest.json` (`--outbox` overrides the location). `rpg-tools wiki import-session N` copies every listed file and the manifest into `content/assets/sessions/{NNN}/` (the working ones, `draft0.md`, `validation_report.json`, are kept off the site by `ignorePatterns`), then fills `templates/Session.md` with the draft and the title and key events the agent passes (`--title`, `--event`, written from the draft by skill import-session; the same skill has Sonnet subagents find the quotes in the transcript). The note starts with `draft: true` (hidden by `RemoveDrafts`, left out of the indexes); finalize-session-recap removes the flag, so a draft never reaches the site. With `--stage --push` it only copies and commits that folder ("{N} init") and pushes, no note: rpgnotes runs it when a package is ready, so the package reaches every workstation and `import-session` later builds the note from the staged folder. rpgnotes never writes into this repo itself.
- **Campaign context** (wiki → rpgnotes): written by `rpg-tools wiki export-context` into rpg-tools' state folder (not this repo; regenerate any time). It carries the party (from `content/02-People/Bohaterowie/`), entity names and aliases, `Campaign_Context.md`, the timeline, and the campaign files: phonetic corrections, learned rules, Whisper hotwords, and the summary sections of the prose rules (sent as `prose_rules` and appended to rpgnotes' summary style prompt). rpgnotes reads nothing else from the wiki.

Draft quality is rpgnotes' job: there is no summarizer here. Corrections flow back through the campaign files (`harvest-corrections`) and reach rpgnotes on the next export.

## Session workflow: the agent drives it

The user does not type skill names and reviews only the recap text. Read what they say and run the right step yourself:

| The user says / the state is | Do |
|---|---|
| "draft N jest", "sesja N", or a draft mentioned without a number (then `rpg-tools wiki status` says which one is `staged`) | `import-session` for N, start to finish, no questions |
| Anything is wrong or missing in a draft ("X tego nie zrobił", "brakuje walki z…") | fix it right away (`iterate-recap` method), one line on what changed |
| "OK", "akceptuję", "finalizuj", "dalej" about a draft | `finalize-session-recap`, start to finish, images included |
| "co z obrazkami", or `rpg-tools wiki status` shows `rendering` (images missing) | rerun `rpg-tools wiki render-images N` in the background |

Ask only when a step cannot go on without the user (no package, an existing note to overwrite). Everything else goes into the one report at the end of a step; the user vetoes there.

## Skills

The skills come from rpg-tools (`skills/`, and `systems/dnd5e/skills/` for `dndbeyond-manager`), installed into `~/.claude/skills` and `~/.agents/skills` with `rpg-tools skills install`; nothing of them is kept in this repo. They are generic: each reads this campaign through `rpg-tools campaign show --json` and its OotD-specific rules (names, Polish wording, known canon) from `files.wiki_rules`, which override the skills' general guidance.

| Skill | Purpose |
|---|---|
| `import-session` | Part 1: the only way a new session enters the wiki. Imports the package, settles open points from the evidence, marks the rest `UNVERIFIED`, edits structure and prose, weaves in the quotes, snapshots `draft_pre_edit.md`. |
| `finalize-session-recap` | Part 2, once the text is approved: harvest, wikilinks and entity pages, image prompts, timeline, context export, render, commit. |
| `iterate-recap` | Targeted fix of a recap from a complaint: greps the transcript, rewrites only the affected sections, carries the fix into the wiki. |
| `harvest-corrections` | Learning loop: diffs `draft_pre_edit.md` against the edited note into the campaign files and entity pages. |
| `rpg-wiki-manager` | Entity extraction, linking, page creation and updates. |
| `rpg-illustrator` | Image prompts and rendering (modes: `Session Recap - Prompts Only`, `Session Recap - Generate Images`, `Single Image`, `Prompt Generation`). |
| `rpg-timeline-manager` | `Timeline.md` and `Campaign_Context.md`. |
| `rpg-chatlog-analyst` | Exact mechanics (damage, who cast what, hit/miss) by grepping a session's `chat_events.txt` / `chat_log.json`; never loads whole logs. |
| `generate-video-script`, `rpg-video-scripter` | On demand only: a paste-ready Google Flow script into `content/assets/sessions/{000}/video_script.md`. |

## Rules (always on)

- **Index files.** After a content file is created, deleted, moved, renamed, or its title changes, run `rpg-tools wiki update-indexes` instead of editing `index.md` files by hand. It regenerates every `index.md` under `content/` with correct links and titles, keeping descriptions and non-list content.
- **Wikilinks.** Simplified Obsidian format: no paths (`[[Zephyrus]]`, not `[[content/02-People/NPCs/Zephyrus.md|Zephyrus]]`), no `.md` (`[[Lutheria]]`), anchors allowed (`[[History of Thylea#The First War]]`). Heroes always by their full file name with an alias, even when the text uses the first name: `[[Felicjan Janus Twardowski|Felicjan]]`, `[[Arevon Elorrenthi|Arevon]]`, `[[Orion Xul|Orion]]`, never `[[Felicjan]]`.
- **Prose.** Polish prose in this repo (session recaps, wiki pages, `Timeline.md`, `Campaign_Context.md`) follows the campaign's prose rules, `files.prose_rules` from `rpg-tools campaign show --json`: section A applies to all prose, B to session recaps, C to wiki pages. The most important rule (A2): when the user corrects or rejects something, write only the corrected version; never echo the rejected version as a denial ("Melania budzi się, w ręku nie ma żadnego listu"). Also avoid closing quips and aphorisms, stock similes ("jakby…", "jak ktoś, kto…"), and narrator commentary that carries no fact. Sections A and B also reach rpgnotes' summary prompt through `rpg-tools wiki export-context`, so run the export after editing the prose rules.
- **Python.** `uv` only: never bare `python` / `python3`, `pip`, or `python3 -m venv`; `uvx <tool>` for a one-off tool. The wiki tools are `rpg-tools` commands, not scripts in this repo.

## Content structure

```
content/
  01-Sessions/      # Session recap Markdown files ("Sesja {N} - {Tytuł}.md") + index.md
  02-People/        # Bohaterowie (PCs), Factions, NPCs/<group folder>/, Katalog postaci.md
  03-Locations/     # Kontynent Thylea/, the seas, Zaświaty i Plany/, Statki i Ruchome Wyspy/
  04-Items-and-Loot/
  05-Lore/
  06-Rules/
  07-Handouts/
  assets/sessions/{000}/  # Per-session: transcript, chat log, quotes, images, prompt .txt files
  Timeline.md       # Chronological campaign events
  Campaign_Context.md  # Running concise campaign summary
```

This is the `ootd-quartz` layout of rpg-tools (the skills' `<sessions>`, `<assets>/{000}`, `<timeline>`, `<context>`).

**Look and navigation ("Brąz i Patyna").** Palette and fonts (Cinzel headers, Alegreya Sans body) are in `quartz.config.ts`; extra tokens, the meander band and page-wide rules in `quartz/styles/custom.scss`; component styles in `quartz/components/styles/theme.scss`. Our own components, all built at build time from the content:

- `HomePage` (home only): banner hero with live counts, latest session with an excerpt, hero portraits, section tiles.
- `pages/CardFolderContent` (every folder page): an image card per page, each with its first image and its italic lead line as the subtitle; a live filter box on folders with more than 8 cards. The `index.md` bullet list that `update-indexes` writes stays for Obsidian and is hidden on the site. The sessions folder groups cards by the story arcs, read from the `### Name: subtitle (Sesje X-Y)` headings of `Campaign_Context.md`, so those headings must keep that form.
- `QuoteBubbles` (transformer, session notes): `> [!quote] Speaker` callouts become speech bubbles with the portrait from the speaker's person page; consecutive quotes alternate sides. Styles in `custom.scss`.
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

**Quartz version.** Quartz core (upstream `jackyzha0/quartz` v4, pinned in rpg-tools) and the shared plugins and components (the components above, `SessionAssets`, `OgImageExtractor`, `FrontmatterTable`, `QuoteBubbles`, the relative-link and GitHub Pages fixes, og-image paths) come from rpg-tools: `rpg-tools site sync` copies them here and records them in `.rpg-site.lock`, and refuses to overwrite a file edited here. Change those files in rpg-tools (`site/`, see its README), never here; upstream Quartz bumps happen there too. This repo owns the theme: `quartz.config.ts`, `quartz.layout.ts`, `quartz/styles/custom.scss`, `quartz/components/styles/theme.scss`, icons and the home-page texts. `site.json` is generated by the sync from the campaign's settings.

**Session "Metadane" list.** The `SessionAssets` transformer (`quartz/plugins/transformers/sessionAssets.ts`) scans `content/assets/sessions/{000}/` at build time for any recap file named `Sesja {N} - …` and lists every file in that directory — grouped into categories (Transkrypty, Logi czatu, Dane, Wideo, Obrazki, Prompty) — under the **Metadane** section rendered by `quartz/components/FrontmatterTable.tsx`. Do **not** add `transcript_*` / `chat_log` / `video_script` links to session frontmatter by hand; drop a file in the asset directory and it appears automatically. rpgnotes' working files (`draft*`, `validation_report*`, `details.json`, `manifest.json`) sit in the same folder but are never listed, and `quartz.config.ts`'s `ignorePatterns` keep them off the site.

Templates for new entity files: `templates/Session.md`, `NPC.md`, `Location.md`, `Item.md`, `Faction.md`, `Handout.md`.

Entity files may have an `image_prompt` frontmatter field — `rpg-illustrator` uses this verbatim (never paraphrase it) when the entity appears in a scene.
