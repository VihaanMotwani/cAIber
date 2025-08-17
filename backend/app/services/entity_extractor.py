"""
entity_extractor.py
Extracts entities and relationships from documents using NLP for cAIber Stage 1
"""

import re
import spacy
import json
from typing import List, Dict, Any
from langchain.schema import Document
from langchain_openai import ChatOpenAI


class EntityExtractor:
    """Extracts entities and relationships from documents using NLP."""
    
    def __init__(self):
        # Load spaCy model if available
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy model loaded successfully")
        except (ImportError, IOError):
            print("⚠️  spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize LLM for advanced entity extraction
        try:
            self.llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")
            print("✅ OpenAI LLM initialized")
        except Exception as e:
            print(f"⚠️  OpenAI LLM initialization failed: {e}")
            self.llm = None
        
        # Define entity patterns for security/business context
        self.entity_patterns = {
            'technology': r'\b(AWS|Azure|Docker|Kubernetes|Python|Java|React|MongoDB|PostgreSQL|Redis|Spring Boot|Node\.js)\b',
            'threat_actor': r'\b(APT\d+|Lazarus|Scattered Spider|FIN\d+|Cozy Bear)\b',
            'vulnerability': r'\b(CVE-\d{4}-\d{4,}|SQL injection|XSS|RCE)\b',
            'business_unit': r'\b(Finance|HR|Manufacturing|Sales|Marketing|IT)\b',
            'geography': r'\b(Southeast Asia|Singapore|Malaysia|Europe|North America|APAC|EMEA)\b'
        }
    
    def extract_entities(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Extract entities and relationships from documents."""
        entities = []
        
        print(f"🔍 Extracting entities from {len(documents)} documents...")
        
        for i, doc in enumerate(documents):
            print(f"Processing document {i+1}/{len(documents)}: {doc.metadata.get('file_name', 'unknown')}")
            doc_entities = self._extract_from_document(doc)
            entities.extend(doc_entities)
        
        # Remove duplicates based on id
        unique_entities = {}
        for entity in entities:
            entity_id = entity['id']
            if entity_id not in unique_entities:
                unique_entities[entity_id] = entity
            else:
                # Keep entity with higher confidence
                if entity['confidence'] > unique_entities[entity_id]['confidence']:
                    unique_entities[entity_id] = entity
        
        return list(unique_entities.values())
    
    def _extract_from_document(self, doc: Document) -> List[Dict[str, Any]]:
        """Extract entities from a single document."""
        entities = []
        content = doc.page_content
        metadata = doc.metadata
        
        # Pattern-based extraction (always runs)
        pattern_entities = self._extract_pattern_entities(content, metadata)
        entities.extend(pattern_entities)
        
        # NLP-based extraction (if spaCy is available)
        if self.nlp:
            nlp_entities = self._extract_nlp_entities(content, metadata)
            entities.extend(nlp_entities)
        
        # LLM-based extraction for complex entities (if OpenAI is available)
        if self.llm:
            llm_entities = self._extract_llm_entities(content, metadata)
            entities.extend(llm_entities)
        
        return entities
    
    def _extract_pattern_entities(self, content: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns."""
        entities = []
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'id': f"{entity_type}_{match.group().lower().replace(' ', '_').replace('.', '_')}",
                    'name': match.group(),
                    'type': entity_type,
                    'source_document': metadata.get('file_name', 'unknown'),
                    'document_type': metadata.get('file_type', 'general'),
                    'confidence': 0.8
                })
        
        return entities
    
    def _extract_nlp_entities(self, content: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Extract entities using spaCy NLP."""
        entities = []
        doc = self.nlp(content)
        
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'MONEY']:
                entities.append({
                    'id': f"nlp_{ent.text.lower().replace(' ', '_').replace('.', '_')}",
                    'name': ent.text,
                    'type': self._map_spacy_label(ent.label_),
                    'source_document': metadata.get('file_name', 'unknown'),
                    'document_type': metadata.get('file_type', 'general'),
                    'confidence': 0.7
                })
        
        return entities
    
    def _extract_llm_entities(self, content: str, metadata: Dict) -> List[Dict[str, Any]]:
        """Extract business-specific entities using LLM."""
        if len(content) > 2000:  # Limit content for API efficiency
            content = content[:2000]
        
        prompt = f"""
        Analyze the following business/security document and extract key entities.
        
        Document content: {content[:800]}...
        
        Extract and categorize entities in JSON format. Focus on:
        1. Business initiatives or projects
        2. Critical assets or systems
        3. Technologies or platforms not already captured
        4. Geographic locations or markets
        5. Compliance requirements
        
        Return ONLY a JSON array with this exact format:
        [
            {{"name": "Q3 Southeast Asia expansion", "type": "business_initiative", "importance": 9}},
            {{"name": "Mobile Banking Platform", "type": "business_asset", "importance": 8}}
        ]
        
        Valid types: business_initiative, business_asset, compliance_requirement, financial_data
        """
        
        try:
            response = self.llm.invoke(prompt)
            entities_text = response.content.strip()
            
            # Try to parse JSON response
            if entities_text.startswith('[') and entities_text.endswith(']'):
                try:
                    llm_data = json.loads(entities_text)
                    entities = []
                    
                    for item in llm_data:
                        if 'name' in item and 'type' in item:
                            entities.append({
                                'id': f"llm_{item['type']}_{item['name'].lower().replace(' ', '_')}",
                                'name': item['name'],
                                'type': item['type'],
                                'source_document': metadata.get('file_name', 'unknown'),
                                'document_type': metadata.get('file_type', 'general'),
                                'confidence': min(item.get('importance', 5) / 10.0, 0.9),
                                'importance': item.get('importance', 5)
                            })
                    
                    return entities
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing error: {e}")
                    return []
            
            return []
            
        except Exception as e:
            print(f"⚠️  LLM extraction error: {e}")
            return []
    
    def _map_spacy_label(self, label: str) -> str:
        """Map spaCy entity labels to our domain."""
        mapping = {
            'ORG': 'organization',
            'PRODUCT': 'technology',
            'GPE': 'geography',
            'MONEY': 'financial_data'
        }
        return mapping.get(label, 'general')