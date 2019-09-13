import math
import operator

from statistics import mean
from scipy.signal import savgol_filter
from plotly.offline import init_notebook_mode, iplot
import plotly.graph_objs as go


init_notebook_mode(connected=True)


def average_doc_size_in_words(docs):
    return mean([doc.words_cnt for doc in docs])


def average_doc_size_in_bytes(docs):
    return mean([doc.bytes_cnt for doc in docs])


def average_doc_text_to_html_ratio(docs):
    return mean([doc.text_to_html_ratio for doc in docs])


def rank_frequency(dictionary):
    sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(1), reverse=True)
    return [(math.log10(i), math.log10(sorted_dictionary[i - 1][1])) for i in range(1, len(sorted_dictionary) + 1)]


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
    smooth_trace = {'type': 'scatter', 'mode': 'lines',
                    'x': [entry[0] for entry in data],
                    'y': savgol_filter([entry[1] for entry in data], 51, 3),
                    'line': {'shape': 'spline', 'smoothing': 1.3}}
    plot_figure(smooth_trace, title, x_axis_title, y_axis_title)


def plot_figure(data, title, x_axis_title, y_axis_title):
    layout = go.Layout(
        title=title,
        xaxis=go.layout.XAxis(title=go.layout.xaxis.Title(text=x_axis_title)),
        yaxis=go.layout.YAxis(title=go.layout.yaxis.Title(text=y_axis_title))
    )
    fig = go.Figure(data=data, layout=layout)
    iplot(fig)


def float_to_str(n):
    return "{0:.2f}".format(n)