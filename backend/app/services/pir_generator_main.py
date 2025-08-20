"""
pir_generator.py
cAIber Stage 2 - Priority Intelligence Requirements Generation
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_neo4j import Neo4jGraph
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()

class PIRGenerator:
    """Generates Priority Intelligence Requirements from organizational knowledge graph."""
    
    def __init__(self):
        print("🧠 Initializing PIR Generator...")
        
        # Check OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not found!")
        
        # Initialize LLM
        self.llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o")
        
        # Initialize Neo4j connection with fallback (using direct driver like autonomous agent)
        self.use_mock = False
        try:
            # First test direct connection (like autonomous agent)
            uri = os.getenv("NEO4J_URI")
            username = os.getenv("NEO4J_USERNAME", "neo4j") 
            password = os.getenv("NEO4J_PASSWORD")
            
            if not password:
                raise ValueError("NEO4J_PASSWORD not set in environment")
            
            print(f"🔍 Testing Neo4j connection to {uri}")
            
            # EXACT pattern from official guide - Step 2
            with GraphDatabase.driver(uri, auth=(username, password)) as driver:
                # Use verify_connectivity() as recommended in guide
                driver.verify_connectivity()
                print("✅ Neo4j connectivity verified!")
                
                # Test a basic query using execute_query (Step 4 pattern)
                records, summary, keys = driver.execute_query("""
                    RETURN 'cAIber connection test' as message, datetime() as timestamp
                    """,
                    database_="neo4j",
                )
                
                if records:
                    print(f"✅ Query successful: {records[0].data()}")
                    print(f"✅ Query executed in {summary.result_available_after} ms")
                
            # Keep a separate driver for the PIR generator
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            
            # Now create the LangChain graph wrapper
            self.graph = Neo4jGraph(
                url=uri,
                username=username,
                password=password
            )
            print("✅ LangChain Neo4j graph wrapper created")
            
            # Create PIR generation chain
            self.chain = GraphCypherQAChain.from_llm(
                llm=self.llm,
                graph=self.graph,
                verbose=True,
                top_k=20,
                allow_dangerous_requests=True,  
            )
            print("✅ PIR generation chain created")
            
        except Exception as e:
            print(f"⚠️  Neo4j connection failed: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Check for specific error types
            if "authentication" in str(e).lower():
                print("   💡 Check your Neo4j username/password in .env")
            elif "routing information" in str(e).lower():
                print("   💡 Your AuraDB instance might be paused - check Neo4j Console")
            elif "connection refused" in str(e).lower():
                print("   💡 Check your Neo4j URI and network connection")
                
            print("   📋 Falling back to mock data")
            self.use_mock = True
            self.graph = None
            self.chain = None
            self.driver = None
        
        # Enhanced PIR generation prompt
        self.PIR_GENERATION_PROMPT = """
        You are a world-class threat intelligence analyst working for a system named cAIber.
        Your task is to analyze the complete knowledge graph of an organization and
        proactively generate Priority Intelligence Requirements (PIRs).

        Based on all the information available in the graph, identify the top 3-5 strategic
        business initiatives, key technologies, people, or assets.

        For each, formulate a concise, actionable intelligence requirement that would help
        the security team mitigate potential threats. Frame these as suggestions.

        Example: "Analysis of business plans indicates expansion into Southeast Asia.
        Suggest prioritizing intelligence on threat actors targeting financial services in that region,
        particularly those exploiting supply chain vulnerabilities."

        Focus on:
        1. Business initiatives and their associated risks
        2. Critical technologies and their vulnerabilities  
        3. Geographic expansion and regional threats
        4. Compliance requirements and regulatory threats
        5. Past incidents and similar attack patterns

        Make each PIR specific, actionable, and tied to the organization's actual context.
        Prioritize PIRs that would have the highest impact on preventing breaches.

        Now, analyze the provided graph data and generate the PIRs.
        """
    
    def validate_graph_data(self) -> bool:
        """Validate that the knowledge graph contains data for PIR generation."""
        if self.use_mock:
            return True
            
        print("🔍 Validating knowledge graph data...")
        
        try:
            # Check total entities
            result = self.graph.query("MATCH (n:Entity) RETURN count(n) as total_entities")
            total = result[0]['total_entities'] if result else 0
            print(f"📊 Total entities in graph: {total}")
            
            if total == 0:
                print("❌ No entities found! Run Stage 1 first to build the knowledge graph.")
                return False
            
            # Show entity breakdown by type
            result = self.graph.query("""
                MATCH (n:Entity) 
                RETURN n.type as type, count(*) as count 
                ORDER BY count DESC
            """)
            
            print("📈 Entity breakdown:")
            entity_types = {}
            for record in result:
                entity_type = record['type']
                count = record['count']
                entity_types[entity_type] = count
                print(f"   • {entity_type}: {count}")
            
            # Check for key entity types needed for good PIRs
            required_types = ['business_initiative', 'technology', 'geography']
            missing_types = [t for t in required_types if t not in entity_types]
            
            if missing_types:
                print(f"⚠️  Missing key entity types: {missing_types}")
                print("   PIR generation may be limited. Consider adding more diverse documents.")
            
            # Show sample entities
            result = self.graph.query("""
                MATCH (n:Entity) 
                RETURN n.name, n.type, n.source_document, n.confidence
                ORDER BY n.confidence DESC
                LIMIT 8
            """)
            
            print("🎯 Top entities by confidence:")
            for record in result:
                print(f"   • {record['n.name']} ({record['n.type']}) - {record['n.confidence']:.2f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Graph validation failed: {e}")
            return False
    
    def generate_pirs(self) -> Dict[str, Any]:
        """Generate Priority Intelligence Requirements from the knowledge graph."""
        print("\n🎯 Generating Priority Intelligence Requirements...")
        print("=" * 60)
        
        try:
            if self.use_mock:
                print("📋 Using mock PIRs (Neo4j unavailable)")
                return self.get_mock_pirs()
            
            # Validate graph first
            if not self.validate_graph_data():
                return {"error": "Knowledge graph validation failed"}
            
            print("\n🧠 Analyzing organizational context and generating PIRs...")
            context = self.get_context_summary()
            result = self.llm.invoke(f"{self.PIR_GENERATION_PROMPT}\n\nContext:\n{context}")

            pir_text = result.content if hasattr(result, "content") else str(result)

            # Extract keywords via LLM
            keywords = self.extract_keywords(pir_text)
            
            print("\n✅ PIR Generation Successful!")
            
            return {
                "success": True,
                "pirs": pir_text,
                "keywords": keywords,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ PIR Generation Failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
    
    def get_mock_pirs(self) -> Dict[str, Any]:
        """Return mock PIRs when Neo4j is not available."""
        mock_pirs = """
