---
name: rpg-summarizer
description: Generates a narrative session recap from a transcript, using campaign context. Processes the transcript in sequential subagent chunks to preserve chronological order.
---

# RPG Summarizer

Convert a raw transcript into a narrative story using the campaign's writing style. The transcript is split into ~800-line chunks processed by dedicated subagents in sequence. Each subagent receives only its chunk plus a rolling summary of prior events, so events can never be reordered or confused across the session.

## Step 1: Context Loading

- **Run the glossary extractor:**
  ```bash
  .venv/bin/python scripts/extract_glossary.py content/assets/sessions/{NNN}/transcript.txt
  ```
  Save the stdout — this is the **canonical-names glossary** for this session. It lists every NPC/location/item/lore entry from the wiki that appears (by phonetic prefix) in the transcript, plus aliases harvested from `[[Canonical|Alias]]` wikilinks. Embed this glossary into every chunk prompt verbatim.
- **Read** `.agent/skills/rpg-summarizer/resources/phonetic_corrections.md` — a curated list of ASR misspellings (e.g. `Pytrion → Raspytrion`). Embed verbatim into every chunk prompt too.
- **Read** the last 3 session files in `content/01-Sessions/` for narrative arc continuity.

You do NOT need to pre-load the full transcript into the orchestrator's context — the chunk subagents read their own slices.

## Step 2: Load Style Prompt

Read `.agent/skills/rpg-summarizer/resources/summary_prompt.txt` in full. You will embed its entire content into every subagent prompt below — it defines tone, character names, section formatting, and language style, plus anti-hallucination guardrails and the IC/OOC distinction.

## Step 3: Chunk the Transcript

Determine the total line count of the transcript via `wc -l`. Divide into sequential chunks of ~800 lines. Record each chunk's start line and end line.

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

Read lines [START]–[END] of `content/assets/sessions/{NNN}/transcript.txt` (use Read tool with `offset: [START-1]` and `limit: [END-START+1]`). Read ONLY this slice.

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
- **Transcript:** `content/assets/sessions/{NNN}/transcript.txt` ([N] lines)
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
