from fastapi import FastAPI, HTTPException, Body, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from tempfile import NamedTemporaryFile
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List
from .services.organisational_dna_builder import OrganizationalDNAEngine
from .services.knowledge_graph_builder import KnowledgeGraphBuilder
from neo4j import GraphDatabase
# Import services
from .services.collection_agent import (
    OTXAgent, CVEAgent, GitHubSecurityAgent, ThreatLandscapeBuilder
)
from .services.autonomous_correlation_agent import AutonomousCorrelationAgent
from .services.pir_generator_main import PIRGenerator
from .services.simple_pipeline import run_pipeline
from .services.threat_modeling import generate_threat_model
from .services.logger_config import logger
from .services.document_processor import DocumentProcessor
from .services.session_store import create_session, add_docs, get_docs, clear_session

load_dotenv()

app = FastAPI(
    title="cAIber API",
    description="Backend services for the cAIber Threat Intelligence Platform.",
    version="0.6.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED = {'.pdf', '.txt', '.docx', '.md'} 

#===================
# Document Upload
#===================

@app.post("/documents/start")
def start_ingest_session():
    sid = create_session()
    return {"session_id": sid}

@app.post("/upload")
async def upload_document(session_id: str = Query(...), file: UploadFile = File(...)):
    processor = DocumentProcessor()
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type: {suffix}")

    raw = await file.read()
    with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        tmp.write(raw); tmp.flush()
        chunks = processor._load_single_document(tmp.name, original_name=file.filename)

    # Save into the session
    add_docs(session_id, chunks)

    return {
        "session_id": session_id,
        "added": len(chunks),
        "total": len(get_docs(session_id))
    }

@app.post("/upload-batch")
async def upload_documents(session_id: str = Query(...), files: List[UploadFile] = File(...)):
    processor = DocumentProcessor()
    total = 0
    for f in files:
        suffix = Path(f.filename).suffix.lower()
        if suffix not in ALLOWED:
            raise HTTPException(415, f"{f.filename}: unsupported file type: {suffix}")
        raw = await f.read()
        with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
            tmp.write(raw); tmp.flush()
            chunks = processor._load_single_document(tmp.name, original_name=f.filename)
            add_docs(session_id, chunks)
            total += len(chunks)

    return {
        "session_id": session_id,
        "added": total,
        "total": len(get_docs(session_id))
    }


ALLOWED = {'.pdf', '.txt', '.docx', '.md'} 

#===================
# Document Upload
#===================

@app.post("/documents/start")
def start_ingest_session():
    sid = create_session()
    return {"session_id": sid}

@app.post("/upload")
async def upload_document(session_id: str = Query(...), file: UploadFile = File(...)):
    processor = DocumentProcessor()
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type: {suffix}")

    raw = await file.read()
    with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
        tmp.write(raw); tmp.flush()
        chunks = processor._load_single_document(tmp.name, original_name=file.filename)

    # Save into the session
    add_docs(session_id, chunks)

    return {
        "session_id": session_id,
        "added": len(chunks),
        "total": len(get_docs(session_id))
    }

@app.post("/upload-batch")
async def upload_documents(session_id: str = Query(...), files: List[UploadFile] = File(...)):
    processor = DocumentProcessor()
    total = 0
    for f in files:
        suffix = Path(f.filename).suffix.lower()
        if suffix not in ALLOWED:
            raise HTTPException(415, f"{f.filename}: unsupported file type: {suffix}")
        raw = await f.read()
        with NamedTemporaryFile(delete=True, suffix=suffix) as tmp:
            tmp.write(raw); tmp.flush()
            chunks = processor._load_single_document(tmp.name, original_name=f.filename)
            add_docs(session_id, chunks)
            total += len(chunks)

    return {
        "session_id": session_id,
        "added": total,
        "total": len(get_docs(session_id))
    }


# Global Neo4j driver
neo4j_driver = None

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    global neo4j_driver
    try:
        neo4j_uri = os.getenv("NEO4J_URI", "neo4j+ssc://cc633ab6.databases.neo4j.io")
        neo4j_user = os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        
        # Test the connection
        with neo4j_driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        
        logger.info("✅ Neo4j connection established on startup")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Neo4j on startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown"""
    global neo4j_driver
    if neo4j_driver:
        neo4j_driver.close()
        logger.info("🔌 Neo4j connection closed")

# ================================
# Stage 1: PIR Generation
# ================================

@app.post("/generate-pirs", status_code=200)
def generate_pirs(payload: dict = Body(...)):
    """
    Stage 1: Generate PIRs after org DNA build from uploaded docs.
    Body: { "session_id": "...", "clear_existing": false }
    """
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(400, "session_id is required")

    docs = get_docs(session_id)
    if not docs:
        raise HTTPException(400, "No uploaded documents found for this session_id")

    # Try to build Organizational DNA first (upload-only)
    try:
        print("🔍 Building Organizational DNA from uploaded files")
        org_gen = OrganizationalDNAEngine(
            neo4j_uri=os.getenv("NEO4J_URI"),
            neo4j_user=os.getenv("NEO4J_USERNAME"),
            neo4j_password=os.getenv("NEO4J_PASSWORD")
        )
        org_gen.build_organizational_dna(
            documents=docs,
            clear_existing=bool(payload.get("clear_existing", False)),
        )
        print("✅ Organizational DNA built successfully")
    except Exception as neo4j_error:
        print(f"❌ Neo4j connection failed: {neo4j_error}")
        print("⚠️  Falling back to mock data mode")

    # Generate PIRs (Neo4j-backed if available; else mock)
    pir_gen = PIRGenerator()
    result = pir_gen.generate_pirs()

    if not result.get("success", True):
        raise HTTPException(status_code=500, detail=result.get("error", "PIR generation failed"))

    return result
    Stage 1: Generate Priority Intelligence Requirements (PIRs).
    Returns both raw PIRs and extracted keywords for collection.
    """
    try:
        # Try to build organizational DNA first
        try:
            print("🔍 Attempting to build Organizational DNA...")
            org_gen = OrganizationalDNAEngine(
                neo4j_uri=os.getenv("NEO4J_URI"),
                neo4j_user=os.getenv("NEO4J_USERNAME"),
                neo4j_password=os.getenv("NEO4J_PASSWORD")
            )
            org_gen.build_organizational_dna("../documents", clear_existing=True)
            print("✅ Organizational DNA built successfully")
        except Exception as neo4j_error:
            print(f"❌ Neo4j connection failed: {neo4j_error}")
            print("⚠️  Falling back to mock data mode")
            # Continue with PIR generation using mock data
        
        # Generate PIRs (will use Neo4j data if available, mock data if not)
        pir_gen = PIRGenerator()
        result = pir_gen.generate_pirs()
        
        # Handle both success and error cases
        if not result.get("success", True):
            raise HTTPException(status_code=500, detail=result.get("error", "PIR generation failed"))
            
        return result

@app.get("/api/organizational-dna", status_code=200)
def get_organizational_dna():
    """
    Get the organizational DNA knowledge graph from Neo4j.
    Returns nodes and relationships in a format suitable for visualization.
    """
    try:
        # Use global Neo4j driver
        global neo4j_driver
        if not neo4j_driver:
            raise HTTPException(status_code=503, detail="Neo4j connection not available")
        
        nodes = []
        links = []
        node_map = {}  # To track unique nodes
        
        with neo4j_driver.session() as session:
            # Fetch all nodes
            result = session.run("""
                MATCH (n:Entity)
                RETURN n.id AS id, 
                       n.name AS label, 
                       n.type AS type,
                       n.confidence AS confidence,
                       n.importance AS importance
                ORDER BY n.confidence DESC
                LIMIT 200
            """)
            
            # Define color mapping for different entity types
            color_map = {
                'technology': '#14b8a6',
                'organization': '#0ea5e9', 
                'geography': '#f59e0b',
                'threat_actor': '#ef4444',
                'vulnerability': '#dc2626',
                'business_initiative': '#8b5cf6',
                'business_asset': '#a855f7',
                'compliance_requirement': '#f97316',
                'financial_data': '#22c55e'
            }
            
            for record in result:
                node_id = record['id']
                node_type = record['type']
                
                # Calculate node size based on confidence and importance
                confidence = record['confidence'] or 0.5
                importance = record['importance'] or 5
                val = int(10 + (confidence * 10) + (importance * 2))
                
                node = {
                    'id': node_id,
                    'label': record['label'],
                    'type': node_type,
                    'val': val,
                    'color': color_map.get(node_type, '#6b7280')
                }
                nodes.append(node)
                node_map[node_id] = node
            
            # Fetch relationships
            result = session.run("""
                MATCH (source:Entity)-[r]->(target:Entity)
                WHERE source.id IN $node_ids AND target.id IN $node_ids
                RETURN source.id AS source, 
                       target.id AS target, 
                       type(r) AS relationship_type,
                       r.confidence AS confidence
                LIMIT 500
            """, node_ids=list(node_map.keys()))
            
            for record in result:
                source_id = record['source']
                target_id = record['target']
                
                # Only include links where both nodes exist
                if source_id in node_map and target_id in node_map:
                    confidence = record['confidence'] or 0.5
                    links.append({
                        'source': source_id,
                        'target': target_id,
                        'value': int(confidence * 5),  # Link thickness based on confidence
                        'type': record['relationship_type']
                    })
        
        # Driver is managed globally, no need to close
        
        # Calculate stats
        node_types = {}
        for node in nodes:
            node_type = node['type']
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        return {
            'nodes': nodes,
            'links': links,
            'stats': {
                'totalNodes': len(nodes),
                'technologies': node_types.get('technology', 0),
                'organizations': node_types.get('organization', 0),
                'geographies': node_types.get('geography', 0),
                'threats': node_types.get('threat_actor', 0),
                'vulnerabilities': node_types.get('vulnerability', 0),
                'business_initiatives': node_types.get('business_initiative', 0),
                'business_assets': node_types.get('business_asset', 0),
                'compliance': node_types.get('compliance_requirement', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch organizational DNA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch organizational DNA: {str(e)}")


# ================================
# Stage 2: Threat Collection
# ================================

@app.post("/collect-threats", status_code=200)
def collect_threats(pir_keywords: dict):
    """
    Stage 2: Run collection agents (OTX, CVE, GitHub)
    to build threat landscape filtered by PIR keywords.
    Accepts keyword dict with categories like technologies, geographies, etc.
    """
    try:
        otx_api_key = os.getenv("OTX_API_KEY")
        github_token = os.getenv("GITHUB_TOKEN")
        nvd_api_key = os.getenv("NVD_API_KEY")

        # Flatten dict into one keyword set
        # Pass PIR keywords into agents
        agents = [
            CVEAgent(api_key=nvd_api_key, keywords=pir_keywords),
            GitHubSecurityAgent(github_token=github_token, keywords=pir_keywords)
        ]
        if otx_api_key:
            agents.append(OTXAgent(api_key=otx_api_key, keywords=pir_keywords))

        builder = ThreatLandscapeBuilder(agents, pir_keywords=pir_keywords)
        landscape = builder.build_threat_landscape()
        return {"landscape": landscape}

    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect-and-correlate", status_code=200)
def collect_and_correlate(pir_keywords: Dict[str, List[str]] = Body(...)):
    """
    Run Stage 2 (collect threats) and immediately feed
    the full threat landscape into Stage 3 (correlate).
    """
    try:
        # Stage 2: Collect threats
        response = collect_threats(pir_keywords)
        landscape = response["landscape"]

        # Stage 3: Correlate using the collected landscape
        agent = AutonomousCorrelationAgent()
        assessments = agent.correlate_threats(landscape)
        agent.close()

        return {"assessments": assessments}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# Stage 3: Correlation Agent
# ================================
@app.post("/correlate-threats", status_code=200)
def correlate_threats(threat_landscape: dict):
    """
    Stage 3: Correlate threats with organizational DNA from Neo4j.
    Input is threat_landscape from Stage 2.
    """
    try:
        agent = AutonomousCorrelationAgent()
        assessments = agent.correlate_threats(threat_landscape)
        agent.close()
        return {"assessments": assessments}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-threat-model", status_code=200)
async def get_comprehensive_threat_model(intelligence_data: dict = Body(...)):
    """
    Accepts a full intelligence package and returns a comprehensive,
    methodology-driven threat model with all plausible attack paths.
    """
    try:
        model_data = generate_threat_model(intelligence_data)
        return {
            "message": f"Comprehensive threat model generated successfully with {len(model_data.get('attack_paths', []))} path(s).",
            "model": model_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# ================================
# Orchestrator: Run all stages
# ================================
# @app.post("/run-all", status_code=200)
# def run_all_stages():
#     """
#     Orchestrates the full pipeline:
#     1. Generate PIRs
#     2. Collect threats (CVE, GitHub, OTX)
#     3. Correlate threats with org DNA
#     """
#     try:
#         # Stage 1: PIRs
#         pir_resp = generate_pirs()
#         keywords = {"cloud", "kubernetes", "azure", "gdpr", "phishing", "supply chain"}  # mock extraction

#         # Stage 2: Collection
#         otx_api_key = os.getenv("OTX_API_KEY")
#         github_token = os.getenv("GITHUB_TOKEN")
#         nvd_api_key = os.getenv("NVD_API_KEY")

#         agents = [
#             CVEAgent(api_key=nvd_api_key, keywords=keywords),
#             GitHubSecurityAgent(github_token=github_token, keywords=keywords)
#         ]
#         if otx_api_key:
#             agents.append(OTXAgent(api_key=otx_api_key, keywords=keywords))

#         builder = ThreatLandscapeBuilder(agents, pir_keywords=keywords)
#         landscape = builder.build_threat_landscape()

#         # Stage 3: Correlation
#         agent = AutonomousCorrelationAgent()
#         assessments = agent.correlate_threats(landscape)
#         agent.close()

#         return {
#             "pirs": pir_resp,
#             "landscape": landscape,
#             "assessments": assessments,
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# ================================
# Complete Pipeline (Uses simple_pipeline.py)
# ================================
@app.post("/run-complete-pipeline", status_code=200)
def run_complete_pipeline(skip_stage1: bool = False, autonomous_correlation: bool = False):
    """
    Run the complete 4-stage cAIber pipeline using simple_pipeline.py.
    - skip_stage1: Skip Organizational DNA building (faster demo mode)
    - autonomous_correlation: Use AI agent for correlation instead of standard
    """
    try:
        result = run_pipeline(
            skip_stage1=skip_stage1,
            autonomous_correlation=autonomous_correlation
        )
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threat-model", status_code=200)
def threat_model_endpoint(intelligence_data: dict):
    """
    Stage 4: Threat Modeling
    Accepts the combined intelligence data from previous stages:
    - pirs
    - keywords
    - threat_landscape
    - risk_assessments
    - executive_summary

    Returns: Generated threat model JSON
    """
    try:
        logger.info("STAGE 4: Threat Modeling")
        threat_model = generate_threat_model(intelligence_data)
        return {"threat_model": threat_model}
    except Exception as e:
        logger.error(f"Threat modeling failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Threat modeling failed: {str(e)}")

# ================================
@app.get("/")
def read_root():
    return {"message": "Welcome to the cAIber Backend!"}
