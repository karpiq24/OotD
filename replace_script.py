import re

file_path = "content/01-Sessions/Sesja 75 - Koniec Przysięgi.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    ("wieży **Praxys** przeznaczone", "wieży **[[Praxys]]** przeznaczone"),
    ("**minotaur** – strażnik", "**[[Minotaur z Thylei|minotaur]]** – strażnik"),
    ("**Versir**, z właściwą", "**[[Versir]]**, z właściwą"),
    ("**Arevon**, czerpiąc", "**[[Arevon Elorrenthi|Arevon]]**, czerpiąc"),
    ("**Orestes**, wykorzystując", "**[[Orestes]]**, wykorzystując"),
    ("**sześcioręki Gygan**", "**sześcioręki [[Gyganie|Gygan]]**"),
    ("włączyła się **Nephele**", "włączyła się **[[Nephele]]**"),
    ("bitwy, **Arevon** przyłożył", "bitwy, **[[Arevon Elorrenthi|Arevon]]** przyłożył"),
    ("amantów **Chalcii**", "amantów **[[Chalcia|Chalcii]]**"),
    ("dusić **Orestesa** i **Versira** gołymi", "dusić **[[Orestes|Orestesa]]** i **[[Versir|Versira]]** gołymi"),
    ("**Orion**, który", "**[[Orion Xul|Orion]]**, który"),
    ("**Circlet of Blasting**", "**[[Circlet of Blasting]]**"),
    ("**Megarę, Alecto i Tyzyfone**. Furie", "**[[Megara|Megarę]], [[Alecto]] i [[Tyzyfone]]**. [[Furie]]"),
    ("niż **Sydon i Lutheria** – zostały", "niż **[[Sydon]] i [[Lutheria]]** – zostały"),
    ("samą **Thyleę** na", "samą **[[Thylea|Thyleę]]** na"),
    ("**Orestes**, niepoprawny", "**[[Orestes]]**, niepoprawny"),
    ("że **Thylea potrzebuje", "że **[[Thylea]] potrzebuje"),
    ("że **Mojry** miały", "że **[[Mojry]]** miały"),
    ("w Thylei – spisku", "w [[Thylea|Thylei]] – spisku"),
    ("**Versi Pierwszą**, matkę Versira", "**[[Versi Pierwsza|Versi Pierwszą]]**, matkę [[Versir|Versira]]"),
    ("Furia Megara zwróciła", "Furia [[Megara]] zwróciła"),
    ("do **Arevona**, ostrzegając", "do **[[Arevon Elorrenthi|Arevona]]**, ostrzegając"),
    ("(Eberronu)", "([[Eberron|Eberronu]])"),
    ("szczycie Praxys** to", "szczycie [[Praxys]]** to"),
    ("istot z Morza Astralnego**", "istot z **[[Morze Astralne|Morza Astralnego]]**"),
    ("przez Sydona w", "przez [[Sydon|Sydona]] w"),
    ("zobaczył **Eberron**, swój", "zobaczył **[[Eberron]]**, swój"),
    ("doków **Praxys**, gdzie", "doków **[[Praxys]]**, gdzie"),
    ("**Kroka**, **Boia**", "**[[Krok|Kroka]]**, **[[Boi|Boia]]**"),
    ("**satyrów-bardów**", "**[[Satyr z Thylei|satyrów-bardów]]**"),
    ("kucharza **Ramsusa**", "kucharza **[[Ramsus|Ramsusa]]**"),
    ("**Pholonem** i **czaszką Balmytrii**", "**[[Pholon|Pholonem]]** i **czaszką [[Balmytria|Balmytrii]]**"),
    ("**Versir** zbliżył", "**[[Versir]]** zbliżył"),
    ("z Morza Astralnego, więzionej", "z [[Morze Astralne|Morza Astralnego]], więzionej"),
    ("momencie **Felicjan** użył", "momencie **[[Felicjan Janus Twardowski|Felicjan]]** użył"),
    ("**Heart of the Gale**", "**[[Heart of the Gale]]**"),
    ("siebie i Versira zaklęcie", "siebie i [[Versir|Versira]] zaklęcie"),
    ("**piętro Sydona**", "**piętro [[Sydon|Sydona]]**"),
    ("do Morza Astralnego.", "do [[Morze Astralne|Morza Astralnego]]."),
    ("że Versir nie", "że [[Versir]] nie"),
    ("Felicjan obwiązał", "[[Felicjan Janus Twardowski|Felicjan]] obwiązał"),
    ("za Versirem. Felicjan wyciągnął", "za [[Versir|Versirem]]. [[Felicjan Janus Twardowski|Felicjan]] wyciągnął"),
    ("Wersira i Felicjana zalała", "[[Versir|Wersira]] i [[Felicjan Janus Twardowski|Felicjana]] zalała"),
    ("uderzając w **Praxys**", "uderzając w **[[Praxys]]**"),
    ("dumą Sydona.", "dumą [[Sydon|Sydona]]."),
    ("to **Hergeron**, tytan", "to **[[Hergeron]]**, tytan"),
    ("na **Versira** z potężną", "na **[[Versir|Versira]]** z potężną"),
    ("perswazja Versira w", "perswazja [[Versir|Versira]] w"),
    ("przeciwnika, Versir zmienił", "przeciwnika, [[Versir]] zmienił"),
    ("to ja, Versir!", "to ja, [[Versir]]!"),
    ("oczach Hergerona pojawiło", "oczach [[Hergeron|Hergerona]] pojawiło"),
    ("zrozumienie. Hergeron zamrugał", "zrozumienie. [[Hergeron]] zamrugał"),
    ("zabij Sydona.", "zabij [[Sydon|Sydona]]."),
    ("w Thylei ponownie", "w [[Thylea|Thylei]] ponownie"),
    ("**Hand of Kentimane**", "**[[Hand of Kentiname|Hand of Kentimane]]**"),
    ("Hergeron rozpłynął", "[[Hergeron]] rozpłynął"),
    ("pokład **Ultrosa**, wciąż", "pokład **[[Ultros|Ultrosa]]**, wciąż"),
    ("pyłem Praxys, wciąż", "pyłem [[Praxys]], wciąż"),
    ("**Volkan**, **Pythor** i **Kyrah**", "**[[Volkan]]**, **[[Pythor]]** i **[[Kyrah]]**"),
    ("zobaczyli **Nephele** oraz", "zobaczyli **[[Nephele]]** oraz"),
    ("przez Pholona, zamarli", "przez [[Pholon|Pholona]], zamarli"),
    ("zamarli. **Pythor**, zwykle", "zamarli. **[[Pythor]]**, zwykle"),
    ("**Kyrah** odwróciła", "**[[Kyrah]]** odwróciła"),
    ("**Volkan** dotknął", "**[[Volkan]]** dotknął"),
    ("Tylko **Felicjan** uśmiechał", "Tylko **[[Felicjan Janus Twardowski|Felicjan]]** uśmiechał"),
    ("**Balmytria była żoną Volkana i matką Kyrah oraz Pythora**", "**[[Balmytria]] była żoną [[Volkan|Volkana]] i matką [[Kyrah]] oraz [[Pythor|Pythora]]**"),
    ("**Przysięga Pokoju wygasała**", "**[[Przysięga Pokoju]] wygasała**"),
    ("**Volkan** poprosił Felicjana", "**[[Volkan]]** poprosił [[Felicjan Janus Twardowski|Felicjana]]"),
    ("pojemnik na zwój, wydarty", "pojemnik na **[[Zwój Przysięgi Pokoju]]**, wydarty"),
    ("skarbca Sydona w Praxys", "skarbca [[Sydon|Sydona]] w [[Praxys]]"),
    ("porządku Thylei.", "porządku [[Thylea|Thylei]]."),
    ("**Felicjan**, na prośbę", "**[[Felicjan Janus Twardowski|Felicjan]]**, na prośbę"),
    ("prawdziwe imię: **Sybolkorax**, smok Rizon Phobas", "prawdziwe imię: **[[Sybolkorax]]**, smok [[Rizon Phobas]]"),
    ("śmierci Balmytrii.", "śmierci [[Balmytria|Balmytrii]]."),
    ("stał się **Raspytrionem**, zaprzysiężonym niegdyś **Adonisowi Neurdagonowi**.", "stał się **[[Raspytrion|Raspytrionem]]**, zaprzysiężonym niegdyś **[[Adonis Neurdagon|Adonisowi Neurdagonowi]]**."),
    ("postać **Arkyrani**, dawnej smoczycy **Estora Arkelandera**", "postać **[[Arkyrania|Arkyrani]]**, dawnej smoczycy **[[Estor Arkelander|Estora Arkelandera]]**"),
    ("rzeziach Gyganów. Felicjan, patrząc", "rzeziach [[Gyganie|Gyganów]]. [[Felicjan Janus Twardowski|Felicjan]], patrząc"),
    ("pełną historię. **Balmytria**, wiedząc", "pełną historię zawartą w legendach jako **[[Gra Bogów]]**. **[[Balmytria]]**, wiedząc"),
    ("wyspie **Złotego Serca**", "**[[Wyspa Złotego Serca|wyspie Złotego Serca]]**"),
    ("Zagrała z nimi siedem partii, pięć wygrywając cierpliwością, a ostatnią przegrywając **celowo** – w tej ostatniej, gdy Sydon i Lutheria wlali w kości swoją boską moc, **Balmytria wbiła sztylet we własną pierś**. Jej krew rozlała się na planszę i związała z ich boskimi domenami ukrytymi w kościach, wykradając potęgę Tytanów i przekazując ją swojemu mężowi i dzieciom. Tak powstała Piątka.", "Zagrała z nimi siedem partii, pierwszą wygrywając, co doprowadziło Sydona do szału i podwojenia stawki. Balmytria wygrała kolejnych pięć partii niezłomną cierpliwością, zmuszając rozwścieczonego Sydona do sięgnięcia po pomoc Lutherii w ostatniej, siódmej partii. Przegrywając ją **celowo** – w tej ostatniej, gdy [[Sydon]] i [[Lutheria]] wlali w kości swoją boską moc, by zapewnić sobie zwycięstwo, **[[Balmytria]] wbiła sztylet we własną pierś**, oddając w stawce własne życie. Jej krew rozlała się na planszę i związała z ich boskimi domenami ukrytymi w kościach, wykradając potęgę Tytanów i przekazując ją swojemu mężowi i dzieciom ([[Vallus]], [[Pythor|Pythorowi]], [[Arezja/Narsus|Narsusowi]] i [[Kyrah]]). Tak powstała Piątka."),
    ("**Sydon i Lutheria** stali", "**[[Sydon]] i [[Lutheria]]** stali"),
    ("**Bitwa o Mytros**", "**[[Bitwa o Mytros]]**"),
    ("stronę **stolicy**, gdzie", "stronę **[[Mytros|stolicy]]**, gdzie"),
    ("gwiazdami Thylei", "gwiazdami [[Thylea|Thylei]]"),
    ("starciem w historii kontynentu.", "starciem w historii kontynentu."),
]

