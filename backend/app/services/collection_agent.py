import requests
from stix2 import Indicator, Vulnerability
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from typing import List, Dict, Any

llm = ChatOpenAI(temperature=0, model_name="gpt-4o")


def flatten_keywords(keywords: Dict[str, List[str]]) -> set:
    """Flatten dict of keyword categories into a lowercase set of terms"""
    if not keywords:
        return {"threat", "vulnerability", "malware"}
    return {kw.lower() for values in keywords.values() for kw in values}


class BaseAgent:
    def __init__(self, keywords: Dict[str, List[str]] = None):
        # Accept dict directly
        self.dna_keywords_dict = keywords or {
            "generic": ["threat", "vulnerability", "malware"]
        }
        # Flattened set for internal filtering
        self.dna_keywords = flatten_keywords(self.dna_keywords_dict)

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
    def __init__(self, api_key, keywords=None):
        super().__init__(keywords)
        self.api_key = api_key
        self.base_url = "https://otx.alienvault.com/api/v1/pulses/subscribed"

    def collect(self):
        """Collects recent threat pulses from AlienVault OTX and prints the date range."""
        print("INFO: Collecting data from AlienVault OTX...")
        headers = {"X-OTX-API-KEY": self.api_key}
        try:
            response = requests.get(self.base_url, headers=headers, params={"limit": 50})
            response.raise_for_status()
            results = response.json().get("results", [])

            if not results:
                print("WARNING: No pulses returned.")
                return None

            # Extract created dates
            dates = [
                datetime.fromisoformat(pulse["created"].replace("Z", "+00:00"))
                for pulse in results
                if "created" in pulse
            ]

            if dates:
                print(
                    f"INFO: Feed covers from {min(dates)} to {max(dates)} "
                    f"({(max(dates)-min(dates)).days} days span)"
                )
            else:
                print("WARNING: No 'created' dates found in pulses.")

            return results
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not collect data from OTX. {e}")
            return None

    def safe_stix_value(self, val: str) -> str:
        """Escape values so STIX parser won't break"""
        return val.replace("'", "''")  # double up quotes

    def map_indicator_type(self, ind_type: str, ind_val: str) -> str:
        """Map OTX indicator types to valid STIX patterns"""
        mapping = {
            "IPv4": "ipv4-addr:value",
            "IPv6": "ipv6-addr:value",
            "domain": "domain-name:value",
            "hostname": "domain-name:value",
            "URL": "url:value",
            "FileHash-SHA256": "file:hashes.'SHA-256'",
            "FileHash-SHA1": "file:hashes.'SHA-1'",
            "FileHash-MD5": "file:hashes.'MD5'",
            "Email": "email-addr:value",
        }
        return mapping.get(ind_type, "artifact:payload_bin")  # fallback

    def process(self, raw_pulses):
        print("INFO: Processing raw data and filtering based on DNA keywords...")
        relevant_indicators = []
        for pulse in raw_pulses:
            pulse_text = pulse.get("name", "") + " " + pulse.get("description", "")

            if any(kw in pulse_text.lower() for kw in self.dna_keywords):
                for indicator in pulse.get("indicators", []):
                    stix_type = self.map_indicator_type(
                        indicator.get("type", ""), indicator.get("indicator", "")
                    )
                    stix_value = self.safe_stix_value(indicator.get("indicator", ""))

                    try:
                        stix_indicator = Indicator(
                            name=pulse.get("name"),
                            pattern_type="stix",
                            pattern=f"[{stix_type} = '{stix_value}']",
                            description=pulse.get("description", ""),
                        )
                        relevant_indicators.append(json.loads(stix_indicator.serialize()))
                    except Exception as e:
                        print(f"[OTX] Skipped bad indicator {indicator}: {e}")
        return relevant_indicators


