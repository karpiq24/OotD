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

The campaign settings (players, Foundry, prep), the tools' campaign files (ASR corrections, learned rules, Whisper hotwords, the prose rules, the skills' wiki rules) and everything DM-only or copyrighted live outside this repo; `rpg-tools campaign show --json` gives their paths (`files.*`). Nothing from there is ever copied into this repo or linked from it.

**rpgnotes** (part of rpg-tools) turns a game's audio and Foundry log into a session draft. Sessions enter only through `rpg-tools wiki import-session` (skill `import-session`); rpgnotes never writes into this repo itself, and a new note starts with `draft: true`, so a draft never reaches the site. Draft quality is rpgnotes' job (no summarizer here); corrections flow back through the campaign files (`harvest-corrections`). The session package, the campaign context and `--stage --push`: [README.md › rpgnotes and this wiki](README.md#rpgnotes-and-this-wiki).

## Session workflow: the agent drives it

The user does not type skill names and reviews only the recap text. Read what they say and run the right step yourself:

| The user says / the state is                                                    | Do                                                                   |
| ------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| "draft N jest", "sesja N", or a draft without a number¹                         | `import-session` for N, start to finish, no questions                |
| Something wrong or missing in a draft ("X tego nie zrobił", "brakuje walki z…") | fix it right away (`iterate-recap` method), one line on what changed |
| "OK", "akceptuję", "finalizuj", "dalej" about a draft                           | `finalize-session-recap`, start to finish, images included           |
| "co z obrazkami", or `rpg-tools wiki status` shows `rendering` (images missing) | rerun `rpg-tools wiki render-images N` in the background             |

¹ Then `rpg-tools wiki status` says which one is `staged`.

Ask only when a step cannot go on without the user (no package, an existing note to overwrite). Everything else goes into the one report at the end of a step; the user vetoes there.

## Skills

The campaign skills come from rpg-tools (`skills/`, and `systems/dnd5e/skills/` for `dndbeyond-manager`), installed into `~/.claude/skills` and `~/.agents/skills` with `rpg-tools skills install`; none of them is kept in this repo. The only skill here is `verify` (`.agents/skills/verify`, linked from `.claude/skills`), for checking a change before a push. The rpg-tools skills are generic: each reads this campaign through `rpg-tools campaign show --json` and its OotD-specific rules (names, Polish wording, known canon) from `files.wiki_rules`, which override the skills' general guidance.

Pipelines: `import-session` (part 1, the only way a new session enters), `finalize-session-recap` (part 2, once the text is approved), `iterate-recap` (targeted fix from a complaint), `harvest-corrections` (learning loop). Capabilities: `rpg-wiki-manager`, `rpg-illustrator`, `rpg-timeline-manager`, `rpg-chatlog-analyst` (exact mechanics; never loads whole logs). What each does: [README.md › Skills in detail](README.md#skills-in-detail).

## Rules (always on)

- **Index files.** After a content file is created, deleted, moved, renamed, or its title changes, run `rpg-tools wiki update-indexes` instead of editing `index.md` files by hand. It regenerates every `index.md` under `content/` with correct links and titles, keeping descriptions and non-list content.
- **Wikilinks.** Simplified Obsidian format: no paths (`[[Zephyrus]]`, not `[[content/02-People/NPCs/Zephyrus.md|Zephyrus]]`), no `.md` (`[[Lutheria]]`), anchors allowed (`[[History of Thylea#The First War]]`). Heroes always by their full file name with an alias, even when the text uses the first name: `[[Felicjan Janus Twardowski|Felicjan]]`, `[[Arevon Elorrenthi|Arevon]]`, `[[Orion Xul|Orion]]`, never `[[Felicjan]]`.
- **Prose.** Polish prose in this repo (session recaps, wiki pages, `Timeline.md`, `Campaign_Context.md`) follows the campaign's prose rules, `files.prose_rules` from `rpg-tools campaign show --json`: section A applies to all prose, B to session recaps, C to wiki pages. The most important rule (A2): when the user corrects or rejects something, write only the corrected version; never echo the rejected version as a denial ("Melania budzi się, w ręku nie ma żadnego listu"). Also avoid closing quips and aphorisms, stock similes ("jakby…", "jak ktoś, kto…"), and narrator commentary that carries no fact. Sections A and B also reach rpgnotes' summary prompt through `rpg-tools wiki export-context`, so run the export after editing the prose rules.
- **Python.** `uv` only: never bare `python` / `python3`, `pip`, or `python3 -m venv`; `uvx <tool>` for a one-off tool. The wiki tools are `rpg-tools` commands, not scripts in this repo.
- **Site code.** Quartz core and the shared components come from `rpg-tools site sync` (listed in `.rpg-site.lock`): change them in rpg-tools, never here. Session asset links are never added to frontmatter by hand; a person has one home folder (other folders through `also_in`). The theme, components and frontmatter fields: [README.md › Site internals](README.md#site-internals).

## Process

- Notes from the rpg-tools skills go straight to `master` (it deploys to GitHub Pages). Anything else (the theme, `quartz.config.ts`, `quartz.layout.ts`, `battle.html`) goes on a branch with a PR: the `check` workflow runs `npm run check` and `npx quartz build`; merge when it is green.
- Before pushing: skill `verify` (`.agents/skills/verify`): which check proves which change and the flows on the built site; at least `rpg-tools wiki check-links`, and `npx quartz build` after a theme or config change.
- A PR says how it was checked; `brak (<powód>)` is allowed when nothing could be run.

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

This is the `ootd-quartz` layout of rpg-tools (the skills' `<sessions>`, `<assets>/{000}`, `<timeline>`, `<context>`). The arc headings of `Campaign_Context.md` keep the form `### Name: subtitle (Sesje X-Y)` (the sessions folder page groups by them).

Templates for new entity files: `templates/Session.md`, `NPC.md`, `Location.md`, `Item.md`, `Faction.md`, `Handout.md`.

Entity files may have an `image_prompt` frontmatter field — `rpg-illustrator` uses this verbatim (never paraphrase it) when the entity appears in a scene.
