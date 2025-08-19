
```markdown
# cAIber Threat Intelligence Platform - Development Task

## Project Overview
cAIber is an AI-powered threat intelligence platform that transforms reactive cybersecurity into proactive, business-aware defense. The system uses multi-agent architecture with Neo4j knowledge graphs to understand organizational context and generate actionable threat intelligence.

## High-Level System Flow (Our Agreed Architecture)

### Stage 1: Organizational DNA & Interactive Analysis ✅ COMPLETE
**Flow**: Documents → 3-layer entity extraction → Knowledge graph → Dual LLM approach
- **Organizational DNA Construction**: Multi-layer NLP pipeline builds Neo4j knowledge graph
- **Interactive Chatbot**: LLM with knowledge graph context for cybersecurity professional queries
- **PIR Generation**: Separate LLM analyzes complete organizational DNA to generate Priority Intelligence Requirements

### Stage 2: PIR-Driven Threat Collection ⚠️ PARTIALLY COMPLETE  
**Flow**: PIRs → Collection agent filtering → Curated threat landscape
- **PIR-Driven Collection**: Generated PIRs guide automated threat collection from external feeds
- **Multi-Feed Integration**: OTX (working) + additional feeds (CVE, GitHub Security) 
- **Intelligent Filtering**: Beyond keyword matching to build relevant threat landscape

### Stage 3: Multi-Context Risk Correlation ❌ NEEDS IMPLEMENTATION
**Flow**: Threat landscape + Organizational DNA + Raw entities → Risk assessment
- **Correlation Agent**: Access to threat landscape, organizational DNA, and raw entity data
- **Multi-Tool Analysis**: Agent uses multiple context sources for comprehensive analysis
- **Risk Scoring**: Output individual threat risk levels with business-aware reasoning

## Current System Architecture

### Stage 1: Organizational DNA Engine ✅ COMPLETE
- **Document Processing** (`document_processor.py`): Multi-format document ingestion with intelligent classification
- **Entity Extraction** (`entity_extractor.py`): 3-layer NLP pipeline (regex + spaCy + LLM) for comprehensive entity identification
- **Knowledge Graph** (`knowledge_graph_builder.py`): Neo4j-based organizational relationship modeling
- **PIR Generation** (`pir_generator_main.py`): Dynamic Priority Intelligence Requirements from organizational context

### Stage 2: Threat Collection ⚠️ PARTIALLY COMPLETE
- **Collection Framework** (`collection_agent.py`): BaseAgent + OTXAgent with PIR-driven filtering
- **STIX Integration**: Industry-standard threat intelligence formatting
- **Missing**: Additional threat feeds (CVE, GitHub Security Advisories)

### Stage 3: Risk Correlation ❌ NEEDS IMPLEMENTATION
**Key Requirement**: Multi-context agent with access to:
- Threat landscape from Stage 2
- Organizational DNA knowledge graph from Stage 1  
- Raw entity information from Stage 1
- Any other relevant context

## Implementation Tasks

### Priority 1: Correlation Agent (`correlation_agent.py`)
Create the multi-context risk assessment agent as outlined in our flow:

```python
class CorrelationAgent:
    def __init__(self, knowledge_graph, threat_landscape, raw_entities):
        """
        Multi-context correlation agent with access to:
        - knowledge_graph: Neo4j organizational DNA
        - threat_landscape: Curated threats from collection agents  
        - raw_entities: Original entity extraction results
        """
        self.kg = knowledge_graph  # Organizational DNA
        self.threat_landscape = threat_landscape  # Stage 2 output
        self.raw_entities = raw_entities  # Stage 1 entity data
        self.llm = ChatOpenAI(model="gpt-4o")
        
        # Multi-tool setup as per our architecture
        self.tools = {
            "query_org_dna": self._query_knowledge_graph,
            "analyze_threat_patterns": self._analyze_threat_landscape,
            "cross_reference_entities": self._cross_reference_raw_entities,
            "assess_business_impact": self._assess_business_context,
            "calculate_exploitability": self._assess_technical_risk
        }
    
    def correlate_threats(self, threat_list):
        """
        Main correlation function using multi-tool approach.
        Agent decides which tools to use for each threat.
        """
        risk_assessments = []
        
        for threat in threat_list:
            # Agent determines what context it needs
            required_context = self._determine_context_needs(threat)
            
            # Gather context using available tools
            context = self._gather_context(threat, required_context)
            
            # Generate risk assessment using all context
            risk_assessment = self._generate_risk_score(threat, context)
            
            risk_assessments.append(risk_assessment)
            
        return risk_assessments
    
    def _gather_context(self, threat, context_needs):
        """Use multiple tools to gather comprehensive context"""
        context = {}
        for tool_name in context_needs:
            if tool_name in self.tools:
                context[tool_name] = self.tools[tool_name](threat)
        return context
