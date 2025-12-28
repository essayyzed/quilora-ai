from haystack.document_stores import InMemoryDocumentStore

class CustomDocumentStore(InMemoryDocumentStore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def custom_method(self):
        # Implement any custom functionality here
        pass

document_store = CustomDocumentStore()