import requests
from stix2 import Indicator
import json
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

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
        print(f"INFO: Running {self.__class__.__name__}...")
        raw_data = self.collect()
        structured_intelligence = []
        if raw_data:
            structured_intelligence = self.process(raw_data)
            print(f"SUCCESS: Collected {len(structured_intelligence)} relevant intelligence items.")
            for item in structured_intelligence:
                print(json.dumps(item, indent=2))
        else:
            print("INFO: No new data collected.")

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