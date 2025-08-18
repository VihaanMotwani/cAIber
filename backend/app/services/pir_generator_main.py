"""
pir_generator.py
cAIber Stage 2 - Priority Intelligence Requirements Generation
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
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
        
        # Initialize Neo4j graph connection
        try:
            self.graph = Neo4jGraph(
                url=os.getenv("NEO4J_URI"),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "password")
            )
            print("✅ Connected to Neo4j knowledge graph")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Neo4j: {e}")
        
        # Create PIR generation chain
        self.chain = GraphCypherQAChain.from_llm(
            llm=self.llm,
            graph=self.graph,
            verbose=True,
            top_k=20,
            allow_dangerous_requests=True,  
        )
        
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
            # Validate graph first
            if not self.validate_graph_data():
                return {"error": "Knowledge graph validation failed"}
            
            print("\n🧠 Analyzing organizational context and generating PIRs...")
            result = self.chain.invoke(self.PIR_GENERATION_PROMPT)
            
            print("\n✅ PIR Generation Successful!")
            return {
                "success": True,
                "pirs": result,
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ PIR Generation Failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": __import__('datetime').datetime.now().isoformat()
            }
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of organizational context for PIR generation."""
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