import os
import re

prompts_data = {
    "076_tsunami_mytros": """A dramatic, apocalyptic scene. A massive, towering wave of dark water (tsunami) is frozen in mid-air above an ancient Greek city with white marble temples and buildings. The sky is dark, filled with swirling storm clouds, heavy rain, and crackling lightning. In the bay, a massive fleet of wooden galleons is scattered. High quality digital fantasy art, epic cinematic lighting.""",
    
    "076_heroes_deck": """A dramatic scene on the wooden deck of an ancient Greek trireme sailing through a storm. Four heroes are standing and looking forward at a ruined city in the distance:
1. adult male with a dark fantasy aesthetic. He has a slender build, pale alabaster skin, and short blonde hair styled in a messy quiff. His face is defined by a strong jawline, high cheekbones, and piercing cyan eyes, often held in a confident smirk. large, jagged scar runs along the side of his neck and jaw. He wears an ornate breastplate. One of his hands is missing, ending in a stump, while the other wears a large, magical gauntlet.
2. young adult male human wizard with a lean, rugged build. He has intense blue-grey eyes, a strong jawline, a weathered complexion, and a prominent scar across his right cheek. His short, messy dark brown hair is complemented by a full dark brown beard. He wears layered medieval clothing, a rust-brown hooded tunic over a coarse off-white linen shirt, with a thick brown leather shoulder strap and buckle. Two bronze circular geometric star emblems are visible on his chest.
3. young adult male elf with a slender build. He has an angular face with high cheekbones, a sharp jawline, intense dark eyes, and long pointed ears. His shoulder-length, wavy dark brown hair frames his face. He wears layered brown leather armor with intricate silver filigree details over a dark, high-collared tunic. He is equipped with black fingerless leather gloves, an ornate silver pendant with a large cracked dark gemstone, and a single silver diamond-shaped earring.
4. powerful male minotaur with a muscular build, broad shoulders, and brown fur. His bovine head features large, curved dark grey horns, piercing glowing blue eyes, and a bull snout. He has stylish, thick blonde hair swept back and a well-groomed blonde fur beard. He is dressed in a draped white toga with an ornate red sash featuring carved patterns and a textured grey shoulder strap.
High quality digital fantasy art, dark and stormy atmosphere.""",

    "076_battle_city": """A chaotic battle scene in the ruined streets of an ancient Greek city. Fire and smoke fill the air. Giant six-armed cyclops monsters are fighting against heavily armored dwarven warriors and ancient Greek hoplites. Dramatic lighting, intense action, high fantasy style, digital painting.""",

    "076_versir_glove": """A quiet scene on the deck of a ship. 
1. adult male with a dark fantasy aesthetic. He has a slender build, pale alabaster skin, and short blonde hair styled in a messy quiff. His face is defined by a strong jawline, high cheekbones, and piercing cyan eyes. large, jagged scar runs along the side of his neck and jaw. He wears an ornate breastplate. One of his hands is missing, ending in a stump, while the other is trying to put on a massive, jagged, dark magical gauntlet. He is examining the gauntlet closely with a focused expression.
High quality digital fantasy art, moody lighting.""",

    "076_kyrah_orestes": """A quiet, melancholic scene on the wooden deck of a ship.
1. young adult female, beautiful ancient Greek goddess, slender build, olive skin, long wavy black hair styled in a braid, loose curls framing her face, captivating green eyes, light freckles across her nose, gentle smile, wearing a white chiton and a dark teal-green himation, adorned with ornate gold jewelry, golden Greek key armband, gold pendant necklace, golden hair clip, dangling gold earrings. She is sitting in the corner, looking sad and thoughtful.
2. powerful male minotaur with a muscular build, broad shoulders, and brown fur. His bovine head features large, curved dark grey horns, piercing glowing blue eyes, and a bull snout. He has stylish, thick blonde hair swept back and a well-groomed blonde fur beard. He is dressed in a draped white toga with an ornate red sash featuring carved patterns and a textured grey shoulder strap. He is standing near her, holding bagpipes and a large wooden mug of beer, offering a simple, kind smile.
High quality digital fantasy art, soft lighting.""",

    "076_arevon_scrying": """A mystical scene inside a ship's cabin.
1. young adult male elf with a slender build. He has an angular face with high cheekbones, a sharp jawline, intense dark eyes, and long pointed ears. His shoulder-length, wavy dark brown hair frames his face. He wears layered brown leather armor with intricate silver filigree details over a dark, high-collared tunic. He is equipped with black fingerless leather gloves, an ornate silver pendant with a large cracked dark gemstone, and a single silver diamond-shaped earring. He is casting a scrying spell, looking into a glowing magical pool of water. In the water's reflection, a chaotic scene of a burning city and a stormy harbor can be seen.
High quality digital fantasy art, magical glowing atmosphere.""",

    "076_yala_cliff": """A moody, atmospheric scene. A towering, powerful female titan with four arms is sitting completely alone on the edge of a high rocky cliff, looking far into the distance at a burning ancient Greek city under a stormy sky. She looks solitary and thoughtful. Dark fantasy oil painting style, dramatic stormy lighting.""",

    "076_vallus_dragon": """A dramatic landing on a ship's deck during a storm.
1. young adult female, regal bearing, Greek goddess, slender build, tan skin, voluminous dark brown curly hair, intense green eyes, high cheekbones, wearing a white chiton with ornate golden trim and shoulder straps, adorned with a large golden laurel crown, extravagant gold earrings with pearl details, a golden leaf-motif armband, and a gold bracelet, red painted fingernails. She is standing amidst the rain, looking desperate and urgent. Behind her, the magical fading silhouette of a large bronze dragon can be seen, as if she just transformed from it.
High quality digital fantasy art, cinematic lighting, stormy weather.""",

    "076_defenders_mytros": """A grand battle preparation scene in an ancient Greek city under siege. Various fantasy factions are standing together in the rain: fierce Amazon warriors with spears, sturdy Dwarves with axes and heavy armor, Centaurs with bows, and tall Barbarians. In the background, the sky is dark with smoke and lightning. Epic fantasy illustration, wide shot, high detail.""",

    "076_delphia_magic": """A magical scene on a ship under heavy fire.
1. Ethereal dryad, a beautiful woman made of green vines, glowing green moss, and bark. She is emerging directly from the main wooden mast of a large ancient Greek trireme. Her hands are glowing with bright green nature magic. Thick, pulsating green vines and moss are growing rapidly from her hands to repair large shattered holes in the wooden deck and hull of the ship.
High quality digital fantasy art, vibrant green magical glow contrasting with a dark stormy background.""",

    "076_ultros_ramming": """A massive ancient Greek trireme ship with a glowing blue ram made of enchanted wood is violently crashing into and splitting a large enemy wooden galleon in half. Wood is splintering everywhere, waves are crashing. The sky above is a raging thunderstorm. Epic naval battle scene, high quality digital fantasy art, dynamic action.""",

    "076_sydon_manifests": """A terrifying manifestation of a titan in the middle of a city harbor.
1. elderly male god, mythological thunder deity, immensely muscular build, tanned skin, glowing red eyes, glowing red third eye on the forehead, stern expression, deep wrinkles, wild flowing thick white hair, large voluminous white beard and mustache, wearing a draped white toga cloth, thick solid gold bicep armbands, heavy gold wrist bracers, wide gold belt, gold circular medallions on the chest. He is gargantuan, rising out of a massive whirlpool in the ocean water. He is holding a giant glaive crackling with blue lightning. A towering wall of black water (tsunami) is rising behind him.
High quality digital fantasy art, terrifying cosmic deity, epic scale.""",

    "076_icarus_mutated": """A horrific mutation scene in the sky.
1. middle-aged male, muscular build, ancient Greek king, stern expression, dark intense eyes, furrowed brow, short dark hair, a thick black beard and mustache, wearing a golden laurel wreath crown, an ornate golden cuirass with a pauldron shaped like a snarling lion's head, a red cape over his shoulder. He is riding on the back of a gargantuan silver dragon. He is desperately plunging a glowing blue, alien-looking spear into the dragon's neck.
The silver dragon is mutating mid-air, its bones cracking, muscles bulging, and its silver scales erupting with sharp, jagged ice spikes. The dragon is exhaling a massive beam of absolute zero cold, freezing a giant tsunami wave into a solid mountain of ice. High quality digital fantasy art, dramatic action, horrific transformation.""",

    "076_amazon_defense": """A fierce battle scene in the docks of an ancient Greek city. A group of athletic, fierce female Amazon warriors wearing bronze armor and red crests are fighting desperately with spears and shields against massive, towering six-armed cyclops monsters. Rain is pouring down, lightning strikes in the background. Action-packed fantasy illustration, digital painting.""",

    "076_dwarf_charge": """A brutal battle scene in a city street. A disciplined, heavily armored phalanx of dwarven warriors with large shields and glowing axes are charging forward, crushing an enemy line of giant, mutated monsters. The dwarves are covered in mud and blood but look victorious. High fantasy battle, cinematic lighting.""",

    "076_ruined_temple": """A macabre and tragic scene. The ruins of a grand ancient Greek temple (Temple of the Five). Large marble statues of gods have been toppled and smashed to pieces. The grand marble stairs are stained with blood and littered with the bodies of fallen acolytes. In the sky above the temple, a dark storm rages. Dark fantasy oil painting style, somber and terrifying atmosphere.""",

    "076_hergeron_sparks": """A terrifying encounter with a crazed demigod above a ruined temple.
1. adult male, mythological god, imposing muscular build, tan skin, short curly dark hair, short dark beard and mustache, blue eyes, intense commanding expression, glowing red third eye on the forehead, elaborate golden spiked crown with upward sweeping horn shapes, massive golden plate armor, large golden shoulder pauldrons with curved horn-like spikes, prominent circular golden chest plate with laurel wreath relief pattern, golden waist tassets with chain details, heavy golden and blue layered wrist bracers, flowing deep blue cape featuring an ethereal glowing cosmic starry nebula pattern, ornate golden spear. He is levitating in the air, his eyes emitting blinding, unstable golden light. He is surrounded by a squad of evil centaurs and minotaurs. He looks insane and drunk on power.
High quality digital fantasy art, celestial ancient Greek aesthetic.""",

    "076_felicjan_simulacrum": """A magical combat scene.
1. young adult male human wizard with a lean, rugged build. He has intense blue-grey eyes, a strong jawline, a weathered complexion, and a prominent scar across his right cheek. His short, messy dark brown hair is complemented by a full dark brown beard. He wears layered medieval clothing, a rust-brown hooded tunic over a coarse off-white linen shirt, with a thick brown leather shoulder strap and buckle. Two bronze circular geometric star emblems are visible on his chest.
He is standing confidently, and right next to him is a perfect, translucent, icy-blue magical duplicate (simulacrum) of himself. Both are raising their hands, preparing to cast powerful spells. High quality digital fantasy art, magical atmosphere.""",

    "076_orestes_critical": """An epic aerial combat scene.
1. powerful male minotaur with a muscular build, broad shoulders, and brown fur. His bovine head features large, curved dark grey horns, piercing glowing blue eyes, and a bull snout. He has stylish, thick blonde hair swept back and a well-groomed blonde fur beard. He is dressed in a draped white toga with an ornate red sash featuring carved patterns and a textured grey shoulder strap. He has large, magical glowing wings spread wide. He is flying through the air with a furious expression, swinging a massive, heavy greataxe in a brutal downward arc.
2. adult male, mythological god, imposing muscular build, tan skin, short curly dark hair, short dark beard and mustache, blue eyes, glowing red third eye on the forehead, elaborate golden spiked crown, massive golden plate armor. He is levitating and is about to be struck by the minotaur's devastating axe blow.
High quality digital fantasy art, dynamic action, intense impact."""
}

