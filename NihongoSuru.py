import json
import random

def normalize_umlauts(text: str) -> str:
    """
    Wandelt ae → ä, oe → ö, ue → ü (und umgekehrt) um,
    um tolerant auf Benutzereingaben zu reagieren.
    """
    umlaut_map = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue"
    }

    for search, replace in umlaut_map.items():
        text = text.replace(search, replace)
    return text

def get_group_number(user_input: str) -> int | None:
    user_input = user_input.strip().lower()

    groups = {
        1: "godan",
        2: "ichidan",
        3: "unregelmaessig"
    }

    # Prüfe, ob es eine Zahl ist
    if user_input.isdigit():
        num = int(user_input)
        if num in groups:
            return num

    # Prüfe, ob es ein gültiger Name ist
    for number, name in groups.items():
        if user_input == name.lower():
            return number

    # Kein Treffer
    return None

def run_quiz(vocab, lang="de-DE"):
    print("📘 Japanisch-Vokabeltrainer")
    print("Sprache:", "Deutsch" if lang == "de-DE" else "Englisch")
    print("Gib 'q' ein, um zu beenden.\n")
    score = 0
    total = 0

    while True:
        entry = random.choice(vocab)
        comment: dict = entry['comment']
        direction = random.choice(["jp2xx", "xx2jp", "group"])

        if direction == "jp2xx":
            print(f"💬 Was heißt '{entry['word']}' ({entry["hiragana"]}, {entry['romaji']})?", end="")
            if len(comment):
                print(f" Comment: {comment[lang]}", end="")
            print()
            words = [a.lower() for a in entry["translation"][lang]]

            correct = words
            for i, word in enumerate(words):
                normalized = normalize_umlauts(word)
                if normalized == word:
                    continue

                correct.append(normalized)

            answer = input("> ").strip().lower()

            if answer == 'q':
                break
            if answer in correct:
                print("✅ Richtig!\n")
                score += 1
            else:
                print(f"❌ Falsch. Richtige Antwort(en): {', '.join(entry['translation'][lang])}\n")
        elif direction == "xx2jp":
            word = random.choice(entry["translation"][lang])
            print(f"💬 Wie sagt man '{word}' auf Japanisch?")
            if len(comment):
                print(f" Comment: {comment[lang]}", end="")
            print()
            answer = input("> ").strip()
            if answer == 'q':
                break
            if answer in [entry["word"], entry["hiragana"], entry["romaji"]]:
                print("✅ Richtig!\n")
                score += 1
            else:
                print(f"❌ Falsch. Richtige Antwort: {entry['word']} ({entry["hiragana"]}, {entry['romaji']})\n")
        else:
            print(f"💬 Zur welcher gruppe gehört '{entry['word']}' ({entry["hiragana"]}, {entry['romaji']})?", end="")
            if len(comment):
                print(f" Comment: {comment[lang]}", end="")
            print()
            answer = input("> ").strip()
            if answer == 'q':
                break

            group_num = get_group_number(answer)

            if group_num == entry["group"]:
                print("✅ Richtig!\n")
                score += 1
            else:
                print(f"❌ Falsch. Richtige Antwort: {entry['word']} ({entry["hiragana"]}, {entry['romaji']})\n")


        total += 1
        print()

    print(f"\n📊 Ergebnis: {score} von {total} richtig beantwortet.")

class Words:

    def __init__(self, words: list[str] = None) -> None:
        self._words: list[str] = words or list()
        self._longest: int     = max((len(w) for w in self._words), default=0)

    def append(self, word: str) -> None:
        self._words.append(word)
        self._longest = max(self._longest, len(word))

    def get_word(self, idx: int) -> str:
        return self._words[idx]

    def get_words(self) -> list[str]:
        return self._words.copy()

    def get_longest_length(self) -> int:
        return self._longest

    def get_longest_words(self) -> list[str]:
        return [w for w in self._words if len(w) == self._longest]

    def get_word_count(self) -> int:
        return len(self._words)

    def clear(self) -> None:
        self._words.clear()
        self._longest = 0

    def __str__(self) -> str:
        return f"Words<{self._longest}>({self._words})"

    def __repr__(self) -> str:
        return f"Words(longest={self._longest}, words={self._words!r})"

if __name__ == '__main__':
    # JSON-Datei laden
    with open("vocab/verbs.json", "r", encoding="utf-8") as f:
        vocab_list = json.load(f)

    japanese_words = Words()
    japanese_hiragana = Words()
    japanese_romaji = Words()
    japanese_translation_en = Words()
    japanese_translation_de = Words()

    for vocab in vocab_list:
        japanese_words.append(vocab['word'])
        japanese_hiragana.append(vocab['hiragana'])
        japanese_romaji.append(vocab['romaji'])
        english = ", ".join(vocab['translation']["en-EN"])
        german = ", ".join(vocab['translation']["de-DE"])

        comment = vocab['comment']
        if len(comment):
            english += " (" + comment["en-EN"] + ")"
            german += " (" + comment["de-DE"] + ")"

        japanese_translation_de.append(german)
        japanese_translation_en.append(english)

    def make_column(identifier: str, words: Words) -> str:
        length = len(identifier)
        if words.get_longest_length() > length:
            length = words.get_longest_length()

        return f"{{{identifier}:{length}}}"

    columns = list()
    columns.append(make_column("Word", japanese_words))
    columns.append(make_column("Hiragana", japanese_hiragana))
    columns.append(make_column("Romaji", japanese_romaji))
    columns.append(make_column("English", japanese_translation_en))

    fmt = " | ".join(columns)
    title = fmt.format(
        Word="Word",
        Hiragana="Hiragana",
        Romaji="Romaji",
        English="English",
        German="German"
    )
    print(title)
    print("-" * len(title))
    for i in range(len(vocab_list)):
        row = fmt.format(
            Word=japanese_words.get_word(i),
            Hiragana=japanese_hiragana.get_word(i),
            Romaji=japanese_romaji.get_word(i),
            English=japanese_translation_en.get_word(i),
            German=japanese_translation_de.get_word(i)
        )
        print(row)

    exit(0)

    # Start
    run_quiz(vocab_list, lang="de-DE")
