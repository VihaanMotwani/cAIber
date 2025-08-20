"""
Simple direct pipeline - minimal changes to connect stages
"""

import os
import time
from dotenv import load_dotenv
load_dotenv()

from .organisational_dna_builder import OrganizationalDNAEngine
from .pir_generator_main import PIRGenerator
from .collection_agent import OTXAgent, CVEAgent, GitHubSecurityAgent, ThreatLandscapeBuilder
from .correlation_agent import CorrelationAgent
from .threat_modeling import generate_threat_model
from langchain_openai import ChatOpenAI
from .logger_config import logger

llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

def extract_keywords_from_pirs(pirs_text):
    """Extract keywords from PIRs using LLM"""
    if not pirs_text:
        return {"threat", "vulnerability", "malware"}
    
    prompt = f"""
    From the following threat intelligence requirements, extract a list of no more than 10 critical, specific, and searchable keywords.
    Focus on technologies, threat actor types, regions, and targeted assets.
    Return the keywords as a single, comma-separated string.

    Requirements:
    "{pirs_text}"

    Keywords:
    """
    response = llm.invoke(prompt)
    keywords_str = response.content
    keywords = {kw.strip().lower() for kw in keywords_str.split(',')}
    print(f"Extracted keywords: {keywords}")
    return keywords

def run_pipeline(skip_stage1=False, autonomous_correlation=False):
    """Run complete pipeline with direct data passing"""
    start_time = time.time()
    logger.info("Starting cAIber pipeline execution")
    
    try:
        if not skip_stage1:
            # Stage 1: Build Organizational DNA
            logger.info("STAGE 1: Building Organizational DNA")
            stage1_start = time.time()
            # Pass Neo4j credentials from environment
            dna_engine = OrganizationalDNAEngine(
                neo4j_uri=os.getenv("NEO4J_URI"),
                neo4j_user=os.getenv("NEO4J_USERNAME"), 
                neo4j_password=os.getenv("NEO4J_PASSWORD")
            )
            dna_engine.build_organizational_dna("./documents", clear_existing=True)
            logger.info(f"DNA building completed in {time.time() - stage1_start:.2f}s")
        else:
            logger.info("Skipping DNA building (using existing)")
        
        # Generate PIRs from knowledge graph
        logger.info("Generating PIRs")
        pir_gen = PIRGenerator()
        pirs_result = pir_gen.generate_pirs()
        pirs_text = pirs_result.get("pirs", {}).get("result", "")
        logger.info("PIR generation complete")
        
        # Extract keywords from PIRs
        keywords = extract_keywords_from_pirs(pirs_text)
        logger.debug(f"Keywords extracted: {keywords}")
        
        # Stage 2: Collect Threats using keywords
        logger.info("STAGE 2: Collecting threats")
        stage2_start = time.time()
        agents = []
        
        # Add agents with keywords passed directly
        otx_key = os.getenv('OTX_API_KEY')
        if otx_key:
            agents.append(OTXAgent(api_key=otx_key, keywords=keywords))
            logger.debug("OTX Agent added")
        
        agents.append(CVEAgent(keywords=keywords))
        logger.debug("CVE Agent added")
        
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            agents.append(GitHubSecurityAgent(github_token=github_token, keywords=keywords))
            logger.debug("GitHub Agent added")
        
        # Build threat landscape
        builder = ThreatLandscapeBuilder(collection_agents=agents)
        threat_landscape = builder.build_threat_landscape()
        
        logger.info(f"Stage 2 completed in {time.time() - stage2_start:.2f}s")
        logger.info(f"Threats collected: {threat_landscape['total_items']} (CVEs: {len(threat_landscape.get('vulnerabilities', []))}, Indicators: {len(threat_landscape.get('indicators', []))})")
        
        # Stage 3: Risk Correlation
        logger.info(f"STAGE 3: Risk Correlation (Mode: {'Autonomous' if autonomous_correlation else 'Standard'})")
        stage3_start = time.time()
        
        if autonomous_correlation:
            # Use autonomous agent with tools
            from .autonomous_correlation_agent import AutonomousCorrelationAgent
            correlator = AutonomousCorrelationAgent()
            try:
                risk_assessments = correlator.correlate_threats(threat_landscape)
                # Generate summary
                from .correlation_agent import CorrelationAgent
                temp_agent = CorrelationAgent()
                executive_summary = temp_agent.generate_executive_summary(risk_assessments)
                temp_agent.close()
            finally:
                correlator.close()
        else:
            # Use standard correlation
            correlator = CorrelationAgent()
            try:
                risk_assessments = correlator.correlate_threats(threat_landscape)
                executive_summary = correlator.generate_executive_summary(risk_assessments)
            finally:
                correlator.close()
        
        logger.info(f"Stage 3 completed in {time.time() - stage3_start:.2f}s")
        logger.info(f"Generated {len(risk_assessments)} risk assessments")
        
        total_time = time.time() - start_time
        logger.info(f"Pipeline completed successfully in {total_time:.2f}s")
        
        intelligence_data =  {
            "pirs": pirs_text,
            "keywords": keywords,
            "threat_landscape": threat_landscape,
            "risk_assessments": risk_assessments,
            "executive_summary": executive_summary
        }

        threat_model = generate_threat_model(intelligence_data)

        return {
            "pirs": pirs_text,
            "keywords": keywords,
            "threat_landscape": threat_landscape,
            "risk_assessments": risk_assessments,
            "executive_summary": executive_summary,
            "threat_model": threat_model
        }
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    results = run_pipeline()
    print("\n✅ Pipeline complete!")