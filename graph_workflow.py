from typing import Literal
from langgraph.graph import StateGraph, START, END
from graph_state import GraphState
from agents.agent1_read_parse_document.read_parse_document import read_parse_document
from agents.agent3_no_claims_provided.no_claims_provided import no_claims_provided
from agents.agent2_extract_claims.extract_claims import extract_claims_agent


def route_initial_claims_check(
    state: GraphState,
) -> Literal["extract_claims", "__end__"]:
    claims = state.get("claims_text")
    if not claims or not claims.strip():
        return "extract_claims"
    return "__end__"


def route_secondary_claims_check(
    state: GraphState,
) -> Literal["no_claims_provided", "__end__"]:
    claims = state.get("claims_text")
    if not claims or not claims.strip():
        return "no_claims_provided"
    return "__end__"


workflow = StateGraph(GraphState)

workflow.add_node("read_parse_document", read_parse_document)
workflow.add_node("extract_claims", extract_claims_agent)
workflow.add_node("no_claims_provided", no_claims_provided)

workflow.add_edge(START, "read_parse_document")
workflow.add_conditional_edges("read_parse_document", route_initial_claims_check)
workflow.add_conditional_edges("extract_claims", route_secondary_claims_check)
workflow.add_edge("no_claims_provided", END)

app_graph = workflow.compile()
