class Vector:
    def __init__(self, bm25_score, title_match, content_match, span, query_length, doc_length, doc_pr, doc_url_length):
        self.bm25_score = bm25_score
        self.title_match = title_match
        self.content_match = content_match
        self.span = span
        self.query_length = query_length
        self.doc_length = doc_length
        self.doc_pr = doc_pr
        self.doc_url_length = doc_url_length
