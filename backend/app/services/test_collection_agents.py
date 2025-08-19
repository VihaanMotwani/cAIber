#!/usr/bin/env python3
"""
Test script for collection agents - only mocking PIR keywords
Testing if Stage 2 threat collection is working correctly
"""

import os
import sys
from unittest.mock import patch
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import the agents
from collection_agent import (
    BaseAgent, 
    OTXAgent, 
    CVEAgent, 
    GitHubSecurityAgent,
    ThreatLandscapeBuilder
)


def mock_pir_keywords():
    """Mock PIR keywords for testing - simulating organizational context"""
    # These keywords simulate a company using cloud infrastructure and modern tech stack
    return {
        "aws",
        "cloud",
        "kubernetes", 
        "docker",
        "api",
        "authentication",
        "sql",
        "nodejs",
        "python",
        "javascript",
        "database",
        "remote code execution",
        "privilege escalation",
        "cross-site scripting",
        "injection"
    }


def test_cve_agent():
    """Test CVEAgent with real NVD API"""
    print("\n[CVE] Testing...")
    
    with patch.object(BaseAgent, '_get_keywords_from_pirs', return_value=mock_pir_keywords()):
        agent = CVEAgent()
        processed = agent.run()
        
        if processed:
            print(f"[CVE] ✅ Found {len(processed)} CVEs")
            if processed:
                sample = processed[0]
                print(f"[CVE] Sample: {sample.get('name')} (Severity: {sample.get('x_severity', 'Unknown')})")
        else:
            print("[CVE] ❌ No results")
            
    return processed


def test_github_agent():
    """Test GitHubSecurityAgent with real GitHub API"""
    print("\n[GitHub] Testing...")
    
    with patch.object(BaseAgent, '_get_keywords_from_pirs', return_value=mock_pir_keywords()):
        agent = GitHubSecurityAgent()
        processed = agent.run()
        
        if processed:
            print(f"[GitHub] ✅ Found {len(processed)} advisories")
            if processed:
                sample = processed[0]
                print(f"[GitHub] Sample: {sample.get('name')} (Severity: {sample.get('x_severity', 'Unknown')})")
        else:
            print("[GitHub] ❌ No results")
            
    return processed


def test_otx_agent():
    """Test OTXAgent with real OTX API"""
    print("\n" + "="*60)
    print("Testing OTXAgent with REAL OTX API")
    print("="*60)
    
    # Check for OTX API key
    otx_key = os.getenv('OTX_API_KEY')
    if not otx_key:
        print("⚠️  OTX_API_KEY not found in environment")
        print("   Set it with: export OTX_API_KEY=''")
        print("   Get a free key at: https://otx.alienvault.com/")
        return None
    
    # Only mock the PIR keywords
    with patch.object(BaseAgent, '_get_keywords_from_pirs', return_value=mock_pir_keywords()):
        agent = OTXAgent(api_key='5afd3484099e6bca2b1106a4cf443b03e7034d481c85c168e9903a64f441008b') #currently hardcoded, change later b4 push
        
        print(f"Using mock PIR keywords: {agent.dna_keywords}")
        print("\nFetching REAL threat pulses from AlienVault OTX...")
        
        # Run the full agent cycle
        processed = agent.run()
        
        if processed:
            print(f"\n✅ Successfully processed {len(processed)} relevant indicators")
            
            # Show first 3 indicators
            print("\nSample OTX Indicators found:")
            for i, indicator in enumerate(processed[:3], 1):
                print(f"\n  {i}. {indicator.get('name', 'Unknown')}")
                pattern = indicator.get('pattern', 'No pattern')
                print(f"     Pattern: {pattern}")
                desc = indicator.get('description', 'No description')
                if desc:
                    print(f"     Context: {desc[:100]}...")
        else:
            print("❌ No OTX pulses matched the PIR keywords")
            
    return processed


def test_threat_landscape_builder():
    """Test ThreatLandscapeBuilder with ALL real APIs"""
    print("\n" + "="*60)
    print("Testing Complete Threat Landscape Builder")
    print("="*60)
    
    # Only mock the PIR keywords - everything else is real
    with patch.object(BaseAgent, '_get_keywords_from_pirs', return_value=mock_pir_keywords()):
        agents = []
        
        # Add CVE agent
        print("Adding CVEAgent (NVD)...")
        agents.append(CVEAgent())
        
        # Add GitHub agent  
        print("Adding GitHubSecurityAgent...")
        agents.append(GitHubSecurityAgent())
        
        # Add OTX agent if API key exists
        otx_key = os.getenv('OTX_API_KEY')
        if otx_key:
            print("Adding OTXAgent...")
            agents.append(OTXAgent(api_key=otx_key))
        else:
            print("⚠️  Skipping OTX (no API key)")
        
        # Build the complete threat landscape
        builder = ThreatLandscapeBuilder(
            collection_agents=agents,
            pir_keywords=mock_pir_keywords()
        )
        
        print("\n🔨 Building comprehensive threat landscape from REAL data...")
        print("This may take a moment as we're querying multiple APIs...\n")
        
        landscape = builder.build_threat_landscape()
        
        # Display results
        print("\n" + "="*60)
        print("📊 THREAT LANDSCAPE SUMMARY")
        print("="*60)
        print(f"Total Unique Items: {landscape['total_items']}")
        print(f"  • Indicators: {len(landscape['indicators'])}")
        print(f"  • Vulnerabilities: {len(landscape['vulnerabilities'])}")
        print(f"Data Sources: {', '.join(landscape['sources'])}")
        print(f"Generated: {landscape['timestamp']}")
        
        # Show samples from each category
        if landscape['vulnerabilities']:
            print("\n🔴 Sample Vulnerabilities:")
            for vuln in landscape['vulnerabilities'][:3]:
                name = vuln.get('name', 'Unknown')
                severity = vuln.get('x_severity', 'Unknown')
                score = vuln.get('x_cvss_score', 'N/A')
                print(f"  • {name} - Severity: {severity}, CVSS: {score}")
        
        if landscape['indicators']:
            print("\n🔵 Sample Indicators:")
            for ind in landscape['indicators'][:3]:
                name = ind.get('name', 'Unknown')
                pattern = ind.get('pattern', 'No pattern')
                print(f"  • {name}")
                print(f"    Pattern: {pattern[:80]}...")
        
        return landscape


def main():
    """Run all tests with REAL data"""
    print("🚀 Testing Stage 2: Collection Agents")
    
    results = {}
    
    # Test CVE Agent
    try:
        cve_results = test_cve_agent()
        results['CVE'] = f"✅ {len(cve_results) if cve_results else 0} CVEs"
    except Exception as e:
        print(f"[CVE] ❌ Exception: {e}")
        results['CVE'] = f"❌ {str(e)[:50]}"
    
    # Test GitHub Agent
    try:
        github_results = test_github_agent()
        results['GitHub'] = f"✅ {len(github_results) if github_results else 0} advisories"
    except Exception as e:
        print(f"[GitHub] ❌ Exception: {e}")
        results['GitHub'] = f"❌ {str(e)[:50]}"
    
    # Test OTX Agent
    try:
        otx_results = test_otx_agent()
        if otx_results is None:
            results['OTX'] = "⚠️ Skipped (no API key)"
        else:
            results['OTX'] = f"✅ {len(otx_results) if otx_results else 0} indicators"
    except Exception as e:
        print(f"[OTX] ❌ Exception: {e}")
        results['OTX'] = f"❌ {str(e)[:50]}"
    
    # Summary
    print(f"\n📊 Results: {results}")
    print("✨ Test complete")


if __name__ == "__main__":
    main()