Priority Intelligence Requirements (PIRs) - TechCorp Inc.

PIR-001: Cloud Infrastructure Threats
- Monitor for vulnerabilities in AWS, Azure, and multi-cloud environments
- Track containerization threats targeting Kubernetes and Docker deployments
- Assess supply chain attacks affecting cloud service providers

PIR-002: Critical Asset Protection
- Intelligence on threats targeting customer databases and payment systems
- Monitor for credential stuffing and account takeover campaigns
- Track insider threats and privileged access abuse

PIR-003: Compliance and Regulatory Threats
- GDPR compliance threats and data privacy violations
- PCI-DSS related attack vectors targeting payment processing
- Monitor for regulatory changes affecting cybersecurity requirements

PIR-004: Emerging Threat Landscape
- Advanced persistent threat (APT) groups targeting financial services
- Ransomware campaigns using double extortion tactics
- Zero-day vulnerabilities in enterprise software stack

PIR-005: Geographic and Sector-Specific Intelligence
- Cyber threats originating from high-risk geographic regions
- Industry-specific attack patterns in fintech and e-commerce
- Nation-state sponsored activities targeting critical infrastructure
        """
        
        keywords = {
            "technologies": ["aws", "azure", "kubernetes", "docker", "postgresql"],
            "threats": ["ransomware", "apt", "supply-chain", "insider-threat"],
            "geographies": ["europe", "us-east", "asia-pacific"],
            "business_initiatives": ["fintech", "e-commerce", "cloud-migration"]
        }
        
        return {
            "success": True,
            "pirs": mock_pirs,
            "keywords": keywords,
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "mock_data": True
        }
    
    def extract_keywords(self, pir_text: str) -> dict:
        """
        Use LLM to extract clean keywords from PIR text.
        Returns a JSON with categories like technologies, geographies, threats, etc.
        """
        prompt = f"""
        Extract the most important keywords from the following Priority Intelligence Requirements (PIRs).
        Categorize them under: technologies, geographies, business_initiatives, and threat_actors.

        PIR text:
        {pir_text}

        Return the result strictly in JSON format like this:
        {{
            "technologies": ["AWS", "Azure", "Kubernetes"],
            "geographies": ["Southeast Asia"],
            "business_initiatives": ["Cloud Expansion"],
            "threat_actors": ["APT29"]
        }}
        """

        response = self.llm.invoke(prompt)

        try:
            # Sometimes LLM wraps JSON in text — extract safely
            import json, re
            match = re.search(r"\{.*\}", response.content, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass

        return {"technologies": [], "geographies": [], "business_initiatives": [], "threat_actors": []}

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of organizational context for PIR generation."""
        if self.use_mock:
            return {
                "business_initiatives": [
                    {"n.name": "Digital Transformation", "n.importance": 0.9, "n.source_document": "mock"},
                    {"n.name": "Cloud Migration", "n.importance": 0.8, "n.source_document": "mock"}
                ],
                "technologies": [
                    {"n.name": "AWS", "n.confidence": 0.9, "n.source_document": "mock"},
                    {"n.name": "Kubernetes", "n.confidence": 0.8, "n.source_document": "mock"}
                ],
                "geographies": [
                    {"n.name": "United States", "n.confidence": 0.9, "n.source_document": "mock"},
                    {"n.name": "Europe", "n.confidence": 0.7, "n.source_document": "mock"}
                ],
                "past_threats": [
                    {"n.name": "Ransomware", "n.confidence": 0.8, "n.source_document": "mock"}
                ]
            }
            
        try:
            # Get business initiatives
            business_initiatives = self.graph.query("""
                MATCH (n:Entity {type: 'business_initiative'})
                RETURN n.name, n.importance, n.source_document
                ORDER BY n.importance DESC
                LIMIT 5
            """)
            
            # Get critical technologies
            technologies = self.graph.query("""
                MATCH (n:Entity {type: 'technology'})
                RETURN n.name, n.confidence, n.source_document
                ORDER BY n.confidence DESC
                LIMIT 10
            """)
            
            # Get geographic presence
            geographies = self.graph.query("""
                MATCH (n:Entity {type: 'geography'})
                RETURN n.name, n.confidence, n.source_document
                ORDER BY n.confidence DESC
                LIMIT 5
            """)
            
            # Get past threats
            threats = self.graph.query("""
                MATCH (n:Entity {type: 'threat_actor'})
                RETURN n.name, n.confidence, n.source_document
                ORDER BY n.confidence DESC
                LIMIT 5
            """)
            
            return {
                "business_initiatives": [dict(record) for record in business_initiatives],
                "technologies": [dict(record) for record in technologies],
                "geographies": [dict(record) for record in geographies],
                "past_threats": [dict(record) for record in threats]
            }
            
        except Exception as e:
            print(f"Error getting context summary: {e}")
            return {}
    
    def close(self):
        """Close Neo4j driver connection if it exists."""
        if hasattr(self, 'driver') and self.driver:
            self.driver.close()
            print("🔌 Neo4j driver connection closed")


