class Query:
    def __init__(self, id, text):
        self.id = id
        self.text = text
        self.relevant_test = set()
        self.irrelevant_test = set()
        self.relevant_train = set()
        self.irrelevant_train = set()