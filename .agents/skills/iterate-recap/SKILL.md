---
name: iterate-recap
description: Targeted fix pass for an existing session recap. Given a session number and a free-form complaint, re-reads only the relevant transcript slices and rewrites only the affected sections. Tool-agnostic — usable from Claude Code or Antigravity.
---

# Iterate Recap

For "the draft is okay, but…" sessions. The user points at something wrong or missing in an already-generated recap; you fix **only that**, re-reading just the relevant transcript slice, and leave the rest of the file untouched.

This skill is deliberately **tool-agnostic**: it uses only *read*, *search/grep*, and *edit* operations, so it can be followed from Antigravity as well as Claude Code. Do not assume any specific agent's tooling.

## Step 0: Inputs

1. **Session number** (`{number}`, padded to `{000}`) — from the invocation argument or ask the user.
2. **Complaint** — the user's free-form description of what is wrong or missing (e.g. "the fight with Versir is in the wrong order", "you dropped the part where Orion found the amulet", "Raspytrion's name is misspelled in the second half").
3. Locate the recap file: `content/01-Sessions/Sesja {number} - *.md`. If several match, ask which. Locate the transcript: `content/assets/sessions/{000}/transcript.txt`.

## Step 1: Derive search keywords from the complaint

From the complaint, extract the concrete anchors to search for:
- Proper nouns (character / NPC / location / item names). Expand each through `.agents/skills/rpg-summarizer/resources/phonetic_corrections.md` — the transcript may hold an ASR-garbled spelling, so search for the wrong forms too, not just the canonical name.
- Distinctive action/keywords ("amulet", "trucizna", "brama", a spell name).
Build a small list of search terms covering both canonical and garbled spellings.

## Step 2: Locate the relevant transcript slice(s)

1. Search (grep) the transcript for each keyword to find the line numbers where the relevant moment occurs. Note the matching line ranges.
2. Read **only** those slices, plus a small margin of context (roughly 30–50 lines on each side of a match), so you understand what actually happened. Do **not** read or re-summarize the whole transcript — this is a targeted pass.
3. If the complaint is about missing content, the grep tells you whether the moment exists in the transcript at all; if it does not, tell the user rather than inventing it.

## Step 3: Locate the affected section(s) in the recap

Read the recap file and identify only the `###` section(s) the complaint touches. Confirm the boundaries of what needs to change before editing.

## Step 4: Targeted rewrite

1. Rewrite **only** the affected section(s), grounded in the transcript slice you read in Step 2. Follow the same style and anti-hallucination bar as the summary prompt (`.agents/skills/rpg-summarizer/resources/summary_prompt.txt`) — correct names via the glossary/phonetic corrections, no invented specifics.
2. **Do not touch any other part of the file.** Preserve unaffected sections, frontmatter, existing wikilinks, image links, and ordering verbatim. Edit surgically — replace only the sentences/sections that are wrong or missing.
3. If reordering is requested, move only the affected passages; do not regenerate surrounding prose.
4. Preserve any `[[wikilinks]]` and image placeholders inside a section you rewrite — do not strip links the finalize pass added.

## Step 5: Report

Tell the user exactly what changed: which section(s) were rewritten and why (cite the transcript line range you used), and confirm the rest of the file is unchanged. If you could not find transcript support for the requested change, say so and make no edit.
