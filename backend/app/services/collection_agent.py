import requests
from stix2 import Indicator
import json
from ..services.dna_engine import get_db # Import the existing db engine

class BaseAgent:
    def __init__(self):
        self.db = get_db()
        self.dna_keywords = self._get_dna_keywords()

    def _get_dna_keywords(self):
        """
        Queries the Neo4j database to get keywords from the 'Organizational DNA'.
        This is the integration point with Stage 1.
        """
        print("INFO: Fetching keywords from Organizational DNA...")
        # This is a sample query. You can make it more sophisticated.
        query = "MATCH (n) RETURN n.id AS keyword"
        results = self.db.query(query)
        keywords = {record["keyword"] for record in results if record["keyword"]}
        print(f"INFO: Loaded {len(keywords)} keywords from DNA.")
        return keywords

    def collect(self):
        raise NotImplementedError

    def process(self, raw_data):
        raise NotImplementedError

    def run(self):
        print(f"INFO: Running {self.__class__.__name__}...")
        raw_data = self.collect()
        if raw_data:
            structured_intelligence = self.process(raw_data)
            print(f"SUCCESS: Collected {len(structured_intelligence)} relevant intelligence items.")
            for item in structured_intelligence:
                print(json.dumps(item, indent=2))
        else:
            print("INFO: No new data collected.")

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