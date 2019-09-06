import os
import xml.etree.ElementTree as et
from document import *
from dictionary import *
from pymystem3 import Mystem
from statistics import mean


def average_doc_size_in_words(docs):
    return mean([doc.words_cnt for doc in docs])


def average_doc_size_in_bytes(docs):
    return mean([doc.bytes_cnt for doc in docs])


def average_doc_text_to_html_ratio(docs):
    return mean([doc.text_to_html_ratio for doc in docs])


def parse_xml(filename):
    docs = []
    tree = et.parse(filename)
    root = tree.getroot()

    for child in root:
        if child.tag == "document":
            content = child[0].text
            url = child[1].text
            doc_id = int(child[2].text)
            doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
            docs.append(doc)
        break  # remove it

    return docs


XML_FOLDER = "byweb_for_course"

if __name__ == '__main__':
    docs_stat = []
    mystem = Mystem()
    dict = Dictionary()

    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            docs = parse_xml(XML_FOLDER + os.sep + filename)
            for doc in docs:
                docs_stat.append(doc.calc_doc_stats())
                # dict stuff
                # text = 'Как насчёт, небольшого стемминга?'
                # lemmas = mystem.lemmatize(text)
                # print(''.join(lemmas))
        break  # remove it

    # link stuff

    # print results
