import base64
import os
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup, Comment
from statistics import mean


class Document:
    def __init__(self, content, doc_id, url):
        self.doc_id = doc_id
        self.url = url
        self.content = content
        self.text = self.parse_html_to_text()
        self.words = list(filter(lambda s: any(ch.isalpha() for ch in s), self.text.split()))

    def calc_doc_stats(self):
        content_urls = self.parse_html_to_links()
        text_bytes_size = string_size_in_bytes(self.text)
        html_bytes_size = string_size_in_bytes(self.content)
        ratio = html_bytes_size / text_bytes_size
        return DocumentStat(self.doc_id, self.url, content_urls, len(self.words), html_bytes_size, ratio)

    def parse_html_to_text(self):
        def decompose_comments(soup):
            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
            return soup

        def decompose_js(soup):
            for script in soup(["script", "style"]):
                script.decompose()

        soup = BeautifulSoup(self.content, 'html.parser')
        decompose_js(soup)
        soup = decompose_comments(soup)
        soup = BeautifulSoup(soup.get_text(separator=" "), 'html.parser')
        soup = decompose_comments(soup)
        return soup.get_text(separator=" ")

    def parse_html_to_links(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        return [link.get('href') for link in soup.find_all('a')]


class DocumentStat:
    def __init__(self, doc_id, url, content_urls, words_cnt, bytes_cnt, text_to_html_ratio):
        self.doc_id = doc_id
        self.url = url
        self.words_cnt = words_cnt
        self.bytes_cnt = bytes_cnt
        self.text_to_html_ratio = text_to_html_ratio
        self.content_urls = content_urls


def string_size_in_bytes(s):
    return len(s.encode('cp1251'))


def decode_base64_cp1251(s):
    return base64.b64decode(s).decode('cp1251')


def average_doc_size_in_words(docs):
    return mean([doc.words_cnt for doc in docs])


def average_doc_size_in_bytes(docs):
    return mean([doc.bytes_cnt for doc in docs])


def average_doc_text_to_html_ratio(docs):
    return mean([doc.text_to_html_ratio for doc in docs])


def parse_xml(filename):
    tree = et.parse(filename)
    root = tree.getroot()

    for child in root:
        if child.tag == "document":
            content = child[0].text
            url = child[1].text
            doc_id = int(child[2].text)
            doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
            documents.append(doc)
        break


XML_FOLDER = "byweb_for_course"

if __name__ == '__main__':
    documents = []
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            parse_xml(XML_FOLDER + os.sep + filename)
        break

    for doc in documents:
        print(doc.text)
