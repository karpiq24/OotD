---
name: rpg-summarizer
description: Generates a narrative session recap from a transcript, using campaign context. Processes the transcript in sequential subagent chunks to preserve chronological order. Mode "from-scratch" (default) writes from the transcript alone; mode "refine" corrects an rpgnotes draft-0 instead.
---

# RPG Summarizer

Convert a raw transcript into a narrative story using the campaign's writing style. The transcript is split into ~800-line chunks processed by dedicated subagents in sequence. Each subagent receives only its chunk plus a rolling summary of prior events, so events can never be reordered or confused across the session.

Two modes, selected by the caller (`generate-session-recap-draft` Step 0):

- **`from-scratch`** (default) — no seed draft; each chunk subagent writes its narrative purely from its transcript slice. This is the flow described below.
- **`refine`** — an rpgnotes handoff bundle (`draft0.md` + `validation_report.md`) is available. Each chunk subagent additionally receives the corresponding slice of `draft0.md` and corrects/refines it instead of writing from scratch. See "Refine mode" at the bottom for the differences; everything else (glossary, phonetic corrections, chunking, validation pass) is identical.

## Step 1: Context Loading

- **Run the glossary extractor:**
  ```bash
  .venv/bin/python scripts/extract_glossary.py content/assets/sessions/{NNN}/transcript.txt
  ```
  Save the stdout — this is the **canonical-names glossary** for this session. It lists every NPC/location/item/lore entry from the wiki that appears (by phonetic prefix) in the transcript, plus aliases harvested from `[[Canonical|Alias]]` wikilinks. Embed this glossary into every chunk prompt verbatim.
- **Read** `.agents/skills/rpg-summarizer/resources/phonetic_corrections.md` — a curated list of ASR misspellings (e.g. `Pytrion → Raspytrion`). Embed verbatim into every chunk prompt too.
- **Read** the last 3 session files in `content/01-Sessions/` for narrative arc continuity.

You do NOT need to pre-load the full transcript into the orchestrator's context — the chunk subagents read their own slices.

## Step 2: Load Style Prompt

Read `.agents/skills/rpg-summarizer/resources/summary_prompt.txt` in full. You will embed its entire content into every subagent prompt below — it defines tone, character names, section formatting, and language style, plus anti-hallucination guardrails and the IC/OOC distinction.

## Step 3: Chunk the Transcript

**Pick the transcript file first**: if `content/assets/sessions/{NNN}/transcript_enriched.txt` exists (rpgnotes bundles it — the full transcript with `[VISUAL]` and `[CZAT]` annotation lines merged in, time-sorted on the shared recording clock), use it **instead of** `transcript.txt` for everything below: line counts, chunk boundaries, chunk slices, and the Step 5 fact-check. Fall back to `transcript.txt` otherwise. This applies in both modes.

Determine the total line count of the chosen file via `wc -l`. Divide into sequential chunks of ~800 lines. Record each chunk's start line and end line.

## Step 4: Sequential Subagent Processing

Process chunks strictly one at a time — never in parallel, since each depends on the previous result.

Start with `rolling_summary = ""`.

**For each chunk, spawn a subagent with this prompt:**

---
You are a narrative summarizer for a Polish D&D campaign session. This is chunk [N of TOTAL].

## Style & Rules

[paste full content of summary_prompt.txt here]

## Canonical Names Glossary

[paste full stdout of extract_glossary.py here]

## Phonetic Corrections

[paste full content of phonetic_corrections.md here]

## Context from previous chunks

[If rolling_summary is empty:]
This is the beginning of the session. No prior context.

[If rolling_summary is not empty:]
**Dotychczasowe wydarzenia sesji:**
[rolling_summary]

Continue the narrative from where these events left off. Do not re-introduce characters or locations already established. Do not recap what has already happened.

## Transcript excerpt

Read lines [START]–[END] of `content/assets/sessions/{NNN}/[transcript_enriched.txt if it exists, else transcript.txt — the file chosen in Step 3]` (use Read tool with `offset: [START-1]` and `limit: [END-START+1]`). Read ONLY this slice.

## Annotation lines (present only in transcript_enriched.txt)

Two kinds of timeline-anchored annotation lines are merged into the transcript:

- `[VISUAL HH:MM:SS] <caption>` — **scene ground truth**: what was actually on the VTT screen at that moment (map, tokens, handouts).
- `[CZAT HH:MM:SS] Speaker (rzut): <text>` / `[CZAT HH:MM:SS] Speaker: <text>` — **mechanical ground truth**: distilled FoundryVTT chat (exact damage numbers, who cast what, hit vs. miss). `[CZAT PRZED NAGRANIEM] ...` lines at the top of the file are pre-recording events.

Rules:
- Use them to get facts right — when the spoken transcript is ambiguous, prefer these lines over guessing (who cast on whom, hit vs. miss, exact totals, which scene is on screen).
- **NEVER quote them as spoken dialogue** and never attribute their text to a player's voice — they are not speech.
- Mechanical numbers still must not be narrated as game mechanics in the prose — the style rules above apply unchanged.

## Your Output

Return exactly two labeled blocks and nothing else:

