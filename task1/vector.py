class Vector:
    def __init__(self, relevant, bm25_score, title_match, content_match, span, query_length, doc_length, doc_pr, doc_url_length):
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
        return f'{self.relevant} qid:{qid} 1:{self.bm25_score} 2:{self.title_match} 3:{self.content_match} ' \
               f'4:{self.span} 5:{self.query_length} 6:{self.doc_length} 7:{self.doc_pr} 8:{self.doc_url_length}'