for old, new in replacements:
    content = content.replace(old, new)

# Update Key Events:
content = content.replace("Chalcii w Komnacie Rozkoszy.", "[[Chalcia|Chalcii]] w Komnacie Rozkoszy.")
content = content.replace("Megary, Alecto i Tyzyfone", "[[Megara|Megary]], [[Alecto]] i [[Tyzyfone]]")
content = content.replace("Arevona", "[[Arevon Elorrenthi|Arevona]]")
content = content.replace("Praxys.", "[[Praxys]].")
content = content.replace("Versira z wujem Hergeronem", "[[Versir|Versira]] z wujem [[Hergeron|Hergeronem]]")
content = content.replace("Sydona i Lutherię.", "[[Sydon|Sydona]] i [[Lutheria|Lutherię]].")
content = content.replace("Sybolkorax, Arkyrani", "[[Sybolkorax]], [[Arkyrania|Arkyrani]]")
content = content.replace("ofierze Balmytrii podczas Królewskiej Gry.", "ofierze [[Balmytria|Balmytrii]] podczas Królewskiej Gry ([[Gra Bogów]]).")
content = content.replace("do Mytros w", "do [[Mytros]] w")

# Update NPCs block
old_npcs = """## Postacie Niezależne (NPC)

* Nephele (smoczy klon pomagający drużynie)
* Megara, Alecto i Tyzyfone (Furie, strażniczki praw)
* Hergeron (Tytan Siły, wuj Versira)
* Volkan (Bóg Kowali, ujawniony jako smok)
* Pythor (Bóg Bitwy, ujawniony jako smok)
* Kyrah (Bogini Muzyki, ujawniona jako smok)
* Balmytria (starożytna smoczyca)
* Ramsus (uratowany kucharz)"""

