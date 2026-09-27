# D&D Beyond Feats: Architectural, Design & Automation Reference

A comprehensive technical reference for designing, structuring, and automating 5e Homebrew Feats on D&D Beyond (DDB).

---

## 1. 5e Design Principles & Feat Balance

Feats are among the most difficult elements to design in D&D 5th Edition. Unlike spells or monsters, which have structured numerical formulas (damage curves, CR tables), feats are compact, powerful, and interact across every pillar of the game (combat, exploration, social interaction, and character advancement).

### 1.1 The Baseline: Ability Score Improvement (ASI) Equivalence
In 5e, feats directly compete with Ability Score Improvements (+2 to one stat or +1 to two stats). Because ability scores govern attack bonuses, damage, saving throws, AC, spell DCs, and skill checks, players sacrifice universal mathematical progression whenever they choose a feat.

#### The Two Core Design Questions (James Introcaso):
1. **"Would I rather take an ASI in my *least* important ability score than take this feat?"**
   * *Answer must be NO.* If a wizard would rather take +2 Strength than your feat, the feat is underpowered.
2. **"Would I rather take an ASI in my *most* important ability score than take this feat?"**
   * *Answer must be YES (or an agonizingly close choice).* If taking the feat is a brainless "must-have" over raising the primary stat to 20, the feat is overpowered.

### 1.2 The Three Types of 5e Feats

| Feat Category | Mechanical Composition | Official Benchmark Examples | Design Rules & Budget |
| :--- | :--- | :--- | :--- |
| **Single-Benefit Feats** | One singular, powerful ability akin to a core class feature. | *Defensive Duelist*, *Inspiring Leader*, *Lucky*, *Ritual Caster*, *Tough* | Feature must be self-contained and potent. If it feels too strong, constrain it with usage limits (e.g., *Lucky* = 3/long rest, *Inspiring Leader* = 1/short rest per creature). |
| **Multiple-Benefit Feats** | 2 to 3 smaller, synergistic features broken into bullet points. | *Alert*, *Dungeon Delver*, *Grappler*, *Shield Master*, *War Caster*, *Sharpshooter* | Individual features are weaker and often conditional (e.g., Advantage on Con saves *only* for spell concentration; cover reduction *only* for ranged attacks). Tradeoffs are common (e.g., -5 attack / +10 damage). |
| **Half-Feats** | +1 Ability Score increase + 1 or 2 minor thematic features. | *Actor*, *Keen Mind*, *Observant*, *Resilient*, *Fey Touched*, *Shadow Touched* | The +1 stat is exactly half the budget of an ASI. The remaining bullet points represent the other half. The increased stat must thematically match the benefits. In rules text, the stat increase is always the **first** bullet point. |

### 1.3 What Feats Must NOT Do: Feat Taxes & Bounded Accuracy
1. **Never Replicate Raw ASIs:** Never give an unconditional static bonus that mimics an ability score increase (e.g., flat +1 to all AC, flat +1 to all melee attack and damage rolls).
2. **Avoid "Feat Taxes":** 3e/4e suffered from "mandatory" feats like *Weapon Focus* or *Iron Will*. 5e intentionally eliminated feat taxes to protect bounded accuracy (where AC 20 and DC 18 remain meaningful across all 20 levels) and preserve build freedom.
3. **No Redundant Class Stealing:** Do not duplicate full, unnerfed high-level class features (e.g., full Cunning Action or full Extra Attack). Instead, grant a specialized or resource-limited aspect (e.g., *Martial Adept* grants 1 die and 2 maneuvers; *Metamagic Adept* grants 2 points and 2 options).

### 1.4 Anatomy of a Feat's Rules Text
Every well-formed 5e feat follows this strict 3-tier structure:
1. **Opening Flavor Sentence:** Explains what the character does in the narrative world and how they learned it.
   * *Example:* *"You have spent countless hours in ancient crypts, attuning your senses to the presence of restless dead."*
