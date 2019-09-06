import subprocess
import re
import os
import string


def process_files(paths):
    document_lemmas = []
    for file in paths:
        stemmed = subprocess.run(["./mystem", file], stdout=subprocess.PIPE, universal_newlines=True).stdout
        lemmas = [x[0] for x in re.findall(r'{(.*?)([}|])', stemmed)]
        document_lemmas.append(lemmas)

    return document_lemmas


def count_stop_words(stop_words_path, lemmas):
    files = [f for f in os.listdir(stop_words_path) if os.path.isfile(os.path.join(stop_words_path, f))]
    stop_words_count = 0
    for file in files:
        content = [s.strip() for s in open(os.path.join(stop_words_path, file), "r").readlines()]
        for word in content:
            if word in all_lemmas:
                stop_words_count += 1
    return stop_words_count


def average_word_length(words):
    return sum(len(word) for word in words) / len(words)


def latin_words_count(words):
    allowed_symbols = list(string.ascii_lowercase + '?')
    return sum(1 if all(ch in allowed_symbols for ch in word) else 0 for word in words) / len(words)


if __name__ == '__main__':
    document_lemmas = process_files(["file.txt"])
    all_lemmas = [item for sublist in document_lemmas for item in sublist]
    stop_words_count = count_stop_words("stopwords", all_lemmas)
    average_word_length_in_collection = average_word_length(all_lemmas)
    latin_words_count_in_collection = latin_words_count(all_lemmas)

    print(stop_words_count)
    print(average_word_length_in_collection)
    print(latin_words_count_in_collection)



