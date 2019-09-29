from urllib.parse import urlparse, urljoin
from networkx import pagerank
import networkx as nx


class LinkGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes = []
        self.urlToId = {}

    def add_document(self, doc):
        try:
            resolver = UrlResolver(doc.url)
            content_urls = resolver.resolve_urls(doc.content_urls)
            self.nodes.append(Node(doc.doc_id, resolver.base_url, content_urls))
            self.graph.add_node(doc.doc_id)
            self.urlToId[resolver.base_url] = doc.doc_id
        except:
            return

    def build(self):
        for node in self.nodes:
            for url in node.neighbors:
                if url != node.url and url in self.urlToId:
                    self.graph.add_edge(node.id, self.urlToId[url])

    def pagerank(self):
        return pagerank(self.graph)


class Node:
    def __init__(self, id, url, neighbors):
        self.id = id
        self.url = url
        self.neighbors = neighbors


class UrlResolver:
    def __init__(self, base_url):
        self.base_url = self.remove_params(base_url)

    def resolve_urls(self, urls):
        resolved = []
        for url in urls:
            try:
                parse_result = urlparse(url)
                if not parse_result.netloc:
                    url = urljoin(self.base_url, url)
                resolved.append(self.remove_params(url))
            except:
                pass
        return resolved

    def remove_params(self, url):
        parse_result = urlparse(url)
        return parse_result.netloc + parse_result.path
