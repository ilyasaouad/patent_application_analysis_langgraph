# Agent 4C: Claims Antecedent Basis Analysis

## Overview

Agent 4C performs **antecedent basis analysis** on patent claims to ensure that all definite references ("the X", "said X", "this X", "that X") have proper antecedent introductions ("a X", "an X", or implicit introductions) within the same claim or ancestor claims.

This is a critical patent examination step under EPO and NIPO standards, ensuring claims are internally consistent and properly drafted.

## Architecture

```
agents/agent4c_claims_antecedent/
├── __init__.py                          # Package initialization
├── antecedent_NLP_analyzer.py           # Core spaCy NLP analysis
├── antecedent_llm_fallback.py          # LLM fallback for ambiguous cases
├── claims_antecedent_agent.py          # LangGraph agent wrapper
└── resources/                          # Additional resources
```

## Files Description

### 1. `__init__.py`
**Purpose**: Package initialization and exports.

**Exports**:
- `claims_antecedent_agent` - Main agent function
- `run_antecedent_analysis` - Standalone analysis function
- `AntecedentAnalyzer` - Core analyzer class
- `Claim` - Data class for claim representation

**Usage**:
```python
from agents.agent4c_claims_antecedent import claims_antecedent_agent
```

---

### 2. `antecedent_NLP_analyzer.py`
**Purpose**: Core antecedent basis analysis using **spaCy NLP**.

**Key Classes**:

#### `Claim`
Dataclass representing a single patent claim.
- `number`: int - Claim number
- `text`: str - Full claim text
- `dependencies`: List[int] - Claim numbers this claim depends on

#### `AntecedentIssue`
Dataclass representing a missing antecedent issue.
- `claim_number`: int - Claim with the issue
- `term`: str - The missing antecedent term
- `definite_reference`: str - Full definite reference (e.g., "the actuator")
- `context`: str - Text context around the issue
- `confidence`: str - "high", "medium", or "low"
- `reasoning`: str - Explanation of why it's an issue

#### `AntecedentAnalyzer`
Main analyzer class with spaCy NLP capabilities.

**Key Methods**:

| Method | Description |
|--------|-------------|
| `__init__(use_spacy=True)` | Initialize analyzer with optional spaCy |
| `analyze_all_claims(claims_text)` | Analyze all claims and return results |
| `analyze_claim(claim, all_claims)` | Analyze single claim with cross-claim context |
| `get_ambiguous_terms(claim)` | Identify terms needing LLM validation |
| `_extract_definite_references(text)` | Extract "the X", "said X" patterns |
| `_extract_antecedents(text)` | Extract "a X", "an X" introductions |
| `_find_ancestor_claims(claim, all_claims)` | Find claims this claim depends on |
| `_normalize_term(term)` | Normalize terms for comparison (handles plurals) |

**Pattern Matching**:

**Definite References** (requiring antecedent):
```python
DEFINITE_PATTERNS = [
    r'\b(the|said|this|that)\s+([a-zA-Z][a-zA-Z0-9\-_\s]{2,100})\b'
]
```

**Indefinite Introductions** (antecedents):
```python
INDEFINITE_PATTERNS = [
    r'\b(a|an)\s+([a-zA-Z][a-zA-Z0-9\-_\s]{2,100})\b',
    r'\b(one\s+or\s+more\s+[a-zA-Z]+|plurality\s+of\s+[a-zA-Z]+)\b'
]
```

**Ignored Terms** (generic patent terms):
```python
IGNORE_TERMS = {
    'method', 'apparatus', 'system', 'device', 'invention', 
    'embodiment', 'example', 'claim', 'figure', 'fig',
    'step', 'process', 'apparatus', 'composition'
}
```

**Analysis Flow**:
1. Parse claims from text
2. For each claim:
   - Extract definite references ("the X")
   - Extract intra-claim antecedents ("a X")
   - Find ancestor claims
   - Extract ancestor claim antecedents
   - Check if each definite reference has matching antecedent
   - Handle singular/plural variants
3. Return list of missing antecedents

**Output Format**:
```json
{
  "status": "SUCCESS",
  "claim_count": 20,
  "issues_found": 3,
  "claims_with_issues": 2,
  "issues": [
    {
      "claim_number": 5,
      "term": "actuator",
      "definite_reference": "the actuator",
      "context": "...comprising a housing, the actuator...",
      "confidence": "high",
      "reasoning": "No antecedent found for 'the actuator' in claim 5 or ancestor claims"
    }
  ]
}
```

**Dependencies**: spaCy (optional but recommended)
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

If spaCy is not installed, falls back to regex-based analysis.

---

### 3. `antecedent_llm_fallback.py`
**Purpose**: LLM validation for ambiguous antecedent cases.

**Key Function**:

