from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from dotenv import load_dotenv
import os

from .services.dna_engine import get_db, close_db, add_graph_to_db
from .services.llm_graph_generator import extract_graph_from_text
from .services.file_processor import extract_text_from_file
from .services.collection_agent import OTXAgent

load_dotenv()

app = FastAPI(
    title="cAIber API",
    description="Backend services for the cAIber Threat Intelligence Platform.",
    version="0.5.0"
)

@app.on_event("startup")
def startup_event():
    get_db()

@app.on_event("shutdown")
def shutdown_event():
    close_db()

@app.post("/upload-and-process", status_code=200)
async def upload_and_process_file(file: UploadFile = File(...)):
    """
    Accepts a file (PDF, TXT, MD), extracts the text, and populates
    the knowledge graph.
    """
    try:
        # 1. Extract text from the uploaded file
        text = await extract_text_from_file(file)

        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from file or file is empty.")

        # 2. Use the LLM to extract graph data from the text
        graph_document = await extract_graph_from_text(text)
        
        if not graph_document or (not graph_document.nodes and not graph_document.relationships):
            return {"message": f"File '{file.filename}' processed, but no graph data could be extracted."}
        
        # 3. Write the extracted data to Neo4j
        add_graph_to_db(graph_document)

        return {
            "message": f"File '{file.filename}' processed and graph generated successfully.",
            "nodes_created": len(graph_document.nodes),
            "relationships_created": len(graph_document.relationships)
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# This endpoint is now async
@app.post("/process-text", status_code=200)
async def process_text_to_graph(text: str = Body(..., embed=True)):
    """
    Receives unstructured text, uses an LLM to extract entities and
    relationships, and populates the 'Organizational DNA' knowledge graph.
    """
    try:
        # 1. Asynchronously use the LLM to extract graph data
        graph_document = await extract_graph_from_text(text)
        
        if not graph_document or (not graph_document.nodes and not graph_document.relationships):
            return {"message": "No graph data could be extracted from the text."}
        
        # 2. Write the extracted data to Neo4j
        # (This function doesn't need to be async as it's a series of quick writes)
        add_graph_to_db(graph_document)

        return {
            "message": "Graph generated and stored successfully.",
            "nodes_created": len(graph_document.nodes),
            "relationships_created": len(graph_document.relationships)
        }
    except Exception as e:
        # It's good practice to log the error here
        # For now, we'll just return it in the response
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/run-collection-agent", status_code=200)
async def run_collection_agent():
    """
    Triggers the AI-powered collection agent and returns the
    filtered, structured threat intelligence.
    """
    otx_api_key = os.getenv("OTX_API_KEY")
    if not otx_api_key:
        raise HTTPException(status_code=500, detail="OTX_API_KEY not configured.")

    try:
        agent = OTXAgent(api_key=otx_api_key)
        collected_data = agent.run() 
        return {
            "message": f"Collection agent run completed. Found {len(collected_data)} items.",
            "intelligence": collected_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the cAIber Backend!"}