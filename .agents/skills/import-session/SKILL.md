---
name: import-session
description: Imports a session that rpgnotes processed (its outbox package) into the wiki, settles what the evidence can settle, marks the rest UNVERIFIED, and leaves a draft session note for the user to read (Part 1 of 2). The only way a new session enters the wiki. Use it without being asked whenever a session is staged and has no note (the user says "draft N jest", "sesja N", "zaimportuj"); also /import-session.
---

# Import Session

rpgnotes is the only author of a session draft: it transcribes, writes the narrative (`draft0.md`), validates it, and derives the title and detail lists (`details.json`) and the quotes (`quotes.json`). This skill brings that package into the wiki and settles what only a human can settle. It does not write the narrative anew from the transcript and adds no facts, but it does edit the draft's structure and prose (Step 2.4): rpgnotes writes the draft chunk by chunk, so only here is the whole text seen at once. Factual errors that recur belong in rpgnotes' prompts or in `campaign/learned_rules.md` (see `/harvest-corrections`), and `/iterate-recap` handles targeted repairs.

## Step 1: Import the package

1. Take the `session_number` from the user's message; if they name none, run `uv run python scripts/session_status.py` and take the one `staged` session. Ask only if that still leaves more than one.
2. Pull first (`git pull`): rpgnotes' `./run.sh` usually staged the package already, on whichever machine ran it, as a commit "{N} init" holding `content/assets/sessions/{000}/` (no note yet).
3. Run `uv run python scripts/import_session.py {N}`.
   - It reads `../rpgnotes/output/{000}/manifest.json` (or `$RPGNOTES_OUTBOX`), else the staged copy in `content/assets/sessions/{000}/`, copies every file the manifest lists into `content/assets/sessions/{000}/` (the working files `draft0.md`, `details.json`, `validation_report.json` and `manifest.json` stay off the site through `quartz.config.ts`'s `ignorePatterns`), and assembles `content/01-Sessions/Sesja {N} - {Title}.md` from `templates/Session.md`.
   - If it stops with an error (no package, incomplete package, unknown schema version, note already exists), relay the message to the user and stop. Only pass `--force` when the user explicitly agrees to replace an existing note.
4. Run `uv run python scripts/update_indexes.py` (a session note was created).

## Step 2: Verification (no questions to the user)

The user reviews only the finished text and does not want to answer questions during the import. Settle every open point you can from the evidence; what the evidence cannot settle is marked in the note and listed for the user to check while reading. Many draft errors are *transcript-faithful yet wrong* (ASR garbled the audio, table talk misread as action, ambiguous intent) — fix them when the transcript, chat log or wiki makes the answer clear, mark them when it does not.

### 2.1 Collect open findings

Gather candidates into one pool:

1. **Validation findings** — every finding in `content/assets/sessions/{000}/validation_report.json` (`quote`, `issue`, `severity`, `suggested_fix`). `error`-severity findings rpgnotes could apply automatically are already gone; what remains needs judgement.
2. **Ambiguous identities** — a name in the note that the glossary (`campaign/phonetic_corrections.md`, the entity names in `content/`) cannot decisively map to one canonical entity, or that `campaign/learned_rules.md` warns about.
3. **Abandoned-action ambiguity** — the note says a character did something, but the transcript shows them only considering it ("chyba odpuszczę", "może rzucę…").

Do not read the whole transcript to hunt for more. For each candidate, grep `content/assets/sessions/{000}/transcript_enriched.txt` (else `transcript.txt`) for its key words and read only those lines plus a little context.

**Before adding a mechanics question** (damage, who cast which spell, hit vs. miss, turn order): if `content/assets/sessions/{000}/chat_events.txt` exists, answer it yourself via skill `rpg-chatlog-analyst` (targeted greps — never read the file whole). A finding the chat log settles is applied directly with the chat line as evidence.

### 2.2 Decide each finding yourself

For each candidate, in order of narrative impact (a wrong death, caster or location beats a cosmetic detail):

- **Evidence is clear** (transcript lines, chat log, glossary or wiki settle it): fix the note. Keep a one-line record (what changed, evidence line numbers) for the Step 4 report.
- **Evidence is not clear**: leave the sentence as rpgnotes wrote it and put `<!-- UNVERIFIED: {what is uncertain; the likely alternative; transcript lines} -->` right after it. Keep these to the ones that matter (at most ~10); drop cosmetic ones silently.
- **Abandoned action** (the transcript shows only "chyba odpuszczę", "może rzucę…"): cut the claim when nothing later in the transcript confirms it happened.

**Two checks you do yourself, no question needed** (both caught real errors in the Oct 2026 audit):
- **Date**: compare the note's `**Data:**` with the timestamps in `content/assets/sessions/{000}/chat_log.json` (the Foundry log). If they differ, use the chat-log date and say so in Step 4.
- **Copied opening**: compare the first sentences of `## Podsumowanie` with the previous session's note. rpgnotes once reused the previous session's opening sentence verbatim (S55 = S54), which later looked like a duplicated recap. If it happens, rewrite only that sentence from the transcript.

### 2.3 Keep the lists in step

If a fix removes or renames something listed under `Kluczowe wydarzenia`, fix that list too.

### 2.4 Redakcja struktury i prozy

Run this after 2.1–2.3 (the `validation_report.json` findings quote the original text, so they come first) and before Step 4 (the snapshot then holds the edited version). It applies only to `## Podsumowanie`. Note the section count before you start, for the Step 4 report.

- **Sekcje.** One scene (the same place, continuous action) is one section, even a long one. Merge neighbouring sections of the same scene and short side threads (e.g. the opening vignettes of each hero). A typical session (3–4 h of play) has 5–7 sections; more only when the session really jumps between many places.
- **Nagłówki.** A heading names the scene: its place or its main event, at most two parts joined by „i”, no lists, no ornaments. Title Case as in earlier notes, each one unique.
- **Akapity.** Each paragraph is one stage of the scene: it opens with who and where, and ends on the last event, with no closing line. Merge paragraphs cut at chunk joins and one-sentence paragraphs, split ones that are too long, and remove repetitions at the joins (a character or place introduced twice, a fact told twice, A5). Rewrite the constructions forbidden in `campaign/proza.md` sections A and B, then run the A6 self-check.
- **Zakazy.** Add no facts, details or interpretations; remove no events; keep the order of events; change no proper names; leave every `<!-- UNVERIFIED -->` marker next to its sentence. Open the transcript only when a sentence cannot be merged correctly without it.
- If a merge or a new heading touches `Kluczowe wydarzenia`, keep that list consistent (as in 2.3).

## Step 3: Weave the quotes into the text

Since session 85 the note has no `## Cytaty` list: the best lines stand in `## Podsumowanie` itself, as speech bubbles with the speaker's portrait. Run this after 2.4, so the quotes land in the final section layout.

`content/assets/sessions/{000}/quotes.json` holds rpgnotes' candidates (`Postać: "cytat"`, raw ASR, more than will be used). For each candidate:

1. **Verify it.** Grep `transcript.txt` for a distinctive part of it. Check that the speaker tag above the line (`[Arevon]`) is the speaker named, that the wording matches, and where in the session it falls (the lines around it). Drop a candidate you cannot find, or one the transcript gives to someone else.
2. **Choose.** Keep 4–7 lines: in character, funny, dramatic or decisive, understandable without the lines around them. At most one per `###` section, or one exchange (two or three lines of a back-and-forth, which alternate sides on the page). Skip DM narration and table talk. A better line you meet in the transcript while verifying may replace a candidate.
3. **Clean.** Fix only evident mishearings that make a line ungrammatical or senseless, following the "Cytaty z `quotes.json`" section of `campaign/phonetic_corrections.md`. Use the canonical spelling of names. Drop a line that cannot be repaired without inventing its wording. Never rephrase. Long lines may be cut at a sentence boundary.
4. **Place.** Right after the paragraph that tells that moment, as an Obsidian callout with the speaker as the title (the name as in the party list or the person's wiki page, so the portrait is found):

   ```markdown
   > [!quote] Arevon
   > Jesteś oskarżony o zdradę stanu. Zdrada stanu kończy się śmiercią.
   ```

   Separate the callouts of one exchange with an empty line. If the paragraph already tells the same line in indirect speech, cut that clause from the paragraph (A5: one fact, one place); add nothing else to the paragraph.

The `QuoteBubbles` transformer (`quartz/plugins/transformers/quoteBubbles.ts`) renders each callout as a bubble with the portrait from the speaker's page (first image, found by file name, title or alias). A speaker without a page gets the bubble without a portrait.

## Step 4: Snapshot and hand over

1. Run `uv run python scripts/import_session.py {N} --snapshot` — it saves the note as it stands to `private/sessions/{000}/draft_pre_edit.md`, the baseline `/harvest-corrections` diffs the user's edits against. From here on, every change to the note (the user's own edits and the corrections they ask for in chat) counts as a user edit.
2. Commit the snapshot in the private repo: `git -C private add sessions/{000} && git -C private commit -m "Sesja {N}: pre-edit snapshot"`.
3. Tell the user, briefly, in Polish:
   - "Szkic gotowy: `content/01-Sessions/Sesja {N} - {Title}.md`."
   - **Do sprawdzenia przy czytaniu**: one numbered line per `UNVERIFIED` marker ("§{section}: {what is uncertain} — {likely alternative}").
   - What you fixed on your own (one line each, with the evidence), so the user can veto it.
   - The quotes placed (speaker, section), one line.
   - The 2.4 edit, concretely: "Redakcja: {X} sekcji → {Y}; scalone: „{A}” + „{B}” → „{C}”, …; akapity zredagowane według proza.md ({what kind, e.g. merged cut paragraphs, removed repeated introductions})." These edits happen before the `draft_pre_edit.md` snapshot, so `harvest-corrections` never sees them; this line is their only record.
   - "Napisz, co jest nie tak (albo popraw plik sam). Gdy tekst będzie OK, napisz „OK” — resztę (wiki, oś czasu, obrazki) zrobię sam."
4. While the user reviews: each correction they write in chat is applied right away with the method of skill `iterate-recap` (targeted transcript greps, rewrite only the affected part). Remove an `UNVERIFIED` marker once the user settles it. No confirmation questions; just apply and say in one line what changed.
5. When the user approves the text ("OK", "akceptuję", "finalizuj", "dalej", or similar), go straight on to skill `finalize-session-recap` without asking.
