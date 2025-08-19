import requests
from stix2 import Indicator, Vulnerability
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from typing import List, Dict, Any
llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

class BaseAgent:
    def __init__(self):
        # --- THE LOGIC HERE IS COMPLETELY NEW ---
        self.dna_keywords = self._get_keywords_from_pirs()
        # --- END OF NEW LOGIC ---

    def _get_keywords_from_pirs(self):
        """
        Fetches PIRs from the API and uses an LLM to extract
        actionable keywords for threat hunting.
        """
        print("INFO: Fetching PIRs from the cAIber API...")
        try:
            # Assumes the app is running on localhost:8000
            response = requests.get("http://127.0.0.1:8000/generate-pirs")
            response.raise_for_status()
            pirs_text = response.json().get("pirs", {}).get("result", "")

            if not pirs_text:
                print("WARNING: No PIRs were generated. Falling back to generic keywords.")
                return {"threat", "vulnerability", "malware"}

            print(f"INFO: Generated PIRs:\n{pirs_text}")

            print("INFO: Using LLM to extract keywords from PIRs...")
            # Use the LLM to "translate" the PIRs into search terms
            prompt = f"""
            From the following threat intelligence requirements, extract a list of no more than 10 critical, specific, and searchable keywords.
            Focus on technologies, threat actor types, regions, and targeted assets.
            Return the keywords as a single, comma-separated string.

            Requirements:
            "{pirs_text}"

            Keywords:
            """
            response = llm.invoke(prompt)
            keywords_str = response.content
            keywords = {kw.strip().lower() for kw in keywords_str.split(',')}

            print(f"INFO: Extracted keywords for collection: {keywords}")
            return keywords

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not fetch PIRs. {e}")
            return {"threat", "vulnerability", "malware"} # Fallback keywords

    def collect(self):
        raise NotImplementedError

    def process(self, raw_data):
        raise NotImplementedError

    def run(self):
        raw_data = self.collect()
        structured_intelligence = []
        if raw_data:
            structured_intelligence = self.process(raw_data)
        return structured_intelligence

class OTXAgent(BaseAgent):
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://otx.alienvault.com/api/v1/pulses/subscribed"

    def collect(self):
        """Collects recent threat pulses from AlienVault OTX."""
        print("INFO: Collecting data from AlienVault OTX...")
        headers = {'X-OTX-API-KEY': self.api_key}
        try:
            response = requests.get(self.base_url, headers=headers, params={'limit': 50})
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not collect data from OTX. {e}")
            return None

    def process(self, raw_pulses):
        """Filters pulses based on DNA and converts them to STIX Indicators."""
        print("INFO: Processing raw data and filtering based on DNA keywords...")
        relevant_indicators = []
        for pulse in raw_pulses:
            pulse_text = pulse.get('name', '') + ' ' + pulse.get('description', '')
            # filtering based on org's data
            if any(keyword.lower() in pulse_text.lower() for keyword in self.dna_keywords):
                for indicator in pulse.get('indicators', []):
                    stix_indicator = Indicator(
                        name=pulse.get('name'),
                        pattern_type="stix",
                        pattern=f"[{indicator['type']}:value = '{indicator['indicator']}']",
                        description=pulse.get('description'),
                    )
                    relevant_indicators.append(json.loads(stix_indicator.serialize()))
        return relevant_indicators


