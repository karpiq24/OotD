---
trigger: always_on
---

# Rule: Prose Rules

## Trigger
This rule applies whenever you write or edit prose in Polish for this campaign: session recaps, wiki pages, `Timeline.md`, `Campaign_Context.md`, and the Nowa Era book (`build/nowa-era-pdf`).

## Action
Follow `campaign/proza.md`, the single source of the campaign's prose rules. Section A applies to all prose; B to session recaps, C to wiki pages, D to the Nowa Era book.

The most important rule (A2): when the user corrects or rejects something, write only the corrected version. Never echo the rejected version as a denial ("Melania budzi się, w ręku nie ma żadnego listu"). Also avoid closing quips and aphorisms, stock similes ("jakby…", "jak ktoś, kto…"), and narrator commentary that carries no fact.

Section A and B also reach rpgnotes' summary prompt through `scripts/export_context.py` (`prose_rules`), so after editing `campaign/proza.md` run the export.
