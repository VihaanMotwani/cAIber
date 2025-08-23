#!/usr/bin/env python3
"""
Analyze threat feeds to understand detection keywords and reverse engineer for demo.
This will help us identify what to plant in our rigged knowledge graph.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append('/Users/home/project/cAIber-1/backend')

def analyze_detection_keywords():
    """Extract keywords from our organizational DNA that should trigger detections"""
    
    print("🔍 ANALYZING THREAT FEED DETECTION PATTERNS")
    print("=" * 60)
    
    # Our rigged company profile keywords
    company_keywords = [
        # Technologies
        "sharepoint", "aws", "kubernetes", "k8s", "postgresql", "postgres", 
        "docker", "container", "microservices", "api", "cloud", "azure",
        
        # Business Context  
        "fintech", "financial", "payment", "transaction", "pci", "gdpr",
        "compliance", "customer data", "database", "payment gateway",
        
        # Geographies
        "singapore", "malaysia", "asia", "southeast asia", "apac",
        
        # Threat Actors (from Microsoft report)
        "storm-2603", "linen typhoon", "violet typhoon", "apt20", "china",
        "chinese", "nation state", "apt", "advanced persistent threat",
        
        # Attack Techniques
        "web shell", "spinstall", "mimikatz", "psexec", "impacket", "warlock",
        "ransomware", "lateral movement", "credential dumping", "lsass"
    ]
    
    print(f"📋 Company Keywords to Plant: {len(company_keywords)}")
    for i, kw in enumerate(company_keywords, 1):
        print(f"  {i:2d}. {kw}")
    
    print(f"\n🎯 REVERSE ENGINEERING PLAN:")
    print("1. Plant these keywords in rigged knowledge graph entities")
    print("2. Add them as entity names, descriptions, and properties")
    print("3. This will trigger PIR keyword matching during feed processing")
    print("4. Result: Real threat feeds will match our rigged company profile")
    
    return company_keywords

def fix_indicator_display_issue():
    """Analyze why all 22 indicators show same CVE"""
    print(f"\n🐛 INDICATOR DISPLAY ISSUE ANALYSIS:")
    print("=" * 60)
    
    print("PROBLEM: All 22 indicators showing 'CVE-2025-49704' instead of actual IOCs")
    print("\nROOT CAUSE:")
    print("- OTX returns 1 pulse about SharePoint vulnerabilities")  
    print("- This pulse contains 22 different indicators (IPs, domains, hashes)")
    print("- Frontend displays pulse name (containing CVE) instead of indicator values")
    print("- Should show: '192.168.1.1', 'malicious.com', 'abc123hash...'")
    print("- Currently shows: 'CVE-2025-49704' for all 22")
    
    print(f"\nFIX NEEDED:")
    print("- Frontend should display indicator.indicator (the actual IOC value)")
    print("- Not the indicator.pulse (which contains CVE names)")
    
def create_plant_keywords_script():
    """Create a script to plant keywords in the rigged knowledge graph"""
    
    script_content = '''#!/usr/bin/env python3
"""
Plant detection keywords into the rigged knowledge graph for demo purposes.
This ensures our threat feeds will detect relevant threats.
"""

def get_rigged_entities_with_keywords():
    """Enhanced rigged entities with threat intelligence keywords"""
    
    entities = [
        # Core Infrastructure (with SharePoint keywords for recent exploit detection)
        {
            "id": "org-root",
            "type": "organization", 
            "name": "TechCorp Inc.", 
            "description": "FinTech company using SharePoint Server 2019 for document collaboration and customer data management",
            "properties": {
                "industry": "financial technology",
                "size": "500-1000 employees",
                "technologies": "sharepoint, aws cloud, kubernetes containers, postgresql database"
            }
        },
        
        # SharePoint Infrastructure (HIGH PRIORITY - recent exploits)
        {
            "id": "sharepoint-server", 
            "type": "technology",
            "name": "SharePoint Server 2019",
            "description": "On-premises SharePoint deployment for document management and collaboration. Vulnerable to CVE-2025-49704, CVE-2025-49706, CVE-2025-53770 exploits",
            "properties": {
                "version": "2019", 
                "deployment": "on-premises",
                "vulnerabilities": "sharepoint server vulnerabilities, web shell attacks, toolpane endpoint exploitation"
            }
        },
        
        # AWS Infrastructure  
        {
            "id": "aws-cloud",
            "type": "technology",
            "name": "AWS Cloud Infrastructure", 
            "description": "Amazon Web Services cloud platform hosting kubernetes clusters and microservices architecture",
            "properties": {
                "services": "aws ec2, aws rds postgresql, aws eks kubernetes",
                "threats": "supply chain attacks, container vulnerabilities, cloud misconfigurations"
            }
        },
        
        # Payment Systems (FinTech context)
        {
            "id": "payment-api",
            "type": "business_asset",
            "name": "Payment Gateway API",
            "description": "PCI-DSS compliant payment processing system handling financial transactions and customer payment data",
            "properties": {
                "compliance": "pci-dss, financial regulations",
                "data_types": "customer payment data, financial transactions, credit card information",
                "threats": "payment fraud, data exfiltration, financial cybercrime"
            }
        },
        
        # Customer Database
        {
            "id": "customer-db",
            "type": "business_asset", 
            "name": "Customer Database",
            "description": "PostgreSQL database containing customer personal information, financial records, and transaction history for GDPR compliance",
            "properties": {
                "technology": "postgresql database server",
                "data_classification": "personal identifiable information, financial data",
                "compliance": "gdpr, data protection regulations",
                "threats": "database vulnerabilities, sql injection, credential dumping, mimikatz attacks"
            }
        },
        
        # Geographic Expansion
        {
            "id": "apac-expansion",
            "type": "business_initiative",
            "name": "APAC Market Expansion", 
            "description": "Business expansion into Singapore and Malaysia markets with focus on Southeast Asia fintech opportunities",
            "properties": {
                "regions": "singapore, malaysia, southeast asia, asia pacific",
                "timeline": "Q3 2024 expansion plan",
                "threats": "regional threat actors, apt20 targeting, nation state attacks, chinese advanced persistent threats"
            }
        },
        
        # Container Infrastructure
        {
            "id": "k8s-cluster",
            "type": "technology",
            "name": "Kubernetes Clusters",
            "description": "Container orchestration platform running microservices with docker containers and automated deployment pipelines", 
            "properties": {
                "deployment": "kubernetes orchestration, docker containers, microservices architecture",
                "vulnerabilities": "container security threats, kubernetes vulnerabilities, supply chain compromises",
                "tools": "docker, container runtime, orchestration"
            }
        }
    ]
    
    relationships = [
        {"source": "org-root", "target": "sharepoint-server", "type": "USES_TECHNOLOGY"},
        {"source": "org-root", "target": "aws-cloud", "type": "USES_TECHNOLOGY"}, 
        {"source": "org-root", "target": "payment-api", "type": "OWNS_ASSET"},
        {"source": "org-root", "target": "customer-db", "type": "OWNS_ASSET"},
        {"source": "sharepoint-server", "target": "customer-db", "type": "ACCESSES_DATA"},
        {"source": "payment-api", "target": "customer-db", "type": "QUERIES_DATA"},
        {"source": "aws-cloud", "target": "k8s-cluster", "type": "HOSTS"},
        {"source": "k8s-cluster", "target": "payment-api", "type": "RUNS_SERVICE"}
    ]
    
    return entities, relationships

if __name__ == "__main__":
    entities, relationships = get_rigged_entities_with_keywords()
    print(f"Generated {len(entities)} entities with threat keywords")
    print(f"Generated {len(relationships)} relationships")
    
    # Keywords that should now trigger detections:
    keywords = [
        "sharepoint", "kubernetes", "postgresql", "aws", "payment", "singapore", 
        "malaysia", "fintech", "financial", "pci", "gdpr", "container", "docker"
    ]
    print(f"\\nKeywords planted for detection: {keywords}")
'''
    
    with open('/Users/home/project/cAIber-1/backend/plant_keywords.py', 'w') as f:
        f.write(script_content)
    
    print(f"\n📝 Created plant_keywords.py script")

if __name__ == "__main__":
    # Step 1: Analyze what keywords we need
    keywords = analyze_detection_keywords()
    
    # Step 2: Analyze the indicator display bug  
    fix_indicator_display_issue()
    
    # Step 3: Create script to plant keywords
    create_plant_keywords_script()
    
    print(f"\n✅ NEXT STEPS:")
    print("1. Update organizational_dna_builder.py with plant_keywords.py entities")
    print("2. Fix frontend indicator display (show indicator.indicator not indicator.pulse)")  
    print("3. Run pipeline - should now detect threats matching our rigged company!")