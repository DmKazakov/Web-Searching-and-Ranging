from pyvis.network import Network


class LinkGraph:
    def __init__(self, ):
        self.net = Network(notebook=True, directed=True)
        self.nodes = {}

    def add_document(self, doc):
        self.nodes[doc.url] = Node(doc.url, doc.content_urls)

    def show(self, node_physics=False, edge_physics=False):
        for node in self.nodes.values():
            for url in node.neighbors:
                if url != node.url and url in self.nodes:
                    node.outdeg += 1
                    self.nodes[url].indeg += 1

        for node in self.nodes.values():
            if node.indeg > 0 or node.outdeg > 0:
                self.net.add_node(node.url, title=node.url, size=node.indeg + 1, label=' ', physics=node_physics)

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
