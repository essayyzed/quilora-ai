from haystack.document_stores import InMemoryDocumentStore
from haystack.pipelines import DocumentPipeline
from haystack.nodes import TextConverter, PreProcessor, DensePassageRetriever

def create_indexing_pipeline():
    document_store = InMemoryDocumentStore()

    # Define the components for the indexing pipeline
    text_converter = TextConverter()
    preprocessor = PreProcessor()
    retriever = DensePassageRetriever(document_store=document_store)

    # Create the indexing pipeline
    pipeline = DocumentPipeline()
    pipeline.add_node(component=text_converter, name="TextConverter", inputs=["File"])
    pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["TextConverter"])
    pipeline.add_node(component=retriever, name="Retriever", inputs=["PreProcessor"])

    return pipeline

def index_documents(documents):
    pipeline = create_indexing_pipeline()
    pipeline.run(documents=documents)