```

### Priority 2: Enhanced Stage 2 - Additional Threat Feeds
Complete the threat landscape building:

```python
class CVEAgent(BaseAgent):
    """CVE database integration for vulnerability intelligence"""
    def collect(self):
        # NVD CVE API integration
        # Filter for technologies in organizational DNA
        
class GitHubSecurityAgent(BaseAgent):
    """GitHub Security Advisories for open source vulnerabilities"""
    def collect(self):
        # GitHub Security Advisory API
        # Focus on dependencies in organizational codebase

# Enhanced threat landscape aggregator
class ThreatLandscapeBuilder:
    def __init__(self, collection_agents, pir_keywords):
        self.agents = collection_agents
        self.pir_keywords = pir_keywords
    
    def build_threat_landscape(self):
        """Aggregate and deduplicate threats from all sources"""
        # Combine OTX + CVE + GitHub Security data
        # Apply PIR-driven filtering
        # Return curated threat landscape for Stage 3
```

### Priority 3: Stage 1 Interactive Chatbot Enhancement
Implement the organizational DNA chatbot:

```python
class OrganizationalDNAChatbot:
    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.chain = GraphCypherQAChain.from_llm(
            llm=ChatOpenAI(model="gpt-4o"),
            graph=Neo4jGraph(),
            verbose=True
        )
    
    def chat(self, user_query):
        """
        Interactive queries about organizational DNA.
        Examples:
        - "What technologies do we use in our Southeast Asia expansion?"
        - "Which business initiatives face the highest cyber risk?"
        - "How is our mobile banking app connected to our AWS infrastructure?"
        """
        response = self.chain.invoke(user_query)
        return response
```

### Priority 4: Pipeline Integration
Connect all stages as per our agreed flow:

```python
class cAIberPipeline:
    def __init__(self):
        # Stage 1 components
        self.org_dna_chatbot = OrganizationalDNAChatbot(knowledge_graph)
        self.pir_generator = PIRGenerator()
        
        # Stage 2 components  
        self.threat_landscape_builder = ThreatLandscapeBuilder(
            agents=[OTXAgent(), CVEAgent(), GitHubSecurityAgent()],
            pir_keywords=[]
        )
        
        # Stage 3 component
        self.correlation_agent = CorrelationAgent(
            knowledge_graph=knowledge_graph,
            threat_landscape=None,  # Will be populated
            raw_entities=entity_repository
        )
    
    async def run_complete_analysis(self):
        """Execute the complete flow we designed"""
        # Stage 1: Generate PIRs from organizational DNA
        pirs = self.pir_generator.generate_pirs()
        
        # Stage 2: Build threat landscape using PIRs
        threat_landscape = self.threat_landscape_builder.build_threat_landscape()
        
        # Stage 3: Correlate threats with organizational context
        risk_assessments = self.correlation_agent.correlate_threats(threat_landscape)
        
        return {
            "pirs": pirs,
            "threat_landscape": threat_landscape, 
            "risk_assessments": risk_assessments
        }
```

### Priority 5: Enhanced API Endpoints
Support the complete flow:

```python
@app.post("/chat/organizational-dna")
async def chat_with_org_dna(query: str):
    """Interactive chatbot for organizational DNA queries"""

@app.get("/threats/landscape") 
async def get_threat_landscape():
    """Retrieve curated threat landscape from Stage 2"""

@app.post("/threats/correlate")
async def correlate_threats():
    """Run Stage 3 correlation analysis"""

@app.get("/pipeline/run-complete")
async def run_complete_pipeline():
    """Execute full Stage 1 → 2 → 3 flow"""
```

## Success Criteria Based on Our Flow
1. **Stage 1**: Interactive organizational DNA chatbot + dynamic PIR generation
2. **Stage 2**: PIR-driven multi-feed threat collection building relevant threat landscape  
3. **Stage 3**: Multi-context correlation agent producing business-aware risk assessments
4. **Integration**: Seamless data flow between all stages
5. **Demo Ready**: Can demonstrate complete organizational understanding → threat awareness → risk assessment workflow

## Notes
- Follow the specific multi-context approach for Stage 3 correlation agent
- Maintain the PIR-driven filtering approach from Stage 1 to Stage 2
- Interactive chatbot should leverage existing GraphCypherQAChain setup
- All agents follow BaseAgent inheritance pattern
- Frontend/visualization deprioritized - focus on core intelligence pipeline
```

Now the Claude Code instructions match exactly the architecture flow you outlined earlier!