---
name: finalize-session-recap
description: Finishes a session recap after the user approved its text, end to end with no questions — harvests the user's corrections, adds wikilinks and entity pages, the timeline, image prompts, and renders the images with agy. Use it without being asked as soon as the user approves a draft ("OK", "akceptuję", "finalizuj", "dalej"); also /finalize-session-recap.
---

# Finalize Session Recap

This skill processes a user-reviewed session recap draft, adding wikilinks, images, and other assets. The user reviews only the recap text: run every step through without asking questions or waiting for confirmation, and report once at the end. Everything it writes is in git, so the user can undo any part afterwards.

## Step 0: Harvest Corrections (learning loop)

Before finalizing, mine the edits the user just made to the draft so the same errors do not recur. This step is **non-blocking**: if there is nothing to harvest, continue silently to Step 1.

1. Take the `session_number` from the conversation (the draft just approved) or from `uv run python scripts/session_status.py` (the one session in `draft`); ask only if neither names exactly one. Activate skill `harvest-corrections` for it in **auto-apply mode**: it diffs `content/assets/sessions/{000}/draft_pre_edit.md` against the user-edited session file and writes the `campaign/` / wiki updates itself, without a confirmation round. Keep its report for Step 6.
2. If `draft_pre_edit.md` is missing (e.g. an older draft), harvest-corrections skips gracefully — do not treat this as an error; proceed to Step 1.

## Step 1: Initialization
1.  Use the `session_number` from Step 0.
2.  **Locate** the draft file: `content/01-Sessions/Sesja {number} - *.md`.
    *   If multiple files match, ask the user to clarify.
    *   If no file matches, error out.

## Step 2: Context Loading
1.  **Read** the *User-Edited* file: `content/01-Sessions/Sesja {number} - ... .md`.

## Step 3: Finalization (Wikilinks, Prompts, Timeline)
1.  **Link, Update and Create Entities**:
    *   Activate skill `rpg-wiki-manager`.
    *   Search for entity names in the text.
    *   Replace with `[[wikilinks]]`.
    *   Update any target entities with new information.
    *   Create any new characters, locations etc.
    *   Save the file.
2.  **Generate Image Prompts**:
    *   Activate skill `rpg-illustrator` with mode `Session Recap - Prompts Only`.
    *   Input: path to the session markdown file.
    *   The skill generates prompts, saves them as `.txt` files in `content/assets/sessions/{000}/`, and inserts placeholder image links into the markdown.
3.  **Timeline & Context**:
    *   Activate skill `rpg-timeline-manager`.
    *   Append Key Events to `content/Timeline.md`.
    *   Update concise summary in `content/Campaign_Context.md`.
4.  **Refresh the campaign context for rpgnotes**:
    *   Run `uv run python scripts/export_context.py`.
    *   This writes `campaign/campaign_context.json` (gitignored), the only thing rpgnotes reads from the wiki: new entities, aliases, the timeline entry, and anything harvested in Step 0 reach the next session's transcription and draft through it.

## Step 4: Image Generation (no review gate)

The user does not review prompts. Render right after Step 3:

1. **Claude Code**: start `uv run python scripts/render_session_images.py {number}` with `run_in_background` and hand the turn back with a short "renderuję {k} obrazków w tle". Do not poll or sleep; the completion notification is the signal. It renders every `{000}_*.txt` that has no `.webp` yet through agy, one at a time, and writes `content/assets/sessions/{000}/{stem}.webp`.
   - Exit 0: all done. Exit 3: some images failed after a retry (listed in the output) — rerun the script once for just those; if they fail again, simplify those prompts (shorter, fewer characters) and rerun. Exit 2: agy's quota ran out — tell the user how many are left; `session_status.py` shows it as `rendering`, and rerunning the script picks up only what is missing.
   - When done, look at each image (Read the `.webp`) for obvious failures: text or captions burned in, a wrong number of main characters, a broken anatomy that stands out, a modern-world element. Rewrite the prompt of a failed one, delete its `.webp`, and rerun the script.
2. **Antigravity**: activate skill `rpg-illustrator` with mode `Session Recap - Generate Images` (it calls `generate_image` itself), input `content/assets/sessions/{000}/`.

## Step 5: Commit

Run Steps 5–6 once the render has finished (in Claude Code: after its completion notification).

1. Run `uv run python scripts/update_indexes.py` and `uv run python scripts/check_wikilinks.py`; fix any broken link this session introduced.
2. Commit in the public repo: the session note, its asset folder, the entity pages, `Timeline.md`, `Campaign_Context.md`, `campaign/` — message `Sesja {number}: {Title}`. Commit any private-repo changes with `git -C private`. Do not push unless the user has asked for pushes.

## Step 6: Completion

One short report in Polish:
- the harvest: what was written to `campaign/` and which wiki facts were fixed (one line each), so the user can veto any of it;
- entity pages created / updated (names only);
- images: rendered / redone / missing;
- the commit hash.
