import lxml.etree as et

from task1.dictionary import *
from task1.document import *
from task1.graph import *


def parse_xml(filename):
    context = et.iterparse(filename, tag='document')

    for (_, elem) in context:
        content = elem[0].text
        url = elem[1].text
        doc_id = int(elem[2].text)
        elem.clear()

        try:
            doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
            stats = doc.calc_doc_stats()
            docs_stats.append(stats)
            graph.add_document(stats)
        except:
            print("Unable to parse " + str(doc_id))


XML_FOLDER = "byweb_for_course"

graph = LinkGraph()
docs_stats = []

for filename in os.listdir(XML_FOLDER):
    if filename.endswith(".xml"):
        parse_xml(XML_FOLDER + os.sep + filename)