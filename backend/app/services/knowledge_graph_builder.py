"""
knowledge_graph_builder.py
Builds Neo4j knowledge graph from extracted entities for cAIber Stage 1
"""

import os
from typing import List, Dict, Any
from neo4j import GraphDatabase


class KnowledgeGraphBuilder:
    """Builds and manages the Neo4j knowledge graph."""
    
    def __init__(self, 
                 neo4j_uri: str = None, 
                 neo4j_user: str = None, 
                 neo4j_password: str = None):
        
        # Use environment variables or defaults
        self.uri = neo4j_uri or os.getenv("NEO4J_URI", "neo4j+ssc://cc633ab6.databases.neo4j.io")
        self.user = neo4j_user or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = neo4j_password or os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✅ Neo4j connection established")
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            print(f"   URI: {self.uri}")
            print(f"   User: {self.user}")
            raise e
    
    def build_knowledge_graph(self, entities: List[Dict[str, Any]], clear_existing: bool = False, relationships: List[Dict[str, Any]] = None) -> None:
        """Build the Neo4j knowledge graph from extracted entities and relationships."""
        relationships = relationships or []
        print(f"🏗️  Building knowledge graph with {len(entities)} entities and {len(relationships)} LLM relationships...")
        
        with self.driver.session() as session:
            if clear_existing:
                print("🗑️  Clearing existing graph data...")
                session.run("MATCH (n) DETACH DELETE n")
            
            # Create entity nodes
            print("📝 Creating entity nodes...")
            for i, entity in enumerate(entities):
                if i % 50 == 0:  # Progress indicator
                    print(f"   Created {i}/{len(entities)} entities...")
                
                session.run("""
                    MERGE (e:Entity {id: $id})
                    SET e.name = $name,
                        e.type = $type,
                        e.source_document = $source_document,
                        e.document_type = $document_type,
                        e.confidence = $confidence,
                        e.importance = $importance
                """, 
                id=entity['id'],
                name=entity['name'],
                type=entity['type'],
                source_document=entity['source_document'],
                document_type=entity['document_type'],
                confidence=entity['confidence'],
                importance=entity.get('importance', 5)
                )
            
            print(f"✅ Created {len(entities)} entity nodes")
            
            # Skip broad document-based relationships to reduce noise
            # Instead, focus only on high-value semantic relationships
            doc_rels = 0
            print("🔗 Skipping document-based relationships to reduce graph noise")
            
            # Create semantic relationships
            print("🧠 Creating semantic relationships...")
            
            # Business initiatives use technologies
            result = session.run("""
                MATCH (bus:Entity), (tech:Entity)
                WHERE bus.type = 'business_initiative' AND tech.type = 'technology'
                AND bus.source_document = tech.source_document
                MERGE (bus)-[:USES_TECHNOLOGY]->(tech)
                RETURN count(*) as relationships_created
            """)
            bus_tech_rels = result.single()['relationships_created']
            
            # Threat actors exploit vulnerabilities
            result = session.run("""
                MATCH (threat:Entity), (vuln:Entity)
                WHERE threat.type = 'threat_actor' AND vuln.type = 'vulnerability'
                AND threat.source_document = vuln.source_document
                MERGE (threat)-[:EXPLOITS]->(vuln)
                RETURN count(*) as relationships_created
            """)
            threat_vuln_rels = result.single()['relationships_created']
            
            # Business initiatives target geographies
            result = session.run("""
                MATCH (bus:Entity), (geo:Entity)
                WHERE bus.type = 'business_initiative' AND geo.type = 'geography'
                AND bus.source_document = geo.source_document
                MERGE (bus)-[:TARGETS_GEOGRAPHY]->(geo)
                RETURN count(*) as relationships_created
            """)
            bus_geo_rels = result.single()['relationships_created']
            
            # Organizations operate in geographies
            result = session.run("""
                MATCH (org:Entity), (geo:Entity)
                WHERE org.type = 'organization' AND geo.type = 'geography'
                AND org.source_document = geo.source_document
                MERGE (org)-[:OPERATES_IN]->(geo)
                RETURN count(*) as relationships_created
            """)
            org_geo_rels = result.single()['relationships_created']
            
            # Organizations use technologies (but limit to high confidence entities)
            result = session.run("""
                MATCH (org:Entity), (tech:Entity)
                WHERE org.type = 'organization' AND tech.type = 'technology'
                AND org.source_document = tech.source_document
                AND org.confidence > 0.7 AND tech.confidence > 0.7
                MERGE (org)-[:USES]->(tech)
                RETURN count(*) as relationships_created
            """)
            org_tech_rels = result.single()['relationships_created']
            
            total_semantic = bus_tech_rels + threat_vuln_rels + bus_geo_rels + org_geo_rels + org_tech_rels
            print(f"✅ Created {total_semantic} semantic relationships")
            print(f"   • Business → Technology: {bus_tech_rels}")
            print(f"   • Threat → Vulnerability: {threat_vuln_rels}")
            print(f"   • Business → Geography: {bus_geo_rels}")
            print(f"   • Organization → Geography: {org_geo_rels}")
            print(f"   • Organization → Technology: {org_tech_rels}")
            
            # Create LLM-discovered relationships
            if relationships:
                print("🤖 Creating LLM-discovered relationships...")
                llm_rels_created = 0
                
                for rel in relationships:
                    try:
                        session.run("""
                            MATCH (source:Entity {id: $source_id})
                            MATCH (target:Entity {id: $target_id})
                            MERGE (source)-[r:%s]->(target)
                            SET r.confidence = $confidence,
                                r.evidence = $evidence,
                                r.source_document = $source_document,
                                r.source_type = 'llm'
                            RETURN r
                        """ % rel['relationship_type'],
                            source_id=rel['source'],
                            target_id=rel['target'],
                            confidence=rel['confidence'],
                            evidence=rel.get('evidence', ''),
                            source_document=rel.get('source_document', '')
                        )
                        llm_rels_created += 1
                    except Exception as e:
                        print(f"⚠️  Failed to create relationship {rel['relationship_type']}: {e}")
                
                print(f"✅ Created {llm_rels_created} LLM-discovered relationships")
                
                # Show LLM relationship breakdown
                llm_rel_types = {}
                for rel in relationships:
                    rel_type = rel['relationship_type']
                    llm_rel_types[rel_type] = llm_rel_types.get(rel_type, 0) + 1
                
                print("🤖 LLM relationship types:")
                for rel_type, count in sorted(llm_rel_types.items()):
                    print(f"   • {rel_type}: {count}")
    
    def get_graph_summary(self) -> Dict[str, Any]:
        """Get a summary of the knowledge graph."""
        with self.driver.session() as session:
            # Entity counts by type
            result = session.run("""
                MATCH (n:Entity)
                RETURN n.type as type, count(*) as count
                ORDER BY count DESC
            """)
            
            entity_counts = {}
            for record in result:
                entity_counts[record['type']] = record['count']
            
            # Relationship counts
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(*) as count
                ORDER BY count DESC
            """)
            
            relationship_counts = {}
            for record in result:
                relationship_counts[record['relationship_type']] = record['count']
            
            # Total counts
            result = session.run("MATCH (n) RETURN count(n) as total_nodes")
            total_nodes = result.single()['total_nodes']
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
            total_relationships = result.single()['total_relationships']
            
            return {
                'total_nodes': total_nodes,
                'total_relationships': total_relationships,
                'entity_counts': entity_counts,
                'relationship_counts': relationship_counts
            }
    
    def get_sample_entities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sample entities for validation."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity)
                RETURN n.id AS id, 
                    n.name AS name, 
                    n.type AS type, 
                    n.source_document AS source_document, 
                    n.confidence AS confidence
                ORDER BY coalesce(n.confidence, 0) DESC
                LIMIT $limit
            """, limit=limit)
            return [dict(record) for record in result]
    
    def close(self):
        """Close the database connection."""
        if self.driver:
            self.driver.close()
            print("📤 Neo4j connection closed")

# Function for Stage 2 integration
def get_db_connection():
    """Get database connection for Stage 2 integration."""
    return GraphDatabase.driver(
        os.getenv("NEO4J_URI", "bolt://localhost:7687"), 
        auth=(
            os.getenv("NEO4J_USERNAME", "neo4j"), 
            os.getenv("NEO4J_PASSWORD", "password")
        )
    )