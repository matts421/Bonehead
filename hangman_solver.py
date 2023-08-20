import requests
import json

WORDLIST_URL = "https://www.mit.edu/~ecprice/wordlist.10000"

# with open("letter_frequency.json", 'r') as file:
#     letter_frequency = json.load(file)

def main():
    raw_words = requests.get(WORDLIST_URL).content.splitlines()
    words = map(lambda word: str(word)[2:-1], raw_words)
    word_length = int(input("Word length: "))
    words = list(filter(lambda word: len(word) == word_length, words))
    print(words)

    while True:
        progress = list(input("Progress: "))
        guesses = list(input("Guesses: "))

        words = refine_search(guesses, progress, words)
        good_guess = suggest_guess(words, guesses)
        print("suggested good guess:", good_guess)
        print("-------------------")


def hangman_guesser(guesses: list, progress: list, words):
    words = refine_search(guesses, progress, words)
    good_guess = suggest_guess(words, guesses)
    return good_guess, words


def refine_search(guesses: list, progress: list, words):
    bad_guesses = list(set(guesses).difference(set(progress)))

    for guess in bad_guesses:
        words = [word for word in words if guess not in word]

    for i, guess in enumerate(progress):
        if guess != r"\_":
            words = [word for word in words if word[i] == guess]

    return list(words)


def suggest_guess(words, guesses):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    letter_frequency = {c:0 for c in alphabet}
    
    for c in letter_frequency.keys():
        for word in list(words):
            if c in word:
                letter_frequency[c] += 1

    valid_letter_frequency = {letter:count for (letter, count) in letter_frequency.items() if letter not in guesses}

    return max(valid_letter_frequency, key = lambda x: valid_letter_frequency[x])


if __name__ == "__main__":
    main()
