"""
Stage 3: Correlation Agent
Correlates threats with organizational context to produce risk assessments
"""

import os
from typing import Dict, Any, List
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from .logger_config import logger

load_dotenv()

llm = ChatOpenAI(temperature=0, model_name="gpt-4o")


class CorrelationAgent:
    """
    Multi-context correlation agent that accesses:
    - Organizational DNA (Neo4j knowledge graph)
    - Threat landscape (from Stage 2)
    - Uses LLM to correlate and assess risks
    """
    
    def __init__(self):
        logger.info("Initializing Correlation Agent")
        
        # Connect to Neo4j for organizational context
        self.neo4j_uri = os.getenv("NEO4J_URI")
        self.neo4j_user = os.getenv("NEO4J_USERNAME")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_user, self.neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.debug("Connected to Neo4j for organizational context")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def correlate_threats(self, threat_landscape: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main correlation function - analyzes each threat against organizational context
        
        Args:
            threat_landscape: Output from Stage 2 ThreatLandscapeBuilder
            
        Returns:
            List of risk assessments with business context
        """
        logger.info("Starting threat correlation analysis")
        
        risk_assessments = []
        
        # Get organizational context
        org_context = self._get_organizational_context()
        
        # Process vulnerabilities
        vulnerabilities = threat_landscape.get('vulnerabilities', [])
        logger.info(f"Correlating {len(vulnerabilities)} vulnerabilities")
        
        for vuln in vulnerabilities[:10]:  # Limit to top 10 for performance
            risk = self._assess_vulnerability_risk(vuln, org_context)
            if risk:
                risk_assessments.append(risk)
        
        # Process indicators
        indicators = threat_landscape.get('indicators', [])
        logger.info(f"Correlating {len(indicators)} threat indicators")
        
        for indicator in indicators[:10]:  # Limit to top 10
            risk = self._assess_indicator_risk(indicator, org_context)
            if risk:
                risk_assessments.append(risk)
        
        # Sort by risk score
        risk_assessments.sort(key=lambda x: x['risk_score'], reverse=True)
        
        logger.info(f"Generated {len(risk_assessments)} risk assessments")
        return risk_assessments
    
    def _get_organizational_context(self) -> Dict[str, Any]:
        """Query Neo4j to get relevant organizational context"""
        context = {
            'technologies': [],
            'business_initiatives': [],
            'geographic_presence': [],
            'critical_assets': []
        }
        
        with self.driver.session() as session:
            # Get technologies
            result = session.run("""
                MATCH (n:Entity {type: 'technology'})
                RETURN n.name as name, n.importance as importance
                ORDER BY n.importance DESC
                LIMIT 20
            """)
            context['technologies'] = [dict(record) for record in result]
            
            # Get business initiatives
            result = session.run("""
                MATCH (n:Entity {type: 'business_initiative'})
                RETURN n.name as name, n.importance as importance
                LIMIT 10
            """)
            context['business_initiatives'] = [dict(record) for record in result]
            
            # Get geographic presence
            result = session.run("""
                MATCH (n:Entity {type: 'geography'})
                RETURN n.name as name
                LIMIT 10
            """)
            context['geographic_presence'] = [record['name'] for record in result]
            
        logger.debug(f"Loaded organizational context: {len(context['technologies'])} technologies, {len(context['business_initiatives'])} initiatives")
        return context
    
    def _assess_vulnerability_risk(self, vuln: Dict[str, Any], org_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of a specific vulnerability against organizational context"""
        
        vuln_name = vuln.get('name', 'Unknown')
        vuln_description = vuln.get('description', '')
        severity = vuln.get('x_severity', 'UNKNOWN')
        cvss_score = vuln.get('x_cvss_score', 0)
        
        # Build context for LLM
        tech_list = ', '.join([t['name'] for t in org_context['technologies'][:5]])
        
        prompt = f"""
        Analyze this vulnerability against our organizational context and provide a risk assessment.
        
        Vulnerability: {vuln_name}
        Description: {vuln_description[:200]}
        Severity: {severity}
        CVSS Score: {cvss_score}
        
        Our Organization Uses:
        Technologies: {tech_list}
        
        Provide a JSON response with:
        1. "affected_assets": List of our technologies/systems that could be affected
        2. "business_impact": Brief description of potential business impact
        3. "risk_score": Number 1-10 based on relevance to our organization
        4. "reasoning": One sentence explanation
        
        If this vulnerability is not relevant to our technologies, return risk_score of 0.
        
        Respond with valid JSON only.
        """
        
        try:
            response = llm.invoke(prompt)
            import json
            assessment = json.loads(response.content)
            
            # Add vulnerability details
            assessment['threat_type'] = 'vulnerability'
            assessment['threat_id'] = vuln_name
            assessment['original_severity'] = severity
            
            return assessment
            
        except Exception as e:
            logger.debug(f"Failed to assess {vuln_name}: {e}")
            return None
    
    def _assess_indicator_risk(self, indicator: Dict[str, Any], org_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of a threat indicator against organizational context"""
        
        indicator_name = indicator.get('name', 'Unknown')
        pattern = indicator.get('pattern', '')
        description = indicator.get('description', '')
        
        # Build context
        tech_list = ', '.join([t['name'] for t in org_context['technologies'][:5]])
        geo_list = ', '.join(org_context['geographic_presence'][:3])
        
        prompt = f"""
        Analyze this threat indicator against our organizational context.
        
        Threat: {indicator_name}
        Pattern: {pattern[:100]}
        Description: {description[:200]}
        
        Our Organization:
        Technologies: {tech_list}
        Locations: {geo_list}
        
        Provide a JSON response with:
        1. "affected_assets": List of our technologies/systems that could be targeted
        2. "business_impact": Brief description of potential impact
        3. "risk_score": Number 1-10 based on relevance
        4. "reasoning": One sentence explanation
        
        If not relevant, return risk_score of 0.
        
        Respond with valid JSON only.
        """
        
        try:
            response = llm.invoke(prompt)
            import json
            assessment = json.loads(response.content)
            
            # Add indicator details
            assessment['threat_type'] = 'indicator'
            assessment['threat_id'] = indicator_name
            
            return assessment
            
        except Exception as e:
            logger.debug(f"Failed to assess indicator {indicator_name}: {e}")
            return None
    
    def generate_executive_summary(self, risk_assessments: List[Dict[str, Any]]) -> str:
        """Generate an executive summary of the risk assessments"""
        
        if not risk_assessments:
            return "No significant risks identified based on current threat landscape."
        
        high_risks = [r for r in risk_assessments if r.get('risk_score', 0) >= 7]
        medium_risks = [r for r in risk_assessments if 4 <= r.get('risk_score', 0) < 7]
        
        summary = f"""
        RISK ASSESSMENT SUMMARY
        =======================
        Total Threats Analyzed: {len(risk_assessments)}
        High Risk: {len(high_risks)}
        Medium Risk: {len(medium_risks)}
        
        TOP RISKS:
        """
        
        for risk in risk_assessments[:3]:
            summary += f"\n• {risk['threat_id']} (Score: {risk['risk_score']}/10)"
            summary += f"\n  Impact: {risk.get('business_impact', 'Unknown')}"
            summary += f"\n  Affected: {', '.join(risk.get('affected_assets', []))}\n"
        
        return summary
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()


def main():
    """Test the correlation agent"""
    
    # Sample threat landscape for testing
    sample_threats = {
        'vulnerabilities': [
            {
                'name': 'CVE-2024-1234',
                'description': 'Remote code execution in Apache Struts',
                'x_severity': 'CRITICAL',
                'x_cvss_score': 9.8
            },
            {
                'name': 'CVE-2024-5678',
                'description': 'SQL injection in MySQL database',
                'x_severity': 'HIGH',
                'x_cvss_score': 7.5
            }
        ],
        'indicators': [
            {
                'name': 'APT Group Targeting Cloud Infrastructure',
                'pattern': '[ipv4-addr:value = "192.168.1.1"]',
                'description': 'Advanced persistent threat targeting AWS environments'
            }
        ]
    }
    
    agent = CorrelationAgent()
    try:
        assessments = agent.correlate_threats(sample_threats)
        print(agent.generate_executive_summary(assessments))
    finally:
        agent.close()


if __name__ == "__main__":
    main()