class CVEAgent(BaseAgent):
    """CVE database integration for vulnerability intelligence using NVD API"""
    
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key  # NVD API key (optional but recommended for higher rate limits)
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        
    def collect(self):
        """Collects recent CVEs from NVD (National Vulnerability Database)"""
        # Get CVEs from the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        params = {
            'lastModStartDate': start_date.strftime('%Y-%m-%dT00:00:00.000'),
            'lastModEndDate': end_date.strftime('%Y-%m-%dT23:59:59.999'),
            'resultsPerPage': 50
        }
        
        headers = {}
        if self.api_key:
            headers['apiKey'] = self.api_key
            
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get('vulnerabilities', [])
        except requests.exceptions.RequestException as e:
            print(f"[CVE] API Error: {response.status_code if 'response' in locals() else 'No response'} - {e}")
            return None
    
    def process(self, raw_cves):
        """Filters CVEs based on DNA keywords and converts them to STIX Vulnerabilities"""
        relevant_vulnerabilities = []
        
        for cve_item in raw_cves:
            cve = cve_item.get('cve', {})
            cve_id = cve.get('id', '')
            
            # Get description text for keyword matching
            descriptions = cve.get('descriptions', [])
            description_text = ' '.join([d.get('value', '') for d in descriptions if d.get('lang') == 'en'])
            
            # Get affected products
            configurations = cve.get('configurations', [])
            weaknesses = cve.get('weaknesses', [])
            
            # Combine all text for keyword matching
            search_text = f"{cve_id} {description_text}".lower()
            
            # Filter based on organizational DNA keywords
            if any(keyword.lower() in search_text for keyword in self.dna_keywords):
                # Get CVSS score if available
                metrics = cve.get('metrics', {})
                cvss_score = None
                severity = "UNKNOWN"
                
                if 'cvssMetricV31' in metrics:
                    cvss_data = metrics['cvssMetricV31'][0] if metrics['cvssMetricV31'] else {}
                    cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                    severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                elif 'cvssMetricV30' in metrics:
                    cvss_data = metrics['cvssMetricV30'][0] if metrics['cvssMetricV30'] else {}
                    cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                    severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                
                # Create STIX Vulnerability object
                stix_vuln = Vulnerability(
                    name=cve_id,
                    description=description_text[:500] if description_text else "No description available",
                    external_references=[{
                        "source_name": "NVD",
                        "external_id": cve_id,
                        "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}"
                    }]
                )
                
                # Add custom fields after serialization
                vuln_dict = json.loads(stix_vuln.serialize())
                vuln_dict['x_cvss_score'] = cvss_score
                vuln_dict['x_severity'] = severity
                
                relevant_vulnerabilities.append(vuln_dict)
                
        return relevant_vulnerabilities


