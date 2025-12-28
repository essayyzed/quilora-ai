from haystack import Document
from haystack.nodes import DensePassageRetriever
from haystack.pipelines import Pipeline

def create_retrieval_pipeline(document_store):
    retriever = DensePassageRetriever(document_store=document_store)
    pipeline = Pipeline()
    pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
    return pipeline

def retrieve_documents(pipeline, query, top_k=5):
    results = pipeline.run(query=query, params={"Retriever": {"top_k": top_k}})
    return results["documents"]