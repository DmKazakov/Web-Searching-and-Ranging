import base64
from bs4 import BeautifulSoup, Comment
from pymystem3 import Mystem

mystem = Mystem()


class Document:
    def __init__(self, content, doc_id, url):
        self.doc_id = doc_id
        self.url = url
        self.content = content
        self.text = self.parse_html_to_text()
        stemmed_words = mystem.lemmatize(self.text)
        self.words = [word for word in stemmed_words if word.isalnum()]

    def calc_doc_stats(self):
        content_urls = self.parse_html_to_links()
        text_bytes_size = string_size_in_bytes(self.text)
        html_bytes_size = string_size_in_bytes(self.content)
        ratio = text_bytes_size / html_bytes_size
        return DocumentStat(self.doc_id, self.url, content_urls, len(self.words), text_bytes_size, ratio)

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
    return len(s.encode('cp1251', errors='replace'))


def decode_base64_cp1251(s):
    return base64.b64decode(s).decode('cp1251')
