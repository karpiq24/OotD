# D&D Beyond Monster Creation & Automation Reference

A comprehensive technical and design reference for creating, calculating, formatting, and automating Monsters on D&D Beyond (DDB).

---

## Table of Contents
1. [5e Monster Design Principles & Math](#1-5e-monster-design-principles--math)
   - [Core Philosophy (James Introcaso / DMG)](#core-philosophy)
   - [Hit Dice & Constitution Math](#hit-dice--constitution-math)
   - [Offensive vs. Defensive Challenge Rating (CR)](#offensive-vs-defensive-challenge-rating-cr)
   - [Action Economy & Legendary Balancing](#action-economy--legendary-balancing)
2. [DDB Monster Form Architecture & Field Details](#2-ddb-monster-form-architecture--field-details)
   - [Entity Lifecycle & Identifiers](#entity-lifecycle--identifiers)
   - [Base Form Field Reference (`/create-monster/create`)](#base-form-field-reference)
   - [Subforms & Nested Sections (Edit Page)](#subforms--nested-sections-edit-page)
3. [Special Traits, Actions & Attacks Setup](#3-special-traits-actions--attacks-setup)
   - [Standard Attack Formatting](#standard-attack-formatting)
   - [Save DCs & Area Effects](#save-dcs--area-effects)
   - [Recharge Mechanics](#recharge-mechanics)
   - [Spellcasting & Psionics Formatting](#spellcasting--psionics-formatting)
4. [Legendary, Mythic & Lair Actions](#4-legendary-mythic--lair-actions)
   - [Legendary Actions Preamble & Action Economy](#legendary-actions-preamble--action-economy)
   - [Mythic Actions Architecture](#mythic-actions-architecture)
   - [Lair Actions & Regional Effects](#lair-actions--regional-effects)
5. [DDB Tooltip Tags & Rollable Engine](#5-ddb-tooltip-tags--rollable-engine)
   - [Interactive Tooltips](#interactive-tooltips)
   - [The Rollable JSON Tag Engine](#the-rollable-json-tag-engine)
6. [Playwright Automation Guide](#6-playwright-automation-guide)
   - [Session & Storage State](#session--storage-state)
   - [DOM Selectors & Input Handling](#dom-selectors--input-handling)
   - [Select2 Multi-Select Handling via jQuery](#select2-multi-select-handling-via-jquery)
   - [TinyMCE Rich Text Management](#tinymce-rich-text-management)
   - [Subform Sequential Automation Flow](#subform-sequential-automation-flow)
   - [Safe Deletion Routine](#safe-deletion-routine)
7. [Common Pitfalls & Traps](#7-common-pitfalls--traps)

---

## 1. 5e Monster Design Principles & Math

### Core Philosophy
*(Ref: James Introcaso, "Design Workshop: Monsters")*

1. **Pick Challenge Rating (CR) First**: Settle on your desired CR *before* assigning numbers. Designing to a target CR provides clear mathematical boundaries for AC, HP, attack bonuses, save DCs, and damage per round (DPR).
2. **Hit Points over Armor Class**: D&D 5e philosophy emphasizes that hitting a monster is fun for players. High AC frustrates players; high HP provides tension and pacing. The toughest monsters in official 5e (the *Tarrasque*, *Tiamat*) max out at AC 25.
3. **Save Symmetry & Weaknesses**: Avoid giving a creature high bonuses across all 6 saving throws. Leave at least one or two weak saves (typically Dexterity, Intelligence, or Charisma) so spellcasters can target strategic vulnerabilities.
4. **Standard Phrasing**: Always mirror official wording (e.g., *Pack Tactics*, *Amorphous*, *Legendary Resistance*). This ensures immediate clarity at the table and consistency across rules engines.

---

### Hit Dice & Constitution Math

A monster's Hit Die size is strictly determined by its physical **Size Category**:

| Size | Hit Die | Average Die Roll | Typical Die Count Formula |
| :--- | :---: | :---: | :--- |
| **Tiny** | `d4` | 2.5 | $Y\text{d}4 + (Y \times \text{CON mod})$ |
| **Small** | `d6` | 3.5 | $Y\text{d}6 + (Y \times \text{CON mod})$ |
| **Medium** | `d8` | 4.5 | $Y\text{d}8 + (Y \times \text{CON mod})$ |
| **Large** | `d10` | 5.5 | $Y\text{d}10 + (Y \times \text{CON mod})$ |
| **Huge** | `d12` | 6.5 | $Y\text{d}12 + (Y \times \text{CON mod})$ |
| **Gargantuan** | `d20` | 10.5 | $Y\text{d}20 + (Y \times \text{CON mod})$ |

#### The Calculation Formula
$$\text{Average HP} = \lfloor Y \times \text{Average Die Roll} \rfloor + (Y \times \text{CON modifier})$$
where $Y$ is the Hit Die Count.

*Example*:
A Medium monster (d8, average 4.5) with CON 20 (+5 modifier) and 20 Hit Dice:
- Formula: $20 \times 4.5 + (20 \times 5) = 90 + 100 = 190$
- Display string: `190 (20d8 + 100)`
- In DDB:
  - `field-average-hit-points` = `190`
  - `field-hit-points-die-count` = `20`
  - `field-hit-points-die-value` = `8` (d8)
  - `field-hit-points-modifier` = `100`

---

### Offensive vs. Defensive Challenge Rating (CR)
*(Dungeon Master's Guide, Chapter 9: "Creating a Monster")*

A monster's final CR is the arithmetic average of its **Defensive CR** and **Offensive CR**, rounded to the nearest integer (or standard fractional tier: 0, 1/8, 1/4, 1/2).

#### Proficiency Bonus Table by CR
| CR Range | Proficiency Bonus |
| :--- | :---: |
| 0 – 4 | +2 |
| 5 – 8 | +3 |
| 9 – 12 | +4 |
| 13 – 16 | +5 |
| 17 – 20 | +6 |
| 21 – 24 | +7 |
| 25 – 28 | +8 |
| 29 – 30 | +9 |

#### Step A: Defensive CR
1. **Calculate Effective HP**:
   - Start with base average HP.
   - Apply Damage Resistances / Immunities multiplier based on expected CR:
     - **CR 1–4**: 2.0x (Resistances) / 2.0x (Immunities)
     - **CR 5–10**: 1.5x (Resistances) / 1.75x (Immunities)
     - **CR 11–16**: 1.25x (Resistances) / 1.5x (Immunities)
     - **CR 17+**: 1.0x (Resistances) / 1.25x (Immunities)
     *(Note: Only apply if the creature resists/is immune to common damage types like B/P/S or multiple elements).*
   - **Legendary Resistance**: Add effective HP:
     - CR 1–4: +10 HP per use (+30 total for 3/day)
     - CR 5–10: +20 HP per use (+60 total for 3/day)
     - CR 11+: +30 HP per use (+90 total for 3/day)
2. **Determine Base Defensive CR from DMG Table**:
   - Match Effective HP against the DMG Monster Statistics table to find the preliminary Defensive CR.
3. **Adjust for Armor Class**:
   - Compare actual AC to the suggested AC for that preliminary Defensive CR.
   - For every **2 points difference** between actual AC and table AC, adjust the Defensive CR up or down by 1.
   - *Traits adjusting AC*: *Magic Resistance* adds +2 effective AC; *Nimble Escape* adds +4 effective AC.

#### Step B: Offensive CR
1. **Calculate Average Damage Per Round (DPR)**:
   - Calculate damage over the first **3 rounds of combat**, assuming all attacks hit and the most damaging abilities/recharge attacks are used first.
   - Include damage from:
     - Multiattack
     - Bonus actions
     - Reactions
     - **Legendary Actions** (3 per round, using the highest damaging options)
   - Take the average of the 3 rounds: $\text{DPR} = \frac{\text{Round 1} + \text{Round 2} + \text{Round 3}}{3}$.
2. **Determine Base Offensive CR from DMG Table**:
   - Match the DPR against the DMG table to find the preliminary Offensive CR.
3. **Adjust for Attack Bonus or Save DC**:
   - Compare the monster's actual Attack Bonus (or primary Save DC) to the suggested value for that preliminary Offensive CR.
   - For every **2 points difference**, adjust the Offensive CR up or down by 1.

---

### Action Economy & Legendary Balancing

| Combat Role | Action Requirements | Design Guidance |
| :--- | :--- | :--- |
| **Standard Minion / Brute (CR 0–4)** | 1 Action, standard Movement | Simple single attack or basic spell/ability. |
| **Elite / Lieutenant (CR 5–10)** | Multiattack (2–3 attacks), 1 Reaction, Bonus Action utility | May have recharge abilities (Recharge 5–6) or special triggers. |
| **Solo Boss (CR 10+)** | Multiattack + 3 Legendary Actions + Reactions | Needs legendary actions to balance the party's action economy. |
| **Apex / Lair Boss** | Multiattack + 3 Legendary Actions + Lair Actions (Init count 20) | Interleaved lair actions deny player positioning and battlefield dominance. |
| **Mythic Encounter** | 2-Phase HP bar + Mythic Trait + Mythic Actions | Second phase resets HP, activates new terrifying legendary choices. |

---

## 2. DDB Monster Form Architecture & Field Details

### Entity Lifecycle & Identifiers
- **Entity Type ID for Monsters**: `779871897`
- **Initial Creation Form**: `https://www.dndbeyond.com/homebrew/creations/create-monster/create`
- **Monster Edit Form**: `https://www.dndbeyond.com/homebrew/creations/monsters/{id}-{slug}/edit`
- **Public View URL**: `https://www.dndbeyond.com/monsters/{id}-{slug}`
- **Delete URL (AJAX)**: `https://www.dndbeyond.com/homebrew/creations/delete?entityTypeId=779871897&id={id}`

---

### Base Form Field Reference
All fields present on `/homebrew/creations/create-monster/create`:

#### 1. Basic Metadata
| Field ID | Name / Selector | Type | Req? | Description & Allowed Values |
| :--- | :--- | :--- | :---: | :--- |
| `field-stat-block-type` | `stat-block-type` | `<select>` | **Yes** | `'0'` = 5e (2014), `'1'` = 5.5e (2024). Default to `'0'` for legacy 5e. |
| `field-Name` | `Name` | `<input text>` | **Yes** | Monster name (2 to 256 chars). |
| `field-version` | `version` | `<input text>` | No | Version identifier (e.g. `1.0`). |
| `field-monster-type` | `monster-type` | `<select>` | **Yes** | `'1'` Aberration, `'2'` Beast, `'3'` Celestial, `'4'` Construct, `'6'` Dragon, `'7'` Elemental, `'8'` Fey, `'9'` Fiend, `'10'` Giant, `'11'` Humanoid, `'13'` Monstrosity, `'14'` Ooze, `'15'` Plant, `'16'` Undead, `'17'` Unknown. |
| `field-monster-sub-type` | `monster-sub-type` | `<select multi>` | No | Select2 multi-select (e.g. `Elf`, `Demon`, `Shapechanger`). |
| `field-size` | `size` | `<select>` | **Yes** | `'2'` Tiny, `'3'` Small, `'4'` Medium, `'5'` Large, `'6'` Huge, `'7'` Gargantuan, `'10'` Medium or Small. |
| `field-swarm-monster` | `swarm-monster` | `<select>` | No | If a swarm, links to base creature type. |
| `field-alignment` | `alignment` | `<select>` | No | `'1'` LG, `'2'` NG, `'3'` CG, `'4'` LN, `'5'` Neutral, `'6'` CN, `'7'` LE, `'8'` NE, `'9'` CE, `'10'` Unaligned, `'11'` Any Alignment, etc. |
| `field-challenge-rating` | `challenge-rating` | `<select>` | **Yes** | `'1'` 0, `'2'` 1/8, `'3'` 1/4, `'4'` 1/2, `'5'` 1, `'6'` 2 ... `'35'` 30. |

#### 2. Defenses & Health
| Field ID | Name / Selector | Type | Req? | Description & Allowed Values |
| :--- | :--- | :--- | :---: | :--- |
| `field-armor-class` | `armor-class` | `<input text>` | **Yes** | Integer AC (e.g. `18`). |
| `field-armor-class-type` | `armor-class-type` | `<input text>` | No | Source/type in parentheses, e.g. `natural armor`, `plate`, `leather armor`. |
| `field-average-hit-points` | `average-hit-points` | `<input text>` | **Yes** | Integer average HP (e.g. `190`). Must match the Hit Die calculation. |
| `field-hit-points-die-count` | `hit-points-die-count`| `<input text>` | **Yes** | Number of Hit Dice (e.g. `20`). |
| `field-hit-points-die-value` | `hit-points-die-value`| `<select>` | **Yes** | `'4'` d4, `'6'` d6, `'8'` d8, `'10'` d10, `'12'` d12, `'20'` d20. |
| `field-hit-points-modifier` | `hit-points-modifier` | `<input text>` | No | Flat HP bonus. Standard 5e equals $\text{Die Count} \times \text{CON mod}$. |

#### 3. Ability Scores & Senses
| Field ID | Name / Selector | Type | Req? | Description & Allowed Values |
| :--- | :--- | :--- | :---: | :--- |
| `field-strength` | dynamic hash | `<input text>` | **Yes** | STR score (1..30). |
| `field-dexterity` | dynamic hash | `<input text>` | **Yes** | DEX score (1..30). |
| `field-constitution` | dynamic hash | `<input text>` | **Yes** | CON score (1..30). |
| `field-intelligence` | dynamic hash | `<input text>` | **Yes** | INT score (1..30). |
| `field-wisdom` | dynamic hash | `<input text>` | **Yes** | WIS score (1..30). |
| `field-charisma` | dynamic hash | `<input text>` | **Yes** | CHA score (1..30). |
| `field-passive-perception` | `passive-perception` | `<input text>` | **Yes** | Integer passive perception score ($10 + \text{WIS mod} + \text{Perception prof}$). |
| `field-initiative-bonus` | dynamic hash | `<input text>` | No | Initiative override bonus (leave empty to default to DEX mod). |

#### 4. Proficiencies, Adjustments & Immunities (Select2 Multi-Selects)
| Field ID | Selector / Name | Type | Options / IDs |
| :--- | :--- | :--- | :--- |
| `field-monster-saving-throw` | `monster-saving-throw` | `<select multi>` | Proficient saves: `'1'` STR, `'2'` DEX, `'3'` CON, `'4'` INT, `'5'` WIS, `'6'` CHA. |
| `field-damage-adjustment` | `damage-adjustment` | `<select multi>` | Resistances, Immunities, Vulnerabilities. Examples: `'11'` Acid Resistance, `'27'` Acid Immunity, `'22'` Poison Immunity, `'47'` Force Resistance, `'17'` Bludgeoning Immunity. |
| `field-condition-immunity` | `condition-immunity` | `<select multi>` | Condition IDs: `'1'` Blinded, `'2'` Charmed, `'3'` Deafened, `'4'` Exhaustion, `'5'` Frightened, `'6'` Grappled, `'7'` Incapacitated, `'8'` Invisible, `'9'` Paralyzed, `'10'` Petrified, `'11'` Poisoned, `'12'` Prone, `'13'` Restrained, `'14'` Stunned, `'15'` Unconscious. |

#### 5. Category Tags, Habitat & Gear
| Field ID | Selector / Name | Type | Notes |
| :--- | :--- | :--- | :--- |
| `field-monster-environments`| `monster-environments` | `<select multi>` | Habitats (Arctic, Coastal, Desert, Forest, Underdark, Urban, etc.). |
| `field-monster-tags-public` | `monster-tags-public` | `<select multi>` | Tags (e.g. *Titan*, *Shapechanger*, *Dracolich*). |
| `field-gear-description` | `gear-description` | `<input text>` | Items carried, e.g. `6 Javelins, Plate Armor`. |
| `field-languages-note` | `languages-note` | `<input text>` | Language condition notes, e.g. `telepathy 120 ft., understands Draconic but can't speak`. |

#### 6. Narrative & Rich Text Description Fields (TinyMCE)
On DDB, all creature actions, traits, and lore are stored as formatted HTML text in dedicated rich textareas:
- `field-special-traits-description-wysiwyg` (Special Traits)
- `field-actions-description-wysiwyg` (Actions)
- `field-bonus-actions-description-wysiwyg` (Bonus Actions)
- `field-reactions-description-wysiwyg` (Reactions)
- `field-monster-characteristics-description-wysiwyg` (Lore, Story & Physiology)
- `field-legendary-actions-description-wysiwyg` (Legendary Actions)
- `field-mythic-actions-description-wysiwyg` (Mythic Actions)
- `field-lair-description-wysiwyg` (Lair Description, Lair Actions, Regional Effects)

---

### Subforms & Nested Sections (Edit Page)

After clicking `#save-changes` on the initial creation page, the browser redirects to the Monster Edit Page (`/homebrew/creations/monsters/{id}-{slug}/edit`). This unlocks 4 subforms:

```mermaid
graph TD
    A[Initial Monster Creation Form] -->|Save Monster| B[Monster Edit Page]
    B --> C[Add a Movement: /monster/movement/create/{id}]
    B --> D[Add a Sense: /monster/senses/create/{id}]
    B --> E[Add a Skill: /monster/skills/create/{id}]
    B --> F[Add a Language: /entity/language/create/{id}-779871897]
```

#### 1. Movement Subform (`/monster/movement/create/{id}`)
- `field-movement-type` (`<select>`):
  - `'1'`: **Walk**
  - `'2'`: **Burrow**
  - `'3'`: **Climb**
  - `'4'`: **Fly**
  - `'5'`: **Swim**
  *(CRITICAL: DDB excludes already-added movement types from this dropdown!)*
- `field-speed` (`<input text>`): Speed in feet (integer, e.g. `40`, `80`).
- `field-note` (`<textarea>`): e.g. `(hover)` for flying creatures.

#### 2. Senses Subform (`/monster/senses/create/{id}`)
- `field-sense` (`<select>`):
  - `Blindsight`
  - `Darkvision`
  - `Tremorsense`
  - `Truesight`
- `field-sense-note` (`<input text>`): Range and notes (e.g. `60 ft.`, `120 ft. (blind beyond this radius)`).
*(Note: Passive Perception is set on the main form, not in this subform!)*

#### 3. Skills Subform (`/monster/skills/create/{id}`)
- `field-skill` (`<select>`): 18 standard 5e skills (Acrobatics, Arcana, Athletics, Deception, History, Insight, Intimidation, Investigation, Medicine, Nature, Perception, Performance, Persuasion, Religion, Sleight of Hand, Stealth, Survival).
- `field-value` (`<input text>`): **Base Value**. This is the creature's Ability Modifier + Proficiency Bonus (e.g. WIS +1 and Prof +5 = `6`).
- `field-additional-bonus` (`<input text>`): **Additional Bonus**. Used for Expertise or miscellaneous bonuses (e.g. `5` for expertise, resulting in total skill bonus of $6 + 5 = 11$).

#### 4. Languages Subform (`/entity/language/create/{id}-779871897`)
- `field-language` (`<select>`): 175 language options (Common, Draconic, Elvish, Undercommon, Telepathy, etc.).
- `field-note` (`<input text>`): Qualification note (e.g. `120 ft.` for Telepathy, or `understands but cannot speak`).

---

## 3. Special Traits, Actions & Attacks Setup

### Standard Attack Formatting

Official 5e monster attack formatting is strictly standardized. Every attack must state:
1. **Name**: In bold italic (`<p><em><strong>Attack Name.</strong></em> ...</p>`)
2. **Attack Type**: `Melee Weapon Attack:`, `Ranged Weapon Attack:`, `Melee Spell Attack:`, or `Ranged Spell Attack:` in italics.
3. **To Hit Bonus**: Expressed with sign (`+7 to hit`).
4. **Range / Reach**: `reach 5 ft.`, `reach 10 ft.`, or `range 150/600 ft.`
5. **Target**: `one target.`, `one creature.`, or `two targets.`
6. **Hit Result**: `Hit:` in italics, followed by average damage, roll expression in parentheses, and damage type. Plus any secondary damage or conditions.

#### Melee Attack Example (with Rollable Tags)
```html
<p><em><strong>Bite.</strong> Melee Weapon Attack:</em> [rollable]+12;{"diceNotation":"1d20+12", "rollType":"to hit", "rollAction":"Bite"}[/rollable] to hit, reach 10 ft., one target. <em>Hit:</em> 18 [rollable](2d10+7);{"diceNotation":"2d10+7", "rollType":"damage", "rollAction":"Bite", "rollDamageType":"piercing"}[/rollable] piercing damage plus 9 [rollable](2d8);{"diceNotation":"2d8", "rollType":"damage", "rollAction":"Bite", "rollDamageType":"force"}[/rollable] force damage.</p>
```

#### Ranged Attack Example
```html
<p><em><strong>Longbow.</strong> Ranged Weapon Attack:</em> [rollable]+7;{"diceNotation":"1d20+7", "rollType":"to hit", "rollAction":"Longbow"}[/rollable] to hit, range 150/600 ft., one target. <em>Hit:</em> 8 [rollable](1d8+4);{"diceNotation":"1d8+4", "rollType":"damage", "rollAction":"Longbow", "rollDamageType":"piercing"}[/rollable] piercing damage.</p>
```

#### Multiattack Example
```html
<p><em><strong>Multiattack.</strong></em> The dragon makes one Bite attack and two Claw attacks.</p>
```

---

### Save DCs & Area Effects

Monster Save DCs follow standard 5e math:
$$\text{Save DC} = 8 + \text{Proficiency Bonus} + \text{Key Ability Modifier}$$

Area effects specify:
1. Target area shape and size (e.g. `60-foot cone`, `20-foot-radius sphere`, `30-foot line that is 5 feet wide`).
2. Saving throw type and DC (`DC 18 Dexterity saving throw`).
3. Full damage on failed save, half damage on success (`taking 54 (12d8) fire damage on a failed save, or half as much damage on a successful one`).

---

### Recharge Mechanics

For abilities that recharge on a d6 roll at the start of the monster's turn:
- **Recharge 5–6**: 33% chance per round (standard for dragon breath weapons).
- **Recharge 6**: 17% chance per round (high-impact abilities).
- **Recharge after Short or Long Rest**: Limited use per encounter.

#### DDB HTML & Rollable Format for Recharge:
```html
<p><em><strong>Singularity Breath [rollable](Recharge 5&ndash;6);{"diceNotation":"1d6", "rollType":"recharge", "rollAction":"Singularity Breath"}[/rollable].</strong></em> The dragon creates a shining bead of gravitational force... Each creature in that area must make a DC 20 Strength saving throw...</p>
```

---

### Spellcasting & Psionics Formatting

There are two primary styles in 5e monster design:

#### 1. Innate Spellcasting / Psionics (Modern 5e Style)
```html
<p><em><strong>Spellcasting (Psionics).</strong></em> The dragon casts one of the following spells, requiring no spell components and using Intelligence as the spellcasting ability (spell save DC 18):</p>
<p>1/day each: [spell]blink[/spell], [spell]control water[/spell], [spell]dispel magic[/spell], [spell]protection from evil and good[/spell], [spell]sending[/spell]</p>
```

#### 2. Traditional Spellcasting (Spell Slots Style)
```html
<p><strong>Spellcasting.</strong> The archmage is an 18th-level spellcaster. Its spellcasting ability is Intelligence (spell save DC 17, +9 to hit with spell attacks). The archmage has the following wizard spells prepared:</p>
<p>Cantrips (at will): [spell]fire bolt[/spell], [spell]light[/spell], [spell]mage hand[/spell], [spell]prestidigitation[/spell], [spell]shocking grasp[/spell]<br />
1st level (4 slots): [spell]detect magic[/spell], [spell]identify[/spell], [spell]mage armor[/spell], [spell]magic missile[/spell]<br />
2nd level (3 slots): [spell]detect thoughts[/spell], [spell]mirror image[/spell], [spell]misty step[/spell]</p>
```

---

## 4. Legendary, Mythic & Lair Actions

### Legendary Actions Preamble & Action Economy
Check `#field-is-legendary` on the base form. In the `field-legendary-actions-description-wysiwyg` editor, start with the canonical D&D preamble:

```html
<p>The [monster name] can take 3 legendary actions, choosing from the options below. Only one legendary action option can be used at a time and only at the end of another creature&rsquo;s turn. The [monster name] regains spent legendary actions at the start of its turn.</p>

<p><strong>Tail Attack.</strong> The dragon makes one tail attack.</p>
<p><strong>Detect.</strong> The dragon makes a Wisdom (Perception) check.</p>
<p><strong>Wing Attack (Costs 2 Actions).</strong> The dragon beats its wings. Each creature within 10 feet of the dragon must succeed on a DC 19 Dexterity saving throw or take 13 [rollable](2d6+6);{"diceNotation":"2d6+6", "rollType":"damage", "rollAction":"Wing Attack", "rollDamageType":"bludgeoning"}[/rollable] bludgeoning damage and be knocked [condition]prone[/condition]. The dragon can then fly up to half its flying speed.</p>
```

---

### Mythic Actions Architecture
Check `#field-is-mythic` on the base form. Mythic monsters have a special trait in their Special Traits section (e.g. *Mythic Trait Name (Recharges after a Short or Long Rest)*) that triggers when reduced to 0 HP.

In `field-mythic-actions-description-wysiwyg`:
```html
<p>If the [monster name]&rsquo;s mythic trait is active, it can use the options below as legendary actions for 1 hour after using [Mythic Trait Name].</p>

<p><strong>Mythic Action 1.</strong> Description of mythic action...</p>
<p><strong>Cataclysmic Strike (Costs 2 Actions).</strong> Description of powerful 2-action mythic option...</p>
```

---

### Lair Actions & Regional Effects
Check `#field-has-lair` on the base form. Optionally set `field-lair-challenge-rating` if the CR changes inside the lair.

In `field-lair-description-wysiwyg`:
```html
<h3>An [Monster Name]&rsquo;s Lair</h3>
<p>Narrative description of the lair environment and structure...</p>

<h4>Lair Actions</h4>
<p>On initiative count 20 (losing initiative ties), the [monster name] takes a lair action to cause one of the following effects; the [monster name] can&rsquo;t use the same effect two rounds in a row:</p>
<ul>
    <li>Effect 1 description...</li>
    <li>Effect 2 description...</li>
</ul>

<h4>Regional Effects</h4>
<p>The region containing a legendary [monster name]&rsquo;s lair is warped by the creature&rsquo;s presence, which creates one or more of the following effects:</p>
<ul>
    <li>Regional effect 1 within 1 mile...</li>
    <li>Regional effect 2 within 6 miles...</li>
</ul>
<p>If the [monster name] dies, these effects fade over the course of 3d10 days.</p>
```

---

## 5. DDB Tooltip Tags & Rollable Engine

### Interactive Tooltips
D&D Beyond parses custom BBCode-style tags into dynamic hoverable tooltips on character sheets and encounter builders:

| Tag Syntax | Example | Renders As |
| :--- | :--- | :--- |
| `[spell]name[/spell]` | `[spell]fireball[/spell]` | Interactive spell tooltip & card |
| `[magicitem]name[/magicitem]` | `[magicitem]flame tongue[/magicitem]` | Magic item stats & details |
| `[item]name[/item]` | `[item]longsword[/item]` | Base equipment tooltip |
| `[monster]name[/monster]` | `[monster]goblin[/monster]` | Monster stat block card |
| `[monster]name;alias[/monster]` | `[monster]goblin;goblins[/monster]` | Aliased link displaying "goblins" |
| `[condition]name[/condition]` | `[condition]poisoned[/condition]` | Condition rule tooltip |
| `[sense]name[/sense]` | `[sense]darkvision[/sense]` | Sense definition |
| `[action]name[/action]` | `[action]dash[/action]` | Combat action explanation |

---

### The Rollable JSON Tag Engine
DDB's Digital Dice roller uses embedded JSON metadata inside `[rollable]` tags:

#### 1. Attack Roll ("to hit")
```text
[rollable]+12;{"diceNotation":"1d20+12", "rollType":"to hit", "rollAction":"Bite"}[/rollable]
```

#### 2. Damage Roll ("damage")
```text
18 [rollable](2d10+7);{"diceNotation":"2d10+7", "rollType":"damage", "rollAction":"Bite", "rollDamageType":"piercing"}[/rollable]
```

#### 3. Recharge Roll ("recharge")
```text
[rollable](Recharge 5&ndash;6);{"diceNotation":"1d6", "rollType":"recharge", "rollAction":"Singularity Breath"}[/rollable]
```

#### 4. Generic Table / Duration Roll ("roll")
```text
[rollable]1d10;{"diceNotation":"1d10", "rollType":"roll", "rollAction":"Days"}[/rollable]
```

---

## 6. Playwright Automation Guide

### Session & Storage State
Use the existing storage state containing active `CobaltSession` and authorization cookies:
```python
from playwright.sync_api import sync_playwright

STORAGE_STATE = "/home/karpiq/.gemini/antigravity-cli/dndbeyond_storage_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(storage_state=STORAGE_STATE)
    page = ctx.new_page()
    # Automation steps...
```

---

### DOM Selectors & Input Handling

#### Always Dismiss Vex Dialogs
DDB frequently opens modal dialogs or cookie overlays that intercept clicks:
```python
page.evaluate("() => document.querySelectorAll('.vex, .vex-overlay, .vex-content').forEach(el => el.remove())")
```

---

### Select2 Multi-Select Handling via jQuery
DDB wraps multiple `<select multiple>` elements with Select2. Interacting directly via Playwright's native `page.select_option()` or clicking pseudo-dropdown elements can fail because the native element has `display: none`.

Because jQuery is natively loaded on DDB pages, setting values and triggering the `change` event is instantaneous and 100% reliable:

```python
# Saving Throw Proficiencies
saves = ["1", "3", "6"]  # STR, CON, CHA
page.evaluate("(vals) => window.jQuery('#field-monster-saving-throw').val(vals).trigger('change')", saves)

# Damage Adjustments
damage = ["11", "27", "22"]  # Acid Resistance, Acid Immunity, Poison Immunity
page.evaluate("(vals) => window.jQuery('#field-damage-adjustment').val(vals).trigger('change')", damage)

# Condition Immunities
conditions = ["2", "4", "5", "11", "12"]  # Charmed, Exhaustion, Frightened, Poisoned, Prone
page.evaluate("(vals) => window.jQuery('#field-condition-immunity').val(vals).trigger('change')", conditions)
```

---

### TinyMCE Rich Text Management
There are 8 TinyMCE instances on the create page. They load asynchronously and finish initializing around `networkidle`.

```python
def set_tinymce_content(page, editor_id, html_content):
    page.evaluate("""({ id, html }) => {
        if (typeof tinymce !== 'undefined' && tinymce.get(id)) {
            tinymce.get(id).setContent(html);
            tinymce.triggerSave();
        } else {
            const ta = document.getElementById(id);
            if (ta) ta.value = html;
        }
    }""", {"id": editor_id, "html": html_content})
```

---

### Subform Sequential Automation Flow

After saving the base monster, extract the monster ID and execute subform creation sequentially:

```python
# 1. Base Save
page.click("#save-changes")
page.wait_for_load_state("networkidle")
import re
match = re.search(r'/monsters/(\d+)', page.url)
monster_id = match.group(1)

# 2. Add Movements
movements = [
    {"type": "1", "speed": 40, "note": ""},         # Walk
    {"type": "4", "speed": 80, "note": "(hover)"},  # Fly
    {"type": "5", "speed": 40, "note": ""}          # Swim
]
for m in movements:
    page.goto(f"https://www.dndbeyond.com/monster/movement/create/{monster_id}", wait_until="networkidle")
    page.select_option("#field-movement-type", value=m["type"])
    page.fill("#field-speed", str(m["speed"]))
    if m["note"]:
        page.fill("#field-note", m["note"])
    page.click("button:has-text('SAVE'), button:has-text('Save')")
    page.wait_for_load_state("networkidle")

# 3. Add Senses
senses = [
    {"name": "Blindsight", "note": "60 ft."},
    {"name": "Darkvision", "note": "120 ft."}
]
for s in senses:
    page.goto(f"https://www.dndbeyond.com/monster/senses/create/{monster_id}", wait_until="networkidle")
    page.select_option("#field-sense", label=s["name"])
    page.fill("#field-sense-note", s["note"])
    page.click("button:has-text('SAVE'), button:has-text('Save')")
    page.wait_for_load_state("networkidle")

# 4. Add Skills
skills = [
    {"name": "Stealth", "val": 7, "bonus": None},
    {"name": "Perception", "val": 6, "bonus": 5}  # Base 6 + Expertise 5 = 11
]
for sk in skills:
    page.goto(f"https://www.dndbeyond.com/monster/skills/create/{monster_id}", wait_until="networkidle")
    page.select_option("#field-skill", label=sk["name"])
    page.fill("#field-value", str(sk["val"]))
    if sk["bonus"]:
        page.fill("#field-additional-bonus", str(sk["bonus"]))
    page.click("button:has-text('SAVE'), button:has-text('Save')")
    page.wait_for_load_state("networkidle")

# 5. Add Languages
languages = [
    {"name": "Common", "note": ""},
    {"name": "Draconic", "note": ""},
    {"name": "Telepathy", "note": "120 ft."}
]
for lang in languages:
    page.goto(f"https://www.dndbeyond.com/entity/language/create/{monster_id}-779871897", wait_until="networkidle")
    page.select_option("#field-language", label=lang["name"])
    if lang["note"]:
        page.fill("#field-note", lang["note"])
    page.click("button:has-text('SAVE'), button:has-text('Save')")
    page.wait_for_load_state("networkidle")
```

---

### Safe Deletion Routine

To delete a homebrew monster (e.g., automated clean-up of test creations):
1. Navigate directly to the deletion confirmation modal URL:
   `https://www.dndbeyond.com/homebrew/creations/delete?entityTypeId=779871897&id={monster_id}`
2. The page renders a confirmation modal containing an `<a>` tag with class `.ajax-post.button`:
   `<a class="ajax-post button" href="/homebrew/creations/delete?entityTypeId=779871897&id={id}">Yes</a>`
3. Click the `Yes` link:
   ```python
   page.goto(f"https://www.dndbeyond.com/homebrew/creations/delete?entityTypeId=779871897&id={monster_id}", wait_until="networkidle")
   page.locator("a.ajax-post.button:has-text('Yes')").click()
   page.wait_for_load_state("networkidle")
   ```
4. This soft-deletes the creature (moving it to trash) and removes it from the user's creations listing.

---

## 7. Common Pitfalls & Traps

1. **HP Math Mismatch**:
   DDB requires `field-average-hit-points`, `field-hit-points-die-count`, `field-hit-points-die-value`, and `field-hit-points-modifier`.
   If $\lfloor \text{die count} \times \text{die average} \rfloor + \text{modifier} \neq \text{average HP}$, the stat block or encounter builder may display inconsistent values. Always ensure strict mathematical equality.

2. **Movement Dropdown Exclusion**:
   Once a speed type (`Walk`, `Fly`, `Swim`, `Burrow`, `Climb`) is added to a monster, DDB **removes** that option from `/monster/movement/create/{id}`. To change a speed, you must navigate to the specific movement edit URL (`/monster/movement/{mapping_id}/edit`).

3. **Passive Perception is Not Automatic**:
   The `field-passive-perception` field on the base form does **not** auto-calculate from Wisdom or Perception proficiency. It defaults to blank or 10. You must calculate $10 + \text{WIS mod} + (\text{Perception prof if any})$ and write it into `#field-passive-perception`.

4. **TinyMCE Overwriting Textarea Values**:
   If a script sets `textarea.value` on a rich-text field while TinyMCE is active, TinyMCE's internal buffer will overwrite the textarea with its initial placeholder text upon form submit. Always set content via `tinymce.get(id).setContent(...)` and invoke `tinymce.triggerSave()`.

5. **Language Notes vs. Subforms**:
   The `field-languages-note` field on the base form is an override/annotation field (e.g. `"understands but cannot speak"`). Standard languages (`Common`, `Elvish`) will not register on character sheets or tooltips unless added via the `/entity/language/create/{id}-779871897` subform.

6. **Select2 Hidden Inputs**:
   Never use Playwright's `page.click()` on the native `<select>` for multi-selects (`monster-saving-throw`, `damage-adjustment`, `condition-immunity`). They are hidden by Select2. Use `window.jQuery('#...').val([...]).trigger('change')` for instant, non-flaky updates.