#### `llm_validate_antecedents()`
Uses Ollama LLM to validate ambiguous antecedent cases that spaCy cannot resolve confidently.

**Parameters**:
- `claim_num`: int - Claim number being analyzed
- `claim_text`: str - Full claim text
- `ambiguous_terms`: List[str] - Terms needing validation
- `ancestor_texts`: str - Combined ancestor claim texts
- `model_name`: str - Ollama model (default: "gpt-oss:120b-cloud")

**LLM Prompt Structure**:
- System prompt defines antecedent rules
- User prompt includes claim text, ambiguous terms, and ancestor context
- Returns structured JSON with missing and valid antecedents

**Return Format**:
```json
{
  "missing_antecedents": ["the actuator", "said housing"],
  "valid_antecedents": ["the plate"],
  "reasoning": "Brief explanation",
  "confidence": "high/medium/low"
}
```

**Usage**:
```python
from agents.agent4c_claims_antecedent.antecedent_llm_fallback import llm_validate_antecedents

result = llm_validate_antecedents(
    claim_num=5,
    claim_text="A system comprising a housing, the actuator...",
    ambiguous_terms=["the actuator"],
    ancestor_texts="Claim 1: A system comprising..."
)
```

---

### 4. `claims_antecedent_agent.py`
**Purpose**: LangGraph-compatible agent wrapper.

**Function**:

#### `claims_antecedent_agent(state)`
Main entry point for LangGraph integration.

**Parameters**:
- `state`: GraphState - Contains claims_text or reads from file

**Workflow**:
1. Read claims from state or `output_text_documents/claims.md`
2. Initialize `AntecedentAnalyzer`
3. Run spaCy analysis on all claims
4. Identify ambiguous terms
5. Run LLM fallback for ambiguous cases (if any)
6. Merge and deduplicate results
7. Generate human-readable report
8. Save results to `claims_analyse_reports/antecedent_analyse/`

**Output Files**:
```
claims_analyse_reports/antecedent_analyse/
├── claims_antecedent_result.json    # Structured results
└── claims_antecedent_report.md      # Human-readable report
```

**Standalone Usage**:
```python
from agents.agent4c_claims_antecedent import run_antecedent_analysis

results = run_antecedent_analysis(claims="1. A system...")
```

---

## Analysis Logic

### Intra-Claim Analysis
For each claim, checks if definite references have antecedents **within the same claim** (earlier in the text).

Example:
```
Claim 5: "A system comprising a housing, the actuator..."
                                          ^^^^^^^^^^^^
                                          Missing antecedent!
                                          (No "an actuator" earlier in claim)
```

### Cross-Claim Analysis
For dependent claims, checks **ancestor claims** for antecedents.

Example:
```
Claim 1: "A system comprising a housing and an actuator..."
                                          ^^^^^^^^^^^^
                                          Antecedent introduced

Claim 5 (depends on Claim 1): "The system of claim 1, wherein the actuator..."
                                                              ^^^^^^^^^^^^
                                                              Valid! (from Claim 1)
```

### Singular/Plural Matching
Handles variants:
- "plate" ≈ "plates"
- "top plate" ≈ "plate"
- "actuator" ≈ "actuators"

### Confidence Levels
- **High**: Clear missing antecedent with no matching term
- **Medium**: Potential issue, may need review
- **Low**: Ambiguous case, requires human review

## Integration with Streamlit

To add Agent 4C to `streamlit_app_next_agents.py`:

```python
from agents.agent4c_claims_antecedent import claims_antecedent_agent

# Add new tab
tab6 = st.tabs([... "🔗 Antecedent Basis"])

with tab6:
    if st.button("Analyze Antecedent Basis"):
        with st.spinner("Analyzing antecedent basis..."):
            result = claims_antecedent_agent(state)
            # Display results...
```

## Dependencies

- **spaCy** (optional): For enhanced NLP analysis
  ```bash
  pip install spacy
  python -m spacy download en_core_web_sm
  ```
- **Ollama**: For LLM fallback validation
- **agents.claims_analyse_libs**: Shared libraries (config, core, utils)

## Error Handling

- **spaCy not installed**: Falls back to regex-based analysis
- **No claims found**: Returns error with instructions
- **LLM unavailable**: Returns spaCy-only results
- **Unicode errors**: Handled gracefully

## Future Enhancements

- [ ] Support for more complex noun phrases
- [ ] Better handling of implicit antecedents
- [ ] Integration with description text for broader context
- [ ] Visualization of claim dependencies
- [ ] Batch processing for multiple patent applications

## References

- EPO Guidelines for Examination
- NIPO Examination Guidelines
- Patent Claim Drafting Best Practices

---

**Created**: 2026-04-27
**Author**: Patent Analysis System
**Status**: Production Ready
