"""
LANGUAGE DRIFT
A tiny linguistic simulation.
"""

import random
import json
import os
from colorama import init, Fore, Style

init(autoreset=True)

SAVE_FILE = "language.json"

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

VOWEL_SHIFT = {"a": "o", "o": "u", "u": "a", "e": "i", "i": "e"}
CONSONANT_SHIFT = {
    "t": "d", "d": "t", "p": "b", "b": "p", "k": "g", "g": "k",
    "f": "v", "v": "f", "s": "z", "z": "s", "c": "k", "n": "m",
    "m": "n", "l": "r", "r": "l", "h": "", "w": "v", "y": "i",
    "j": "y", "q": "k", "x": "s",
}

ONSETS = ["b", "d", "f", "g", "k", "l", "m", "n", "r", "s", "t", "v", "sh", "th", "kr", "vr"]
CODAS = ["", "n", "r", "l", "s", "t", "k", "d", "m"]

STARTING_WORDS = [
    "the", "water", "fire", "stone", "tree", "bird", "house", "person", "mother",
    "father", "child", "walk", "run", "eat", "sleep", "day", "night", "moon", "sun",
    "river", "mountain", "sky", "earth", "wind", "rain", "snow", "leaf", "root",
    "seed", "flower", "grass", "sand", "rock", "path", "road", "village", "city",
    "friend", "enemy", "love", "hate", "fear", "hope", "dream", "song", "dance",
    "voice", "word", "name", "story", "light", "dark", "shadow", "star", "cloud",
    "storm", "fish", "wolf", "bear", "deer", "horse", "dog", "cat", "cow", "sheep",
    "goat", "eagle", "snake", "spider", "ant", "bee", "tooth", "hand", "foot", "eye",
    "ear", "hair", "blood", "bone", "heart", "head", "mouth", "nose", "arm", "leg",
    "knife", "spear", "shield", "fire", "smoke", "ash", "gold", "silver", "iron",
    "salt", "bread", "milk", "meat", "honey", "wine", "boat", "wheel",
]
# de-duplicate while preserving order (fire appears twice above)
STARTING_WORDS = list(dict.fromkeys(STARTING_WORDS))[:100]


def load_state():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    language = {w: w for w in STARTING_WORDS}
    return {"generation": 0, "year": 0, "language": language, "history": []}


def save_state(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4, ensure_ascii=False)


def letter_swap(word):
    if len(word) < 2:
        return word
    i = random.randint(0, len(word) - 2)
    chars = list(word)
    chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return "".join(chars)


def insert_letter(word):
    i = random.randint(0, len(word))
    pool = VOWELS if random.random() < 0.5 else CONSONANTS
    return word[:i] + random.choice(pool) + word[i:]


def remove_letter(word):
    if len(word) <= 3:
        return word
    i = random.randint(1, len(word) - 1)
    return word[:i] + word[i + 1:]


def duplicate_letter(word):
    if not word:
        return word
    i = random.randint(0, len(word) - 1)
    return word[:i + 1] + word[i] + word[i + 1:]


def replace_letter(word):
    if not word:
        return word
    i = random.randint(0, len(word) - 1)
    letter = word[i]
    pool = VOWELS if letter in VOWELS else CONSONANTS
    new_letter = random.choice([c for c in pool if c != letter] or [letter])
    return word[:i] + new_letter + word[i + 1:]


def shift_vowel(word):
    positions = [i for i, c in enumerate(word) if c in VOWEL_SHIFT]
    if not positions:
        return word
    i = random.choice(positions)
    return word[:i] + VOWEL_SHIFT[word[i]] + word[i + 1:]


def shift_consonant(word):
    positions = [i for i, c in enumerate(word) if c in CONSONANT_SHIFT]
    if not positions:
        return word
    i = random.choice(positions)
    return word[:i] + CONSONANT_SHIFT[word[i]] + word[i + 1:]


def invent_syllable(word):
    syllables = max(1, min(3, round(len(word) / 3)))
    new_word = ""
    for _ in range(syllables):
        new_word += random.choice(ONSETS) + random.choice(VOWELS) + random.choice(CODAS)
    return new_word


SIMPLE_MUTATIONS = [
    letter_swap, insert_letter, remove_letter, duplicate_letter,
    replace_letter, shift_vowel, shift_consonant,
]


def double_mutation(word):
    a, b = random.sample(SIMPLE_MUTATIONS, 2)
    return b(a(word))


MUTATIONS = SIMPLE_MUTATIONS + [double_mutation, invent_syllable]
WEIGHTS = [15, 15, 15, 10, 20, 15, 15, 8, 2]


def mutate(word):
    fn = random.choices(MUTATIONS, weights=WEIGHTS, k=1)[0]
    result = fn(word)
    if not result or len(result) > 14:
        return word
    return result


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_header(state):
    print(Fore.CYAN + "=" * 38)
    print(Fore.CYAN + Style.BRIGHT + "        LANGUAGE DRIFT")
    print(Fore.CYAN + "=" * 38)
    print(Fore.CYAN + f"Year: {state['year']}")
    print(Fore.CYAN + f"Generations: {state['generation']}")
    print()


def print_sample(state):
    values = list(state["language"].values())
    sample = random.sample(values, min(10, len(values)))
    print(Fore.MAGENTA + "Language Sample")
    for word in sample:
        print(Fore.MAGENTA + word)
    print()


def print_latest_mutation(state):
    if not state["history"]:
        print(Fore.GREEN + "Latest Mutation")
        print(Fore.GREEN + "(the language has not yet drifted)")
        print()
        return
    latest = state["history"][-1]
    print(Fore.GREEN + "Latest Mutation")
    print(Fore.GREEN + latest["before"])
    print(Fore.GREEN + "  \u2193")
    print(Fore.GREEN + latest["after"])
    print()


def print_history(state):
    print(Fore.YELLOW + "History")
    for entry in state["history"][-10:]:
        print(Fore.YELLOW + f"{entry['before']} \u2192 {entry['after']}")
    print()


def print_dictionary(state):
    clear_screen()
    print(Fore.CYAN + "English           Current Language")
    print(Fore.CYAN + "-" * 36)
    for english, current in state["language"].items():
        print(f"{english:<18}{current}")
    print()
    input("Press ENTER to return...")


def advance_generation(state):
    english_word = random.choice(list(state["language"].keys()))
    before = state["language"][english_word]
    after = mutate(before)
    state["language"][english_word] = after
    state["history"].append({"english": english_word, "before": before, "after": after})
    state["history"] = state["history"][-10:]
    state["generation"] += 1
    state["year"] += 1


def main():
    state = load_state()
    while True:
        clear_screen()
        print_header(state)
        print_sample(state)
        print_latest_mutation(state)
        print_history(state)
        print("Type 'dict' to view the full dictionary")
        print("Press ENTER to advance, or Q to quit")
        cmd = input("> ").strip().lower()

        if cmd == "q":
            save_state(state)
            print("The language sleeps, for now.")
            break
        elif cmd == "dict":
            print_dictionary(state)
            continue
        else:
            advance_generation(state)
            save_state(state)
            if state["generation"] % 100 == 0:
                clear_screen()
                print(Fore.CYAN + "=" * 22)
                print(Fore.CYAN + "LANGUAGE SHIFT")
                print(Fore.CYAN + "=" * 22)
                print("The language is becoming harder to recognize...")
                input("Press ENTER to continue...")


if __name__ == "__main__":
    main()