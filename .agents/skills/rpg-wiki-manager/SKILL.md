---
name: rpg-wiki-manager
description: Extracts entities (NPCs, Locations, Items, Lore, Handouts) from RPG session recaps and input files, updating the wiki structure.
---

# RPG Wiki Manager Skill

This skill allows the agent to process session recaps and raw input files to update the D&D Campaign Wiki.

## 1. Input Processing Strategy (Manual Agentic Workflow)

The agent must manually read, analyze, and process each file. **Do not rely on scripts for content extraction** due to inconsistent formats.

### Core Loop
For each file you are given — a session recap already in `content/01-Sessions/` (from `finalize-session-recap`), or a raw file staged in `input/`:
1.  **READ**: Read the full content of the file.
2.  **IDENTIFY**: Determine the type (Session Recap, Handout, Source Material).
3.  **PARSE**: Go through the content section by section (or paragraph by paragraph).
4.  **LINK/CREATE**: For every proper noun (Person, Place, Item), check if it exists in the wiki. Link it or create it.
5.  **HANDLE ASSETS**: Move linked images/videos to appropriate asset folders and update links.
6.  **MOVE**: If the file is not yet under `content/`, move it to its final destination there.

## 2. File Type Handling

-   **Session Recaps** (e.g., "Sesja 64..."):
    -   **Destination**: `content/01-Sessions/`
    -   **Filename Format**: `Sesja X - Title.md` (e.g. `Sesja 3 - Skradziony Róg.md`).
    -   **Assets**: Create a subdirectory `content/assets/sessions/<000>/` (3-digit session number).
        -   **Images**: Move all images used in the recap there. Update links.
        -   **Videos**: Only if the user mentions videos for this session, ask where they are, move them to the asset folder, and append them to the end of the recap file under the `## Filmy` section using `![Title](../assets/sessions/<000>/video.mp4)`. Do not go looking for them.
    -   **Action**: Extract entities (NPCs, Locations) mentioned. Update the "Session Index" if one exists.
-   **Handouts** (Letters, Notes, Images):
    -   **Destination**: `content/07-Handouts/`
    -   **Action**: Ensure it has a meaningful title. If it's an image, create a wrapper Markdown file.
-   **Source Material** (Lore, Rulebooks):
    -   **Destination**: `content/` (appropriate subfolder)

## 3. Entity Linking and Creation Rules

**Goal**: Every significant entity mentioned in the text must be wikilinked: `[[Entity Name]]`.
**Constraint**: Do NOT modify the narrative content of the summary itself, only add wikilinks.

### The "Preserve Image Prompts" Rule
When copying, moving, or editing files, keep every image embed exactly as it is: its alt text, its path, and the `[Prompt](….txt)` link that follows it. Current recaps keep the generation prompt in that `.txt` file; in older recaps the alt text itself is the prompt (e.g. `![Draw a fantasy castle...](path.png)`), so never shorten it to `![Image]` or anything else. Losing the prompt means the user cannot regenerate the image in the same style.

### The "Search First" Rule
Before creating ANY new file or link:
1.  **SEARCH**: Search the wiki by file name to see if the entity already exists.
    -   *Example*: Input says "Kyrah the Goddess". Search for "Kyrah". Found `content/02-People/Kyrah.md`. Acknowledge existence.
2.  **LINK**: In the text, replace "Kyrah the Goddess" with `[[Kyrah|Kyrah the Goddess]]`.
    -   *Rule*: Always alias to the existing filename if the text differs.

### The "Create with Template" Rule
If the entity does **NOT** exist:
1.  **DETERMINE TYPE**: Is it an NPC, Location, Item, Faction, or Handout?
2.  **READ TEMPLATE**: Read the appropriate template in the root `templates/` directory.
3.  **CREATE**: Create the new file in the correct directory using the template content.
4.  **LINK**: Update the source text to link to this new file: `[[New Entity Name]]`.

