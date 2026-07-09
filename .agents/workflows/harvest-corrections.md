---
description: Mines the user's manual draft edits (draft_pre_edit.md vs the final session file) and folds them back into the corrections files, prompt rules, and wiki. Invoked as /harvest-corrections, and automatically as Step 0 of finalize-session-recap.
---

# Harvest Corrections Workflow

When the user hand-edits a recap draft, their fixes (corrected names, removed hallucinations, entity facts, style trims) normally evaporate. This workflow captures them: it diffs the pristine pre-edit draft against the user's edited file and folds each correction back into the pipeline so the same error class never needs manual fixing twice.

All file writes in this workflow are **proposals** — nothing is written until the user confirms.

## Step 0: Initialization

1. Determine `session_number` (padded 3 digits → `{000}`): from the invocation argument, the calling workflow, or by asking the user.
2. Locate the two files to diff:
   - **Pre-edit baseline**: `content/assets/sessions/{000}/draft_pre_edit.md` (saved by `generate-session-recap-draft` Step 4.5.5).
   - **User-edited final**: `content/01-Sessions/Sesja {number} - *.md` (the current session file). If multiple match, ask which one.
3. **Graceful skip**: If `draft_pre_edit.md` does not exist, say so plainly — "No `draft_pre_edit.md` for session {number}; nothing to harvest (this draft predates the learning loop, or was written from scratch without the pre-edit snapshot)." — and stop. This is not an error; when called from `finalize-session-recap` Step 0, continue silently.

## Step 1: Diff

1. Diff the pre-edit baseline against the user-edited file, e.g. `diff content/assets/sessions/{000}/draft_pre_edit.md "content/01-Sessions/Sesja {number} - ....md"`, or read both and compare.
2. If there is no meaningful difference (only whitespace / frontmatter housekeeping), report "No substantive edits to harvest." and stop.
3. Otherwise collect each substantive change as a `(before → after)` pair (or a pure deletion / pure addition). Ignore any `<!-- UNVERIFIED: ... -->` markers the user simply removed without other change — that is just accepting the sentence.

## Step 2: Classify each change

Sort every change into exactly one bucket:

- **Name correction** — a proper noun was replaced with a different spelling of the same entity (e.g. `Pytrion → Raspytrion`, `Wersir → Versir`). Signal: same referent, changed spelling; the "after" form usually matches a canonical glossary/wiki name.
- **Deleted claim** — the user removed a specific factual claim (a spell, item, number, death, cause-effect) without replacing it. Signal: a sentence or clause vanished. These are candidate anti-hallucination examples.
- **Entity fact fix** — the user changed a *fact about a named entity* (its role, allegiance, status, relationship, location), not merely its spelling. Signal: the entity survives but an assertion about it changed.
- **Pure style edit** — wording/tone/length change with no change to who-did-what (shortened purple prose, reworded a sentence, split a paragraph). No factual delta.

If a single change spans two buckets (e.g. a name fix *and* a fact fix), record it in both.

## Step 3: Prepare proposals per bucket

Build a set of proposed file updates. **Do not write anything yet.**

### 3a. Name corrections → `phonetic_corrections.md`
1. **Read `.agents/skills/rpg-summarizer/resources/phonetic_corrections.md` first** and match its exact format — a Markdown table under `## Imiona własne` with rows `| W transkrypcji (forma błędna) | Zapisz jako |`, canonical target in **bold**.
2. For each name correction, propose either:
   - a **new row** `| {wrong form(s) seen} | **{canonical}** |`, or
   - **appending the wrong form** to an existing row's left column (pipe-separated, as existing rows do) if that canonical target already has a row.
3. **Dedupe**: skip any wrong→canonical mapping already covered by an existing row. Never add a duplicate row or a duplicate left-column variant.

### 3b. Deleted claims → anti-hallucination examples / ZAKAZY rule
1. Collect each deleted claim as a candidate anti-hallucination example (the exact text the user cut, plus a one-line reason if inferable — invented spell, uncited number, etc.).
2. **Cross-session pattern check**: look at prior harvested deletions (scan the current session's deletions against the same class of deletions — e.g. read earlier `draft_pre_edit.md`/session pairs if quick, or rely on the recurring theme). If the *same kind* of hallucination has now been deleted by the user across **≥2 sessions**, propose a **new numbered ZAKAZY rule** for `.agents/skills/rpg-summarizer/resources/summary_prompt.txt` (in the *ZAKAZY — anty-halucynacje* section, matching its numbered style and Polish wording), phrased as a hard prohibition covering that class.
3. A single-session deletion is recorded as a candidate only; do not propose a rule change for a one-off.

### 3c. Entity fact fixes → wiki entity file
1. For each entity fact fix, locate the entity's file under `content/02-People/`, `content/03-Locations/`, `content/04-Items-and-Loot/`, or `content/05-Lore/` (search by the entity name).
2. If the wiki file states the **old** fact (or lacks the corrected one), propose the same fix to that entity file so the wiki and the recap agree.
3. If no entity file exists, note it as "no wiki file to update" — do not create one here (entity creation is `rpg-wiki-manager`'s job during `/finalize-session-recap`).

### 3d. Pure style edits → style-rule amendment
1. Collect style edits and look for a **consistent** pattern (e.g. the user always trims superlatives, always shortens multi-clause sentences, always cuts a stock phrase).
2. Only if the same pattern appears **repeatedly** in this diff (or matches a pattern seen before), propose a small amendment to the style section of `.agents/skills/rpg-summarizer/resources/summary_prompt.txt` capturing that preference.
3. A one-off rewording is not a pattern — record nothing.

## Step 4: Present proposals for confirmation

1. Show the user a single, compact summary grouped by bucket. For each proposed write show: the target file, and the exact before/after (the row to add, the rule text to insert, the entity-file line to change).
2. If a bucket produced nothing, say so in one line ("No name corrections found.").
3. **Wait for explicit confirmation.** The user may approve all, approve a subset (by number), or reject. Apply **only** what the user approves.

## Step 5: Apply approved writes

1. Write each approved change to its target file, preserving that file's existing format exactly (table layout, numbering, Polish wording).
2. After writing, if any `content/` file was changed (an entity file in 3c), run `python3 scripts/update_indexes.py` per the indexes rule. Changes to `.agents/` resources do not need index regeneration.
3. **Report** what was written and what was skipped: "Harvested session {number}: {N} name corrections, {M} entity fixes applied; {K} deletion candidates recorded; {style/ZAKAZY proposals}." Keep it to a few lines.