def main():
    """Main execution for PIR generation testing."""
    print("🎯 cAIber Stage 2 - PIR Generation")
    print("=" * 50)
    
    # Environment check
    print("🔧 Checking environment...")
    required_env = ["OPENAI_API_KEY"]
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print(f"❌ Missing environment variables: {missing_env}")
        print("Set them with:")
        for env in missing_env:
            print(f"   export {env}='your-{env.lower().replace('_', '-')}'")
        return
    
    print("✅ Environment check passed")
    
    # Initialize PIR Generator
    try:
        pir_gen = PIRGenerator()
    except Exception as e:
        print(f"❌ Failed to initialize PIR Generator: {e}")
        return
    
    # Generate PIRs
    try:
        result = pir_gen.generate_pirs()
        
        print("\n" + "=" * 60)
        print("🎉 PIR GENERATION RESULTS")
        print("=" * 60)
        
        if result["success"]:
            # Display the PIRs
            pirs_content = result["pirs"]
            if hasattr(pirs_content, 'content'):
                print(pirs_content.content)
            elif isinstance(pirs_content, dict):
                for key, value in pirs_content.items():
                    print(f"{key}: {value}")
            else:
                print(pirs_content)
                
            # Show context summary
            print("\n" + "=" * 60)
            print("📊 ORGANIZATIONAL CONTEXT SUMMARY")
            print("=" * 60)
            
            context = pir_gen.get_context_summary()
            for section, items in context.items():
                if items:
                    print(f"\n{section.replace('_', ' ').title()}:")
                    for item in items:
                        print(f"   • {item.get('n.name', 'Unknown')}")
                        
        else:
            print(f"❌ PIR Generation Failed: {result['error']}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()