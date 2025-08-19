from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from dotenv import load_dotenv
import os

from .services.dna_engine import get_db, close_db, add_graph_to_db
from .services.llm_graph_generator import extract_graph_from_text
from .services.file_processor import extract_text_from_file
from .services.collection_agent import OTXAgent
from .services.pir_generator_main import PIRGenerator

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
        text = await extract_text_from_file(file)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from file or file is empty.")

        graph_document = await extract_graph_from_text(text)
        if not graph_document or (not graph_document.nodes and not graph_document.relationships):
            return {"message": f"File '{file.filename}' processed, but no graph data could be extracted."}

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

@app.post("/process-text", status_code=200)
async def process_text_to_graph(text: str = Body(..., embed=True)):
    """
    Receives unstructured text, uses an LLM to extract entities and
    relationships, and populates the 'Organizational DNA' knowledge graph.
    """
    try:
        graph_document = await extract_graph_from_text(text)
        if not graph_document or (not graph_document.nodes and not graph_document.relationships):
            return {"message": "No graph data could be extracted from the text."}

        add_graph_to_db(graph_document)
        return {
            "message": "Graph generated and stored successfully.",
            "nodes_created": len(graph_document.nodes),
            "relationships_created": len(graph_document.relationships)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/run-collection-agent", status_code=200)
def run_collection_agent():
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

@app.get("/generate-pirs", status_code=200)
def get_priority_intelligence_requirements():
    """
    Analyzes the knowledge graph to generate and return
    Priority Intelligence Requirements (PIRs).
    """
    try:
        # pir_gen = PIRGenerator()
        # pirs = pir_gen.generate_pirs()
        # return {"pirs": pirs}
        mock_pirs = {
            "result": """
            1. Business Expansion into Southeast Asia:
            The organization is planning new data centers in Singapore and Malaysia.
            Suggest prioritizing intelligence on threat actors targeting financial institutions in ASEAN,
            especially those exploiting cloud supply chain providers and regional managed service providers.

            2. Cloud Adoption and Kubernetes Deployment:
            Critical workloads are being migrated to Microsoft Azure and deployed on Kubernetes clusters.
            Recommend monitoring for vulnerabilities in container orchestration (e.g., misconfigured RBAC, exposed APIs),
            and threat groups known for targeting Azure services (e.g., UNC2452 / APT29).

            3. Third-Party Vendor and Supply Chain Dependencies:
            The organization relies heavily on GitHub repositories and open-source dependencies for core products.
            Recommend intelligence collection on malicious package injections (e.g., typosquatting in PyPI/NPM),
            and campaigns targeting CI/CD pipelines.

            4. Compliance & Regulatory Exposure:
            Expansion into Europe requires GDPR and PCI-DSS compliance.
            Suggest monitoring enforcement trends, insider threats tied to data exfiltration,
            and ransomware groups exploiting regulatory deadlines for extortion leverage.

            5. Past Incident Patterns:
            Historical incidents show repeated phishing campaigns against executives using lookalike domains.
            Recommend prioritizing intelligence on phishing kits, domain registrations,
            and credential harvesting tools (e.g., Evilginx2) linked to spearphishing.
            """
        }
        return {"pirs": mock_pirs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the cAIber Backend!"}