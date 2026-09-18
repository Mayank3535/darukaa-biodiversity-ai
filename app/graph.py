from typing import Any, Dict, List, TypedDict, Optional

from langgraph.graph import END, StateGraph

from app.llm import extract_json
from app.prompts import (
    CLARIFICATION_PROMPT,
    EXTRACTION_PROMPT,
    REASONING_PROMPT,
)
from app.retrieval import retrieve


class GraphState(TypedDict, total=False):
    user_input: str
    previous_state: Dict[str, Any]
    environmental_state: Dict[str, Any]
    missing: List[str]
    evidence: List[Dict[str, Any]]
    answer: Dict[str, Any]


def parse_node(state: GraphState) -> GraphState:
    previous_state = state.get("previous_state", {})

    extraction_prompt = EXTRACTION_PROMPT + f"""

PREVIOUS ENVIRONMENTAL CONTEXT:

{previous_state}

CURRENT USER MESSAGE:

{state["user_input"]}

IMPORTANT:

Merge information from the previous context with information
explicitly provided in the current message.

The current message takes precedence when it provides a new
value.

Do not invent values.

If a field is known from previous context and the user does not
change it, preserve it.
"""

    extracted = extract_json(extraction_prompt)

    return {
        **state,
        "environmental_state": extracted,
    }


def validate_node(state: GraphState) -> GraphState:
    env = state.get("environmental_state", {})

    missing = []

    if not env.get("region"):
        missing.append("region or climatic zone")

    if not env.get("rainfall"):
        missing.append("rainfall or water-availability information")

    soil = env.get("soil") or {}

    if soil.get("organic_carbon") is None:
        missing.append("soil organic carbon or another soil-health indicator")

    land_use = env.get("land_use") or {}

    if not land_use.get("crop"):
        missing.append("current crop or vegetation")

    if not land_use.get("system"):
        missing.append("land-use system, such as monoculture, mixed cropping, agroforestry, pasture, or natural vegetation")

    return {
        **state,
        "missing": missing,
    }


def route_after_validation(state: GraphState):
    missing = state.get("missing", [])

    # We only interrupt the workflow when several important
    # variables are unavailable.
    if len(missing) >= 2:
        return "clarify"

    return "retrieve"


def clarify_node(state: GraphState) -> GraphState:
    missing = state.get("missing", [])

    prompt = CLARIFICATION_PROMPT.format(
        missing="\n".join(f"- {item}" for item in missing)
    )

    answer = {
        "type": "clarification",
        "message": extract_json(
            """
Return JSON:
{
  "message": "..."
}

""" + prompt
        ).get("message", prompt)
    }

    return {
        **state,
        "answer": answer,
    }


def retrieve_node(state: GraphState) -> GraphState:
    env = state.get("environmental_state", {})

    retrieval_query = f"""
    Environmental assessment.

    Region: {env.get("region")}

    Rainfall: {env.get("rainfall")}

    Soil: {env.get("soil")}

    Land use: {env.get("land_use")}

    Biodiversity: {env.get("biodiversity")}

    Climate: {env.get("climate")}
    """

    evidence = retrieve(retrieval_query, k=5)

    return {
        **state,
        "evidence": evidence,
    }


def reason_node(state: GraphState) -> GraphState:
    env = state.get("environmental_state", {})
    evidence = state.get("evidence", [])

    evidence_text = "\n\n".join(
        [
            (
                f"SOURCE {i + 1}\n"
                f"Title: {item.get('title')}\n"
                f"Organization: {item.get('organization')}\n"
                f"URL: {item.get('url')}\n"
                f"Topic: {item.get('topic')}\n"
                f"Content: {item.get('content')}"
            )
            for i, item in enumerate(evidence)
        ]
    )

    prompt = REASONING_PROMPT.replace("{state}", str(env)).replace("{evidence}", evidence_text)

    answer = extract_json(prompt)

    return {
        **state,
        "answer": answer,
    }


builder = StateGraph(GraphState)

builder.add_node("parse", parse_node)
builder.add_node("validate", validate_node)
builder.add_node("clarify", clarify_node)
builder.add_node("retrieve", retrieve_node)
builder.add_node("reason", reason_node)

builder.set_entry_point("parse")

builder.add_edge("parse", "validate")

builder.add_conditional_edges(
    "validate",
    route_after_validation,
    {
        "clarify": "clarify",
        "retrieve": "retrieve",
    },
)

builder.add_edge("clarify", END)
builder.add_edge("retrieve", "reason")
builder.add_edge("reason", END)

graph = builder.compile()