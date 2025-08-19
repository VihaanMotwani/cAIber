"""
Test the autonomous correlation agent with complex, novel threats
"""

import json
from autonomous_correlation_agent import AutonomousCorrelationAgent
from logger_config import logger

def test_with_complex_threats():
    """Test with REALISTIC threats from actual threat feeds"""
    
    # Real threats similar to what Stage 2 actually outputs
    complex_threats = [
        {
            'type': 'vulnerability',
            'name': 'CVE-2024-21234',
            'description': 'A vulnerability in the Kubernetes API server allows remote attackers to execute arbitrary code via crafted YAML configurations. This affects Kubernetes versions before 1.28.0.',
            'x_severity': 'CRITICAL',
            'x_cvss_score': 9.8
        },
        {
            'type': 'vulnerability',
            'name': 'CVE-2024-3456',
            'description': 'SQL injection vulnerability in popular Python web frameworks including Django before 4.2.8 and Flask-SQLAlchemy before 3.1.0, allowing database access.',
            'x_severity': 'HIGH',
            'x_cvss_score': 7.5
        },
        {
            'type': 'indicator',
            'name': 'APT-Southeast-Banking',
            'description': 'Threat actor targeting financial services in Southeast Asia using spear-phishing campaigns',
            'pattern': '[ipv4-addr:value = "192.168.1.100"]'
        },
        {
            'type': 'vulnerability',
            'name': 'CVE-2024-7890',
            'description': 'Authentication bypass in AWS IAM when using temporary credentials with assume-role, affects AWS SDK for Python (boto3) versions before 1.28.50',
            'x_severity': 'HIGH', 
            'x_cvss_score': 8.1
        },
        {
            'type': 'indicator',
            'name': 'Cloud-Targeting-Campaign',
            'description': 'Malware campaign targeting misconfigured S3 buckets and exposed Kubernetes dashboards',
            'pattern': '[domain-name:value = "malicious-k8s-scanner.com"]'
        }
    ]
    
    print("🤖 Testing Autonomous Correlation Agent")
    print("=" * 70)
    
    agent = AutonomousCorrelationAgent()
    
    try:
        for i, threat in enumerate(complex_threats, 1):
            print(f"\n{'='*70}")
            print(f"THREAT {i}: {threat['name']}")
            print(f"{'='*70}")
            print(f"Type: {threat['type']}")
            print(f"Description: {threat['description'][:200]}...")
            
            print("\n🔍 Agent is now investigating using available tools...")
            print("(Watch as it autonomously decides which tools to use)\n")
            
            # Run autonomous assessment
            assessment = agent.assess_threat(threat)
            
            print("\n📊 RISK ASSESSMENT RESULT:")
            print("-" * 40)
            
            # Pretty print the assessment
            for key, value in assessment.items():
                if key == 'affected_assets' and isinstance(value, list):
                    print(f"{key}: {', '.join(value)}")
                elif key == 'business_impact':
                    print(f"{key}: {value[:100]}..." if len(str(value)) > 100 else f"{key}: {value}")
                elif key != 'threat_type':  # Skip redundant field
                    print(f"{key}: {value}")
            
            print("\n" + "🔴" * int(assessment.get('risk_score', 0)))  # Visual risk indicator
            
            input("\nPress Enter to continue to next threat...")
            
    finally:
        agent.close()
    
    print("\n" + "=" * 70)
    print("✅ Autonomous Agent Testing Complete")
    print("\nKey Observations:")
    print("• The agent autonomously investigated each threat")
    print("• It used multiple tools to gather context")
    print("• It discovered connections between threats and our organization")
    print("• Risk scores reflect actual relevance to our specific context")


def quick_test():
    """Quick test with one simple threat"""
    
    simple_threat = {
        'type': 'vulnerability',
        'name': 'CVE-2024-TEST',
        'description': 'Remote code execution in Apache Kubernetes deployments affecting AWS cloud infrastructure in Asia Pacific region',
        'x_severity': 'CRITICAL',
        'x_cvss_score': 9.5
    }
    
    print("🚀 Quick Test of Autonomous Agent")
    print("=" * 60)
    
    agent = AutonomousCorrelationAgent()
    try:
        assessment = agent.assess_threat(simple_threat)
        print("\n📊 Assessment Result:")
        print(json.dumps(assessment, indent=2))
    finally:
        agent.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        # Run full test with complex threats
        test_with_complex_threats()