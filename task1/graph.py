from pyvis.network import Network
from urllib.parse import urlparse, urljoin


class LinkGraph:
    def __init__(self, min_indeg=0):
        self.net = Network(notebook=True, directed=True)
        self.nodes = {}
        self.min_indeg = min_indeg

    def add_document(self, doc):
        try:
            resolver = UrlResolver(doc.url)
            content_urls = resolver.resolve_urls(doc.content_urls)
            self.nodes[resolver.base_url] = Node(resolver.base_url, content_urls)
        except:
            return

    def show(self, node_physics=False, edge_physics=False):
        for node in self.nodes.values():
            for url in node.neighbors:
                if url != node.url and url in self.nodes:
                    node.outdeg += 1
                    self.nodes[url].indeg += 1

        for node in self.nodes.values():
            if node.indeg >= self.min_indeg:
                size = (node.indeg - self.min_indeg + 1) // 10
                self.net.add_node(node.url, title=node.url, size=size, label=' ', physics=node_physics)

        for node in self.nodes.values():
            for url in node.neighbors:
                if url != node.url:
                    try:
                        self.net.add_edge(node.url, url, physics=edge_physics)
                    except:
                        pass

        return self.net.show("links.html")


class Node:
    def __init__(self, url, neighbors):
        self.indeg = 0
        self.outdeg = 0
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