2. **Prerequisite Line (Optional):** Placed right under the title or opening line.
   * *Example:* *Prerequisite: The ability to cast at least one spell*, or *Prerequisite: Strength 13 or higher*.
3. **Mechanical Bullets:** Clear, unambiguous rules phrasing using official 5e terminology (Actions, Bonus Actions, Reactions, Short/Long Rests, saving throws).

---

## 2. DDB Form Architecture & Subforms Guide

Creating a feat on D&D Beyond is a **multi-stage process**. The initial page creates the parent entity; once created, DDB generates a permanent entity ID and unlocks six distinct sub-entity forms.

```
Base Feat Creation (/homebrew/creations/create-feat/create)
  │
  ├──> Edit Feat Dashboard (/homebrew/creations/create-feat/{id}-{slug}/edit)
  │      │
  │      ├──> Prerequisites (/entity/prerequisite/create/{feat_id})
  │      │       └──> Prereq Mapping (/entity/prerequisite-mapping/create/{prereq_id})
  │      │
  │      ├──> Modifiers (/modifier/create/{feat_id}/0)
  │      │
  │      ├──> Actions & Limited Uses (/entity/limited-use/create/{feat_id})
  │      │       ├──> Limited Use Data (/entity/limited-use/{act_id}/level-scale/create)
  │      │       └──> Level Overrides (/entity/limited-use/{act_id}/level-override/create)
  │      │
  │      ├──> Spells (/entity/spell/create/{feat_id})
  │      │
  │      ├──> Feat Options (/feats/{slug}/feat-option/create)
  │      │       ├──> Option Actions (/entity/limited-use/create/{opt_id})
  │      │       └──> Option Spells (/entity/spell/create/{opt_id})
  │      │
  │      └──> Creature Rules (/creature-rule/create/{feat_id})
```

---

### 2.1 Base Form (`/homebrew/creations/create-feat/create`)

| Element | Selector / ID | Type | Description & Notes |
| :--- | :--- | :--- | :--- |
| Feat Name | `#field-name` | `text` | Required. The public display name. |
| Version | `#field-version` | `text` | e.g. `1`, `1.5`. Used for tracking iterations. |
| Description (WYSIWYG) | `#field-item-description-wysiwyg` | TinyMCE | Full rules HTML. Must sync via `tinymce.triggerSave()`. |
| Description (Raw Fallback) | `#field-item-description` | `textarea` | Used if TinyMCE is inactive. |
| Snippet | `#field-snippet` | `textarea` | Crucial! Text displayed in the digital character sheet drawer (< 250 chars). Supports snippet math codes. |
| Feat Tags | `#field-feat-tags-public` | Select2 Multi | Tags for indexing (Combat, Buff, Damage, Utility, Origin, Species Feat, etc.). |
| Submit Button | `button[type="submit"]:has-text("CREATE FEAT")` | Button | Saves and redirects to edit page: `/homebrew/creations/create-feat/{id}-{slug}/edit`. |

---

### 2.2 Subform: Prerequisites

Prerequisites on DDB are a **two-stage configuration**:
1. **Stage 1 (Text Header):** At `/entity/prerequisite/create/{feat_id}`, you fill `#field-description` with the player-facing text (e.g. `Strength 13 or higher`). Saving redirects to `/entity/prerequisite/{prereq_id}/edit`.
2. **Stage 2 (Character Sheet Engine Mapping):** On `/entity/prerequisite/{prereq_id}/edit`, a second subform posts to `/entity/prerequisite-mapping/create/{prereq_id}`. This is what the DDB character builder evaluates to lock or unlock the feat.

#### Prerequisite Form Selectors:
* Description: `#field-description`
* Prerequisite Type: `#field-prereq-type` (Select2 container: `#s2id_field-prereq-type`)
* Prerequisite Sub-Type: `#field-prereq-sub-type` (Select2 container: `#s2id_field-prereq-sub-type`)
* Value: `#field-value` (Text: integer threshold like `13` or `4`)
* Exclusive Checkbox: `#field-create-should-exclude` (Excludes characters meeting this condition)

