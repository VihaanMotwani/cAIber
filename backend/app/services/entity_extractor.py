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
    
    def extract_entities_and_relationships(self, documents: List[Document]) -> Dict[str, Any]:
        """Extract entities and relationships from documents."""
        entities = []
        relationships = []
        
        print(f"🔍 Extracting entities and relationships from {len(documents)} documents...")
        
        for i, doc in enumerate(documents):
            print(f"Processing document {i+1}/{len(documents)}: {doc.metadata.get('file_name', 'unknown')}")
            print(f"   🚀 ABOUT TO CALL _extract_from_document...")
            try:
                doc_entities = self._extract_from_document(doc)
                print(f"   ✅ RETURNED FROM _extract_from_document with {len(doc_entities)} entities")
                entities.extend(doc_entities)
            except Exception as e:
                print(f"   🛑 EXCEPTION in _extract_from_document: {e}")
                print(f"   🛑 Exception type: {type(e).__name__}")
                import traceback
                print(f"   🛑 Traceback: {traceback.format_exc()}")
                doc_entities = []  # Continue with empty entities for this document
                entities.extend(doc_entities)
            
            # Debug: Check relationship extraction conditions
            print(f"   📊 Found {len(doc_entities)} entities in document")
            print(f"   🤖 LLM available: {self.llm is not None}")
            
            # Extract relationships if LLM is available
            if self.llm and len(doc_entities) > 1:
                print(f"   🔗 Extracting relationships between {len(doc_entities)} entities...")
                doc_relationships = self._extract_relationships_from_document(doc, doc_entities)
                print(f"   ✅ Found {len(doc_relationships)} relationships")
                relationships.extend(doc_relationships)
            else:
                if not self.llm:
                    print("   ⚠️  Skipping relationship extraction: LLM not available")
                else:
                    print("   ⚠️  Skipping relationship extraction: Not enough entities (need >1)")
        
        # Remove duplicate entities based on id
        unique_entities = {}
        for entity in entities:
            entity_id = entity['id']
            if entity_id not in unique_entities:
                unique_entities[entity_id] = entity
            else:
                # Keep entity with higher confidence
                if entity['confidence'] > unique_entities[entity_id]['confidence']:
                    unique_entities[entity_id] = entity
        
        # Remove duplicate relationships
        unique_relationships = []
        seen_rels = set()
        for rel in relationships:
            rel_key = f"{rel['source']}-{rel['relationship_type']}-{rel['target']}"
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                unique_relationships.append(rel)
        
        return {
            'entities': list(unique_entities.values()),
            'relationships': unique_relationships
        }
    
    # Keep backward compatibility
    def extract_entities(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Extract entities from documents (backward compatibility)."""
        result = self.extract_entities_and_relationships(documents)
        return result['entities']
    
    def _extract_from_document(self, doc: Document) -> List[Dict[str, Any]]:
        """Extract entities from a single document."""
        entities = []
        content = doc.page_content
        metadata = doc.metadata
        
        print(f"\n=== ENTITY EXTRACTION START: {metadata.get('file_name', 'unknown')} ===")
        
        # Pattern-based extraction (always runs)
        pattern_entities = self._extract_pattern_entities(content, metadata)
        entities.extend(pattern_entities)
        print(f"      📝 Pattern-based: {len(pattern_entities)} entities")
        
        # NLP-based extraction (if spaCy is available)
        if self.nlp:
            nlp_entities = self._extract_nlp_entities(content, metadata)
            entities.extend(nlp_entities)
            print(f"      🧠 NLP-based: {len(nlp_entities)} entities")
        else:
            print(f"      ⚠️  NLP-based: Skipped (spaCy not available)")
        
        # LLM-based extraction for complex entities (if OpenAI is available)
        if self.llm:
            print(f"      🤖 LLM-based extraction starting for {metadata.get('file_name', 'unknown')}...")
            llm_entities = self._extract_llm_entities(content, metadata)
            entities.extend(llm_entities)
            print(f"      🤖 LLM-based: {len(llm_entities)} entities extracted")
        else:
            print(f"      ⚠️  LLM-based: Skipped (OpenAI LLM not available)")
        
        print(f"=== ENTITY EXTRACTION END: {len(entities)} entities ===")
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
        print(f"      🚀 ENTERING _extract_llm_entities for {metadata.get('file_name', 'unknown')}")
        print(f"         Content length: {len(content)} chars")
        
        # Smart truncation - keep more content for business documents
        if len(content) > 4000:
            # Keep beginning and end to capture both strategy and details
            content = content[:2500] + "\n\n[...document continues...]\n\n" + content[-1500:]
            print(f"         Content truncated to: {len(content)} chars")
        
        prompt = f"""
        Analyze this business/security document and extract key strategic entities.
        
        Document content:
        {content}
        
        Extract and categorize entities with focus on strategic intelligence. Look for:

        1. BUSINESS INITIATIVES: Strategic projects, transformation programs, expansion plans, digital initiatives, growth strategies
        2. BUSINESS ASSETS: Critical systems, platforms, applications, infrastructure components
        3. COMPLIANCE REQUIREMENTS: Standards, certifications, regulatory frameworks, audit requirements
        4. FINANCIAL DATA: Revenue targets, budget allocations, cost metrics, financial goals
        5. GEOGRAPHIC MARKETS: Target markets, operational regions, expansion territories
        
        Examples of what to extract:
        - "Digital Banking Expansion" (business_initiative)
        - "Zero-trust network architecture" (business_initiative) 
        - "Mobile Banking Platform" (business_asset)
        - "ISO 27001 compliance" (compliance_requirement)
        - "USD 120M ARR target" (financial_data)
        
        Return ONLY a JSON array with this exact format:
        [
            {{"name": "Digital Banking Expansion", "type": "business_initiative", "importance": 9}},
            {{"name": "Mobile Banking Platform", "type": "business_asset", "importance": 8}},
            {{"name": "ISO 27001 compliance", "type": "compliance_requirement", "importance": 7}}
        ]
        
        Valid types: business_initiative, business_asset, compliance_requirement, financial_data, geography
        Importance scale: 1-10 (10 = critical strategic importance)
        """
        
        try:
            response = self.llm.invoke(prompt)
            entities_text = response.content.strip()
            
            # Debug: Show LLM response
            print(f"      🤖 LLM Entity Response: {entities_text[:200]}{'...' if len(entities_text) > 200 else ''}")
            
            # Clean the response - remove markdown code blocks if present
            clean_text = entities_text
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]  # Remove ```json
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]   # Remove ```
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]  # Remove trailing ```
            clean_text = clean_text.strip()
            
            # Try to parse JSON response
            if clean_text.startswith('[') and clean_text.endswith(']'):
                try:
                    llm_data = json.loads(clean_text)
                    print(f"      ✅ Parsed {len(llm_data)} potential entities from LLM")
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
                            print(f"      🎯 Found LLM entity: {item['name']} ({item['type']}) - importance: {item.get('importance', 5)} - confidence: {min(item.get('importance', 5) / 10.0, 0.9):.2f}")
                    
                    print(f"      ✅ Successfully extracted {len(entities)} LLM entities")
                    print(f"      🏁 EXITING _extract_llm_entities with {len(entities)} entities")
                    return entities
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing error for entities: {e}")
                    print(f"      Raw cleaned text: {clean_text[:100]}...")
                    print(f"      🚫 EXITING _extract_llm_entities with 0 entities (JSON error)")
                    return []
            else:
                print(f"⚠️  LLM response doesn't look like JSON array: starts with '{clean_text[:20]}', ends with '{clean_text[-20:]}'")
                print(f"      🚫 EXITING _extract_llm_entities with 0 entities (not JSON array)")
                return []
            
        except Exception as e:
            print(f"⚠️  LLM entity extraction error: {e}")
            print(f"      🚫 EXITING _extract_llm_entities with 0 entities (exception)")
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
    
    def _extract_relationships_from_document(self, doc: Document, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract relationships between entities using LLM."""
        if not self.llm or len(entities) < 2:
            return []
        
        relationships = []
        content = doc.page_content[:3000]  # Limit context size
        
        # Create entity pairs for relationship extraction
        entity_pairs = []
        for i, entity1 in enumerate(entities[:10]):  # Limit to prevent prompt explosion
            for entity2 in entities[i+1:min(i+5, len(entities))]:  # Check up to 5 related entities
                entity_pairs.append((entity1, entity2))
        
        if not entity_pairs:
            return []
        
        # Build prompt for relationship extraction
        prompt = f"""Analyze the following text and identify relationships between the given entities.
        
TEXT:
{content}

ENTITY PAIRS TO ANALYZE:
"""
        for e1, e2 in entity_pairs[:15]:  # Limit pairs to prevent token overflow
            prompt += f"- {e1['name']} ({e1['type']}) <-> {e2['name']} ({e2['type']})\n"
        
        prompt += """
TASK: For each entity pair, determine if there's a relationship in the text and what type.

Return ONLY a JSON array with this format:
[
    {"source": "AWS", "relationship_type": "HOSTS", "target": "payment system", "confidence": 0.9, "evidence": "AWS hosts our payment system"},
    {"source": "payment system", "relationship_type": "PROCESSES", "target": "customer data", "confidence": 0.85, "evidence": "payment system processes customer data"}
]

Common relationship types (use these when applicable, but create specific ones when needed):
- USES, DEPENDS_ON, HOSTS, RUNS_ON (for technology dependencies)
- OWNS, MANAGES, RESPONSIBLE_FOR (for ownership)
- LOCATED_IN, OPERATES_IN, DEPLOYED_TO (for geography)
- REQUIRES, MUST_COMPLY_WITH, GOVERNED_BY (for compliance)
- INTEGRATES_WITH, CONNECTS_TO, SENDS_DATA_TO (for integrations)
- THREATENS, EXPLOITS, TARGETS (for security threats)
- IMPLEMENTS, SUPPORTS, ENABLES (for business processes)

Return empty array [] if no clear relationships exist.
"""
        
        try:
            response = self.llm.invoke(prompt)
            relationships_text = response.content.strip()
            
            # Debug: Show LLM response
            print(f"      🤖 LLM Response: {relationships_text[:200]}{'...' if len(relationships_text) > 200 else ''}")
            
            # Clean the response - remove markdown code blocks if present
            clean_text = relationships_text
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:]  # Remove ```json
            if clean_text.startswith('```'):
                clean_text = clean_text[3:]   # Remove ```
            if clean_text.endswith('```'):
                clean_text = clean_text[:-3]  # Remove trailing ```
            clean_text = clean_text.strip()
            
            # Parse JSON response
            if clean_text.startswith('[') and clean_text.endswith(']'):
                try:
                    llm_relationships = json.loads(clean_text)
                    print(f"      ✅ Parsed {len(llm_relationships)} potential relationships")
                    
                    for rel in llm_relationships:
                        if all(k in rel for k in ['source', 'relationship_type', 'target']):
                            print(f"      🔍 Trying to match: {rel['source']} -> {rel['target']}")
                            # Find matching entity IDs
                            source_id = None
                            target_id = None
                            
                            for entity in entities:
                                if entity['name'].lower() == rel['source'].lower():
                                    source_id = entity['id']
                                if entity['name'].lower() == rel['target'].lower():
                                    target_id = entity['id']
                            
                            print(f"      🎯 Match result: source_id={source_id}, target_id={target_id}")
                            
                            if source_id and target_id:
                                relationships.append({
                                    'source': source_id,
                                    'target': target_id,
                                    'relationship_type': rel['relationship_type'].upper().replace(' ', '_'),
                                    'confidence': rel.get('confidence', 0.7),
                                    'evidence': rel.get('evidence', ''),
                                    'source_document': doc.metadata.get('file_name', 'unknown')
                                })
                    
                    return relationships
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing error for relationships: {e}")
                    return []
            
            return []
            
        except Exception as e:
            print(f"⚠️  LLM relationship extraction error: {e}")
            return []