new_npcs = """## Postacie Niezależne (NPC)

* [[Nephele]] (smoczy klon pomagający drużynie)
* [[Megara]], [[Alecto]] i [[Tyzyfone]] ([[Furie]], strażniczki praw)
* [[Hergeron]] (Tytan Siły, wuj [[Versir|Versira]])
* [[Volkan]] (Bóg Kowali, ujawniony jako smok [[Sybolkorax]])
* [[Pythor]] (Bóg Bitwy, ujawniony jako smok [[Raspytrion]])
* [[Kyrah]] (Bogini Muzyki, ujawniona jako smok [[Arkyrania|Arkyrani]])
* [[Balmytria]] (starożytna smoczyca)
* [[Ramsus]] (uratowany kucharz)
* [[Krok]] (uwolniony więzień)
* [[Boi]] (obsługa windy)
* [[Pholon]]
* [[Chalcia]]
* [[Sydon]] i [[Lutheria]]
* [[Satyr z Thylei|Satyrowie-bardowie]]"""
content = content.replace(old_npcs, new_npcs)

# Update Lokacje block
old_lokacje = """## Lokacje

* Praxys (wieża Sydona)
* Statek Ultros"""
new_lokacje = """## Lokacje

* [[Praxys]] (wieża [[Sydon|Sydona]])
* Statek [[Ultros]]
* [[Morze Astralne]]
* [[Eberron]]
* [[Wyspa Złotego Serca]]
* [[Mytros]]"""
content = content.replace(old_lokacje, new_lokacje)

# Update Przedmioty block
old_przedmioty = """## Przedmioty

* Magiczny diadem z sypialni Chalcii
* Czaszka Balmytrii
* Zwój z pełnym tekstem Przysięgi Pokoju"""
new_przedmioty = """## Przedmioty

* [[Circlet of Blasting|Magiczny diadem]] z sypialni [[Chalcia|Chalcii]]
* Czaszka [[Balmytria|Balmytrii]]
* [[Zwój Przysięgi Pokoju]]
* [[Hand of Kentiname|Hand of Kentimane]]
* [[Heart of the Gale]]"""
content = content.replace(old_przedmioty, new_przedmioty)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Replacements done.")