#### Complete Prerequisite Types Reference:

| Type Name | Type Value | Subtype Examples & Count | Usage & Mechanical Value |
| :--- | :--- | :--- | :--- |
| **Ability Score** | `1` | 6 subtypes: `Strength` (1), `Dexterity` (88), `Constitution` (89), `Intelligence` (90), `Wisdom` (91), `Charisma` (92) | Value field receives the minimum score (e.g. `13`). |
| **Class** | `9` | 608 subtypes: `Fighter`, `Wizard`, `Artificer - Armorer`, etc. | Restricts feat to specific classes or subclasses. Optional class level in Value. |
| **Class Feature** | `11` | 4,211 subtypes: `Spellcasting`, `Sneak Attack`, `Wild Shape`, `Channel Divinity`, etc. | Requires a specific class feature on the character sheet. |
| **Custom Value** | `6` | 1 subtype: `The ability to cast at least one spell` (96) | Standard spellcaster prerequisite (e.g. for *War Caster*, *Elemental Adept*). |
| **Feat** | `10` | 707 subtypes: Any published or homebrew feat. | Enables feat chains/trees (requires another feat first). |
| **Level** | `7` | 1 subtype: `Character Level` (139) | Value receives the minimum character level (e.g. `4` for 2024 general feats). |
| **Proficiency** | `5` | 5 subtypes: `Heavy Armor` (95), `Light Armor` (93), `Martial Weapons` (4656), `Medium Armor` (94), `Shields` (1915) | Validates armor or weapon proficiencies (e.g. *Heavy Armor Master*). |
| **Size** | `4` | 6 subtypes: `Tiny` (54), `Small` (55), `Medium` (56), `Large` (57), `Huge` (58), `Gargantuan` (59) | Restricts feat to specific creature sizes (e.g. *Squat Nimbleness*). |
| **Species** | `2` | 240 subtypes: `Elf`, `Dwarf`, `Dragonborn`, `Tiefling`, etc. | Species/Racial feats (e.g. *Elven Accuracy*, *Dwarven Fortitude*). |
| **Species Option** | `3` | 114 subtypes: `High Elf`, `Wood Elf`, `Fallen Aasimar`, etc. | Restricts to specific subraces or species variants. |

---

### 2.3 Subform: Spells (`/entity/spell/create/{feat_id}`)

Allows the feat to grant one or more spells, with custom casting stats, slotless casts, or ritual tags.

#### Form Selectors & Architecture:
* Spell Multi-Select: `#field-spell` (Select2 container: `#s2id_field-spell`) — Select specific spells (e.g. *Misty Step*, *Darkness*).
* Spell Levels: `#field-spell-levels` — Cantrip through 9th level filters.
* Spell Class: `#field-spell-class` — Filters by class spell list.
* Spell School: `#field-spell-school` — Abjuration, Conjuration, Evocation, etc.
* Casting Ability: `#field-ability-score` (1=STR, 2=DEX, 3=CON, 4=INT, 5=WIS, 6=CHA).
* Number of Uses: `#field-number-of-uses` (Integer or blank for at-will).
* Stat Modifier for Uses: `#field-number-of-uses-ability-modifier` (e.g. WIS mod uses).
* Proficiency Bonus for Uses: `#field-use-proficiency-bonus` (Checkbox) + `#field-proficiency-bonus-operator` (`+` or `x`).
* Reset Type: `#field-reset-type` (1=Short Rest, 2=Long Rest, 3=Dawn, 4=Other).
* Cast at Level: `#field-cast-at-level` (1 to 9; defaults to base spell level).
* Ritual Cast Type: `#field-ritual-cast-type` (1 = "Can Cast As Ritual", 2 = "Must Cast As Ritual").
* At-Will / Infinite: `#field-is-infinite` (Checkbox — check for cantrips or at-will spells like *Mage Armor* from Armor of Shadows).