class CVEAgent(BaseAgent):
    """CVE database integration for vulnerability intelligence using NVD API"""

    def __init__(self, api_key=None, keywords=None):
        super().__init__(keywords)
        self.api_key = api_key
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def collect(self):
        """Collects recent CVEs from NVD (National Vulnerability Database)"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        params = {
            "lastModStartDate": start_date.strftime("%Y-%m-%dT00:00:00.000"),
            "lastModEndDate": end_date.strftime("%Y-%m-%dT23:59:59.999"),
            "resultsPerPage": 50,
        }

        headers = {}
        if self.api_key:
            headers["apiKey"] = self.api_key

        try:
            response = requests.get(
                self.base_url, params=params, headers=headers, timeout=30
            )
            response.raise_for_status()
            return response.json().get("vulnerabilities", [])
        except requests.exceptions.RequestException as e:
            print(
                f"[CVE] API Error: {response.status_code if 'response' in locals() else 'No response'} - {e}"
            )
            return None

    def process(self, raw_cves):
        relevant_vulnerabilities = []

        for cve_item in raw_cves:
            cve = cve_item.get("cve", {})
            cve_id = cve.get("id", "")

            descriptions = cve.get("descriptions", [])
            description_text = " ".join(
                [d.get("value", "") for d in descriptions if d.get("lang") == "en"]
            )

            search_text = f"{cve_id} {description_text}".lower()

            if any(kw in search_text for kw in self.dna_keywords):
                metrics = cve.get("metrics", {})
                cvss_score = None
                severity = "UNKNOWN"

                if "cvssMetricV31" in metrics:
                    cvss_data = metrics["cvssMetricV31"][0] if metrics["cvssMetricV31"] else {}
                    cvss_score = cvss_data.get("cvssData", {}).get("baseScore")
                    severity = cvss_data.get("cvssData", {}).get("baseSeverity", "UNKNOWN")
                elif "cvssMetricV30" in metrics:
                    cvss_data = metrics["cvssMetricV30"][0] if metrics["cvssMetricV30"] else {}
                    cvss_score = cvss_data.get("cvssData", {}).get("baseScore")
                    severity = cvss_data.get("cvssData", {}).get("baseSeverity", "UNKNOWN")

                stix_vuln = Vulnerability(
                    name=cve_id,
                    description=description_text[:500] if description_text else "No description available",
                    external_references=[
                        {
                            "source_name": "NVD",
                            "external_id": cve_id,
                            "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                        }
                    ],
                )

                vuln_dict = json.loads(stix_vuln.serialize())
                vuln_dict["x_cvss_score"] = cvss_score
                vuln_dict["x_severity"] = severity

                relevant_vulnerabilities.append(vuln_dict)

        return relevant_vulnerabilities


class GitHubSecurityAgent(BaseAgent):
    """GitHub Security Advisories for open source vulnerabilities"""

    def __init__(self, github_token=None, keywords=None):
        super().__init__(keywords)
        self.github_token = github_token
        self.base_url = "https://api.github.com/graphql"

    def collect(self):
        query = """
        query {
            securityAdvisories(first: 50, orderBy: {field: PUBLISHED_AT, direction: DESC}) {
                nodes {
                    ghsaId
                    summary
                    description
                    severity
                    vulnerabilities(first: 10) {
                        nodes {
                            package {
                                ecosystem
                                name
                            }
                        }
                    }
                    cvss {
                        score
                    }
                    references {
                        url
                    }
                }
            }
        }
        """

        headers = {"Content-Type": "application/json"}
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        try:
            response = requests.post(
                self.base_url, json={"query": query}, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if "errors" in data:
                print(f"[GitHub] API Errors: {data['errors']}")
                return None

            return data.get("data", {}).get("securityAdvisories", {}).get("nodes", [])
        except requests.exceptions.RequestException as e:
            print(
                f"[GitHub] API Error: {response.status_code if 'response' in locals() else 'No response'} - {e}"
            )
            return None

    def process(self, raw_advisories):
        relevant_advisories = []

        for advisory in raw_advisories:
            ghsa_id = advisory.get("ghsaId", "")
            summary = advisory.get("summary", "")
            description = advisory.get("description", "")
            severity = advisory.get("severity", "UNKNOWN")

            vulnerabilities = advisory.get("vulnerabilities", {}).get("nodes", [])
            affected_packages = []
            for vuln in vulnerabilities:
                package = vuln.get("package", {})
                if package:
                    affected_packages.append(
                        f"{package.get('ecosystem', '')}/{package.get('name', '')}"
                    )

            search_text = f"{ghsa_id} {summary} {description} {' '.join(affected_packages)}".lower()

            if any(kw in search_text for kw in self.dna_keywords):
                cvss = advisory.get("cvss", {})
                cvss_score = cvss.get("score") if cvss else None

                stix_vuln = Vulnerability(
                    name=ghsa_id,
                    description=f"{summary}. {description[:400] if description else ''}",
                    external_references=[
                        {
                            "source_name": "GitHub Advisory",
                            "external_id": ghsa_id,
                            "url": f"https://github.com/advisories/{ghsa_id}",
                        }
                    ],
                )

                vuln_dict = json.loads(stix_vuln.serialize())
                vuln_dict["x_cvss_score"] = cvss_score
                vuln_dict["x_severity"] = severity
                vuln_dict["x_affected_packages"] = affected_packages

                relevant_advisories.append(vuln_dict)

        return relevant_advisories


class ThreatLandscapeBuilder:
    def __init__(self, collection_agents: List[BaseAgent], pir_keywords: dict = None):
        self.agents = collection_agents
        self.pir_keywords = pir_keywords or {}

    def build_threat_landscape(self) -> Dict[str, Any]:
        print("INFO: Building comprehensive threat landscape...")

        threat_landscape = {
            "indicators": [],
            "vulnerabilities": [],
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "total_items": 0,
            "keywords": self.pir_keywords,
        }

        for agent in self.agents:
            agent_name = agent.__class__.__name__
            print(f"INFO: Collecting from {agent_name}...")

            try:
                threat_data = agent.run()

                if threat_data:
                    for item in threat_data:
                        stix_type = item.get("type", "")

                        if stix_type == "indicator":
                            threat_landscape["indicators"].append(item)
                        elif stix_type == "vulnerability":
                            threat_landscape["vulnerabilities"].append(item)
                        else:
                            threat_landscape["indicators"].append(item)

                    threat_landscape["sources"].append(agent_name)

            except Exception as e:
                print(f"ERROR: Failed to collect from {agent_name}: {e}")
                continue

        threat_landscape["indicators"] = self._deduplicate_items(
            threat_landscape["indicators"]
        )
        threat_landscape["vulnerabilities"] = self._deduplicate_items(
            threat_landscape["vulnerabilities"]
        )

        threat_landscape["total_items"] = len(threat_landscape["indicators"]) + len(
            threat_landscape["vulnerabilities"]
        )

        print(f"SUCCESS: Built threat landscape with {threat_landscape['total_items']} unique items")
        print(f"  - Indicators: {len(threat_landscape['indicators'])}")
        print(f"  - Vulnerabilities: {len(threat_landscape['vulnerabilities'])}")
        print(f"  - Sources: {', '.join(threat_landscape['sources'])}")

        return threat_landscape

    def _deduplicate_items(self, items: List[Dict]) -> List[Dict]:
        seen = set()
        unique_items = []

        for item in items:
            identifier = item.get("id") or item.get("name", "")
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique_items.append(item)

        return unique_items
