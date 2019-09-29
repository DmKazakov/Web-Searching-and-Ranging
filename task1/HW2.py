import os
import time
import zipfile

import lxml.etree as et
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

from task1.document import *
from task1.query import *

INDEX = "ind"


def create_action(doc_id, doc_json):
    return {
        '_index': INDEX,
        '_id': doc_id,
        '_source': doc_json
    }


def action_generator():
    DOCS_FOLDER = "documents"
    for filename in os.listdir(DOCS_FOLDER):
        name = DOCS_FOLDER + os.sep + filename
        zip_file = zipfile.ZipFile(name, 'r')

        i = 0
        for filename in zip_file.filelist:
            try:
                i += 1
                if i == 10:
                    break
                doc_json = zip_file.read(filename).decode('utf-8')
                yield create_action(filename.orig_filename.strip(".txt"), doc_json)
            except:
                print(filename.orig_filename)
                return


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
        },
        'index': {
            'blocks': {
                'read_only_allow_delete': 'false'
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


def search_static_and_dynamic_features_query(query_text, query_result_size=20):
    query = {
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'text': query_text
                        }
                    },
                    {
                        'rank_feature': {
                            'field': 'pagerank',
                            'saturation': {
                                'pivot': 1e-6
                            }
                        }
                    }
                ]
            }
        }
    }
    query_result = es.search(index=INDEX, body=query, size=query_result_size)
    return list(map(lambda x: (x['_id'], x['_score']), query_result['hits']['hits']))


def search_query_with_titles(query_text, query_result_size=20):
    lemmatized_query = mystem.lemmatize(query_text)
    query = {
        'query': {
            'bool': {
                'should': [
                    {
                        'match': {
                            'stemmed': " ".join(lemmatized_query)
                        }
                    },
                    {
                        'match': {
                            'titles': {
                                'query': " ".join(lemmatized_query),
                                'boost': '1.5'
                            }
                        }
                    }
                ]

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
    expected_len = min(len(expected), k)

    precision = intersection_size / k
    rprecision = intersection_size_rprecision / expected_len
    recall = intersection_size / expected_len
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
    queries_precision = {}
    total_precision = 0
    total_recall = 0
    total_rprecision = 0
    total_average_precision = 0
    i = 0
    for query_id in queries:
        query_result = search_function(queries[query_id].text)
        doc_ids = [doc_id for (doc_id, _) in query_result]
        precision, recall, rprecision = precision_recall(queries[query_id].relevant,
                                                         doc_ids)
        queries_precision[query_id] = 2 * precision * recall / (precision + recall)
        total_precision += precision
        total_recall += recall
        total_rprecision += rprecision
        total_average_precision += average_precision(queries[query_id].relevant, doc_ids)
        i += 1
        if i % 100 == 0:
            print("still searching, now at i = ", i)
    return total_precision / len(queries), total_recall / len(queries), total_rprecision / len(queries), \
           total_average_precision / len(queries), queries_precision


es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'timeout': 360, 'maxsize': 25}])

recreate_index()

start_indexing = time.time()
for ok, result in parallel_bulk(es, action_generator(), queue_size=1, thread_count=1, chunk_size=1):
    if not ok:
        print(result)
print("Indexing time: ", time.time() - start_indexing)
print("Index size in bytes: ", es.indices.stats()['_all']['primaries']['store']['size_in_bytes'])

pagerank_file = open("pageranks.txt", "r")
line = pagerank_file.readline()
while line:
    doc_id, pr = line.strip().split(":")
    es.update(index=INDEX, id=doc_id, body={'doc': {'pagerank': pr}})
    line = pagerank_file.readline()


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
            queries[id].relevant.add(doc_id)
    element.clear()
queries = {query_id: queries[query_id] for query_id in queries if len(queries[query_id].relevant) > 0}

start_queries_plain_text = time.time()
plain_text_statistics = search_statistics(search_query, queries)
print("Average precision for plain text, k = 20: ", plain_text_statistics[0])
print("Average recall for plain text, k = 20: ", plain_text_statistics[1])
print("Average R-precision for plain text: ", plain_text_statistics[2])
print("Mean Average Precision for plain text: ", plain_text_statistics[3])
print("Queries execution time for plain text: ", time.time() - start_queries_plain_text)

start_queries_lemmatized = time.time()
lemmatized_text_statistics = search_statistics(search_stemmed_query, queries)
print("Average precision for lemmatized text, k = 20: ", lemmatized_text_statistics[0])
print("Average recall for lemmatized text, k = 20: ", lemmatized_text_statistics[1])
print("Average R-precision for lemmatized text: ", lemmatized_text_statistics[2])
print("Mean Average Precision for lemmatized text: ", lemmatized_text_statistics[3])
print("Queries execution time for lemmatized text: ", time.time() - start_queries_lemmatized)

start_queries_pagerank = time.time()
pagerank_statistics = search_statistics(search_static_and_dynamic_features_query, queries)
print("Average precision for plain text with pagerank, k = 20: ", pagerank_statistics[0])
print("Average recall for plain text with pagerank, k = 20: ", pagerank_statistics[1])
print("Average R-precision for plain text with pagerank: ", pagerank_statistics[2])
print("Mean Average Precision for plain text with pagerank: ", pagerank_statistics[3])
print("Queries execution time for plain text with pagerank: ", time.time() - start_queries_pagerank)

start_queries_with_titles = time.time()
titles_statistics = search_statistics(search_query_with_titles, queries)
print("Average precision for plain text with titles, k = 20: ", titles_statistics[0])
print("Average recall for plain text with titles, k = 20: ", titles_statistics[1])
print("Average R-precision for plain text with titles: ", titles_statistics[2])
print("Mean Average Precision for plain text with titles: ", titles_statistics[3])
print("Queries execution time for plain text with titles: ", time.time() - start_queries_with_titles)

plain_text_precisions = plain_text_statistics[4]
lemmatized_text_precisions = lemmatized_text_statistics[4]
queries_precision_diff = [(abs(lemmatized_text_precisions[id] - plain_text_precisions[id]), id) for id in queries.keys()]
for _, id in sorted(queries_precision_diff, reverse=True, key=lambda tup: tup[0])[:3]:
    print("Query text:", queries[id].text)
    print("Precision for plain text:", plain_text_precisions[id])
    print("Precision for lemmatized text:", lemmatized_text_precisions[id])
