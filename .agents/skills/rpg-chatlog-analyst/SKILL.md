---
name: rpg-chatlog-analyst
description: Answers precise mechanics questions (exact damage, who cast which spell, initiative order, roll results) from the FoundryVTT chat log of a session, cross-referenced with the transcript and screenshot timeline. Use on demand during recap refinement or fact-checking — never load whole logs into context.
---

# RPG Chatlog Analyst

The FoundryVTT chat archive is the only *mechanically exact* record of a session: the transcript is fuzzy ASR of spoken Polish, but the chat log has the literal dice formulas, totals, spell names and who rolled them. Use it to settle questions the transcript can't: "how much damage did the Colossus take?", "who actually cast that Fireball?", "did Versir hit or miss?".

## Data sources (per session, in `content/assets/sessions/{NNN}/`)

| File | What it is | How to use |
|---|---|---|
| `chat_events.txt` | Distilled log: one line per message, `[HH:MM:SS] Speaker (rzut): text \| rzuty: formula = total` | **Primary source.** Grep it. |
| `chat_events.json` | Same events, structured: `{offset_secs, speaker, kind, text}` | For scripted filtering (jq / python). |
| `chat_log.json` | Raw Foundry archive (HTML content, ISO timestamps) | Last resort when the distilled text lost a detail. |
| `transcript_enriched.txt` | Full transcript with `[CZAT ...]` (and `[VISUAL ...]`) lines already merged inline, time-sorted | Good for **reading a moment in context** — what was said around a chat event. For precise/mechanical queries, still grep `chat_events.txt` / `chat_log.json`. |
| `recording_start.txt` | Unix timestamp of Craig recording start | The shared t=0 (see below). |

These arrive via the rpgnotes handoff bundle; if only `chat_log.json` exists, fall back to grepping it (content is HTML — expect noise).

## The shared timeline

All three evidence streams use **the same clock**: seconds since the Craig recording started (`recording_start.txt`).

- Transcript: chronological order; `transcript.json` has exact `start` offsets per segment.
- `[VISUAL HH:MM:SS]` and `[CZAT HH:MM:SS]` lines in `transcript_enriched.txt`: screenshot captions and distilled chat events merged into the transcript at that offset (`[CZAT PRZED NAGRANIEM]` = before recording start).
- `[HH:MM:SS]` prefixes in `chat_events.txt`: chat messages at that offset. `[PRZED NAGRANIEM]` = before the recording started (setup chatter — usually ignorable).

So to verify a transcript moment mechanically: note roughly where in the session it happens (fraction of the transcript ≈ fraction of the recording, or use a nearby `[VISUAL]` anchor), then grep `chat_events.txt` for lines within ± a few minutes of that offset.

## Context discipline (hard rules)

- **NEVER read `chat_log.json` or `chat_events.txt` in full into your context.** A session has 300-500 events; you need 5-20 lines.
- Query with targeted tools: `grep -n "Fireball" chat_events.txt`, `grep -n "^\[02:3" chat_events.txt` (time window), `jq '[.[] | select(.offset_secs > 9000 and .offset_secs < 9600)]' chat_events.json`.
- Quote back only the matching lines, with their timestamps, as evidence.

## Typical queries

```bash
# Everything a character did:
grep -n "Versir (rzut)" chat_events.txt
# A specific spell/weapon:
grep -in "cataclysmic bolt" chat_events.txt
# A time window around a transcript/[VISUAL] moment at 02:33:
grep -n "^\[02:3[0-5]" chat_events.txt
# Big damage numbers (rolls render as "formula = total"):
grep -n "= [0-9]\{2,\}" chat_events.txt
```

## When to use this skill

- **During recap refinement** (`rpg-summarizer` refine mode): a draft sentence names a number, spell, or attacker that the validation report flagged — check the chat log before touching the prose.
- **Interactive verification (Step 4.5 of `/generate-session-recap-draft`)**: before asking the user a *mechanics* question, try answering it from the chat events; only ask the user what the chat log genuinely cannot answer (intent, off-screen fiction, table talk).
- **On-demand user questions** ("ile obrażeń zadał X?", "kto rzucił ten czar?") — answer with the exact chat line(s) as citation.

## Caveats

- Chat speakers are token/actor names, not player names — map via the party roster in `Campaign_Context.md` if needed.
- Beyond20 rolls (from D&D Beyond) render slightly differently than native Foundry rolls; totals appear as `= N` either way.
- The chat log only knows what went through Foundry — theatre-of-mind rulings, verbal GM fiat, and Discord-only banter exist solely in the transcript.
