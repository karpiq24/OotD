---
name: import-session
description: Imports a session that rpgnotes processed (its outbox package) into the wiki, resolves open questions with the user, and leaves a draft session note for review (Part 1 of 2). The only way a new session enters the wiki. Invoke on-demand as /import-session after rpgnotes finished.
---

# Import Session

rpgnotes is the only author of a session draft: it transcribes, writes the narrative (`draft0.md`), validates it, and derives the title and detail lists (`details.json`) and the quotes (`quotes.json`). This skill brings that package into the wiki and settles what only a human can settle. It never rewrites the narrative from the transcript — if a draft is badly wrong, the fix belongs in rpgnotes' prompts or in `campaign/learned_rules.md` (see `/harvest-corrections`), and `/iterate-recap` handles targeted repairs.

## Step 1: Import the package

1. Ask the user for the `session_number` (unless given).
2. Run `uv run python scripts/import_session.py {N}`.
   - It reads `../rpgnotes/output/{000}/manifest.json` (or `$RPGNOTES_OUTBOX`), copies the published files into `content/assets/sessions/{000}/` and the working files (`draft0.md`, `details.json`, `validation_report.json`) into `private/sessions/{000}/`, and assembles `content/01-Sessions/Sesja {N} - {Title}.md` from `templates/Session.md`.
   - If it stops with an error (no package, incomplete package, unknown schema version, note already exists), relay the message to the user and stop. Only pass `--force` when the user explicitly agrees to replace an existing note.
3. Run `uv run python scripts/update_indexes.py` (a session note was created).

## Step 2: Interactive verification

Run one short structured Q&A to resolve claims that only a human can decide. Many draft errors are *transcript-faithful yet wrong* (ASR garbled the audio, table talk misread as action, ambiguous intent) — the validator could not resolve those, only the user can.

### 2.1 Collect open findings

Gather candidates into one pool:

1. **Validation findings** — every finding in `private/sessions/{000}/validation_report.json` (`quote`, `issue`, `severity`, `suggested_fix`). `error`-severity findings rpgnotes could apply automatically are already gone; what remains needs judgement.
2. **Ambiguous identities** — a name in the note that the glossary (`campaign/phonetic_corrections.md`, the entity names in `content/`) cannot decisively map to one canonical entity, or that `campaign/learned_rules.md` warns about.
3. **Abandoned-action ambiguity** — the note says a character did something, but the transcript shows them only considering it ("chyba odpuszczę", "może rzucę…").

Do not read the whole transcript to hunt for more. For each candidate, grep `content/assets/sessions/{000}/transcript_enriched.txt` (else `transcript.txt`) for its key words and read only those lines plus a little context.

**Before adding a mechanics question** (damage, who cast which spell, hit vs. miss, turn order): if `content/assets/sessions/{000}/chat_events.txt` exists, answer it yourself via skill `rpg-chatlog-analyst` (targeted greps — never read the file whole). A finding the chat log settles is applied directly with the chat line as evidence and does NOT go to the user.

### 2.2 Select and order

- **Hard cap: 10 questions.** Keep the ones with the highest narrative impact (a wrong death, caster or location beats a cosmetic detail); drop the rest silently, or mark them `UNVERIFIED` (2.4) if they matter.
- Order by impact, most consequential first.
- Every question must be decidable in seconds — yes/no or pick-one, never open-ended.

### 2.3 Ask in one message

Ask **all** questions in a single chat message, numbered, using exactly this template:

```
**Q{n}. {one-line what's uncertain}**
Draft: "{the exact sentence from the note}"
Transcript (lines {START}–{END}): "{the relevant transcript evidence}"
  a) {candidate answer A}
  b) {candidate answer B}
  c) remove it — cut the sentence / claim from the note
Reply: {n}{letter}  (e.g. "{n}a"), or "skip"
```

- Always cite transcript line numbers.
- Always offer 2–3 candidates, **"remove it" always among them**.
- Close with: "Reply with e.g. `1a 2c 3skip`, or `skip all` to leave everything unverified."

If there are no candidates at all, ask nothing and go on to Step 3.

**Two checks you do yourself, no question needed** (both caught real errors in the Oct 2026 audit):
- **Date**: compare the note's `**Data:**` with the timestamps in `content/assets/sessions/{000}/chat_log.json` (the Foundry log). If they differ, use the chat-log date and say so in Step 4.
- **Copied opening**: compare the first sentences of `## Podsumowanie` with the previous session's note. rpgnotes once reused the previous session's opening sentence verbatim (S55 = S54), which later looked like a duplicated recap. If it happens, rewrite only that sentence from the transcript.

### 2.4 Apply answers

- Edit `content/01-Sessions/Sesja {N} - {Title}.md` for each answer (rewrite the sentence, fix the name, delete the claim). If an answer removes or renames something listed under `Kluczowe wydarzenia`, `Postacie`, `Lokacje` or `Przedmioty`, fix that list too.
- For a skipped question, do not guess: put `<!-- UNVERIFIED: {short reason} -->` right before or after the sentence.

## Step 3: Clean up the quotes

`## Cytaty` holds `quotes.json` verbatim, which is raw ASR. Fix only evident mishearings that make a quote ungrammatical or senseless, following the "Cytaty z `quotes.json`" section of `campaign/phonetic_corrections.md`. Drop a quote that cannot be repaired without inventing its wording. Never rephrase.

## Step 4: Snapshot and hand over

1. Run `uv run python scripts/import_session.py {N} --snapshot` — it saves the note as it stands to `private/sessions/{000}/draft_pre_edit.md`, the baseline `/harvest-corrections` diffs the user's edits against. Do not edit the note after this.
2. Tell the user, in this order:
   - Validation findings that were neither asked about nor resolved in Step 2 (quote, issue, suggested fix) as a short list, or "No unresolved validation findings."
   - The number of `UNVERIFIED` markers, if any ("search the note for `UNVERIFIED`").
   - "Draft created at `content/01-Sessions/Sesja {N} - {Title}.md`. Review and edit it, then run `/finalize-session-recap` for wikilinks, images and the timeline."
3. Remind the user that `private/sessions/{000}/` holds new files to commit in the private repo (`git -C private add sessions/{000}`).