### The "Update Existing" Rule
If the entity **DOES** exist and plays a major role in the session (e.g. death, major revelation, change of status):
1.  **UPDATE**: Edit the entity's file.
2.  **APPEND**: Add a sentence to the `## Historia` section summarizing the new event, in chronological order.
3.  **REFERENCE**: Explicitly link the session: `W [[Sesja X - Tytuł]]...`
4.  **CURRENT STATE**: If the status changed (died, destroyed, abdicated, changed sides, moved, lost or gave away an item), also fix the italic lead line, `## Opis` and any present-tense section so they describe the entity *as it is now*. Goals that are over (achieved, failed, abandoned) move into `## Historia` in the past tense — never leave a stale "Cele" claiming the entity still pursues them.
5.  **SPREAD THE FACT**: If the same fact appears elsewhere (the other side of a relationship, the owner of an item, the location's "Mieszkańcy", `content/Timeline.md`, `content/Campaign_Context.md`), make those agree too. Grep for the name before finishing.

## 3a. How entity pages are written (learned in the Oct 2026 canon audit)

These rules come from the full audit that brought all 490 entity pages in line with the recaps. Follow them for every page you create or edit.

1.  **Sources and their weight.** Session recaps (`content/01-Sessions/`) are canon. Below them: transcripts (`content/assets/sessions/{000}/transcript.txt`, sessions 32+), the in-world handouts (`content/07-Handouts/` — legends, journals, letters, tomb inscriptions; often the only source for backstory), then the sourcebook vault (`input/vault/`). A recap beats the book and the handouts. The user is the DM: their ruling beats everything, including a recap.
2.  **No invention.** Every sentence must come from one of those sources. Do not fill a page with plausible-sounding sourcebook lore, appearance or personality that no source states. A short true page beats a long invented one.
3.  **Conflicting sources.** When two recaps contradict each other with no in-story explanation, do not pick silently: write the later version, add `<!-- CONFLICT: S{a} „…” vs S{b} „…” -->` and ask the user. Known example: the S81 vs S82 Lamia kill — the DM ruled S81.
4.  **In-world voice.** Entity pages are written from inside the world. Never "kampania", "sesja" (outside the `[[Sesja N - …]]` citation links), "gracze", "MG", game mechanics talk in prose, memes or real-world references ("Charon from the Hades game", "named after Gordon Ramsay"). Use "w czasie wojny z Tytanami", "zanim bohaterowie przybyli do Mytros", "po wojnie", "jego dalsze losy pozostają nieznane". `Campaign_Context.md` is the exception (it is context for rpgnotes, not a wiki page).
5.  **Aliases.** Add a frontmatter list `aliases:` with the nominative name variants actually used for the entity in recaps or transcripts: short names (`Arevon`), alternative spellings (`Kasandra`), epithets (`Pan Burz`). Never declensions (`Arevona`), generic words (`stolica`), misspellings of another entity's name, or a name that is another page's file name. `scripts/export_context.py` passes these aliases to rpgnotes. Before inventing a new page, search file names **and** `aliases:` — the entity may exist under another name (e.g. `Hubert` = Hoobert, `Ikar` = Ikar V2, `Blemys` = Blemysi).
6.  **Links must resolve.** Link only to pages that exist (or that you create in the same pass). Do not leave `[[Name]]` pointing nowhere — either create the page or write plain text. Heroes always by full file name with alias (`[[Arevon Elorrenthi|Arevon]]`), never `[[Arevon]]`, even though that alias resolves. Watch for malformed links with two pipes (`[[A|B|C]]`).
7.  **What gets a page.** Named NPCs, places, items, factions and creature types that matter to the story. Not one-line cameos, table jokes or out-of-world references (Karol Strasburger, Dolores Umbridge, Kapitan Bomba, Koło Fortuny were deliberately not given pages). When unsure, ask the user.
8.  **Prose.** Follow `campaign/proza.md` (sections A and C): concrete facts, no epithets or narrator commentary, no closing quips, and when a fact is corrected write only the new version, never a denial of the old one.
9.  **User notes are context, not text.** When the user explains something ("he's basically Charon from Hades", "it's a meme"), write in-world prose that follows the intent; never paste the note or its real-world reference into the page.
10. **Item pages with mechanics.** Type line in Polish (`_Cudowny przedmiot, legendarny (wymaga dostrojenia przez Poszukującego)_`; epic paths by their Polish names from `content/05-Lore/Epickie Ścieżki.md`). `## Właściwości` in clear Polish 5e terms (ułatwienie, rzut obronny, akcja dodatkowa, reakcja, długi odpoczynek, ST, KP, obrażenia od błyskawic…), spell names in English italics (*misty step*), upgrades as `###` tiers (`Dotknięte przez Boga`, `Wzmocnienie Mojr`) naming the price paid. The user's own homebrew text may be translated in full; never paste copyrighted sourcebook text.
11. **Known campaign facts that look like errors but are not**: Hoobert is Felicjan's familiar — he dies and is summoned again (one extra "o" per death), so his deaths are not contradictions. The Isle of Oathbreakers arena (S68–S69) set the heroes against foes they had already defeated (the Nether Sea is a realm of the dead), so dead bosses reappearing there is intended. There were three different Cerbers. Thessilea is the long-dead true queen of Themis; Nastura ruled in her name.

## 4. Inconsistency Handling

-   **Ambiguous Names**: If "The Captain" is mentioned and you know who it is, link it: `[[Orestes|The Captain]]`.
-   **Variant Spellings**: Fix spelling only if it's clearly a typo of a known name, and link it.
-   **Missing Data**: If creating an NPC and you only know their name, fill the template with known info and drop the empty sections (no "TBD" or placeholder text left on the page). Do NOT invent information.
-   **Checks before finishing**: run `uv run python scripts/update_indexes.py` after creating or renaming pages. `uv run python scripts/check_wikilinks.py` reports broken wikilinks and alias collisions across `content/`.

## 5. Standard Directories for New Entities
When creating NEW entities, always use these target directories:
-   **NPCs**: always a subfolder of `content/02-People/NPCs/`, never the folder itself. Pick the one place or group the person mainly belongs to (`Mytros/`, `Praxys/`, `Kult Węża/`, `Smoki/`, `Potwory/`…); `Inne/` only when nothing fits. If the person also belongs elsewhere (a cult member living in Mytros, a hero's family, a god's dragon form, a crew member), keep one file and add `also_in:` with those other folder names (e.g. `also_in: [Mytros, Bohaterowie]`); the site then lists them there too. A hero's partner, children, parents or closest companion get `Bohaterowie` in `also_in`. A new NPC folder needs an `index.md` with `title:` and `group:` (one of the sections in `02-People/NPCs/index.md` `groups:`).
-   **Lead line**: the first italic line under the image (`_Złodziejka i członkini Kultu Węża._`) is shown as the subtitle on every card listing, so keep it one short sentence that says who or what this is.
-   **PCs**: `content/02-People/Bohaterowie/`
-   **Locations**: `content/03-Locations/` (use `Kontynent Thylea/` or appropriate region if known)
-   **Items**: `content/04-Items-and-Loot/`
-   **Factions**: `content/02-People/Factions/`
-   **Lore**: `content/05-Lore/`

## 6. Templates

All templates are in the root `templates/` directory. Use these for new files:
-   **NPCs**: `templates/NPC.md`
-   **Locations**: `templates/Location.md`
-   **Items**: `templates/Item.md`
-   **Handouts**: `templates/Handout.md`
-   **Factions**: `templates/Faction.md`