#### Common Spell Granting Configurations:
1. **1st/2nd Level Spell 1/Long Rest (e.g. *Fey Touched*):**
   * Spell: Select spell.
   * Ability Score: Choose INT/WIS/CHA.
   * Number of Uses: `1`.
   * Reset Type: `Long Rest`.
   * Note: Characters with spell slots can also automatically expend their spell slots to cast spells added this way on the DDB character sheet.
2. **Cantrip (At-Will):**
   * Spell: Select cantrip.
   * Ability Score: Choose casting stat.
   * `is-infinite`: Checked (`y`).
3. **Ritual Caster Only:**
   * Spell: Select ritual spell.
   * Ritual Cast Type: `Must Cast As Ritual`.
   * Number of Uses: Leave blank; `is-infinite`: Leave blank.

---

### 2.4 Subform: Feat Options (`/feats/{slug}/feat-option/create`)

Used when a feat requires the player to choose from a list of predefined sub-features upon taking the feat (e.g. *Elemental Adept* choosing Acid/Cold/Fire/Lightning/Thunder, or *Metamagic Adept* choosing metamagic options).

#### Form Fields:
* Option Name: `#field-name`
* Description: `#field-description-wysiwyg` or `#field-description`
* Snippet: `#field-snippet`
* Submit Button: `button[type="submit"]:has-text("CREATE OPTION")` (Notice: button text is "CREATE OPTION", not "SAVE"!).

#### Critical Architectural Limitation of Feat Options on DDB:
* **What Options SUPPORT:**
  * Nested Actions & Limited Use trackers (`/entity/limited-use/create/{option_entity_id}`)
  * Nested Spells (`/entity/spell/create/{option_entity_id}`)
* **What Options DO NOT SUPPORT:**
  * **Nested Modifiers:** Directly navigating to `/modifier/create/{option_entity_id}/0` returns an **HTTP 404**. DDB does not route modifier evaluation through feat options.
  * **Workaround for Stat Choices (e.g. *Resilient* choosing a stat):** Because options cannot grant modifiers, official feats like *Resilient* use internal system-level hardcoding that homebrewers cannot replicate directly. Homebrew creators must either:
    1. Create distinct individual feats (e.g., *Resilient (Constitution)*, *Resilient (Wisdom)*).
    2. Instruct players to manually use character sheet overrides for the stat bump and save proficiency.

---

### 2.5 Subform: Creature Rules (`/creature-rule/create/{feat_id}`)

Used for feats granting pets, mounts, companions, or familiars (e.g. *Mounted Combatant* companion adjustments, homebrew beastmaster feats).

#### Form Fields:
* Rule Type: `#field-rule-type` (1 = "Create a Rule", 2 = "Choose Monsters").
* Creature Group: `#field-creature-group` (Familiar, Mount, Pet, Summoned, Sidekick, Wild Shape 2014, Wild Shape 2024).
* Monster Type: `#field-monster-type` (Beast, Celestial, Dragon, Fey, Fiend, etc.).
* Max CR: `#field-max-challenge-rating` (0, 1/8, 1/4, 1/2, 1, 2, ...).
* Movements: `#field-movements` (Burrow, Climb, Fly, Swim, Walk).
* Sizes: `#field-sizes` (Tiny, Small, Medium, Large, Huge, Gargantuan).

---

## 3. Complete Modifier Reference Table

Modifiers are the mechanical engine of DDB. Text descriptions in TinyMCE do **nothing** to character sheets. Every stat change, save proficiency, AC boost, or sense must be registered as a Modifier.

