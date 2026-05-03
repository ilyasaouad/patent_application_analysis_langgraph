from typing import Literal
from langgraph.graph import StateGraph, START, END
from graph_state import GraphState
from agents.agent1_read_parse_document.read_parse_document import read_parse_document
from agents.agent3_no_claims_provided.no_claims_provided import no_claims_provided
from agents.agent2_extract_claims.extract_claims import extract_claims_agent
from agents.agent3b_claims_founded.claims_founded_agent import claims_founded_agent
from agents.agent2b_ai_generated_document.ai_generated_detection_agent import (
    ai_generated_detection_agent,
)
from agents.agent4a_claims_clarity.claims_clarity_agent import claims_clarity_agent
from agents.agent4b_claims_unity.claims_unity_agent import claims_unity_agent
from agents.agent4c_claims_antecedent.claims_antecedent_agent import (
    claims_antecedent_agent,
)
from agents.agent4_claims_legal_analyse.claims_legal_analyse_agent import (
    claims_legal_analyse_agent,
)
from agents.agent5_cpc_classify.cpc_classify_agent import cpc_classify_agent


def route_initial_claims_check(
    state: GraphState,
) -> Literal["extract_claims", "claims_founded"]:
    claims = state.get("claims_text")
    if not claims or not claims.strip():
        return "extract_claims"
    return "claims_founded"


def route_secondary_claims_check(
    state: GraphState,
) -> Literal["no_claims_provided", "claims_founded"]:
    claims = state.get("claims_text")
    if not claims or not claims.strip():
        return "no_claims_provided"
    return "claims_founded"


workflow = StateGraph(GraphState)

# Document extraction nodes
workflow.add_node("read_parse_document", read_parse_document)
workflow.add_node("extract_claims", extract_claims_agent)
workflow.add_node("no_claims_provided", no_claims_provided)

# Structural analysis node
workflow.add_node("claims_founded", claims_founded_agent)

# Parallel analysis nodes (all independent, only need raw texts)
workflow.add_node("ai_detection", ai_generated_detection_agent)
workflow.add_node("claims_clarity", claims_clarity_agent)
workflow.add_node("claims_unity", claims_unity_agent)
workflow.add_node("claims_antecedent", claims_antecedent_agent)

# Master synthesis node (waits for all parallel agents)
workflow.add_node("claims_legal_analyse", claims_legal_analyse_agent)

# CPC Classification node (Agent 5)
workflow.add_node("cpc_classify", cpc_classify_agent)

# Define the flow
workflow.add_edge(START, "read_parse_document")
workflow.add_conditional_edges("read_parse_document", route_initial_claims_check)
workflow.add_conditional_edges("extract_claims", route_secondary_claims_check)

# If no claims provided: end immediately with rejection letter
workflow.add_edge("no_claims_provided", END)

# After claims_founded: fan out to 5 parallel independent agents
workflow.add_edge("claims_founded", "ai_detection")
workflow.add_edge("claims_founded", "claims_clarity")
workflow.add_edge("claims_founded", "claims_unity")
workflow.add_edge("claims_founded", "claims_antecedent")
workflow.add_edge("claims_founded", "cpc_classify")

# Join: all 5 parallel agents must complete before Master agent
workflow.add_edge("ai_detection", "claims_legal_analyse")
workflow.add_edge("claims_clarity", "claims_legal_analyse")
workflow.add_edge("claims_unity", "claims_legal_analyse")
workflow.add_edge("claims_antecedent", "claims_legal_analyse")
workflow.add_edge("cpc_classify", "claims_legal_analyse")

# End after Master synthesis
workflow.add_edge("claims_legal_analyse", END)

app_graph = workflow.compile()
