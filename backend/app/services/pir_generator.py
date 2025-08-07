from langchain_openai import ChatOpenAI
from langchain.chains import GraphQAChain
from langchain_community.graphs import Neo4jGraph

# Initialize a powerful LLM for the analysis task
llm = ChatOpenAI(temperature=0.1, model_name="gpt-4o")

# Initialize the Neo4jGraph object for LangChain to interact with
graph = Neo4jGraph()

# This is a more advanced chain that can reason over the graph
chain = GraphQAChain.from_llm(llm=llm, graph=graph, verbose=True)

# The prompt is the "brain" of this operation.
# It instructs the LLM how to behave.
PIR_GENERATION_PROMPT = """
You are a world-class threat intelligence analyst working for a system named cAIber.
Your task is to analyze the complete knowledge graph of an organization and
proactively generate Priority Intelligence Requirements (PIRs).

Based on all the information available in the graph, identify the top 3-5 strategic
business initiatives, key technologies, people, or assets.

For each, formulate a concise, actionable intelligence requirement that would help
the security team mitigate potential threats. Frame these as suggestions.

Example: "Analysis of business plans indicates expansion into Southeast Asia.
Suggest prioritizing intelligence on threat actors targeting financial services in that region,
particularly those exploiting supply chain vulnerabilities."

Now, analyze the provided graph data and generate the PIRs.
"""

def generate_pirs() -> dict:
    """
    Analyzes the entire knowledge graph to generate Priority Intelligence Requirements (PIRs).
    
    Returns:
        dict: The LLM's generated response containing suggested PIRs.
    """
    return chain.invoke(PIR_GENERATION_PROMPT)