### Modifier Form Architecture (`/modifier/create/{feat_id}/0`):
1. **Modifier Type (`#field-spell-modifier-type`):** Select2 dropdown with 35 master types. Selecting a type triggers an AJAX call to load the Subtype options.
2. **Modifier Subtype (`#field-spell-modifier-sub-type`):** Select2 dropdown with dynamic subtypes.
3. **Ability Stat (`#field-rpg-stat`):** Native `<select>`: STR (1), DEX (2), CON (3), INT (4), WIS (5), CHA (6).
4. **Fixed Value (`#field-fixed-value`):** Text input for numerical bonuses (e.g. `1`, `2`, `10`).
5. **Dice Count & Dice Value (`#field-dice-count`, `#field-dice-value`):** e.g. `1` + `d6` for bonus damage.
6. **Additional Bonus Type (`#field-additional-bonus-type`):** Proficiency Bonus, Attuned Item Count, Spell Level.
7. **Restriction (`#field-restriction`):** Plain text caveat shown in parentheses on the sheet (e.g. *While wearing light armor*).

### Master Modifier Lookup Table

| Modifier Type | Common Subtypes | Ability Stat | Fixed Value | Behavior on Character Sheet |
| :--- | :--- | :--- | :--- | :--- |
| **Bonus** | `Constitution Score` (or any stat) | — | `1` or `2` | Directly increases ability score by fixed value. |
| **Bonus** | `Ability Score Maximum` | `CON` (or any) | `1` or `2` | Raises the 20 stat cap to 21 or 22. **Required** alongside stat bonus if exceeding 20. |
| **Bonus** | `Armor Class` | — | `1` | Adds flat static bonus to Armor Class. |
| **Bonus** | `Armored Armor Class` | — | `1` | Adds AC bonus only when wearing armor. |
| **Bonus** | `Saving Throws` | — | `1` | Adds flat bonus to all 6 saving throws. |
| **Bonus** | `Speed` | — | `10` | Adds +10 ft to walking speed (e.g. *Mobile*). |
| **Bonus** | `Initiative` | — | `5` | Adds flat bonus to initiative rolls (e.g. *Alert*). |
| **Bonus** | `Hit Points per Level` | — | `2` | Grants HP retroactively and prospectively (e.g. *Tough*). |
| **Advantage** | `Saving Throws` | — | — | Flags character sheet with green Advantage marker on all saves. |
| **Advantage** | `Death Saving Throws` | — | — | Adds advantage marker specifically to Death Saves. |
| **Advantage** | `Constitution Saving Throws` | — | — | e.g. *War Caster* (use Restriction: "to maintain concentration"). |
| **Advantage** | `Initiative` | — | — | Advantage on initiative rolls. |
| **Disadvantage** | `Stealth Disadvantage` | — | — | Imposes stealth disadvantage marker. |
| **Disadvantage** | `Attack Rolls Against You` | — | — | Note/reminder flag on defense tab. |
| **Resistance** | `Fire`, `Cold`, `Poison`, `All`, etc. | — | — | Adds damage resistance to character defenses block. |
| **Resistance** | `Bludgeoning, Piercing, and Slashing from Nonmagical Attacks` | — | — | High-level protection resistance. |
| **Immunity** | `Poison`, `Charmed`, `Frightened`, `Disease`, `Exhaustion`, `Critical Hits` | — | — | Adds condition or damage immunities. |
| **Vulnerability** | `Fire`, `Radiant`, etc. | — | — | Adds damage vulnerability tag. |
| **Proficiency** | `Saving Throws` | `CON` | — | Grants saving throw proficiency in designated stat (e.g. *Resilient*). |
| **Proficiency** | `Athletics` (or any skill) | — | — | Grants full proficiency in chosen skill. |
| **Proficiency** | `Heavy Armor`, `Medium Armor`, `Shields` | — | — | Grants armor category proficiencies. |
| **Proficiency** | `Martial Weapons`, `Simple Weapons`, or specific weapon | — | — | Grants weapon proficiency. |
| **Expertise** | `Athletics` (or any skill/tool) | — | — | Doubles proficiency bonus on checks with this skill. |
| **Half Proficiency** | `Ability Checks` | — | — | Grants half-PB round down to unproficient checks (Jack of All Trades). |
| **Half Proficiency Round Up** | `Ability Checks` | — | — | Half-PB round up. |
| **Language** | `All`, `Draconic`, `Elvish`, `Sylvan`, etc. | — | — | Adds language to character sheet proficiency box. |
| **Sense** | `Darkvision` | — | `60` | Adds or extends Darkvision distance in senses drawer. |
| **Sense** | `Blindsight`, `Tremorsense`, `Truesight` | — | `30` | Adds exotic senses. |
| **Set** | `Constitution Score` | — | `19` | Overrides stat to a fixed value (similar to *Amulet of Health*). |
| **Set** | `Innate Speed (Flying)` | — | `30` | Sets base fly speed. |
| **Ignore** | `Heavy Armor Speed Reduction` | — | — | Cancels the 10 ft penalty for low Strength in heavy armor. |
| **Ignore** | `Dual Wield Light Restrictions` | — | — | Allows two-weapon fighting with non-light weapons (*Dual Wielder*). |
| **Weapon Property** | `Finesse`, `Reach`, `Thrown`, `Versatile` | — | — | Adds weapon property to weapon attacks. |
| **Weapon Mastery** | `Cleave (...)`, `Nick (...)`, `Vex (...)`, `Topple (...)` | — | — | 2024 rules: Enables weapon mastery properties. |
| **Enable Feature** | `Enable Hex Weapon`, `Enable Pact Weapon` | — | — | Unlocks specific subclass integrations. |

