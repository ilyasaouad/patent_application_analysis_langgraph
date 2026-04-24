import re
import os
import requests
from typing import Tuple
from graph_state import GraphState

# Load prompt from resources (easy to update without code changes)
PROMPT_PATH = os.path.join("resources_for_agents", "extract_claims", "prompt.md")


def load_prompt() -> str:
    """Load LLM prompt from file, fallback to inline."""
    if os.path.exists(PROMPT_PATH):
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    # Fallback inline prompt
    return (
        "You are an expert patent document analyzer. "
        "I will provide you with the text of a patent description. "
        "Your task is to identify and extract ONLY the 'Claims' or 'Patent Claims' section of the patent. "
        "Please return ONLY the exact extracted claims text. Do not add any preamble, explanations, or conversational text."
    )


def clean_margin_numbers(text: str) -> str:
    """
    Cleans OCR margin line numbers (like 1, 5, 10, 15) that get accidentally scattered
    throughout the text during OCR.
    """
    cleaned = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
    cleaned = re.sub(r"^(#+)\s*\d+\s+", r"\1 ", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*\d+\s+(?=[A-Za-z])", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_claims_regex(text: str) -> Tuple[str, str]:
    """
    Detects and extracts the claims section from the description text using standard regular expressions.
    Returns a tuple: (extracted_claims_text, remaining_description_text)
    """
    pattern = re.compile(
        r"^(#*\s*(?:PATENT\s+)?CLAIMS?|PATENTKRAV|KRAV)\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    match = pattern.search(text)
    if not match:
        return "", text

    start_idx = match.start()

    end_pattern = re.compile(
        r"^(#+\s*ABSTRACT|SAMMENDRAG)\s*$", re.IGNORECASE | re.MULTILINE
    )
    end_match = end_pattern.search(text, match.end())

    if end_match:
        end_idx = end_match.start()
        claims_text = text[start_idx:end_idx].strip()
        rest_of_text = (text[:start_idx] + "\n\n" + text[end_idx:]).strip()
        return claims_text, rest_of_text
    else:
        claims_text = text[start_idx:].strip()
        rest_of_text = text[:start_idx].strip()
        return claims_text, rest_of_text


def extract_claims_llm_fallback(text: str) -> Tuple[str, str]:
    """
    Method using a local Ollama LLM to extract claims.
    """
    print("Executing LLM fallback extraction...")
    url = "http://localhost:11434/api/generate"
    prompt = load_prompt() + f"\n\n--- Patent Description ---\n{text}"
    payload = {"model": "gpt-oss:120b-cloud", "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=300)
        if response.status_code == 200:
            claims_text = response.json().get("response", "").strip()
            if not claims_text:
                return "", text

            if claims_text in text:
                rest_of_text = text.replace(claims_text, "").strip()
                return claims_text, rest_of_text

            start_substring = claims_text[:50]
            end_substring = claims_text[-50:]
            start_idx = text.find(start_substring)
            end_idx = text.rfind(end_substring)

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                exact_claims = text[start_idx : end_idx + len(end_substring)]
                rest_of_text = (
                    text[:start_idx] + "\n\n" + text[end_idx + len(end_substring) :]
                ).strip()
                return exact_claims, rest_of_text

            return claims_text, text
    except requests.exceptions.RequestException as e:
        print(f"Failed to connect to Ollama fallback API: {e}")
        pass

    return "", text


def extract_claims(description_text: str) -> Tuple[str, str]:
    """
    Coordinates the extraction of claims from the description body.
    Returns (claims_text, clean_description_text)
    """
    orig_text = clean_margin_numbers(description_text)
    if not orig_text:
        return "", ""

    orig_len = len(orig_text)
    final_claims, final_remaining = extract_claims_regex(orig_text)

    is_regex_good = (
        final_claims and len(final_claims) > 50 and len(final_claims) < (orig_len * 0.9)
    )

    if not is_regex_good:
        print("Regex claim extraction unavailable/insufficient. Trying LLM fallback...")
        llm_claims, llm_remaining = extract_claims_llm_fallback(orig_text)
        if llm_claims and len(llm_claims) > 50:
            return llm_claims, llm_remaining

        # If everything fails, return whatever regex gave us, or blank.
        if final_claims:
            return final_claims, final_remaining
        return "", orig_text

    return final_claims, final_remaining


def extract_claims_agent(state: GraphState) -> GraphState:
    """
    LangGraph Node: Triggered independently if initial backend extraction fails to isolate claims.
    Takes the available description_text and attempts Regex/LLM structural splitting.
    """
    desc_text = state.get("description_text", "")

    print(
        "[Extract Claims Agent] Routing hit. Attempting to artificially extract claims from description body..."
    )

    if not desc_text or not desc_text.strip():
        print("[Extract Claims Agent] Description text is empty. Nothing to analyze.")
        return {}  # Leaves state as is, prompting immediate routing to empty_claims

    extracted_claims, remaining_desc = extract_claims(desc_text)

    if extracted_claims and extracted_claims.strip():
        print(
            f"[Extract Claims Agent] Extracted {len(extracted_claims)} characters. Updating State."
        )
        return {"description_text": remaining_desc, "claims_text": extracted_claims}
    else:
        print(
            "[Extract Claims Agent] Both Regex and LLM extraction completely failed. Passing empty state forward."
        )
        return {}
