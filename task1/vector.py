import numpy as np
from sklearn.preprocessing import RobustScaler


class Vector:
    def __init__(self, relevant, bm25_score, title_match, content_match, span, query_length, doc_length, doc_pr,
                 doc_url_length):
        self.relevant = relevant
        self.bm25_score = bm25_score
        self.title_match = title_match
        self.content_match = content_match
        self.span = span
        self.query_length = query_length
        self.doc_length = doc_length
        self.doc_pr = doc_pr
        self.doc_url_length = doc_url_length

    def to_string(self, qid):
        array = self.to_scaled_array()
        return f'{self.relevant} qid:{qid} 1:{array[1]} 2:{array[2]} 3:{array[3]} ' \
               f'4:{array[4]} 5:{array[5]} 6:{array[6]} 7:{array[7]} 8:{array[8]}'

    def to_array(self):
        return [0, self.bm25_score, self.title_match, self.content_match, self.span, self.query_length,
                self.doc_length, self.doc_pr, self.doc_url_length]

    def to_scaled_array(self):
        return RobustScaler().fit_transform(np.asarray(self.to_array()).reshape(-1, 1)).flatten()