---

## 4. Action & Limited Use Architecture

Active abilities, rerolls, limited-use attacks, and resource pools are managed through DDB's **Action & Limited Use Engine**.

### 4.1 The Two-Step Workflow (Mandatory for Checkboxes)
Saving a base Action does **NOT** create interactive checkbox trackers on the character sheet! You must execute two distinct steps:
1. **Step 1: Save the Base Action** (`/entity/limited-use/create/{feat_id}`):
   * Select `ACTION TYPE *` first: `General` (3), `Weapon` (1), or `Spell` (2).
   * Fill Name, Activation (`Special`, `Action`, `Bonus Action`, `Reaction`), and Reset Type (`Long Rest`, `Short Rest`, `Dawn`).
   * Save. DDB redirects to `/entity/limited-use/{action_id}/edit`.
2. **Step 2: Add Limited Use Data** (`/entity/limited-use/{action_id}/level-scale/create`):
   * Click **"ADD LIMITED USE DATA"**.
   * Fill `#field-number-of-uses` (e.g. `1`, `3`).
   * (Optional) Check `#field-use-proficiency-bonus` for PB-scaling uses.
   * (Optional) Select `#field-stat-modifier` for stat-scaling uses (e.g. CHA mod).
   * Save. **This generates the interactive checkboxes on the character sheet.**

### 4.2 Scaling Uses and Level Overrides

| Use Case | Implementation Strategy |
| :--- | :--- |
| **Fixed Uses (e.g. *Lucky* = 3/Long Rest)** | Level Scale: `number-of-uses = 3`, `reset-type = Long Rest`. |
| **Proficiency Bonus Uses (e.g. PB/Long Rest)** | Level Scale: `use-proficiency-bonus = checked`, `reset-type = Long Rest`. Leave `number-of-uses` empty. |
| **Stat Mod Uses (e.g. WIS mod/Long Rest)** | Level Scale: `stat-modifier = WIS`, `reset-type = Long Rest`. |
| **Stat Mod + Fixed (e.g. 1 + WIS mod)** | Level Scale: `number-of-uses = 1`, `operator = +`, `stat-modifier = WIS`. |
| **Scaling Dice per Level (e.g. Martial Arts die)** | Use **"ADD A LEVEL OVERRIDE"** (`/level-override/create`):<br>Level 1: 1d4<br>Level 5: 1d6<br>Level 11: 1d8<br>Level 17: 1d10 |

