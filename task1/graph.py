from pyvis.network import Network


class LinkGraph:
    def __init__(self):
        self.net = Network(notebook=True, directed=True)
        self.nodes = {}

    def add_document(self, doc):
        self.nodes[doc.url] = Node(doc.url, doc.content_urls)

    def show(self):
        for node in self.nodes.values():
            for url in node.neighbors:
                if url != node.url and url in self.nodes:
                    node.outdeg += 1
                    self.nodes[url].indeg += 1

        for node in self.nodes.values():
            if node.indeg > 0 or node.outdeg > 0:
                self.net.add_node(node.url, title=node.url, size=node.indeg, label=' ')

        for node in self.nodes.values():
            for url in node.neighbors:
                try:
                    self.net.add_edge(node.url, url, physics=False)
                except:
                    pass

        return self.net.show("links.html")


class Node:
    def __init__(self, url, neighbors):
        self.indeg = 0
        self.outdeg = 0
        self.url = url
        self.neighbors = neighbors