base_dir = "/home/bartosz/Projekty/OotD/content/assets/sessions/076"
os.makedirs(base_dir, exist_ok=True)

for name, prompt in prompts_data.items():
    with open(f"{base_dir}/{name}.txt", "w") as f:
        f.write(prompt)

filepath = "/home/bartosz/Projekty/OotD/content/01-Sessions/Sesja 76 - Bitwa o Mytros: Pierwsza Fala.md"
with open(filepath, "r") as f:
    content = f.read()

replacements = [
    (r"(## Podsumowanie\n)", r"\1\n![Tsunami nad miastem](../assets/sessions/076/076_tsunami_mytros.png)\n[Prompt](../assets/sessions/076/076_tsunami_mytros.txt)\n\n![Bohaterowie na pokładzie](../assets/sessions/076/076_heroes_deck.png)\n[Prompt](../assets/sessions/076/076_heroes_deck.txt)\n\n![Bitwa w mieście](../assets/sessions/076/076_battle_city.png)\n[Prompt](../assets/sessions/076/076_battle_city.txt)\n"),
    (r"(### Ostatnie Chwile Spokoju na Pokładzie Ultrosa\n)", r"\1\n![Versir bada rękawicę](../assets/sessions/076/076_versir_glove.png)\n[Prompt](../assets/sessions/076/076_versir_glove.txt)\n\n![Rozmowa z Kyrą](../assets/sessions/076/076_kyrah_orestes.png)\n[Prompt](../assets/sessions/076/076_kyrah_orestes.txt)\n"),
    (r"(### Wizje Płonącego Miasta\n)", r"\1\n![Wizje Arevona](../assets/sessions/076/076_arevon_scrying.png)\n[Prompt](../assets/sessions/076/076_arevon_scrying.txt)\n\n![Samotna Yala](../assets/sessions/076/076_yala_cliff.png)\n[Prompt](../assets/sessions/076/076_yala_cliff.txt)\n"),
    (r"(### Przybycie do Krwawiącej Stolicy\n)", r"\1\n![Lądowanie Vallus](../assets/sessions/076/076_vallus_dragon.png)\n[Prompt](../assets/sessions/076/076_vallus_dragon.txt)\n\n![Obrońcy Mytros](../assets/sessions/076/076_defenders_mytros.png)\n[Prompt](../assets/sessions/076/076_defenders_mytros.txt)\n"),
    (r"(### Cud Delphi i Przebicie Blokady\n)", r"\1\n![Magia Delphi](../assets/sessions/076/076_delphia_magic.png)\n[Prompt](../assets/sessions/076/076_delphia_magic.txt)\n\n![Ultros taranujący blokadę](../assets/sessions/076/076_ultros_ramming.png)\n[Prompt](../assets/sessions/076/076_ultros_ramming.txt)\n"),
    (r"(### Walka Acastusa i Szaleństwo Icarusa\n)", r"\1\n![Sydon wyłania się z morza](../assets/sessions/076/076_sydon_manifests.png)\n[Prompt](../assets/sessions/076/076_sydon_manifests.txt)\n\n![Zmutowany Icarus zamraża falę](../assets/sessions/076/076_icarus_mutated.png)\n[Prompt](../assets/sessions/076/076_icarus_mutated.txt)\n"),
    (r"(### Bitwa o Mytros\n)", r"\1\n![Obrona Amazonek](../assets/sessions/076/076_amazon_defense.png)\n[Prompt](../assets/sessions/076/076_amazon_defense.txt)\n\n![Szarża Krasnoludów](../assets/sessions/076/076_dwarf_charge.png)\n[Prompt](../assets/sessions/076/076_dwarf_charge.txt)\n"),
    (r"(### Świątynia Pięciu i Iskry Półboga\n)", r"\1\n![Zniszczona Świątynia Pięciu](../assets/sessions/076/076_ruined_temple.png)\n[Prompt](../assets/sessions/076/076_ruined_temple.txt)\n\n![Hergeron i boskie iskry](../assets/sessions/076/076_hergeron_sparks.png)\n[Prompt](../assets/sessions/076/076_hergeron_sparks.txt)\n"),
    (r"(### Pojedynek z Synem Burzy\n)", r"\1\n![Klon Felicjana](../assets/sessions/076/076_felicjan_simulacrum.png)\n[Prompt](../assets/sessions/076/076_felicjan_simulacrum.txt)\n\n![Krytyczny cios Orestesa](../assets/sessions/076/076_orestes_critical.png)\n[Prompt](../assets/sessions/076/076_orestes_critical.txt)\n")
]

for pat, repl in replacements:
    content = re.sub(pat, repl, content, count=1)

with open(filepath, "w") as f:
    f.write(content)

print("Done generating prompts and updating markdown file.")
