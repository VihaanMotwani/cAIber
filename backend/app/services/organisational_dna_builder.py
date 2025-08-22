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

        print("\n🔍 Extracting entities...")
        entities = self.entity_extractor.extract_entities(documents)
        if not entities:
            print("❌ No entities extracted!")
            return

        print("\n🕸️ Building knowledge graph...")
        self.graph_builder.build_knowledge_graph(entities, clear_existing)
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
