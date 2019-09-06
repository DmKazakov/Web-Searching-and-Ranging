import base64
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup, Comment


class Document:
    def __init__(self, content, doc_id, url):
        self.content = content
        self.doc_id = doc_id
        self.url = url
        self.text = parse_html_to_text(self.content)
        self.content_urls = parse_html_to_links(self.content)


res_file = open("result.txt", "w+")
doc_lengths_in_words_file = open("doc_length_in_words.txt", "w+")
doc_lengths_in_bytes_file = open("doc_length_in_bytes.txt", "w+")
doc_to_html_volume_ratio_file = open("doc_to_html_volume_ratio.txt", "w+")


def parse_xml(filename):
    tree = et.parse(filename)
    root = tree.getroot()
    documents = []

    for child in root:
        if child.tag == "document":
            content = child[0].text
            url = child[1].text
            doc_id = int(child[2].text)
            doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))

            doc_lengths_in_words_file.write(str(len(split_into_words(doc.text))) + " ")
            doc_lengths_in_bytes_file.write(str(string_length_in_bytes(doc.text)) + " ")
            ratio = string_length_in_bytes(doc.text) / string_length_in_bytes(doc.content)
            doc_to_html_volume_ratio_file.write(str(ratio) + " ")

            documents.append(doc)

    return documents


def decode_base64_cp1251(s):
    return base64.decodebytes(bytes(s, 'cp1251')).decode('cp1251')


def parse_html_to_text(html_string):
    def extract_comments(soup):
        comments = soup.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]
        return soup

    soup = BeautifulSoup(html_string, 'html.parser')
    soup = extract_comments(soup)
    soup = BeautifulSoup(soup.get_text(separator=" "), 'html.parser')
    soup = extract_comments(soup)
    return soup.get_text(separator=" ")


def parse_html_to_links(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    return [link.get('href') for link in soup.find_all('a')]


def split_into_words(string):
    return list(filter(lambda s: any(ch.isalpha() for ch in s), string.split()))


def average_doc_size_in_words(docs):
    av = 0
    for doc in docs:
        words = split_into_words(doc.text)
        av += len(words)
    return av / len(docs)


def string_length_in_bytes(s):
    return len(s.encode('cp1251'))


def average_doc_size_in_bytes(docs):
    av = 0
    for doc in docs:
        av += string_length_in_bytes(doc.text)
    return av / len(docs)


def average_doc_text_to_html_in_words(docs):
    av = 0
    for doc in docs:
        av += string_length_in_bytes(doc.text) / string_length_in_bytes(doc.content)
    return av / len(docs)


if __name__ == '__main__':
    docs = parse_xml("byweb.0.xml")

    res_file.write("documents: " + str(len(docs)))
    res_file.write("\n")
    res_file.write(str(average_doc_size_in_words(docs)))
    res_file.write("\n")
    res_file.write(str(average_doc_size_in_bytes(docs)))
    res_file.write("\n")
    res_file.write((str(average_doc_text_to_html_in_words(docs))))

    doc_lengths_in_words = [len(split_into_words(doc.text)) for doc in docs]
    doc_lengths_in_bytes = [string_length_in_bytes(doc.text) for doc in docs]

    res_file.write("\n")
    res_file.write(str(doc_lengths_in_words))
    res_file.write("\n")
    res_file.write(str(doc_lengths_in_bytes))
