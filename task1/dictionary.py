from collections import defaultdict
import os

STOP_WORDS_FOLDER = "stopwords"


class Dictionary:
    def __init__(self):
        self.dict = defaultdict(lambda: DictionaryEntry())
        self.words_len = 0
        self.words_cnt = 0

    def add_doc_words(self, words):
        self.words_cnt += len(words)

        for word in words:
            self.dict[word].cnt += 1
            self.words_len += len(word)

        for word in set(words):
            self.dict[word].doc_cnt += 1

    def average_word_len(self):
        return self.words_len / self.words_cnt

    def average_dic_word_len(self):
        dic_word_len = 0
        for k, _ in self.dict.items():
            dic_word_len += len(k)
        return dic_word_len / len(self.dict)

    def latin_words_proportion(self, in_collection=False):
        latin_words = 0
        for k, v in self.dict.items():
            t = v.cnt if in_collection else 1
            latin_words += t if all(ord(c) < 128 for c in k) else 0
        return latin_words / self.words_cnt

    def stop_words_proportion(self, in_collection=False):
        files = [f for f in os.listdir(STOP_WORDS_FOLDER) if os.path.isfile(os.path.join(STOP_WORDS_FOLDER, f))]
        stop_words = [s.strip() for file in files for s in open(os.path.join(STOP_WORDS_FOLDER, file), "r").readlines()]
        stop_words_count = 0
        for k, v in self.dict.items():
            t = v.cnt if in_collection else 1
            stop_words_count += t if k in stop_words else 0
        return stop_words_count / self.words_cnt


class DictionaryEntry:
    def __init__(self):
        self.cnt = 0
        self.doc_cnt = 0
