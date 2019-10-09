import os
import zipfile

import lxml.etree as et

from task1.document import *
from task1.graph import *


def parse_xml():
    XML_FOLDER = "byweb_for_course"
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            name = XML_FOLDER + os.sep + filename
            context = et.iterparse(name, tag='document')

            zip_file = zipfile.ZipFile("documents" + os.sep + filename.strip(".xml") + ".zip", 'w',
                                       zipfile.ZIP_DEFLATED)

            for (_, elem) in context:
                content = elem[0].text
                url = elem[1].text
                doc_id = int(elem[2].text)
                elem.clear()

                doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
                filepath = f"{doc.doc_id}.txt"
                docfile = open(filepath, "w+")
                docfile.write(doc.to_json())
                docfile.close()
                zip_file.write(filepath)
                os.remove(filepath)
                graph.add_document(doc)
            zip_file.close()


graph = LinkGraph()
parse_xml()
graph.build()

for doc_id, pr in graph.pagerank().items():
    pagerank_file = open("pageranks.txt", "a")
    pagerank_file.write(str(doc_id) + ":" + str(pr) + str("\n"))
