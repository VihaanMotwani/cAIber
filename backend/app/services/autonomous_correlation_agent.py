"""
Autonomous Correlation Agent with Tools
The agent decides which tools to use for risk assessment
"""

import os
import json
from typing import Dict, Any, List
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
try:
    from .logger_config import logger
except ImportError:
    from logger_config import logger

load_dotenv()


class AutonomousCorrelationAgent:
    """
    Autonomous agent that uses tools to correlate threats with organizational context
    """
    
    def __init__(self):
        logger.info("Initializing Autonomous Correlation Agent")
        
        # Try Neo4j connection, fallback to mock if fails
        self.use_mock = False
        try:
            uri = os.getenv("NEO4J_URI")
            username = os.getenv("NEO4J_USERNAME")
            password = os.getenv("NEO4J_PASSWORD")
            
            # Test connection using official guide pattern
            with GraphDatabase.driver(uri, auth=(username, password)) as test_driver:
                test_driver.verify_connectivity()
                logger.info("Neo4j connectivity verified!")
            
            # Create persistent driver
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
        except Exception as e:
            logger.warning(f"Neo4j not available, using mock data: {e}")
            self.use_mock = True
            self.driver = None
        
        # LLM
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools the agent can use"""
        
        tools = [
            Tool(
                name="search_technologies",
                description="Search for specific technologies in our organization's knowledge graph. Input: technology name (e.g., 'AWS', 'Python')",
                func=self._search_technologies
            ),
            Tool(
                name="get_critical_assets",
                description="Get list of critical assets and systems in our organization",
                func=self._get_critical_assets
            ),
            Tool(
                name="check_geographic_presence",
                description="Check if we have presence in a specific geographic location. Input: location name",
                func=self._check_geographic_presence
            ),
            Tool(
                name="find_related_entities",
                description="Find entities related to a specific keyword. Input: keyword",
                func=self._find_related_entities
            ),
            Tool(
                name="get_business_initiatives",
                description="Get our current business initiatives and projects",
                func=self._get_business_initiatives
            )
        ]
        
        return tools
    
    def _search_technologies(self, technology: str) -> str:
        """Search for a technology in our stack"""
        if self.use_mock:
            # Mock data for common technologies
            mock_tech = {
                'kubernetes': 'Kubernetes (importance: 0.9), K8s-dashboard (importance: 0.7)',
                'aws': 'AWS-EC2 (importance: 0.95), AWS-S3 (importance: 0.8), AWS-Lambda (importance: 0.7)',
                'python': 'Python-3.9 (importance: 0.9), Django (importance: 0.8), Flask (importance: 0.6)',
                'docker': 'Docker (importance: 0.85), Docker-Registry (importance: 0.7)',
                'sql': 'MySQL (importance: 0.9), PostgreSQL (importance: 0.7)',
                'apache': 'Apache-Struts (importance: 0.6), Apache-Kafka (importance: 0.8)',
                'nodejs': 'Node.js-16 (importance: 0.7), Express.js (importance: 0.6)'
            }
            
            tech_lower = technology.lower()
            for key, value in mock_tech.items():
                if key in tech_lower or tech_lower in key:
                    return f"Found technologies: {value}"
            return f"No '{technology}' found in our tech stack"
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.type = 'technology' AND toLower(n.name) CONTAINS toLower($tech)
                RETURN n.name as name, n.importance as importance
                LIMIT 5
            """, tech=technology)
            
            techs = [f"{r['name']} (importance: {r['importance']})" for r in result]
            
            if techs:
                return f"Found technologies: {', '.join(techs)}"
            return f"No '{technology}' found in our tech stack"
    
    def _get_critical_assets(self, _: str = "") -> str:
        """Get critical organizational assets"""
        if self.use_mock:
            return "Critical assets: Customer-Database (database), Payment-API (application), Auth-Service (system), Mobile-Banking-App (application), Trading-Platform (system)"
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.importance > 0.7 OR n.type IN ['system', 'application', 'database']
                RETURN n.name as name, n.type as type
                ORDER BY n.importance DESC
                LIMIT 10
            """)
            
            assets = [f"{r['name']} ({r['type']})" for r in result]
            return f"Critical assets: {', '.join(assets)}" if assets else "No critical assets identified"
    
    def _check_geographic_presence(self, location: str) -> str:
        """Check geographic presence"""
        if self.use_mock:
            mock_locations = ['singapore', 'jakarta', 'manila', 'southeast asia', 'asia pacific']
            if any(loc in location.lower() for loc in mock_locations):
                return f"We have presence in: Singapore, Jakarta, Manila"
            return f"No presence found in '{location}'"
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.type = 'geography' AND toLower(n.name) CONTAINS toLower($loc)
                RETURN n.name as name
                LIMIT 5
            """, loc=location)
            
            locations = [r['name'] for r in result]
            
            if locations:
                return f"We have presence in: {', '.join(locations)}"
            return f"No presence found in '{location}'"
    
    def _find_related_entities(self, keyword: str) -> str:
        """Find any entities related to a keyword"""
        if self.use_mock:
            mock_entities = {
                'cloud': 'AWS-Migration-Project (project), Cloud-Infrastructure (system)',
                'banking': 'Digital-Banking-Initiative (business_initiative), Core-Banking-System (system)',
                'mobile': 'Mobile-Banking-App (application), Mobile-Payment-Service (system)',
                'api': 'Payment-API (application), REST-API-Gateway (system)'
            }
            keyword_lower = keyword.lower()
            for key, value in mock_entities.items():
                if key in keyword_lower:
                    return f"Related entities: {value}"
            return f"No entities found related to '{keyword}'"
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE toLower(n.name) CONTAINS toLower($keyword)
                   OR toLower(n.description) CONTAINS toLower($keyword)
                RETURN n.name as name, n.type as type
                LIMIT 10
            """, keyword=keyword)
            
            entities = [f"{r['name']} ({r['type']})" for r in result]
            
            if entities:
                return f"Related entities: {', '.join(entities)}"
            return f"No entities found related to '{keyword}'"
    
    def _get_business_initiatives(self, _: str = "") -> str:
        """Get business initiatives"""
        if self.use_mock:
            return "Business initiatives: Southeast-Asia-Expansion, Digital-Banking-Transformation, Cloud-Migration-2024, Mobile-First-Strategy"
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                WHERE n.type = 'business_initiative' OR n.type = 'project'
                RETURN n.name as name
                LIMIT 10
            """)
            
            initiatives = [r['name'] for r in result]
            return f"Business initiatives: {', '.join(initiatives)}" if initiatives else "No initiatives found"
    
    def _create_agent(self) -> AgentExecutor:
        """Create the autonomous agent"""
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a cybersecurity risk assessment expert. Your job is to analyze threats 
            against our organization's context and determine risk levels.
            
            Use the available tools to investigate:
            1. Whether the threat affects our technologies
            2. If it targets our geographic regions
            3. Which critical assets could be impacted
            4. How it relates to our business initiatives
            
            For each threat, provide a risk assessment with:
            - Risk Score (1-10)
            - Affected Assets
            - Business Impact
            - Reasoning
            
            Be thorough but efficient. Use tools to gather context, then make your assessment."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        # Create executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # Set to False in production
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def assess_threat(self, threat: Dict[str, Any]) -> Dict[str, Any]:
        """
        Autonomously assess a single threat using tools
        """
        threat_type = threat.get('type', 'unknown')
        threat_name = threat.get('name', 'Unknown')
        description = threat.get('description', '')
        
        # Build input for agent
        if threat_type == 'vulnerability':
            severity = threat.get('x_severity', 'UNKNOWN')
            cvss = threat.get('x_cvss_score', 'N/A')
            
            agent_input = f"""
            Analyze this vulnerability:
            Name: {threat_name}
            Description: {description[:300]}
            Severity: {severity}
            CVSS Score: {cvss}
            
            Use tools to determine if this affects our organization.
            Provide a JSON risk assessment.
            """
        else:
            agent_input = f"""
            Analyze this threat indicator:
            Name: {threat_name}
            Description: {description[:300]}
            
            Use tools to determine if this threat is relevant to us.
            Provide a JSON risk assessment.
            """
        
        try:
            # Run the agent
            result = self.agent.invoke({"input": agent_input})
            
            # Parse the output
            output = result.get('output', '')
            
            # Try to extract JSON from the output
            if '{' in output and '}' in output:
                json_start = output.index('{')
                json_end = output.rindex('}') + 1
                json_str = output[json_start:json_end]
                assessment = json.loads(json_str)
            else:
                # Fallback if no JSON found
                assessment = {
                    "risk_score": 5,
                    "affected_assets": ["Unknown"],
                    "business_impact": "Unable to determine",
                    "reasoning": output[:200]
                }
            
            assessment['threat_id'] = threat_name
            assessment['threat_type'] = threat_type
            
            return assessment
            
        except Exception as e:
            logger.error(f"Agent failed for {threat_name}: {e}")
            return {
                "threat_id": threat_name,
                "threat_type": threat_type,
                "risk_score": 0,
                "error": str(e)
            }
    
    def correlate_threats(self, threat_landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process multiple threats autonomously
        """
        logger.info("Starting autonomous threat correlation")
        
        risk_assessments = []
        
        # Process top vulnerabilities
        vulnerabilities = threat_landscape.get('vulnerabilities', [])[:5]  # Limit for demo
        for vuln in vulnerabilities:
            logger.info(f"Assessing vulnerability: {vuln.get('name')}")
            assessment = self.assess_threat(vuln)
            if assessment.get('risk_score', 0) > 0:
                risk_assessments.append(assessment)
        
        # Process top indicators
        indicators = threat_landscape.get('indicators', [])[:5]  # Limit for demo
        for indicator in indicators:
            logger.info(f"Assessing indicator: {indicator.get('name')}")
            assessment = self.assess_threat(indicator)
            if assessment.get('risk_score', 0) > 0:
                risk_assessments.append(assessment)
        
        # Sort by risk score
        risk_assessments.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        
        logger.info(f"Completed autonomous assessment: {len(risk_assessments)} risks identified")
        return risk_assessments
    
    def close(self):
        """Clean up resources"""
        if self.driver and not self.use_mock:
            self.driver.close()


def test_autonomous_agent():
    """Test the autonomous agent"""
    
    # Sample threat
    sample_threat = {
        'type': 'vulnerability',
        'name': 'CVE-2024-1234',
        'description': 'Remote code execution vulnerability in Kubernetes API server allows attackers to execute arbitrary code',
        'x_severity': 'CRITICAL',
        'x_cvss_score': 9.8
    }
    
    agent = AutonomousCorrelationAgent()
    try:
        print("\n🤖 Autonomous Agent Analyzing Threat...")
        print("=" * 60)
        
        assessment = agent.assess_threat(sample_threat)
        
        print("\n📊 Risk Assessment:")
        print(json.dumps(assessment, indent=2))
        
    finally:
        agent.close()


if __name__ == "__main__":
    test_autonomous_agent()