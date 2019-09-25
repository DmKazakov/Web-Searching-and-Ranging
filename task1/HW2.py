import os
import time

import lxml.etree as et
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

from task1.document import *
from task1.graph import *
from task1.query import *

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
        if filename.endswith(".0.xml"):
            name = XML_FOLDER + os.sep + filename
            context = et.iterparse(name, tag='document')

            # TODO this is for debug, remove in the final version
            limit = 50
            i = 0

            for (_, elem) in context:
                content = elem[0].text
                url = elem[1].text
                doc_id = int(elem[2].text)
                elem.clear()

                # TODO this is for debug, remove in the final version
                if i == limit:
                    break
                i += 1

                try:
                    doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
                    graph.add_document(doc)
                    yield create_action(doc)
                except:
                    print("Unable to parse " + str(doc_id))
            break


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


def search_query(query_text, query_result_size=20):
    query = {
        'query': {
            'bool': {
                'should': {
                    'match': {
                        'content': query_text
                    }
                }

            }
        }
    }
    query_result = es.search(index=INDEX, body=query, size=query_result_size)
    return list(map(lambda x: (x['_id'], x['_score']), query_result['hits']['hits']))


def search_stemmed_query(query_text, query_result_size=20):
    lemmatized_query = mystem.lemmatize(query_text)
    query = {
        'query': {
            'bool': {
                'should': {
                    'match': {
                        'stemmed': " ".join(lemmatized_query)
                    }
                }

            }
        }
    }
    query_result = es.search(index=INDEX, body=query, size=query_result_size)
    return list(map(lambda x: (x['_id'], x['_score']), query_result['hits']['hits']))


def precision_recall(expected, actual_data, k=20):
    actual = set(actual_data[:k])
    actual_rprecision = set(actual_data[:len(expected)])
    intersection_size = len(actual.intersection(expected))
    intersection_size_rprecision = len(actual_rprecision.intersection(expected))

    precision = intersection_size / k
    rprecision = (intersection_size_rprecision / len(expected)) if len(expected) > 0 else 0
    recall = (intersection_size / len(expected)) if len(expected) > 0 else 0
    return precision, recall, rprecision


def average_precision(expected, actual, k=20):
    k = min(k, len(actual))
    s = 0
    n = 0
    for i in range(k):
        if actual[i] in expected:
            s += precision_recall(expected, actual, i + 1)[0]
            n += 1
    return 0 if n == 0 else s / n


def search_statistics(search_function, queries):
    total_precision = 0
    total_recall = 0
    total_rprecision = 0
    total_average_precision = 0
    for query_id in queries:
        query_result = search_function(queries[query_id].text)
        doc_ids = [doc_id for (doc_id, _) in query_result]
        precision, recall, rprecision = precision_recall(queries[query_id].relevant,
                                                         doc_ids)
        total_precision += precision
        total_recall += recall
        total_rprecision += rprecision
        total_average_precision += average_precision(queries[query_id].relevant, doc_ids)
    return total_precision / len(queries), total_recall / len(queries), total_rprecision / len(queries), \
        total_average_precision / len(queries)


graph = LinkGraph()
es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 360, 'maxsize': 25}])
recreate_index()

start_indexing = time.time()
for ok, result in parallel_bulk(es, action_generator(), queue_size=4, thread_count=4, chunk_size=1000):
    if not ok:
        print(result)
print("Indexing time: ", time.time() - start_indexing)
print("Index size in bytes: ", es.indices.stats()['_all']['primaries']['store']['size_in_bytes'])

for id, pr in graph.pagerank().items():
    # TODO: doc_type?
    es.update(index=INDEX, id=id, body={'doc': {'pagerank': pr}})

QUERIES_FILE = "web2008_adhoc.xml"
RELEVANCE_FILE = "or_relevant-minus_table.xml"
queries = {}
root = et.parse(QUERIES_FILE).getroot()
for element in root.iterfind('task', namespaces=root.nsmap):
    text = element[0].text
    id = element.attrib.get('id')
    element.clear()
    queries[id] = Query(id, text)
root = et.parse(RELEVANCE_FILE).getroot()
for element in root.iterfind('task', namespaces=root.nsmap):
    id = element.attrib.get('id')
    for document in element.iterfind('document', namespaces=root.nsmap):
        doc_id = document.attrib.get('id')
        relevance = document.attrib.get('relevance')
        document.clear()
        if relevance == 'vital':
            queries[id].relevant.append(doc_id)
    element.clear()

start_queries_plain_text = time.time()
plain_text_statistics = search_statistics(search_query, queries)
print("Average precision for plain text, k = 20: ", plain_text_statistics[0])
print("Average recall for plain text, k = 20: ", plain_text_statistics[1])
print("Average R-precision for plain text: ", plain_text_statistics[2])
print("Mean Average Precision for plain text: ", plain_text_statistics[3])
print("Queries execution time for plain text: ", time.time() - start_queries_plain_text)

start_queries_lemmatized = time.time()
lemmatized_text_statistics = search_statistics(search_query, queries)
print("Average precision for lemmatized text, k = 20: ", plain_text_statistics[0])
print("Average recall for lemmatized text, k = 20: ", plain_text_statistics[1])
print("Average R-precision for lemmatized text: ", plain_text_statistics[2])
print("Mean Average Precision for lemmatized text: ", plain_text_statistics[3])
print("Queries execution time for lemmatized text: ", time.time() - start_queries_lemmatized)
