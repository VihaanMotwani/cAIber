"""
organizational_dna_engine.py
Main orchestrator for cAIber Stage 1 - Organizational DNA Engine
"""

import os
from typing import Dict, Any
from .document_processor import DocumentProcessor
from .entity_extractor import EntityExtractor
from .knowledge_graph_builder import KnowledgeGraphBuilder

from dotenv import load_dotenv
load_dotenv()

class OrganizationalDNAEngine:
    """Main engine that coordinates document processing and knowledge graph building."""
    
    def __init__(self, 
                 neo4j_uri: str = None, 
                 neo4j_user: str = None, 
                 neo4j_password: str = None):
        
        print("🚀 Initializing cAIber Organizational DNA Engine")
        print("=" * 50)
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.entity_extractor = EntityExtractor()
        self.graph_builder = KnowledgeGraphBuilder(neo4j_uri, neo4j_user, neo4j_password)
    
    def build_organizational_dna(self, documents_directory: str, clear_existing: bool = False) -> None:
        """Main method to build the organizational DNA knowledge graph."""
        print("🧬 Building Organizational DNA")
        print("=" * 50)
        
        # Step 1: Load and process documents
        print("\n📄 Step 1: Loading documents...")
        documents = self.doc_processor.load_documents(documents_directory)
        
        if not documents:
            print("❌ No documents found! Please check the directory path.")
            return
            
        print(f"✅ Loaded {len(documents)} document chunks")
        
        # Show document breakdown
        doc_types = {}
        for doc in documents:
            doc_type = doc.metadata.get('file_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        print("📊 Document breakdown:")
        for doc_type, count in doc_types.items():
            print(f"   • {doc_type}: {count} chunks")
        
        # Step 2: Extract entities and relationships
        print("\n🔍 Step 2: Extracting entities...")
        entities = self.entity_extractor.extract_entities(documents)
        
        if not entities:
            print("❌ No entities extracted! Check your documents or extraction logic.")
            return
            
        print(f"✅ Extracted {len(entities)} unique entities")
        
        # Show entity breakdown
        entity_types = {}
        for entity in entities:
            entity_type = entity['type']
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        print("📊 Entity breakdown:")
        for entity_type, count in entity_types.items():
            print(f"   • {entity_type}: {count} entities")
        
        # Step 3: Build knowledge graph
        print("\n🕸️  Step 3: Building knowledge graph...")
        self.graph_builder.build_knowledge_graph(entities, clear_existing)
        
        print("\n✅ Organizational DNA Build Complete!")
        print("=" * 50)
    
    def get_dna_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the organizational DNA."""
        return self.graph_builder.get_graph_summary()
    
    def validate_build(self) -> bool:
        """Validate that the knowledge graph was built successfully."""
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
            
            # Show sample entities
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
        """Close all connections and cleanup."""
        self.graph_builder.close()


def main():
    """Main execution for standalone testing."""
    print("🎯 cAIber Stage 1 - Organizational DNA Engine")
    print("=" * 60)
    
    # Check environment
    documents_dir = "./documents"
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