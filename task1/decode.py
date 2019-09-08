import xml.etree.ElementTree as et
import math
import operator
from statistics import mean

from pymystem3 import Mystem

from task1.dictionary import *
from task1.document import *


def average_doc_size_in_words(docs):
    return mean([doc.words_cnt for doc in docs])


def average_doc_size_in_bytes(docs):
    return mean([doc.bytes_cnt for doc in docs])


def average_doc_text_to_html_ratio(docs):
    return mean([doc.text_to_html_ratio for doc in docs])


def inverse_document_frequency(dictionary, docs):
    return {word: math.log10(len(docs) / dictionary[word].doc_cnt) for word in dictionary}


def most_popular_word(dictionary, limit=5, get_max=True):
    sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(1))
    dictionary_top = sorted_dictionary[-limit:] if get_max else sorted_dictionary[:limit]
    max_values = [entry[1] for entry in dictionary_top]
    return [word for (word, _) in sorted_dictionary if dictionary[word] in max_values]


def stem_words(words, stem):
    return stem.lemmatize(" ".join(words))


def parse_xml(filename):
    docs = []
    tree = et.parse(filename)
    root = tree.getroot()

    # TODO remove this for final result
    cnt = 0

    for child in root:
        if child.tag == "document":
            content = child[0].text
            url = child[1].text
            doc_id = int(child[2].text)
            doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
            docs.append(doc)
        # TODO remove this for final result
        cnt += 1
        if cnt == 5:
            break

    return docs


XML_FOLDER = "byweb_for_course"

if __name__ == '__main__':
    docs_stat = []
    mystem = Mystem()
    dictionary = Dictionary()

    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            docs = parse_xml(XML_FOLDER + os.sep + filename)
            for doc in docs:
                docs_stat.append(doc.calc_doc_stats())
                stemmed_words = [word.lower() for word in stem_words(doc.words, mystem) if word.isalnum()]
                dictionary.add_doc_words(stemmed_words)
                # dict stuff
                # text = 'Как насчёт небольшого стемминга?'
                # lemmas = mystem.lemmatize(text)
                # print(''.join(lemmas))
        break  # remove it

    # link stuff

    # print results
    print("Total documents count: " + str(len(docs_stat)))
    print("Average document length: " + str(average_doc_size_in_words(docs_stat)) + " words")
    print("Average document length: " + str(average_doc_size_in_bytes(docs_stat)) + " bytes")
    print("Average text content to HTML content ratio: " + str(average_doc_text_to_html_ratio(docs_stat)))
    # TODO distribution
    print("Words with largest collection frequency: " +
          str(most_popular_word({word: dictionary.dict[word].cnt for word in dictionary.dict})))
    print("Words with smallest inverse document frequency: " +
          str(most_popular_word(inverse_document_frequency(dictionary.dict, docs_stat), get_max=False)))
