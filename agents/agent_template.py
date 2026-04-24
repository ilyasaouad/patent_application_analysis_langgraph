"""
Agent Template - Copy this file to create new agents.

Structure:
1. Prompts (in resources/prompts/)
2. Examples (in resources/examples/)
3. Agent logic (in agents/)
"""

# =============================================================================
# PART 1: PROMPTS (resources/prompts/<agent_name>_prompt.md)
# =============================================================================
# Create: resources/prompts/extract_claims_prompt.md
# =============================================================================
"""
You are an expert patent analyzer. Your task is to identify and extract the CLAIMS section 
from the patent description text.

Guidelines:
- Look for headers like "PATENT CLAIMS", "KRAV", "CLAIMS"
- Extract ONLY the claims, not the description or abstract
- Maintain the original numbering

Return the extracted claims text ONLY.
"""

# =============================================================================
# PART 2: EXAMPLES (resources/examples/<agent_name>_examples.md)
# =============================================================================
# Create: resources/examples/extract_claims_examples.md
# =============================================================================
"""
Example 1:
Input: "...PATENT CLAIMS\n1. A system for processing data...\n2. The system of claim 1..."
Output: "PATENT CLAIMS\n1. A system for processing data...\n2. The system of claim 1..."

Example 2:
Input: "KRAV\n1. An apparatus comprising..."
Output: "KRAV\n1. An apparatus comprising..."
"""

# =============================================================================
# PART 3: AGENT CODE (agents/<agent_name>.py)
# =============================================================================
# Copy this template to agents/<your_agent>.py
# =============================================================================

import os
from typing import TypedDict
from graph_state import GraphState

# -----------------------------------------------------------------------------
# Configuration - Load guidelines and examples from files
# -----------------------------------------------------------------------------
AGENT_NAME = "my_agent"

PROMPTS_DIR = os.path.join("resources", "prompts")
EXAMPLES_DIR = os.path.join("resources", "examples")


def load_prompt() -> str:
    """Load agent prompt from file."""
    prompt_path = os.path.join(PROMPTS_DIR, f"{AGENT_NAME}_prompt.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a patent analysis agent."


def load_examples() -> str:
    """Load few-shot examples from file."""
    examples_path = os.path.join(EXAMPLES_DIR, f"{AGENT_NAME}_examples.md")
    if os.path.exists(examples_path):
        with open(examples_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def build_prompt(input_text: str) -> str:
    """Build full prompt with guidelines + examples."""
    prompt = load_prompt()
    examples = load_examples()

    full_prompt = prompt
    if examples:
        full_prompt += "\n\n### Examples:\n" + examples
    full_prompt += f"\n\n### Input:\n{input_text}"

    return full_prompt


# -----------------------------------------------------------------------------
# LLM Call - Customize for your model
# -----------------------------------------------------------------------------
def call_llm(prompt: str, model: str = "gpt-4o") -> str:
    """Call LLM with prompt. Customize based on your API."""
    from openai import OpenAI

    client = OpenAI()

    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}], temperature=0.0
    )
    return response.choices[0].message.content


# -----------------------------------------------------------------------------
# Agent Function - Main logic
# -----------------------------------------------------------------------------
def my_agent(state: GraphState) -> GraphState:
    """
    LangGraph Node: [Your agent description]

    Input from state: description_text, claims_text, etc.
    Output to state: analysis_result, status, etc.
    """
    # 1. Get input from state
    input_text = state.get("description_text", "")

    print(f"[{AGENT_NAME}] Processing input...")

    if not input_text:
        return {"status": "ERROR", "error_message": "No input text"}

    # 2. Build prompt
    prompt = build_prompt(input_text)

    # 3. Call LLM
    try:
        result = call_llm(prompt)
        return {"analysis_result": result, "status": "SUCCESS"}
    except Exception as e:
        return {"status": "ERROR", "error_message": str(e)}


# -----------------------------------------------------------------------------
# PART 4: Add to graph_workflow.py
# -----------------------------------------------------------------------------
# In graph_workflow.py, add:
#
# from agents.my_agent import my_agent
#
# workflow.add_node("my_agent", my_agent)
# workflow.add_edge("read_parse_document", "my_agent")
# workflow.add_edge("my_agent", "extract_claims")  # or whatever next node