---

## 5. DDB Tooltip Tags and Snippet Codes

D&D Beyond features a rich internal parser that converts bracket tags into hoverable tooltips and evaluates handlebars-style calculation formulas inside Snippet textboxes.

### 5.1 Interactive Tooltip Tags (Use in Descriptions)
Wrap keywords in these tags to generate official interactive DDB modal tooltips:

```html
[spell]darkness[/spell]
[spell]misty step|teleport away[/spell] <!-- Custom display text -->
[magicitem]flame tongue[/magicitem]
[condition]poisoned[/condition]
[condition]incapacitated[/condition]
[sense]darkvision[/sense]
[action]dash[/action]
[action]dodge[/action]
[skill]athletics[/skill]
[monster]adult red dragon[/monster]
[feat]alert[/feat]
[class]fighter[/class]
[subclass]battle master[/subclass]
```

### 5.2 Snippet Calculation Syntax (Use in `#field-snippet`)
Snippets appear in the right-side summary drawer on the character sheet. Use these codes to display dynamic numbers calculated directly from the character's live stats:

| Code Syntax | Output on Character Sheet | Example Use Case |
| :--- | :--- | :--- |
| `{{modifier:str}}` | `+3` or `-1` (signed) | Damage bonus or attack roll addition. |
| `{{modifier:con#unsigned}}` | `3` (unsigned integer) | Resource count (e.g. "CON mod times per day"). |
| `{{proficiency}}` | `+2`, `+3`, `+4`... | Proficiency bonus. |
| `{{proficiency#unsigned}}` | `2`, `3`, `4`... | Raw integer for math strings. |
| `{{characterlevel}}` | `1` to `20` | Character total level. |
| `{{maxhp}}` | e.g. `68` | Total maximum hit points. |
| `{{savedc:wis}}` | e.g. `15` | Calculated 8 + PB + Wis save DC. |
| `{{scalevalue}}` | Variable | Current value from the active Level Scale. |
| `{{fixedvalue}}` | Integer | Value set in the action's Fixed Value box. |
| `{{rounddown(characterlevel/2)}}` | `1`, `2`, `3`... | Half character level rounded down. |
| `{{roundup(characterlevel/2)}}` | `1`, `2`, `3`... | Half character level rounded up. |
| `{{(modifier:con*2)#unsigned}}` | Integer | Dynamic mathematical expressions. |

*Example Snippet String:*
```text
As a bonus action, expend 1 charge to heal a creature for 1d8 + {{modifier:wis}} hit points (save DC {{savedc:wis}}). You can use this {{proficiency#unsigned}} times per long rest.
```

---

## 6. Playwright Automation Selectors & Recipes

Automating D&D Beyond requires handling Select2 custom elements, asynchronous AJAX cascades, dynamic Vex overlays, and TinyMCE iframe editors.

### 6.1 Authentication Context
Always initialize Playwright with the user's persistent storage state:
```python
from playwright.sync_api import sync_playwright

STORAGE_STATE = "/home/karpiq/.gemini/antigravity-cli/dndbeyond_storage_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        storage_state=STORAGE_STATE,
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    page = context.new_page()
```

### 6.2 Dismissing Modals & Overlays
Vex dialogs and marketing overlays often intercept pointer events:
```python
def clear_overlays(page):
    page.evaluate("""() => {
        document.querySelectorAll('.vex, .vex-overlay, .vex-content, .modal-backdrop, ._modal_1olz2_1').forEach(el => el.remove());
    }""")
```

### 6.3 Automating Select2 Dropdowns
DDB replaces native `<select>` tags with Select2 widgets. Direct `.select_option()` calls fail on these elements.

