from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import Dict, List
from .services.organisational_dna_builder import OrganizationalDNAEngine
# Import services
from .services.collection_agent import (
    OTXAgent, CVEAgent, GitHubSecurityAgent, ThreatLandscapeBuilder
)
from .services.autonomous_correlation_agent import AutonomousCorrelationAgent
from .services.pir_generator_main import PIRGenerator
from .services.simple_pipeline import run_pipeline
from .services.threat_modeling import generate_threat_model
from .services.logger_config import logger

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

# ================================
# Stage 1: PIR Generation
# ================================

@app.get("/generate-pirs", status_code=200)
def generate_pirs():
    """
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
            org_gen.build_organizational_dna("./documents", clear_existing=True)
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

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PIR generation failed: {str(e)}")


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
