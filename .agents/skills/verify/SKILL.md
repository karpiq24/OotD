---
name: verify
description: Use before pushing to master or opening a PR in the OotD wiki - which check proves which change (the build is the run) and the flows to walk through on the built site.
---

# Verify a change in the wiki

This repo is content: running it means building it. Quartz code under `quartz/` comes from
`rpg-tools site sync` (change it in rpg-tools, not here), so a check here proves the notes, the theme,
the config and `battle.html`.

| Command                         | Proves                                                             | When                                                       |
| ------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------- |
| `rpg-tools wiki check-links`    | no broken wikilinks, alias collisions or duplicate note names      | every change to `content/`                                 |
| `rpg-tools wiki update-indexes` | the section indexes list every note (a second run changes nothing) | notes added, moved or removed                              |
| `npm run check`                 | types and formatting of the theme and config (the PR check)        | theme, `quartz.config.ts`, `quartz.layout.ts`, `*.md` docs |
| `npx quartz build`              | the whole site builds into `public/` (the PR check and the deploy) | before every push                                          |

Before pushing to `master` or opening a PR: the rows that apply are green, and the flows your change
touches pass. A PR says how it was checked; when nothing could be run, write `brak (<powód>)`.

## Feature map: flows on the built site

Run `npm ci` once, then `npx quartz build --serve` (http://localhost:8080) for the flows that need a browser.

1. **Build** - `npx quartz build` ends without errors and `public/index.html` exists.
2. **Links and indexes** - `rpg-tools wiki check-links` reports nothing; after `rpg-tools wiki update-indexes`,
   `git status` shows only the notes you meant to change.
3. **Session note** - after `rpg-tools wiki import-session N` (skill `import-session`) the note is in
   `content/01-Sessions/` with `draft: true`, so the site does not show it yet (do not remove the flag by
   hand). After `finalize-session-recap` the flag is gone and its images are in
   `content/assets/sessions/NNN/`; on the served site the page opens, the images load, the Metadane list
   shows the session's files and its links lead to existing pages.
4. **New or moved note** - it is listed in its section's index page and found by the site search.
5. **Theme or layout change** - the home page, one folder page and one session page look right in light
   and dark mode, at desktop and phone width.
6. **`battle.html`** - the deploy copies it verbatim to `public/battle.html` (it is not built by Quartz):
   after `npx quartz build`, `cp battle.html public/` and open `/battle.html` on the served site.
7. **Public repo** - `git diff --staged` holds no DM-only notes, spoilers or private data (they stay
   outside this repo).

## When a check fails

Fix the cause: never push past a failing build or a broken link. If `quartz/` itself is broken, run
`rpg-tools site sync` or report it in rpg-tools; three failed rounds of fixes: stop and ask the GM.
