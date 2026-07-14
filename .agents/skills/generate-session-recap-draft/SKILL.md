---
name: generate-session-recap-draft
description: Generates a session recap draft from a transcript (Part 1 of 2). Runs in refine mode when rpgnotes has already dropped a draft0.md into content/assets/sessions/{NNN}/. Invoke on-demand as /generate-session-recap-draft when starting a new session's recap.
---

# Generate Session Recap Draft

This skill processes a raw transcript into a markdown draft. It has two modes:

- **Refine mode** — rpgnotes has already run for this session and written `draft0.md` + `validation_report.md` straight into `content/assets/sessions/{NNN}/` (rpgnotes' `OUTPUT_DIR` points at this repo's `content/`, so there's no copy step — its output lands here directly). The chunk subagents correct/refine that draft instead of writing from scratch. Cheaper, faster, and the draft anchors chronology.
- **From-scratch mode** — no `draft0.md` found for this session. Current behavior, unchanged.

## Step 1: Initialization

1. Ask the user for the `session_number`.
2. Confirm the input files exist in `content/assets/sessions/{000}/`:
   - `transcript.txt` (Required)
   - `transcript_enriched.txt` (Optional — transcript with `[VISUAL]`/`[CZAT]` annotation lines merged in; when present, chunking and fact-checking use it instead of `transcript.txt`)
   - `chat_log.json` (Optional)
   - `chat_events.json` / `chat_events.txt` (Optional — distilled, timeline-anchored Foundry chat; see skill `rpg-chatlog-analyst`)
   - `transcript.json` (Optional)
   - **Refine mode**: `draft0.md` present ⇒ refine mode; `validation_report.md` and `quotes.json` also expected alongside it.
3. If none of these exist yet, they may still be loose in `input/` from an older rpgnotes run — move them into `content/assets/sessions/{000}/` first, then continue.

## Step 2: Context Loading & Analysis

1. **Line Count**: Run `wc -l` on `content/assets/sessions/{000}/transcript_enriched.txt` if present, else `transcript.txt` — the skill chunks whichever file exists (enriched preferred) and needs this count to plan chunks.
2. **Build canonical glossary**: Run `.venv/bin/python scripts/extract_glossary.py content/assets/sessions/{000}/transcript.txt`. The stdout is the session-specific canonical-names list (filtered to names that appear in this transcript). Pass it verbatim into every chunk subagent prompt.
3. **Read phonetic corrections**: `.agents/skills/rpg-summarizer/resources/phonetic_corrections.md` — list of known ASR misspellings. Pass verbatim into every chunk subagent prompt too.
4. **Read** the last 3 session files in `content/01-Sessions/` to understand the current narrative arc. Do NOT load all transcript dialogue into your context — the rpg-summarizer skill handles the full text via chunk subagents.
5. **Refine mode only**: Read `content/assets/sessions/{000}/draft0.md` and `content/assets/sessions/{000}/validation_report.md` in full — these are small (a chunked, already-validated Gemini summary) and are needed to slice per-chunk in Step 4.

## Step 4: Draft Generation (Text Only)

1. **Activate** skill `rpg-summarizer`, passing the mode determined in Step 1 (`refine` if `draft0.md` was found, else `from-scratch`). In refine mode, also pass the full text of `draft0.md` and `validation_report.md` loaded in Step 2.5.
2. **Generate** the narrative draft (the skill returns the narrative text only — the structured details sections are derived later, in Step 4.7).
   - Pick a provisional `title` from the narrative (Step 4.7 finalizes it).
   - **NO** Wikilinks at this stage.
   - **NO** Images at this stage.
3. **Save** the narrative draft to `content/01-Sessions/Sesja {number} - {Title}.md`.

## Step 4.5: Interactive Verification

Before telling the user "draft ready", run one short structured Q&A to resolve claims that only a human can decide. Many draft errors are *transcript-faithful yet wrong* (ASR garbled the audio, table talk misread as action, ambiguous intent) — the fact-checker cannot resolve those from the transcript, only the user can.

### 4.5.1 Collect open findings

Gather every unresolved question from these sources into one candidate pool:

1. **Fact-checker findings** — the `rpg-summarizer` Step 5 validation pass returned findings the orchestrator could not confidently resolve from the transcript alone (anything you would otherwise have guessed at).
2. **Refine mode — handoff validation report** — findings in `content/assets/sessions/{000}/validation_report.md` with severity `suspicious` or `question_for_user` that were not already fixed during refinement.
3. **Ambiguous identity resolutions** — a name the glossary + phonetic corrections + context could not decisively map to one canonical entity (the Versir / Versi Wyrocznia / Versi Pierwsza class of problem).
4. **Abandoned-action ambiguity** — the transcript shows a character considering but maybe not committing an action ("chyba odpuszczę", "może rzucę…") and it is unclear whether it happened.
5. **Chunk-boundary chronology joints** — where two chunks meet, whether scene X really preceded scene Y or was a flashback / table talk misplaced into the narrative.

**Before adding a mechanics question to the pool** (damage numbers, who cast which spell, hit vs. miss, initiative/turn order): if `content/assets/sessions/{000}/chat_events.txt` exists, first try to answer it yourself via skill `rpg-chatlog-analyst` (targeted greps — never read the file whole). A finding the chat log settles is applied directly with the chat line as evidence and does NOT go to the user; only questions the chat log genuinely cannot answer (intent, off-screen fiction, table talk) remain candidates.

### 4.5.2 Select and order

- **Hard cap: 10 questions.** Respect the user's time.
- If there are more than 10 candidates, keep the 10 with the highest **narrative impact** (a wrong death, wrong caster, wrong location beats a cosmetic detail). Silently drop the rest — do not ask about low-impact items; for those, prefer the `UNVERIFIED` marker path in 4.5.4.
- Order the surviving questions by narrative impact, most consequential first.
- Every question must be **decidable in seconds** — yes/no or pick-one only. Never open-ended. Bad: "What happened in this scene?" Good: "Did Orestes drink the potion, or only consider it?"

### 4.5.3 Ask in one message

Ask **all** questions in a **single chat message** as a numbered list. Do not ask them one at a time. Use exactly this per-question template:

```
**Q{n}. {one-line what's uncertain}**
Draft: "{the exact draft sentence}"
Transcript (lines {START}–{END}): "{the relevant transcript evidence}"
  a) {candidate answer A}
  b) {candidate answer B}
  c) remove it — cut the sentence / claim from the draft
Reply: {n}{letter}  (e.g. "{n}a"), or "skip"
```

Rules for the template:
- Always cite transcript line refs so the user can check the source fast.
- Always offer 2–3 candidate answers, and **"remove it" must always be one of them**.
- Close the message with one line: "Reply with e.g. `1a 2c 3skip`, or `skip all` to leave everything unverified."

### 4.5.4 Apply answers immediately

- For each answered question, edit the draft **now** to reflect the chosen answer (rewrite the sentence, fix the name/caster/order, or delete the claim for "remove it"). Note each resolution to yourself so Step 5 does not re-list it.
- For any question the user **skips** (or leaves unanswered, or `skip all`), do not guess: wrap the affected sentence in an inline HTML comment so the review gate highlights it:
  `<!-- UNVERIFIED: {short reason, e.g. "ASR unclear — did the spell land?"} -->` placed immediately before or after the sentence.
- Re-save the updated draft to `content/01-Sessions/Sesja {number} - {Title}.md`.

### 4.5.5 Save a pristine pre-edit copy

After Step 4.7 assembles the complete session file, copy it verbatim to `content/assets/sessions/{000}/draft_pre_edit.md`. This is the baseline the `harvest-corrections` learning loop diffs against after the user hand-edits the draft — save it before the user touches the file, and do not modify it afterwards. (So the actual copy happens at the end of Step 4.7, not here.)

If there were **no** candidate findings at all, skip 4.5.3 (ask nothing) and proceed to Step 4.7 — an empty Q&A round is silent.

## Step 4.7: Generate Session Details & Assemble the Final File

rpgnotes no longer pre-renders any part of the session file — this skill assembles it, here, after refinement and interactive verification.

1. **Derive the details from the final refined draft** (not from the transcript), per `templates/Session.md`:
   - **Title** — concise and evocative; it names the file: `Sesja {N} - {Title}.md`. If it differs from the provisional title from Step 4.3, rename the file.
   - `## Kluczowe wydarzenia` — bullet list of the session's key events.
   - `## Postacie` — NPCs who appeared.
   - `## Lokacje` — locations visited.
   - `## Przedmioty` — notable items gained, lost, or used.
2. **Populate `## Cytaty`** from `content/assets/sessions/{000}/quotes.json` if present — quotes are verbatim; pick the good ones, never rephrase them. If the file is absent, leave the section empty.
3. **Assemble the complete session file**: `templates/Session.md` frontmatter (just `title` — asset links are no longer written by hand; the `SessionAssets` transformer scans `content/assets/sessions/{000}/` at build time and lists every file under **Metadane** automatically) + `**Data**` + the narrative under `## Podsumowanie` + the sections above. Still **NO** wikilinks and **NO** images (that is skill `finalize-session-recap`). Save to `content/01-Sessions/Sesja {number} - {Title}.md`.
4. **Save the pristine copy**: copy the assembled file verbatim to `content/assets/sessions/{000}/draft_pre_edit.md` (see 4.5.5).

## Step 5: Completion & Review Reminder

1. **Refine mode only**: Re-read `content/assets/sessions/{000}/validation_report.md` and list every unresolved finding with severity `suspicious` or `question_for_user` that was **not already answered in Step 4.5** (rpgnotes already auto-applies simple `error`-severity fixes; a finding resolved interactively must not be re-listed here). Present any remainder as a short bulleted list — quote, issue, suggested fix — right above the completion notice.
2. **UNVERIFIED markers**: If Step 4.5 left any `<!-- UNVERIFIED: ... -->` markers in the draft, mention the count in the review notice and tell the user to search the file for `UNVERIFIED` — these are the sentences the agent could not verify and the user skipped.
3. **Notify User**: "Draft created at `content/01-Sessions/Sesja {number} - {Title}.md`. Please review the text, make edits as needed, and then run `/finalize-session-recap` to generate wikilinks, images, and other assets." In refine mode, prepend the validation findings from step 5.1 to this message (or state "No unresolved validation findings." if none remain). Append the UNVERIFIED notice from step 5.2 if any markers remain.