```python
def select2_choose(page, container_id, option_text):
    """
    Selects an option from a D&D Beyond Select2 dropdown.
    container_id: The ID of the Select2 wrapper, e.g. '#s2id_field-spell-modifier-type'
    """
    # 1. Click the Select2 container to open dropdown
    page.locator(container_id).click()
    page.wait_for_timeout(500)
    
    # 2. If a search input exists in the dropdown, type into it
    search_input = page.locator(".select2-drop-active .select2-input")
    if search_input.count() > 0 and search_input.is_visible():
        search_input.fill(option_text)
        page.wait_for_timeout(500)
        
    # 3. Click the matching option
    page.locator(".select2-drop-active .select2-result-label", has_text=option_text).first.click()
    page.wait_for_timeout(1000)
```

### 6.4 Setting TinyMCE Content Safely
```python
def set_wysiwyg_content(page, editor_id, html_content):
    page.evaluate("""({id, html}) => {
        if (typeof tinymce !== 'undefined' && tinymce.get(id)) {
            tinymce.get(id).setContent(html);
            tinymce.triggerSave();
        } else {
            const el = document.getElementById(id) || document.getElementById(id.replace('-wysiwyg', ''));
            if (el) el.value = html;
        }
    }""", {"id": editor_id, "html": html_content})
```

### 6.5 Safe Deletion of Homebrew Content
Navigating directly to `/homebrew/creations/delete?entityTypeId={typeId}&id={id}` presents a modal confirmation. The confirmation button is an `<a>` with classes `ajax-post button`:
```python
def delete_homebrew_entity(page, entity_type_id, entity_id):
    url = f"https://www.dndbeyond.com/homebrew/creations/view?entityTypeId={entity_type_id}&id={entity_id}"
    page.goto(url, wait_until="networkidle")
    
    # Trigger delete modal
    del_link = page.locator("a.homebrew-creation-actions-item-delete, a:has-text('DELETE')").first
    del_link.click()
    page.wait_for_selector(".modal, .t-submit-hb-content-modal, a.ajax-post", timeout=10000)
    
    # Confirm via AJAX post
    confirm_btn = page.locator("a.ajax-post:has-text('Yes')").first
    confirm_btn.click()
    page.wait_for_load_state("networkidle")
```

---

## 7. Common Pitfalls & Traps

| Trap | Symptom | Root Cause | Antidote |
| :--- | :--- | :--- | :--- |
| **Missing Checkboxes** | Action appears on character sheet, but has zero checkboxes to track uses. | Created the action but omitted Step 2 (`/level-scale/create`). | Always navigate to `/entity/limited-use/{id}/level-scale/create` and set `number-of-uses`. |
| **Select2 AJAX Race** | Subtype dropdown is empty or fails to select. | Clicked Subtype before the Type's AJAX response completed. | Add a 1.5s–2.0s sleep or `wait_for_response` after selecting `field-spell-modifier-type`. |
| **Option Modifiers Myth** | 404 Not Found error when automating feat options. | Attempted to POST `/modifier/create/{option_id}/0`. | Feat Options do **not** support modifiers on DDB. Use Actions/Spells, or split into separate feats. |
| **The Stat Cap Trap** | Stat bonus caps out at 20 even though the feat says "up to a maximum of 22". | Added `Bonus -> Constitution Score (+2)`, but forgot `Ability Score Maximum`. | Add a second modifier: `Bonus -> Ability Score Maximum -> CON (+2)`. |
| **TinyMCE Desync** | Feat saves with an empty description. | Modified TinyMCE DOM directly without firing `triggerSave()`. | Call `tinymce.get(...).setContent()` followed immediately by `tinymce.triggerSave()`. |
| **Vex Interception** | Playwright throws `TimeoutError: element is not clickable`. | An invisible Vex dialog or backdrop is hovering over the target button. | Execute `clear_overlays(page)` or pass `force=True` to the click locator. |
| **Public Publishing Lock** | Feat cannot be modified or deleted. | Clicked "MAKE PUBLIC". DDB locks published homebrew permanently. | **Never publish test/campaign homebrew.** Private homebrew is automatically shared with all characters in the user's DDB campaigns! |
