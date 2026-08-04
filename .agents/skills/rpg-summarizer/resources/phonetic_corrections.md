# Phonetic / ASR Corrections

Transkrypcja głosowa polskiego RPG regularnie myli rzadkie imiona własne.
Poniższa lista to skumulowane korekty — gdy w transkrypcji widzisz lewą
kolumnę, **zawsze** zapisuj prawą.

Lista rośnie po każdej sesji — dopisuj nowe pomyłki, gdy je zauważysz.

## Imiona własne

| W transkrypcji (forma błędna) | Zapisz jako |
|--------------------------------|-------------|
| Sybol Korax / Symbol Korax / Sybol Corex / Symbol Koraxa | **Sybolkorax** |
| Pytrion / Raz Pytrion / Pytriona / Raspython | **Raspytrion** |
| Tyspohale / Tysopale | **Tysophale** |
| Arkyrani / Arkurania | **Arkyrania** |
| Akastus / Akastusa | **Acastus** |
| Ikarus / Ikar | **Icarus** |
| Aparia / Apazja | **Apasia** |
| Helios / Heliosem (gdy chodzi o smoka, nie boga) | **Helios** (Złoty Smok) |
| Jugolof / Jugolofy / Yugolof | **Yugoloth / Yugolothy** |
| Wersir / Versila / Versyl | **Versir** |
| Felician | **Felicjan** |
| Anora | **Anora** (córka Pythora) |
| Tromba | **Trąba** |
| Sidon | **Sydon** |

## Słowa polskie, które brzmią jak fantasy

| Co słyszysz | Co to naprawdę jest |
|-------------|---------------------|
| "ork" (jako wróg w walce) | Najpierw sprawdź kontekst — może to **orka** (zabójczy wieloryb, druid w transformacji Wild Shape). "Ork" jako rasa w tej kampanii nie występuje. |
| "rosomak" / "wolwerina" | Może to **wolverine** (zwierzęca forma druida) |
| "kosa" | Arevon nie ma kosy. Sprawdź czy to nie zaklęcie typu Spirit Guardians lub Spiritual Weapon. |
| "stary las" | **Stary Las** (Oldwood) — kanoniczna nazwa lokacji |

## Cytaty z `quotes.json` też są surowym ASR

`quotes.json` jest wklejany do sekcji `Cytaty` "verbatim", ale to nadal
transkrypcja głosowa — regularnie gubi końcówki i myli podobnie brzmiące słowa.
**Przed wklejeniem sprawdź każdy cytat pod kątem polskiej gramatyki**: jeśli
zdanie jest niegramatyczne albo bez sensu, popraw oczywistą pomyłkę ASR.
Nigdy nie zmyślaj brzmienia cytatu — poprawiaj tylko to, co ewidentnie jest
przesłyszeniem.

Przykłady z sesji 83:

| W `quotes.json` | Poprawnie |
|-----------------|-----------|
| "Nabiegłbym się piwa" | "Napiłbym się piwa" |
| "Zajebałem twoje dzieci, zajebili ciebie" | "Zajebałem twoje dzieci, zajebie i ciebie" |
| "ja ją zrobiłem tak do końca" | "ja ją zabiłem tak do końca" |

## Imiona graczy (IGNORUJ w narracji)

Te imiona pojawiają się przy stole, ale **nie należą do świata gry**:

- **Bartek** — gra Versirem
- **Maciek** — gra Felicjanem
- **Hubert** / **Hubcio** — gra Orestesem
- **Karol** — gra Orionem
- **Adam** — gra Arevonem (lub DM)

**Wyjątek**: "Hubert" jest też imieniem familiara Felicjana. Po kontekście
rozpoznasz, czy chodzi o gracza, czy o ptaka.

## Terminy mechaniczne (też zwykle IGNORUJ)

Te słowa pojawiają się przy stole jako mechanika — w narracji opisuj wynik,
nie nazwę technikalium:

- `advantage / disadvantage / save / DC / k20 / k12 / k8 / k6 / k4`
- `rzut na inicjatywę / rzut na atak / rzut obronny`
- `roll / reroll / nat 20 / nat 1`
- `modifier / proficiency / bonus akcja`
- `HP / hit points / temp HP`
- nazwy zaklęć po angielsku przemieszane z polskim (Hold Monster, Wall of Fire, Shield) —
  używaj angielskich nazw zaklęć **gdy są wypowiedziane**, nie wymyślaj własnych
