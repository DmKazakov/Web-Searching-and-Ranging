import math
import operator
import lxml.etree as et
from statistics import mean

import plotly.graph_objs as go

from task1.dictionary import *
from task1.document import *


def average_doc_size_in_words(docs):
    return mean([doc.words_cnt for doc in docs])


def average_doc_size_in_bytes(docs):
    return mean([doc.bytes_cnt for doc in docs])


def average_doc_text_to_html_ratio(docs):
    return mean([doc.text_to_html_ratio for doc in docs])


def rank_frequency(dictionary):
    sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)
    return [(math.log10(i), math.log10(sorted_dictionary[i - 1][1])) for i in range(1, len(sorted_dictionary) + 1)]


def parse_xml(filename):
    context = et.iterparse(filename, tag='document')

    for (_, elem) in context:
        content = elem[0].text
        url = elem[1].text
        doc_id = int(elem[2].text)
        elem.clear()

        doc = Document(decode_base64_cp1251(content), doc_id, decode_base64_cp1251(url))
        docs_stat.append(doc.calc_doc_stats())
        dictionary.add_doc_words(doc.words)

        if len(docs_stat) == 50:
            return


def plot_histogram(data, title, x_axis_title, y_axis_title, step):
    histogram = go.Histogram(
        x=data,
        xbins=dict(
            start=0,
            end=max(data),
            size=step
        ),
    )
    plot_figure(histogram, title, x_axis_title, y_axis_title)


def plot_line(data, title, x_axis_title, y_axis_title):
    line_graph = go.Scatter(x=[entry[0] for entry in data], y=[entry[1] for entry in data], mode='lines')
    plot_figure(line_graph, title, x_axis_title, y_axis_title)


def plot_figure(data, title, x_axis_title, y_axis_title):
    layout = go.Layout(
        title=title,
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text=x_axis_title)),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text=y_axis_title))
    )
    fig = go.Figure(data=data, layout=layout)
    fig.show()


def float_to_str(n):
    return "{0:.2f}".format(n)


XML_FOLDER = "byweb_for_course"

docs_stat = []
dictionary = Dictionary()

for filename in os.listdir(XML_FOLDER):
    if filename.endswith(".xml"):
        parse_xml(XML_FOLDER + os.sep + filename)
        break

print("Total documents count: " + str(len(docs_stat)))
print("Average document length: " + float_to_str(average_doc_size_in_words(docs_stat)) + " words")
print("Average document length: " + float_to_str(average_doc_size_in_bytes(docs_stat)) + " bytes")
print("Average text content to HTML content ratio: " + float_to_str(average_doc_text_to_html_ratio(docs_stat)))
plot_histogram(
    data=[stat.words_cnt for stat in docs_stat],
    title="Length in words distribution",
    x_axis_title="words",
    y_axis_title="documents",
    step=250
)
plot_histogram(
    data=[stat.bytes_cnt for stat in docs_stat],
    title="Length in bytes distribution",
    x_axis_title="bytes",
    y_axis_title="documents",
    step=5000
)

print("Collection stop words ratio: " + float_to_str(dictionary.stop_words_proportion(in_collection=True)))
print("Collection latin words ratio: " + float_to_str(dictionary.latin_words_proportion(in_collection=True)))
print("Dictionary latin words ratio: " + float_to_str(dictionary.latin_words_proportion(in_collection=False)))
print("Dictionary average word length: " + float_to_str(dictionary.average_dic_word_len()))
print("Collection average word length: " + float_to_str(dictionary.average_word_len()))

print("Words with largest collection frequency: " +
      str(dictionary.most_popular_word(lambda v: dictionary.dict[v].cnt)))
print("Words with smallest inverse document frequency: " +
      str(dictionary.most_popular_word(lambda v: math.log10(len(docs_stat) / dictionary.dict[v].doc_cnt),
                                       get_max=False)))

rf = rank_frequency({word: dictionary.dict[word].cnt for word in dictionary.dict})
plot_line(rf, "Rank-frequency", "rank", "frequency")
