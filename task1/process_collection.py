import os

import lxml.etree as et

from task1.document import *
from task1.graph import *


def parse_xml():
    XML_FOLDER = "byweb_for_course"
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".0.xml"):
            name = XML_FOLDER + os.sep + filename
            context = et.iterparse(name, tag='document')

            i = 0
            for (_, elem) in context:
                content = elem[0].text
                url = elem[1].text
                doc_id = int(elem[2].text)
                elem.clear()

                i += 1
                if i == 3000:
                    break

                doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
                docfile = open(f"documents/{doc.doc_id}.txt", "w+")
                docfile.write(doc.to_json())
                graph.add_document(doc)



graph = LinkGraph()

parse_xml()

for id, pr in graph.pagerank().items():
    pagerank_file = open(f"pageranks.txt", "a")
    pagerank_file.write(str(id) + ":" + str(pr) + str("\n"))
