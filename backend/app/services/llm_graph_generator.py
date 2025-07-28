import os
from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM, using gpt-4o as inspired by the reference project
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

# Initialize the Graph Transformer
graph_transformer = LLMGraphTransformer(llm=llm)

async def extract_graph_from_text(text: str) -> GraphDocument:
    """
    Asynchronously extracts graph data from unstructured text using the LLMGraphTransformer.
    This is the core of turning business documents into 'Organizational DNA'.
    
    Args:
        text (str): The unstructured text to be processed.

    Returns:
        GraphDocument: An object containing the extracted nodes and relationships.
    """
    # The transformer expects a list of documents
    documents = [Document(page_content=text)]
    
    # Asynchronously convert the documents to graph documents
    graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
    
    # Return the first graph document, if it exists
    return graph_documents[0] if graph_documents else None