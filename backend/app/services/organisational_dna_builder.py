"""
organizational_dna_engine.py
Main orchestrator for cAIber Stage 1 - Organizational DNA Engine (upload-only)
"""

from typing import Dict, Any, List
from langchain.schema import Document
from .entity_extractor import EntityExtractor
from .knowledge_graph_builder import KnowledgeGraphBuilder
from dotenv import load_dotenv

load_dotenv()

class OrganizationalDNAEngine:
    """Coordinates entity extraction and knowledge graph building from uploaded doc chunks."""

    def __init__(self,
                 neo4j_uri: str | None = None,
                 neo4j_user: str | None = None,
                 neo4j_password: str | None = None):
        print("🚀 Initializing cAIber Organizational DNA Engine")
        print("=" * 50)
        self.entity_extractor = EntityExtractor()
        self.graph_builder = KnowledgeGraphBuilder(neo4j_uri, neo4j_user, neo4j_password)

    def build_organizational_dna(
        self,
        documents: List[Document],
        clear_existing: bool = False,
    ) -> None:
        """Build the knowledge graph strictly from uploaded in-memory documents."""
        if not documents:
            print("❌ No documents provided!")
            return

        print(f"✅ Received {len(documents)} document chunks")

        # breakdown
        doc_types: Dict[str, int] = {}
        for d in documents:
            dt = d.metadata.get("file_type", "unknown")
            doc_types[dt] = doc_types.get(dt, 0) + 1
        print("📊 Document breakdown:", doc_types)

        print("\n🔍 Extracting entities and relationships...")
        extraction_result = self.entity_extractor.extract_entities_and_relationships(documents)
        entities = extraction_result['entities']
        relationships = extraction_result['relationships']
        if not entities:
            print("❌ No entities extracted!")
            return
            
        print(f"✅ Extracted {len(entities)} unique entities and {len(relationships)} relationships")
        
        # Show entity breakdown
        entity_types = {}
        for entity in entities:
            entity_type = entity['type']
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print("📊 Entity breakdown:")
        for entity_type, count in entity_types.items():
            print(f"   • {entity_type}: {count} entities")
        
        # Show relationship breakdown
        if relationships:
            relationship_types = {}
            for rel in relationships:
                rel_type = rel['relationship_type']
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            
            print("🔗 Relationship breakdown:")
            for rel_type, count in sorted(relationship_types.items()):
                print(f"   • {rel_type}: {count} relationships")
        
        # Step 3: Build knowledge graph
        print("\n🕸️  Step 3: Building knowledge graph...")
        self.graph_builder.build_knowledge_graph(entities, clear_existing, relationships)
        
        print("\n✅ Organizational DNA Build Complete!")

    def get_dna_summary(self) -> Dict[str, Any]:
        """Return a summary from the graph backend."""
        return self.graph_builder.get_graph_summary()

    def validate_build(self) -> bool:
        """Validate that the graph contains data."""
        print("\n🔧 Validating Organizational DNA Build...")
        print("=" * 40)

        try:
            summary = self.get_dna_summary()
            print(f"📊 Graph Statistics:")
            print(f"   • Total nodes: {summary['total_nodes']}")
            print(f"   • Total relationships: {summary['total_relationships']}")

            print(f"\n📈 Entity Distribution:")
            for entity_type, count in summary['entity_counts'].items():
                print(f"   • {entity_type}: {count}")

            if summary['relationship_counts']:
                print(f"\n🔗 Relationship Distribution:")
                for rel_type, count in summary['relationship_counts'].items():
                    print(f"   • {rel_type}: {count}")

            sample_entities = self.graph_builder.get_sample_entities(5)
            if sample_entities:
                print(f"\n🎯 Sample High-Confidence Entities:")
                for entity in sample_entities:
                    print(f"   • {entity['name']} ({entity['type']}) - {entity['confidence']:.2f}")

            if summary['total_nodes'] > 0:
                print("\n✅ Build validation successful!")
                return True
            else:
                print("\n❌ Build validation failed - no nodes created")
                return False

        except Exception as e:
            print(f"\n❌ Build validation failed: {e}")
            return False

    def close(self):
        """Cleanup resources."""
        self.graph_builder.close()


def main():
    """Main execution for standalone testing."""
    print("🎯 cAIber Stage 1 - Organizational DNA Engine")
    print("=" * 60)
    
    # Check environment
    documents_dir = "../documents"
    if not os.path.exists(documents_dir):
        print(f"❌ Documents directory '{documents_dir}' not found!")
        print("   Create it and add some sample documents (PDF, TXT, DOCX, MD)")
        return
    
    # Initialize DNA Engine
    try:
        dna_engine = OrganizationalDNAEngine()
    except Exception as e:
        print(f"❌ Failed to initialize DNA Engine: {e}")
        print("   Make sure Neo4j is running and credentials are correct")
        return
    
    try:
        # Build organizational DNA
        dna_engine.build_organizational_dna(documents_dir, clear_existing=True)
        
        # Validate the build
        if dna_engine.validate_build():
            print("\n🎉 Ready for Stage 2 PIR Generation!")
            print("   Your knowledge graph is now available for threat intelligence analysis.")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
    
    finally:
        dna_engine.close()


if __name__ == "__main__":
    main()