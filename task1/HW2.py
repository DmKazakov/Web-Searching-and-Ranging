import lxml.etree as et
import os
import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

from task1.document import *
from task1.graph import *


INDEX = "ind"

def create_action(doc):
    return {
        '_index': INDEX,
        '_id': doc.doc_id,
        '_source': doc.to_json()
    }


def action_generator():
    XML_FOLDER = "byweb_for_course"
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            name = XML_FOLDER + os.sep + filename
            context = et.iterparse(name, tag='document')

            for (_, elem) in context:
                content = elem[0].text
                url = elem[1].text
                doc_id = int(elem[2].text)
                elem.clear()

                try:
                    doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
                    graph.add_document(doc)
                    yield create_action(doc)
                except:
                    print("Unable to parse " + str(doc_id))


SETTINGS = {
    'mappings': {
        'properties': {
            'content': {
                'type': 'text',
                'analyzer': 'russian_plain'
            },
            'stemmed': {
                'type': 'text',
                'analyzer': 'russian_stemmed'
            },
            'titles': {
                'type': 'text',
                'analyzer': 'russian_plain'
            },
            'pagerank': {
                'type': 'rank_feature'
            }
        }
    },
    'settings': {
        'analysis': {
            'analyzer': {
                'russian_plain': {
                    'char_filter': ['yo'],
                    'tokenizer': 'alphanum',
                    'filter': ['lowercase']
                },
                'russian_stemmed': {
                    'char_filter': ['yo'],
                    'tokenizer': 'whitespace',
                    'filter': ['lowercase']
                }
            },
            'char_filter': {
                'yo': {
                    'type': 'mapping',
                    'mappings': ['ё => е']
                }
            },
            'tokenizer': {
                'alphanum': {
                    'type': 'char_group',
                    'tokenize_on_chars': ["whitespace", "punctuation", "symbol", "\n"]
                }
            }
        }
    }
}


def recreate_index():
    try:
        es.indices.delete(index=INDEX)
    except:
        pass
    es.indices.create(index=INDEX, body=SETTINGS)


graph = LinkGraph()
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 360, 'maxsize': 25}])
recreate_index()

start_indexing = time.time()
for ok, result in parallel_bulk(es, action_generator(), queue_size=4, thread_count=4, chunk_size=1000):
    if not ok:
        print(result)
print("Indexing time: ", time.time() - start_indexing)

for id, pr in graph.pagerank().items():
    # TODO: doc_type?
    es.update(index=INDEX, id=id, body={'doc': {'pagerank': pr}})