class GitHubSecurityAgent(BaseAgent):
    """GitHub Security Advisories for open source vulnerabilities"""
    
    def __init__(self, github_token=None): #hardcode it here 
        super().__init__()
        self.github_token = github_token  # GitHub personal access token (optional)
        self.base_url = "https://api.github.com/graphql"
        
    def collect(self):
        """Collects recent security advisories from GitHub"""
        # GraphQL query for recent security advisories
        query = """
        query {
            securityAdvisories(first: 50, orderBy: {field: PUBLISHED_AT, direction: DESC}) {
                nodes {
                    id
                    ghsaId
                    summary
                    description
                    severity
                    publishedAt
                    updatedAt
                    vulnerabilities(first: 10) {
                        nodes {
                            package {
                                ecosystem
                                name
                            }
                            vulnerableVersionRange
                            firstPatchedVersion {
                                identifier
                            }
                        }
                    }
                    cvss {
                        score
                        vectorString
                    }
                    references {
                        url
                    }
                }
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.github_token:
            headers['Authorization'] = f'Bearer {self.github_token}'
            
        try:
            response = requests.post(
                self.base_url,
                json={'query': query},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                print(f"[GitHub] API Errors: {data['errors']}")
                return None
                
            return data.get('data', {}).get('securityAdvisories', {}).get('nodes', [])
        except requests.exceptions.RequestException as e:
            print(f"[GitHub] API Error: {response.status_code if 'response' in locals() else 'No response'} - {e}")
            return None
    
    def process(self, raw_advisories):
        """Filters advisories based on DNA keywords and converts them to STIX format"""
        relevant_advisories = []
        
        for advisory in raw_advisories:
            ghsa_id = advisory.get('ghsaId', '')
            summary = advisory.get('summary', '')
            description = advisory.get('description', '')
            severity = advisory.get('severity', 'UNKNOWN')
            
            # Get affected packages
            vulnerabilities = advisory.get('vulnerabilities', {}).get('nodes', [])
            affected_packages = []
            for vuln in vulnerabilities:
                package = vuln.get('package', {})
                if package:
                    affected_packages.append(f"{package.get('ecosystem', '')}/{package.get('name', '')}")
            
            # Combine text for keyword matching
            search_text = f"{ghsa_id} {summary} {description} {' '.join(affected_packages)}".lower()
            
            # Filter based on organizational DNA keywords
            if any(keyword.lower() in search_text for keyword in self.dna_keywords):
                # Get CVSS score if available
                cvss = advisory.get('cvss', {})
                cvss_score = cvss.get('score') if cvss else None
                
                # Create STIX Vulnerability object
                stix_vuln = Vulnerability(
                    name=ghsa_id,
                    description=f"{summary}. {description[:400] if description else ''}",
                    external_references=[{
                        "source_name": "GitHub Advisory",
                        "external_id": ghsa_id,
                        "url": f"https://github.com/advisories/{ghsa_id}"
                    }]
                )
                
                # Add custom fields after serialization
                vuln_dict = json.loads(stix_vuln.serialize())
                vuln_dict['x_cvss_score'] = cvss_score
                vuln_dict['x_severity'] = severity
                vuln_dict['x_affected_packages'] = affected_packages
                
                relevant_advisories.append(vuln_dict)
                
        return relevant_advisories


class ThreatLandscapeBuilder:
    """Aggregates and deduplicates threats from all collection agents"""
    
    def __init__(self, collection_agents: List[BaseAgent], pir_keywords: set = None):
        self.agents = collection_agents
        self.pir_keywords = pir_keywords or set()
        
    def build_threat_landscape(self) -> Dict[str, Any]:
        """Aggregate and deduplicate threats from all sources"""
        print("INFO: Building comprehensive threat landscape...")
        
        threat_landscape = {
            "indicators": [],
            "vulnerabilities": [],
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "total_items": 0
        }
        
        # Collect from all agents
        for agent in self.agents:
            agent_name = agent.__class__.__name__
            print(f"INFO: Collecting from {agent_name}...")
            
            try:
                threat_data = agent.run()
                
                if threat_data:
                    # Categorize by STIX type
                    for item in threat_data:
                        stix_type = item.get('type', '')
                        
                        if stix_type == 'indicator':
                            threat_landscape["indicators"].append(item)
                        elif stix_type == 'vulnerability':
                            threat_landscape["vulnerabilities"].append(item)
                        else:
                            # Handle other types as needed
                            if "indicators" not in threat_landscape:
                                threat_landscape["indicators"] = []
                            threat_landscape["indicators"].append(item)
                    
                    threat_landscape["sources"].append(agent_name)
                    
            except Exception as e:
                print(f"ERROR: Failed to collect from {agent_name}: {e}")
                continue
        
        # Deduplicate based on ID/name
        threat_landscape["indicators"] = self._deduplicate_items(threat_landscape["indicators"])
        threat_landscape["vulnerabilities"] = self._deduplicate_items(threat_landscape["vulnerabilities"])
        
        # Calculate totals
        threat_landscape["total_items"] = (
            len(threat_landscape["indicators"]) + 
            len(threat_landscape["vulnerabilities"])
        )
        
        print(f"SUCCESS: Built threat landscape with {threat_landscape['total_items']} unique items")
        print(f"  - Indicators: {len(threat_landscape['indicators'])}")
        print(f"  - Vulnerabilities: {len(threat_landscape['vulnerabilities'])}")
        print(f"  - Sources: {', '.join(threat_landscape['sources'])}")
        
        return threat_landscape
    
    def _deduplicate_items(self, items: List[Dict]) -> List[Dict]:
        """Remove duplicate items based on ID or name"""
        seen = set()
        unique_items = []
        
        for item in items:
            # Use ID or name as unique identifier
            identifier = item.get('id') or item.get('name', '')
            
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_items.append(item)
                
        return unique_items