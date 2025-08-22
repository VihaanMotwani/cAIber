from langchain_openai import ChatOpenAI
import os
import json
from dotenv import load_dotenv
import re

load_dotenv()

# We only need the LLM for this service, no graph connection is needed here
# as the context is provided directly in the input data.
llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

# This is a much more advanced prompt to guide the LLM's analysis.
COMPREHENSIVE_MODEL_PROMPT = """
You are a senior cybersecurity threat intelligence analyst. Your task is to create a comprehensive threat model based on the provided JSON intelligence summary.

Your analysis must:
1.  Identify ALL plausible attack paths from the threat actors to the key assets mentioned in the risk assessments.
2.  For each identified attack path, break it down into a sequence of steps.
3.  For each step, provide a detailed analysis including:
    a. A clear description of the attacker's action.
    b. The most relevant **MITRE ATT&CK Tactic and Technique** (e.g., "Initial Access (T1566): Phishing").
    c. A **STRIDE Threat Classification** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, or Elevation of Privilege).
    d. A brief justification for your classifications.

Structure your final output as a single JSON object with one key: "attack_paths".
The value should be a list of paths. Each path object should contain a "path_description" and a list of "steps".

Now, analyze the following intelligence data and generate the comprehensive threat model.

Data:
{context_data}
"""

def generate_threat_model(intelligence_data: dict) -> dict:
    """
    Analyzes a full intelligence package to generate a comprehensive threat model
    with multiple, fully analyzed attack paths.
    """
    # Truncate PIRs to prevent token overflow
    truncated_data = intelligence_data.copy()
    if 'pirs' in truncated_data and len(truncated_data['pirs']) > 10000:
        truncated_data['pirs'] = truncated_data['pirs'][:10000] + "\n\n[... PIRs truncated to prevent token overflow ...]"
    
    context_str = json.dumps(truncated_data, indent=2)
    prompt = COMPREHENSIVE_MODEL_PROMPT.format(context_data=context_str)
    
    response = llm.invoke(prompt)
    raw_output = response.content

    cleaned_output = re.sub(r"^```(?:json)?\n|\n```$", "", raw_output.strip())

    print(cleaned_output)
    try:
        # The LLM is instructed to return a clean JSON string
        model_data = json.loads(cleaned_output)
        return model_data
    except json.JSONDecodeError:
        print("ERROR: LLM did not return valid JSON for the threat model.")
        return {"attack_paths": []}

intelligence = {
  "executive_summary": "Analysis indicates a high risk from the state-sponsored actor APT41, which has been observed exploiting a critical remote code execution vulnerability (CVE-2024-21748) in externally facing Confluence servers. Our own 'Confluence Wiki Server' is unpatched and directly exposed, creating a potential vector for initial access to our internal network and threatening sensitive project documentation, including the 'Q3 Product Launch Plans'.",
  "pirs": [
    "What are the TTPs used by APT41 to exploit web-facing collaboration tools?",
    "Is there any evidence of APT41 targeting intellectual property related to our industry in the last 6 months?"
  ],
  "keywords": [
    "apt41",
    "confluence",
    "cve-2024-21748",
    "initial access",
    "intellectual property",
    "wiki"
  ],
  "threat_landscape": {
    "actors": [
      {
        "name": "APT41",
        "motivation": "Espionage, Intellectual Property Theft",
        "primary_targets": ["Technology", "Healthcare", "Telecommunications"],
        "common_ttps": ["T1566: Phishing", "T1190: Exploit Public-Facing Application", "T1059: Command and Scripting Interpreter"]
      }
    ],
    "vulnerabilities": [
      {
        "cve_id": "CVE-2024-21748",
        "product": "Confluence Data Center and Server",
        "description": "A critical remote code execution (RCE) vulnerability that allows an unauthenticated attacker to execute arbitrary code.",
        "cvss_score": 9.8
      }
    ]
  },
  "risk_assessments": [
    {
      "risk_id": "RISK-001",
      "title": "Compromise of External Confluence Server",
      "threat": "APT41",
      "vulnerability": "CVE-2024-21748",
      "asset": "Confluence Wiki Server (ext.wiki.globaltech.com)",
      "impact": "High. Initial access to the internal network, potential for data exfiltration.",
      "likelihood": "High",
      "recommendation": "Patch Confluence server to the latest version immediately."
    },
    {
      "risk_id": "RISK-002",
      "title": "Exfiltration of Sensitive Project Plans",
      "threat": "APT41",
      "vulnerability": "Lateral movement from compromised wiki server",
      "asset": "Q3 Product Launch Plans (stored on internal file share)",
      "impact": "Critical. Loss of competitive advantage and intellectual property.",
      "likelihood": "Medium",
      "recommendation": "Implement network segmentation to isolate the Confluence server from critical file shares."
    }
  ]
}
generate_threat_model(intelligence)