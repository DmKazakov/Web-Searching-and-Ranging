import pybase64
import json

from bs4 import BeautifulSoup, Comment
from pymystem3 import Mystem

mystem = Mystem(disambiguation=False)


class Document:
    def __init__(self, content, doc_id, url):
        self.doc_id = doc_id
        self.url = url
        self.parse_html(content)
        stemmed_words = mystem.lemmatize(self.text)
        self.words = [word.lower() for word in stemmed_words if word.isalnum()]

    def parse_html(self, content):
        def decompose_comments(soup):
            comments = soup.findAll(text=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
            return soup

        def decompose_js(soup):
            for script in soup(["script", "style"]):
                script.decompose()

        soup = BeautifulSoup(content, 'lxml')

        self.content_urls = [link.get('href') for link in soup.find_all('a')]
        self.titles = [word for word in mystem.lemmatize(title.string) for title in soup.find_all('title')]

        decompose_js(soup)
        soup = decompose_comments(soup)
        soup = BeautifulSoup(soup.get_text(separator=" "), 'lxml')
        soup = decompose_comments(soup)

        self.text = soup.get_text(separator=" ")

    def to_json(self):
        obj = {
            "content": self.text,
            "stemmed": self.words,
            "titles": self.titles,
            "pagerank": 1
        }
        return json.dumps(obj)


def decode_base64_cp1251(s):
    return pybase64.urlsafe_b64decode(s).decode('cp1251')
