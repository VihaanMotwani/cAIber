from langchain_openai import ChatOpenAI
import os
import json

# We only need the LLM for this service, no graph connection is needed here
# as the context is provided directly in the input data.
llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))

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

Example Output Format:
{{
  "attack_paths": [
    {{
      "path_description": "Attack path leveraging a known vulnerability in the external VPN.",
      "steps": [
        {{
          "step": 1,
          "action": "Threat Actor 'APT28' sends a spearphishing email to an employee.",
          "mitre_attack": "Initial Access (T1566.001): Spearphishing Attachment",
          "stride_classification": "Spoofing",
          "justification": "The actor is impersonating a trusted entity to deceive the employee."
        }},
        {{
          "step": 2,
          "action": "The employee's compromised credentials are used to access the VPN.",
          "mitre_attack": "Credential Access (T1110.001): Brute Force",
          "stride_classification": "Elevation of Privilege",
          "justification": "The actor gains authorized access to a protected system."
        }}
      ]
    }}
  ]
}}

Now, analyze the following intelligence data and generate the comprehensive threat model.

Data:
{context_data}
"""

def generate_comprehensive_threat_model(intelligence_data: dict) -> dict:
    """
    Analyzes a full intelligence package to generate a comprehensive threat model
    with multiple, fully analyzed attack paths.
    """
    context_str = json.dumps(intelligence_data, indent=2)
    prompt = COMPREHENSIVE_MODEL_PROMPT.format(context_data=context_str)
    
    response = llm.invoke(prompt)
    
    try:
        # The LLM is instructed to return a clean JSON string
        model_data = json.loads(response.content)
        return model_data
    except json.JSONDecodeError:
        print("ERROR: LLM did not return valid JSON for the threat model.")
        return {"attack_paths": []}