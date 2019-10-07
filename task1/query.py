class Query:
    def __init__(self, id, text):
        self.id = id
        self.text = text
        self.relevant = set()
        self.relevant_train = set()
