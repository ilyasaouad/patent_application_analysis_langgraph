"""
Agent Resources Helper - Load prompts, guidelines, and examples from resources_for_agents/

Usage:
    from resources_loader import load_agent_resources

    prompt, guidelines, examples = load_agent_resources("extract_claims")
"""

import os
from typing import Tuple, Optional
from pathlib import Path

RESOURCES_DIR = Path("resources_for_agents")


def load_file(agent_name: str, file_name: str) -> str:
    """Load a specific file from agent folder."""
    file_path = RESOURCES_DIR / agent_name / file_name
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_agent_resources(
    agent_name: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Load all resources for an agent.

    Returns: (prompt, guidelines, examples)
    """
    prompt = load_file(agent_name, "prompt.md")
    guidelines = load_file(agent_name, "guidelines.md")
    examples = load_file(agent_name, "examples.md")

    return prompt, guidelines, examples


def load_prompt(agent_name: str) -> str:
    """Load just the prompt."""
    prompt = load_file(agent_name, "prompt.md")
    if prompt:
        return prompt

    # Try fallback in agent folder
    fallback_dir = Path("resources", "agents", agent_name)
    if fallback_dir.exists():
        return ""

    raise FileNotFoundError(f"No prompt.md found for agent: {agent_name}")


if __name__ == "__main__":
    # Test
    prompt, guidelines, examples = load_agent_resources("extract_claims")
    print(f"extract_claims prompt: {len(prompt)} chars")
    print(f"extract_claims guidelines: {len(guidelines)} chars")
    print(f"extract_claims examples: {len(examples)} chars")