### NARRATIVE
[1–4 narrative `###` sections in Polish covering this chunk's events, following the style rules above. Each section has a descriptive heading and 1–3 rich paragraphs.]

### ROLLING_SUMMARY
[3–5 bullet points in Polish: key events, decisions, revelations, and the party's location/situation at the end of this chunk. Be specific — this is the only context the next chunk will receive.]

---

After each subagent completes:
- Append its `NARRATIVE` block to your running output.
- Replace `rolling_summary` with its `ROLLING_SUMMARY` block for the next iteration.

## Step 5: Validation Pass

Before returning the assembled draft, run **one final subagent** as a fact-checker. Its job is to spot fabrications and propagated errors that slipped past the chunk subagents.

**Spawn a subagent with this prompt:**

---
You are a fact-checker for a Polish D&D session recap draft. Your job is to find specific factual claims that are NOT supported by the transcript, and propagated hallucinations.

## Inputs

- **Draft to verify:** [paste the assembled NARRATIVE here]
- **Transcript:** `content/assets/sessions/{NNN}/[transcript_enriched.txt if it exists, else transcript.txt — same file as Step 3]` ([N] lines). In the enriched file, `[VISUAL ...]` lines are scene ground truth and `[CZAT ...]` lines are mechanical ground truth (exact rolls, casters, damage) — treat them as authoritative evidence when checking claims, but flag any draft sentence that quotes them as spoken dialogue.
- **Canonical glossary:** [paste glossary]
- **Phonetic corrections:** [paste corrections]

## Method

For each claim in the draft that names a **specific spell, item, NPC, number, or "first/last/never" superlative**:
1. Find a transcript line that supports it (use Grep/Bash to search by keyword).
2. If you cannot find supporting evidence, flag it.

Also flag:
- Names not in the canonical glossary (likely ASR misspellings the chunk subagent didn't correct)
- Items/buffs/effects that come from a previous session and may have expired
- Direction-of-spell errors (who cast on whom)
- Mechanical numbers narrated as in-fiction events (e.g. "advantage k8")

## Output

Return a list, one finding per line:
- `LINE_OR_QUOTE | what's wrong | suggested fix (or "remove")`

If nothing is wrong, return exactly: `NO ISSUES`.

Do not rewrite the draft. Do not be conservative — flag anything you cannot verify.

---

The orchestrator then applies (or asks the user about) each finding before saving the file.

## Step 6: Output

Concatenate all `NARRATIVE` blocks in chunk order. Do not reorder sections. Apply validation findings.

- **Constraint**: No `[[wiki links]]` yet — plain text only.
- **Constraint**: Follow the structure from `templates/Session.md`.
- Return the complete Markdown. Do not save to a file (the workflow handles that).

## Refine mode

Everything above (Steps 1-6) is unchanged and is the default. Refine mode only changes what's added to the **per-chunk subagent prompt** in Step 4 and its instructions — chunking, the glossary, phonetic corrections, rolling summary, and the final validation pass (Step 5) all still apply exactly as described.

### Extra per-chunk input

Before Step 4, slice `draft0.md` (already read in full by the orchestrator) into `TOTAL` pieces proportional to the chunk count — the same `TOTAL` computed in Step 3 from the transcript's line count. Split `draft0.md` on its `###` headings, then assign headings to chunks by position: chunk `N` of `TOTAL` gets the headings in index range `floor((N-1)/TOTAL * num_headings)` to `floor(N/TOTAL * num_headings)`. This is an approximation (rpgnotes' chunk boundaries don't line up exactly with OotD's), so err on the side of giving a chunk one extra heading at each edge if the split looks uneven — better to over-share draft-0 content than to leave a chunk with none.

Also pass the full text of `validation_report.md` to every chunk subagent — it's short, and each subagent only needs to check whether any of its findings' quoted text falls within its own draft-0 slice.

### Modified per-chunk prompt (refine mode)

Use the same prompt template as Step 4, with two additions inserted after "## Context from previous chunks" and before "## Transcript excerpt":

---
## Draft-0 to Refine

[paste this chunk's proportional slice of draft0.md headings here]

## Validation Report (apply only findings whose quote falls in the slice above)

[paste full validation_report.md here]

## Instructions for This Draft

This is an existing narrative draft for roughly this chunk's portion of the session, generated by an automated pass with less context than you have. Your job is to **correct and refine it, not rewrite it from scratch**:

- **Anchor chronology to the draft-0 order above** — it was generated in the correct sequence; do not reorder events unless the transcript excerpt clearly shows the draft got the order wrong.
- **Fix names using the Canonical Names Glossary and Phonetic Corrections** — the draft-0 pass may have used ASR-garbled or non-canonical names.
- **Remove or correct anything the Validation Report flags** for this slice (per the note above — only findings whose quote appears in this slice apply to you).
- **Verify every remaining claim against the transcript excerpt below** — if a specific spell, item, NPC, number, or superlative in the draft isn't supported by the transcript, fix or remove it (same anti-hallucination bar as Step 4's `summary_prompt.txt`).
- Preserve the draft's section structure and headings where they're accurate; only reorganize where necessary.
- You may still add narrative color, but keep the existing prose as the starting point rather than regenerating it wholesale.
---

The rest of the chunk subagent's output contract (`NARRATIVE` + `ROLLING_SUMMARY` blocks) is unchanged.

### Validation pass (Step 5) in refine mode

Unchanged — it fact-checks the *assembled, refined* draft against the transcript exactly as in from-scratch mode. This catches anything the per-chunk refine step missed or introduced.

### Mechanics facts: use the inline [CZAT] lines, don't guess

When `transcript_enriched.txt` is in use, the chat facts for each chunk's own time window are already **inline** as `[CZAT ...]` lines in the chunk's slice — verify mechanical claims (damage totals, who cast which spell, hit vs. miss) directly against them instead of guessing or asking the user. For questions **outside** the current slice's time window, or that need the raw log (Beyond20 formatting quirks, lost details), `rpg-chatlog-analyst` and targeted greps of `chat_events.txt` / `chat_log.json` remain the tool. See that skill for query patterns and context-discipline rules (never load the whole file).
