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
        
        # FOR DEMO: Use mock data instead of LLM-extracted entities
        USE_MOCK_DATA = True  # Toggle this for demo vs real extraction
        
        if USE_MOCK_DATA:
            print("🎭 DEMO MODE: Using curated mock knowledge graph...")
            entities, relationships = self._get_mock_demo_data()
        else:
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

    def _get_mock_demo_data(self):
        """Generate realistic mock data for demo purposes."""
        entities = [
            # Core Organization
            {"id": "org_techcorp", "name": "TechCorp Inc", "type": "organization", "confidence": 0.95, "importance": 10, "source_document": "company_overview.pdf", "document_type": "business_strategy"},
            
            # Technology Stack (Realistic and balanced)
            {"id": "tech_aws", "name": "AWS", "type": "technology", "confidence": 0.95, "importance": 9, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_azure", "name": "Microsoft Azure", "type": "technology", "confidence": 0.90, "importance": 8, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_kubernetes", "name": "Kubernetes", "type": "technology", "confidence": 0.92, "importance": 8, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_docker", "name": "Docker", "type": "technology", "confidence": 0.91, "importance": 7, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_postgresql", "name": "PostgreSQL", "type": "technology", "confidence": 0.93, "importance": 8, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_mongodb", "name": "MongoDB", "type": "technology", "confidence": 0.88, "importance": 6, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_redis", "name": "Redis", "type": "technology", "confidence": 0.89, "importance": 6, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_react", "name": "React", "type": "technology", "confidence": 0.90, "importance": 7, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_nodejs", "name": "Node.js", "type": "technology", "confidence": 0.91, "importance": 7, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_python", "name": "Python", "type": "technology", "confidence": 0.92, "importance": 8, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_nginx", "name": "NGINX", "type": "technology", "confidence": 0.87, "importance": 6, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "tech_elasticsearch", "name": "Elasticsearch", "type": "technology", "confidence": 0.86, "importance": 5, "source_document": "tech_architecture.pdf", "document_type": "technical_architecture"},
            
            # PLANTED KEYWORDS FOR THREAT DETECTION (SharePoint vulnerabilities)
            {"id": "tech_sharepoint", "name": "SharePoint Server 2019", "type": "technology", "confidence": 0.94, "importance": 9, "source_document": "sharepoint_deployment.pdf", "document_type": "technical_architecture"},
            {"id": "tech_sharepoint_2016", "name": "SharePoint Server 2016", "type": "technology", "confidence": 0.89, "importance": 7, "source_document": "legacy_systems.pdf", "document_type": "technical_architecture"},
            {"id": "tech_iis", "name": "IIS Web Server", "type": "technology", "confidence": 0.91, "importance": 8, "source_document": "web_infrastructure.pdf", "document_type": "technical_architecture"},
            
            # PLANTED KEYWORDS FOR GITHUB SECURITY ADVISORIES DETECTION
            {"id": "tech_spring", "name": "Spring Framework", "type": "technology", "confidence": 0.90, "importance": 8, "source_document": "java_stack.pdf", "document_type": "technical_architecture"},
            {"id": "tech_log4j", "name": "Apache Log4j", "type": "technology", "confidence": 0.92, "importance": 9, "source_document": "logging_infrastructure.pdf", "document_type": "technical_architecture"},
            {"id": "tech_apache", "name": "Apache HTTP Server", "type": "technology", "confidence": 0.89, "importance": 7, "source_document": "web_servers.pdf", "document_type": "technical_architecture"},
            {"id": "tech_tomcat", "name": "Apache Tomcat", "type": "technology", "confidence": 0.88, "importance": 7, "source_document": "application_servers.pdf", "document_type": "technical_architecture"},
            {"id": "tech_struts", "name": "Apache Struts", "type": "technology", "confidence": 0.85, "importance": 6, "source_document": "java_frameworks.pdf", "document_type": "technical_architecture"},
            {"id": "tech_jenkins", "name": "Jenkins", "type": "technology", "confidence": 0.87, "importance": 7, "source_document": "cicd_pipeline.pdf", "document_type": "technical_architecture"},
            {"id": "tech_grafana", "name": "Grafana", "type": "technology", "confidence": 0.86, "importance": 6, "source_document": "monitoring_stack.pdf", "document_type": "technical_architecture"},
            {"id": "tech_prometheus", "name": "Prometheus", "type": "technology", "confidence": 0.87, "importance": 7, "source_document": "metrics_collection.pdf", "document_type": "technical_architecture"},
            {"id": "tech_helm", "name": "Helm", "type": "technology", "confidence": 0.84, "importance": 6, "source_document": "kubernetes_tooling.pdf", "document_type": "technical_architecture"},
            {"id": "tech_istio", "name": "Istio Service Mesh", "type": "technology", "confidence": 0.83, "importance": 6, "source_document": "microservices_architecture.pdf", "document_type": "technical_architecture"},
            
            # POPULAR PACKAGES FOR GITHUB ADVISORY DETECTION
            {"id": "tech_express", "name": "Express.js", "type": "technology", "confidence": 0.91, "importance": 8, "source_document": "nodejs_backend.pdf", "document_type": "technical_architecture"},
            {"id": "tech_lodash", "name": "Lodash", "type": "technology", "confidence": 0.88, "importance": 6, "source_document": "javascript_libraries.pdf", "document_type": "technical_architecture"},
            {"id": "tech_django", "name": "Django", "type": "technology", "confidence": 0.89, "importance": 7, "source_document": "python_web_framework.pdf", "document_type": "technical_architecture"},
            {"id": "tech_flask", "name": "Flask", "type": "technology", "confidence": 0.87, "importance": 7, "source_document": "python_microservices.pdf", "document_type": "technical_architecture"},
            {"id": "tech_requests", "name": "Python Requests", "type": "technology", "confidence": 0.90, "importance": 7, "source_document": "python_dependencies.pdf", "document_type": "technical_architecture"},
            {"id": "tech_npm", "name": "NPM Packages", "type": "technology", "confidence": 0.92, "importance": 8, "source_document": "package_management.pdf", "document_type": "technical_architecture"},
            
            # Business Assets
            {"id": "asset_customer_db", "name": "Customer Database", "type": "business_asset", "confidence": 0.95, "importance": 10, "source_document": "data_inventory.pdf", "document_type": "compliance"},
            {"id": "asset_payment_system", "name": "Payment Processing System", "type": "business_asset", "confidence": 0.94, "importance": 10, "source_document": "system_overview.pdf", "document_type": "technical_architecture"},
            {"id": "asset_auth_service", "name": "Authentication Service", "type": "business_asset", "confidence": 0.93, "importance": 9, "source_document": "security_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "asset_api_gateway", "name": "API Gateway", "type": "business_asset", "confidence": 0.92, "importance": 8, "source_document": "api_documentation.pdf", "document_type": "technical_architecture"},
            {"id": "asset_data_warehouse", "name": "Data Warehouse", "type": "business_asset", "confidence": 0.90, "importance": 8, "source_document": "data_architecture.pdf", "document_type": "technical_architecture"},
            {"id": "asset_ml_platform", "name": "ML Platform", "type": "business_asset", "confidence": 0.88, "importance": 7, "source_document": "ml_infrastructure.pdf", "document_type": "technical_architecture"},
            {"id": "asset_mobile_app", "name": "Mobile Application", "type": "business_asset", "confidence": 0.91, "importance": 8, "source_document": "mobile_strategy.pdf", "document_type": "business_strategy"},
            {"id": "asset_web_portal", "name": "Web Portal", "type": "business_asset", "confidence": 0.92, "importance": 8, "source_document": "frontend_architecture.pdf", "document_type": "technical_architecture"},
            
            # Business Initiatives
            {"id": "init_digital_transform", "name": "Digital Transformation", "type": "business_initiative", "confidence": 0.90, "importance": 9, "source_document": "strategic_plan.pdf", "document_type": "business_strategy"},
            {"id": "init_cloud_migration", "name": "Cloud Migration Initiative", "type": "business_initiative", "confidence": 0.88, "importance": 8, "source_document": "cloud_strategy.pdf", "document_type": "business_strategy"},
            {"id": "init_ai_adoption", "name": "AI/ML Adoption", "type": "business_initiative", "confidence": 0.85, "importance": 7, "source_document": "ai_strategy.pdf", "document_type": "business_strategy"},
            {"id": "init_security_enhance", "name": "Security Enhancement Program", "type": "business_initiative", "confidence": 0.92, "importance": 9, "source_document": "security_roadmap.pdf", "document_type": "business_strategy"},
            {"id": "init_global_expansion", "name": "Global Expansion", "type": "business_initiative", "confidence": 0.87, "importance": 8, "source_document": "expansion_plan.pdf", "document_type": "business_strategy"},
            
            # PLANTED GEOGRAPHIC KEYWORDS FOR THREAT DETECTION
            {"id": "geo_singapore", "name": "Singapore Operations", "type": "geography", "confidence": 0.89, "importance": 8, "source_document": "apac_expansion.pdf", "document_type": "business_strategy"},
            {"id": "geo_malaysia", "name": "Malaysia Market", "type": "geography", "confidence": 0.87, "importance": 7, "source_document": "southeast_asia_strategy.pdf", "document_type": "business_strategy"},
            {"id": "init_fintech", "name": "FinTech Innovation Program", "type": "business_initiative", "confidence": 0.90, "importance": 8, "source_document": "fintech_roadmap.pdf", "document_type": "business_strategy"},
            
            # Compliance Requirements
            {"id": "comp_gdpr", "name": "GDPR", "type": "compliance_requirement", "confidence": 0.95, "importance": 9, "source_document": "compliance_framework.pdf", "document_type": "compliance"},
            {"id": "comp_pci_dss", "name": "PCI-DSS", "type": "compliance_requirement", "confidence": 0.94, "importance": 9, "source_document": "payment_compliance.pdf", "document_type": "compliance"},
            {"id": "comp_sox", "name": "SOX", "type": "compliance_requirement", "confidence": 0.90, "importance": 7, "source_document": "sox_compliance.pdf", "document_type": "compliance"},
            {"id": "comp_hipaa", "name": "HIPAA", "type": "compliance_requirement", "confidence": 0.88, "importance": 6, "source_document": "healthcare_compliance.pdf", "document_type": "compliance"},
            {"id": "comp_iso27001", "name": "ISO 27001", "type": "compliance_requirement", "confidence": 0.91, "importance": 8, "source_document": "iso_certification.pdf", "document_type": "compliance"},
            
            # Threat Actors & Vulnerabilities
            {"id": "threat_apt29", "name": "APT29 (Cozy Bear)", "type": "threat_actor", "confidence": 0.85, "importance": 8, "source_document": "threat_intelligence.pdf", "document_type": "security_incident"},
            {"id": "threat_apt28", "name": "APT28 (Fancy Bear)", "type": "threat_actor", "confidence": 0.84, "importance": 8, "source_document": "threat_intelligence.pdf", "document_type": "security_incident"},
            {"id": "threat_lazarus", "name": "Lazarus Group", "type": "threat_actor", "confidence": 0.83, "importance": 7, "source_document": "threat_intelligence.pdf", "document_type": "security_incident"},
            {"id": "threat_ransomware", "name": "Ransomware Groups", "type": "threat_actor", "confidence": 0.86, "importance": 9, "source_document": "ransomware_report.pdf", "document_type": "security_incident"},
            
            # PLANTED THREAT ACTORS FOR SHAREPOINT VULNERABILITY DETECTION
            {"id": "threat_storm2603", "name": "Storm-2603", "type": "threat_actor", "confidence": 0.88, "importance": 9, "source_document": "microsoft_sharepoint_advisory.pdf", "document_type": "security_incident"},
            {"id": "threat_linen_typhoon", "name": "Linen Typhoon", "type": "threat_actor", "confidence": 0.87, "importance": 8, "source_document": "chinese_apt_analysis.pdf", "document_type": "security_incident"},
            {"id": "threat_violet_typhoon", "name": "Violet Typhoon", "type": "threat_actor", "confidence": 0.86, "importance": 8, "source_document": "espionage_campaigns.pdf", "document_type": "security_incident"},
            {"id": "threat_chinese_apt", "name": "Chinese Nation State Actors", "type": "threat_actor", "confidence": 0.85, "importance": 9, "source_document": "geopolitical_threats.pdf", "document_type": "security_incident"},
            
            {"id": "vuln_log4j", "name": "CVE-2021-44228 (Log4j)", "type": "vulnerability", "confidence": 0.95, "importance": 10, "source_document": "vulnerability_assessment.pdf", "document_type": "security_incident"},
            {"id": "vuln_citrix", "name": "CVE-2023-4966 (Citrix Bleed)", "type": "vulnerability", "confidence": 0.93, "importance": 9, "source_document": "vulnerability_assessment.pdf", "document_type": "security_incident"},
            {"id": "vuln_exchange", "name": "CVE-2021-34473 (ProxyShell)", "type": "vulnerability", "confidence": 0.91, "importance": 8, "source_document": "exchange_security.pdf", "document_type": "security_incident"},
            {"id": "vuln_ssl", "name": "SSL/TLS Vulnerabilities", "type": "vulnerability", "confidence": 0.87, "importance": 6, "source_document": "network_security.pdf", "document_type": "security_incident"},
            
            # Key Geographic Locations (Limited and relevant)
            {"id": "geo_us_east", "name": "US East Region", "type": "geography", "confidence": 0.90, "importance": 8, "source_document": "infrastructure_map.pdf", "document_type": "technical_architecture"},
            {"id": "geo_eu_west", "name": "EU West Region", "type": "geography", "confidence": 0.89, "importance": 7, "source_document": "infrastructure_map.pdf", "document_type": "technical_architecture"},
            {"id": "geo_apac", "name": "APAC Region", "type": "geography", "confidence": 0.88, "importance": 6, "source_document": "infrastructure_map.pdf", "document_type": "technical_architecture"},
            
            # Key Partner Organizations
            {"id": "org_aws_partner", "name": "AWS Partner Network", "type": "organization", "confidence": 0.85, "importance": 6, "source_document": "partner_agreements.pdf", "document_type": "business_strategy"},
            {"id": "org_msft_partner", "name": "Microsoft Partner", "type": "organization", "confidence": 0.84, "importance": 6, "source_document": "partner_agreements.pdf", "document_type": "business_strategy"},
            {"id": "org_security_vendor", "name": "CrowdStrike", "type": "organization", "confidence": 0.86, "importance": 7, "source_document": "vendor_contracts.pdf", "document_type": "business_strategy"},
        ]
        
        relationships = [
            # Technology Dependencies
            {"source": "tech_kubernetes", "target": "tech_docker", "relationship_type": "DEPENDS_ON", "confidence": 0.95, "evidence": "Kubernetes orchestrates Docker containers"},
            {"source": "tech_react", "target": "tech_nodejs", "relationship_type": "INTEGRATES_WITH", "confidence": 0.90, "evidence": "React frontend connects to Node.js backend"},
            {"source": "tech_nodejs", "target": "tech_postgresql", "relationship_type": "CONNECTS_TO", "confidence": 0.92, "evidence": "Node.js services use PostgreSQL for data persistence"},
            {"source": "tech_python", "target": "tech_mongodb", "relationship_type": "CONNECTS_TO", "confidence": 0.88, "evidence": "Python analytics services use MongoDB"},
            {"source": "tech_nodejs", "target": "tech_redis", "relationship_type": "USES", "confidence": 0.89, "evidence": "Node.js uses Redis for caching"},
            {"source": "tech_nginx", "target": "tech_nodejs", "relationship_type": "PROXIES_TO", "confidence": 0.87, "evidence": "NGINX proxies requests to Node.js"},
            
            # Business Assets using Technologies
            {"source": "asset_customer_db", "target": "tech_postgresql", "relationship_type": "RUNS_ON", "confidence": 0.94, "evidence": "Customer database runs on PostgreSQL"},
            {"source": "asset_payment_system", "target": "tech_aws", "relationship_type": "HOSTED_ON", "confidence": 0.93, "evidence": "Payment system hosted on AWS"},
            {"source": "asset_auth_service", "target": "tech_redis", "relationship_type": "USES", "confidence": 0.90, "evidence": "Auth service uses Redis for session management"},
            {"source": "asset_api_gateway", "target": "tech_nginx", "relationship_type": "IMPLEMENTED_WITH", "confidence": 0.89, "evidence": "API Gateway implemented with NGINX"},
            {"source": "asset_data_warehouse", "target": "tech_aws", "relationship_type": "HOSTED_ON", "confidence": 0.91, "evidence": "Data warehouse on AWS Redshift"},
            {"source": "asset_ml_platform", "target": "tech_python", "relationship_type": "BUILT_WITH", "confidence": 0.88, "evidence": "ML platform built with Python"},
            {"source": "asset_mobile_app", "target": "tech_react", "relationship_type": "BUILT_WITH", "confidence": 0.87, "evidence": "Mobile app uses React Native"},
            {"source": "asset_web_portal", "target": "tech_react", "relationship_type": "BUILT_WITH", "confidence": 0.92, "evidence": "Web portal built with React"},
            
            # Business Initiatives using Technologies
            {"source": "init_cloud_migration", "target": "tech_aws", "relationship_type": "USES_TECHNOLOGY", "confidence": 0.91, "evidence": "Cloud migration leverages AWS"},
            {"source": "init_cloud_migration", "target": "tech_azure", "relationship_type": "USES_TECHNOLOGY", "confidence": 0.88, "evidence": "Multi-cloud strategy includes Azure"},
            {"source": "init_cloud_migration", "target": "tech_kubernetes", "relationship_type": "ADOPTS", "confidence": 0.90, "evidence": "Cloud migration adopts Kubernetes"},
            {"source": "init_ai_adoption", "target": "tech_python", "relationship_type": "USES_TECHNOLOGY", "confidence": 0.89, "evidence": "AI initiatives use Python ecosystem"},
            {"source": "init_ai_adoption", "target": "asset_ml_platform", "relationship_type": "DEVELOPS", "confidence": 0.87, "evidence": "AI adoption develops ML platform"},
            {"source": "init_digital_transform", "target": "asset_mobile_app", "relationship_type": "DELIVERS", "confidence": 0.86, "evidence": "Digital transformation delivers mobile app"},
            {"source": "init_security_enhance", "target": "asset_auth_service", "relationship_type": "ENHANCES", "confidence": 0.92, "evidence": "Security program enhances authentication"},
            
            # Compliance Requirements
            {"source": "asset_customer_db", "target": "comp_gdpr", "relationship_type": "MUST_COMPLY_WITH", "confidence": 0.95, "evidence": "Customer data must comply with GDPR"},
            {"source": "asset_payment_system", "target": "comp_pci_dss", "relationship_type": "MUST_COMPLY_WITH", "confidence": 0.94, "evidence": "Payment system requires PCI-DSS compliance"},
            {"source": "org_techcorp", "target": "comp_sox", "relationship_type": "SUBJECT_TO", "confidence": 0.90, "evidence": "Public company subject to SOX"},
            {"source": "asset_data_warehouse", "target": "comp_gdpr", "relationship_type": "MUST_COMPLY_WITH", "confidence": 0.91, "evidence": "Data warehouse must comply with GDPR"},
            
            # Threat Relationships
            {"source": "threat_apt29", "target": "tech_aws", "relationship_type": "TARGETS", "confidence": 0.85, "evidence": "APT29 targets cloud infrastructure"},
            {"source": "threat_ransomware", "target": "asset_customer_db", "relationship_type": "THREATENS", "confidence": 0.88, "evidence": "Ransomware groups target customer databases"},
            {"source": "vuln_log4j", "target": "tech_elasticsearch", "relationship_type": "AFFECTS", "confidence": 0.92, "evidence": "Log4j vulnerability affects Elasticsearch"},
            {"source": "threat_lazarus", "target": "asset_payment_system", "relationship_type": "TARGETS", "confidence": 0.84, "evidence": "Lazarus targets payment systems"},
            
            # Geographic Deployments (Limited and meaningful)
            {"source": "tech_aws", "target": "geo_us_east", "relationship_type": "DEPLOYED_IN", "confidence": 0.90, "evidence": "Primary AWS deployment in US East"},
            {"source": "tech_azure", "target": "geo_eu_west", "relationship_type": "DEPLOYED_IN", "confidence": 0.89, "evidence": "Azure deployment in EU West"},
            {"source": "asset_data_warehouse", "target": "geo_us_east", "relationship_type": "LOCATED_IN", "confidence": 0.88, "evidence": "Data warehouse in US East"},
            
            # Partner Relationships
            {"source": "org_techcorp", "target": "org_aws_partner", "relationship_type": "PARTNERS_WITH", "confidence": 0.86, "evidence": "TechCorp is AWS partner"},
            {"source": "org_techcorp", "target": "org_security_vendor", "relationship_type": "CONTRACTS_WITH", "confidence": 0.87, "evidence": "Security services from CrowdStrike"},
            {"source": "init_security_enhance", "target": "org_security_vendor", "relationship_type": "ENGAGES", "confidence": 0.85, "evidence": "Security enhancement engages CrowdStrike"},
        ]
        
        return entities, relationships

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