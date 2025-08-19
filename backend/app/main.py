from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv

# Import services
from .services.collection_agent import (
    OTXAgent, CVEAgent, GitHubSecurityAgent, ThreatLandscapeBuilder
)
from .services.autonomous_correlation_agent import AutonomousCorrelationAgent

load_dotenv()

app = FastAPI(
    title="cAIber API",
    description="Backend services for the cAIber Threat Intelligence Platform.",
    version="0.6.0"
)

# ================================
# Stage 1: PIR Generation
# ================================
@app.get("/generate-pirs", status_code=200)
def generate_pirs():
    """
    Stage 1: Generate Priority Intelligence Requirements (PIRs).
    (Mocked for now — replace with real LLM logic later.)
    """
    try:
        # pir_gen = PIRGenerator()
        # pirs = pir_gen.generate_pirs()
        # return {"pirs": pirs}

        mock_pirs = {
            "result": """
            1. Cloud expansion into Southeast Asia (Azure, Kubernetes).
            2. Supply chain dependencies on GitHub/CI-CD pipelines.
            3. Regulatory exposure: GDPR + PCI-DSS.
            4. Increased phishing targeting executives (lookalike domains).
            """
        }
        return {"pirs": mock_pirs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# Stage 2: Threat Collection
# ================================
@app.post("/collect-threats", status_code=200)
def collect_threats():
    """
    Stage 2: Run collection agents (OTX, CVE, GitHub) 
    to build threat landscape filtered by PIR keywords.
    """
    try:
        otx_api_key = os.getenv("OTX_API_KEY")
        github_token = os.getenv("GITHUB_TOKEN")
        nvd_api_key = os.getenv("NVD_API_KEY")

        agents = [
            CVEAgent(api_key=nvd_api_key),
            GitHubSecurityAgent(github_token=github_token)
        ]
        if otx_api_key:
            agents.append(OTXAgent(api_key=otx_api_key))

        builder = ThreatLandscapeBuilder(agents)
        landscape = builder.build_threat_landscape()
        return {"landscape": landscape}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect-and-correlate", status_code=200)
def collect_and_correlate():
    """
    Run Stage 2 (collect threats) and immediately feed
    the full threat landscape into Stage 3 (correlate).
    """
    try:
        # Stage 2: Collect threats
        response = collect_threats()
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


# ================================
# Orchestrator: Run all stages
# ================================
@app.post("/run-all", status_code=200)
def run_all_stages():
    """
    Orchestrates the full pipeline:
    1. Generate PIRs
    2. Collect threats (CVE, GitHub, OTX)
    3. Correlate threats with org DNA
    """
    try:
        # Stage 1: PIRs
        pir_resp = generate_pirs()
        keywords = {"cloud", "kubernetes", "azure", "gdpr", "phishing", "supply chain"}  # mock extraction

        # Stage 2: Collection
        otx_api_key = os.getenv("OTX_API_KEY")
        github_token = os.getenv("GITHUB_TOKEN")
        nvd_api_key = os.getenv("NVD_API_KEY")

        agents = [
            CVEAgent(api_key=nvd_api_key, keywords=keywords),
            GitHubSecurityAgent(github_token=github_token, keywords=keywords)
        ]
        if otx_api_key:
            agents.append(OTXAgent(api_key=otx_api_key, keywords=keywords))

        builder = ThreatLandscapeBuilder(agents, pir_keywords=keywords)
        landscape = builder.build_threat_landscape()

        # Stage 3: Correlation
        agent = AutonomousCorrelationAgent()
        assessments = agent.correlate_threats(landscape)
        agent.close()

        return {
            "pirs": pir_resp,
            "landscape": landscape,
            "assessments": assessments,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================================
@app.get("/")
def read_root():
    return {"message": "Welcome to the cAIber Backend!"}
