import os
from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from neo4j import GraphDatabase
import asyncio

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

file_path = "/Users/vihaanmotwani/Documents/cAIber/documents/technical_architecture_v2.txt"
try:
    with open(file_path, "r") as file:
        content = file.read()
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
except Exception as e:
    print(f"An error occurred: {e}")

graph_doc = asyncio.run(extract_graph_from_text(content))

driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=("neo4j", os.getenv("NEO4J_PASSWORD")))

import json

def safe_props(props):
    """Convert any property dict into Neo4j-safe primitives."""
    if not props:
        return {}
    safe = {}
    for k, v in props.items():
        if isinstance(v, (str, int, float, bool)):
            safe[k] = v
        else:
            # serialize anything else (lists, dicts, Node objects, etc.)
            safe[k] = json.dumps(str(v))
    return safe


def ingest_graph_document(graph_doc: GraphDocument):
    if not graph_doc:
        print("No graph extracted.")
        return

    with driver.session() as session:
        # Ingest nodes
        for node in graph_doc.nodes:
            props = safe_props(node.properties or {})
            session.run(
                f"MERGE (n:{node.type} {{id: $id}}) SET n += $props",
                id=str(node.id),
                props=props
            )

        # Ingest relationships
        for rel in graph_doc.relationships:
            props = safe_props(rel.properties or {})

            # unwrap Node objects into IDs
            src_id = rel.source.id if hasattr(rel.source, "id") else str(rel.source)
            tgt_id = rel.target.id if hasattr(rel.target, "id") else str(rel.target)

            session.run(
                f"""
                MATCH (a {{id: $src}}), (b {{id: $tgt}})
                MERGE (a)-[r:{rel.type}]->(b)
                SET r += $props
                """,
                src=src_id,
                tgt=tgt_id,
                props=props
            )



ingest_graph_document(graph_doc)