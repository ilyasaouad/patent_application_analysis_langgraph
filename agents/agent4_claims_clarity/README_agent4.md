# Agent 4: Claims Clarity Analysis

## Overview

Agent 4 performs **legal clarity analysis** on patent claims under Norwegian Patents Act §8. It analyzes three key legal aspects:
- **Enablement** (Art. 83 EPC / §8 Patentloven): Can a skilled person reproduce the invention?
- **Clarity** (Art. 84 EPC): Are claims clear, precise, and unambiguous?
- **Support** (Art. 84 EPC): Are claims supported by the description?

This analysis assists patent examiners in identifying legal deficiencies before formal examination.

## Architecture

```
agents/agent4_claims_clarity/
├── __init__.py                          # Package initialization
├── claims_clarity_agent.py              # LangGraph agent wrapper
├── claims_legal_analyzer.py             # Core legal analyzer
├── claims_config/                       # Configuration & prompts
│   ├── __init__.py
│   └── legal_prompts.py                 # Legal analysis prompts
├── claims_core/                         # Core models
│   ├── __init__.py
│   └── legal_models.py                  # Data models
├── claims_utils/                        # Utilities
│   ├── __init__.py
│   └── guideline_loader.py              # NIPO guideline loader
├── resources/                           # Guidelines & resources
│   └── guidelines/
│       ├── clarity.txt
│       ├── enablement.txt
│       └── support.txt
└── skill.md                             # Skill documentation
```

## Files Description

### 1. `__init__.py`
**Purpose**: Package initialization and exports.

**Exports**:
- `claims_clarity_agent` - Main agent function
- `PatentLegalAnalyzer` - Core legal analyzer class

**Usage**:
```python
from agents.agent4_claims_clarity import claims_clarity_agent
```

---

### 2. `claims_clarity_agent.py`
**Purpose**: LangGraph-compatible agent wrapper for claims clarity analysis.

**Function**:

#### `claims_clarity_agent(state)`
Main entry point for LangGraph integration.

**Parameters**:
- `state`: GraphState - Contains description_text, claims_text, drawings_text

**Workflow**:
1. Read extracted documents from state or `output_text_documents/`
2. Initialize `PatentLegalAnalyzer` with configuration
3. Run three-phase legal analysis:
   - Enablement analysis
   - Clarity analysis  
   - Support analysis
4. Generate overall assessment
5. Create formal NIPO examination report
6. Save results to `claims_analyse_reports/clarity_analyse/`

**Output Files**:
```
claims_analyse_reports/clarity_analyse/
├── claims_clarity_result.json      # Structured JSON results
└── claims_clarity_report.md        # Formal NIPO examination report
```

**Output Format**:
```json
{
  "status": "SUCCESS",
  "enablement": {
    "status": "ENABLED" | "NOT_ENABLED",
    "issues": ["Missing algorithm details", "No working examples"],
    "missing_elements": ["Specific parameters", "Implementation steps"],
    "reproducibility_score": 0.75,
    "confidence": "HIGH"
  },
  "clarity": {
    "status": "CLEAR" | "UNCLEAR",
    "vague_terms": ["optimal", "suitable"],
    "undefined_terms": ["processing unit"],
    "clarity_score": 0.65
  },
  "support": {
    "status": "SUPPORTED" | "NOT_SUPPORTED",
    "unsupported_elements": ["Feature X not in description"],
    "support_score": 0.80
  },
  "overall": {
    "risk_level": "MEDIUM",
    "examination_decision": "FURTHER_EXAMINATION",
    "summary": "Claims require clarification..."
  },
  "formal_report": "**Formal Objection:** The application..."
}
```

---

### 3. `claims_legal_analyzer.py`
**Purpose**: Core legal analyzer implementing three-phase patent examination.

**Key Class**:

#### `PatentLegalAnalyzer`
Main analyzer implementing NIPO examination standards.

**Key Methods**:

| Method | Description |
|--------|-------------|
| `__init__(config)` | Initialize with AnalyzerConfig |
| `analyze(claims, description, drawings)` | Run full three-phase analysis |
| `_analyze_enablement(claims, description)` | Enablement compliance check |
| `_analyze_clarity(claims)` | Claim clarity evaluation |
| `_analyze_support(claims, description, drawings)` | Support validation |
| `_generate_formal_report(results)` | Generate NIPO examination report |
| `_load_guidelines()` | Load NIPO examination guidelines |

**Analysis Phases**:

#### Phase 1: Enablement (Art. 83 EPC / §8)
Checks if the description enables the claims by verifying:
- Missing technical parameters (ranges, values)
- Lack of implementation details
- Functional language without mechanism
- Absence of working examples
- Reproducibility assessment

#### Phase 2: Clarity (Art. 84 EPC)
Evaluates claims for:
- Vague terms ("optimal", "suitable", "appropriate")
- Undefined terms
- Overly broad functional language
- Missing structural limitations
- Ambiguous phrases

#### Phase 3: Support (Art. 84 EPC)
Validates:
- Claim elements have basis in description
- Embodiments cover claim scope
- Drawings referenced and explained
- Claims not broader than description

---

### 4. `claims_config/legal_prompts.py`
**Purpose**: LLM prompts for legal analysis with NIPO standards.

**Key Components**:

#### `ENABLEMENT_SYSTEM`
System prompt for enablement analysis with:
- Norwegian Patents Act §8 legal standard
- EPO Board of Appeal exemplars (T 0488/13, T 0024/10, T 0899/91)
- Strict JSON output format
- Overreach filter (no mandatory language)
- Legal citation rules (only §8(2))

#### `CLARITY_SYSTEM`
System prompt for clarity analysis with:
- Art. 84 EPC legal standard
- EPO exemplars for vague terms
- Specific issue categories
- JSON output format

#### `SUPPORT_SYSTEM`
System prompt for support analysis with:
- Art. 84 EPC legal standard
- Description-claim mapping rules
- Breadth assessment criteria
- JSON output format

#### `FORMAL_REPORT_SYSTEM`
System prompt for generating formal NIPO examination reports with:
- Formal objection structure
- Norwegian legal language
- Grouped issue presentation
- Conclusion summary format

**Exemplar Usage Rules**:
- For analogy/in-context teaching only
- NOT binding legal authority
- Max 3 exemplars per response
- Verbatim quotes when available
- No fabrication of case numbers

---

### 5. `claims_core/legal_models.py`
**Purpose**: Data models for legal analysis results.

**Key Classes**:

#### `EnablementResult`
```python
@dataclass
class EnablementResult:
    status: str              # "ENABLED" or "NOT_ENABLED"
    status_reason: str       # Legal reasoning
    issues: List[str]        # Specific issues found
    missing_elements: List[str]
    technical_deficiencies: List[str]
    reproducibility_score: float
    confidence: str          # "HIGH", "MEDIUM", or "LOW"
```

#### `ClarityResult`
```python
@dataclass
class ClarityResult:
    status: str              # "CLEAR" or "UNCLEAR"
    status_reason: str
    issues: List[str]
    vague_terms: List[str]
    undefined_terms: List[str]
    ambiguous_phrases: List[str]
    clarity_score: float
    confidence: str
```

#### `SupportResult`
```python
@dataclass
class SupportResult:
    status: str              # "SUPPORTED" or "NOT_SUPPORTED"
    status_reason: str
    issues: List[str]
    unsupported_elements: List[str]
    broader_than_description: List[str]
    missing_embodiments: List[str]
    support_score: float
    confidence: str
```

#### `LegalAnalysisResult`
Combined result with overall assessment.

---

### 6. `claims_utils/guideline_loader.py`
**Purpose**: Load and format NIPO examination guidelines.

**Key Functions**:
- `load_guidelines()`: Load guideline text files
- `format_for_prompt()`: Format guidelines for LLM prompts
- `get_section(section_name)`: Extract specific guideline sections

---

### 7. `skill.md`
**Purpose**: Agent skill documentation.

Documents:
- Legal framework (EPC Art. 83, 84)
- Analysis tasks (enablement, clarity, support)
- Input/output formats
- Reasoning rules for examiners

---

## Analysis Logic

### Enablement Analysis
**Legal Standard**: The invention must be disclosed clearly and completely enough for a skilled person to carry it out (Norwegian Patents Act §8).

**Checks**:
1. All claimed elements described?
2. Technical parameters specified?
3. Implementation details provided?
4. Working examples present?
5. Functional language supported by mechanism?

**Scoring**:
- Reproducibility score: 0.0-1.0
- Confidence: HIGH/MEDIUM/LOW

### Clarity Analysis
**Legal Standard**: Claims must be clear, precise, and unambiguous (EPC Art. 84).

**Checks**:
1. Vague terms identified?
2. Terms defined in description?
3. Functional language bounded?
4. Structural limitations present?
5. Claim scope determinable?

**Issue Categories**:
- Vague terms: "optimal", "suitable", "appropriate"
- Undefined terms: Technical terms not defined
- Ambiguous phrases: Multiple interpretations possible

### Support Analysis
**Legal Standard**: Claims must be supported by the description (EPC Art. 84).

**Checks**:
1. Claim elements in description?
2. Embodiments cover claim scope?
3. Drawings support claims?
4. Claims not broader than described?

**Issue Types**:
- Unsupported elements
- Claims broader than description
- Missing embodiments

## Integration with Streamlit

Tab 4 in `streamlit_app_next_agents.py`:

```python
from agents.agent4_claims_clarity.claims_clarity_agent import claims_clarity_agent

with tab4:
    st.subheader("Claims Clarity Analysis")
    if st.button("Run Clarity Analysis"):
        result = claims_clarity_agent(state)
        # Display:
        # - Overall metrics (Decision, Risk, Issues)
        # - Summary
        # - Enablement/Clarity/Support tabs
        # - Formal Report tab
        # - Recommendations
```

## Dependencies

- **Ollama**: LLM for legal analysis (model: gpt-oss:120b-cloud)
- **agents.claims_analyse_libs**: Shared libraries
  - `config.AnalyzerConfig`
  - `core.OllamaClient`
  - `utils.parse_json_safe`, `utils.truncate_text`
- **NIPO Guidelines**: Text files in `resources/guidelines/`

## Error Handling

- Missing documents: Returns error with instructions
- LLM failure: Returns partial results or error
- Invalid JSON: Uses fallback parsing
- Empty claims: Returns early with warning

## Output Directory

```
claims_analyse_reports/clarity_analyse/
```

## Legal Framework

- Norwegian Patents Act §8 (Enablement)
- EPC Art. 83 (Enablement)
- EPC Art. 84 (Clarity & Support)
- Patent Regulations §8

## References

- EPO Guidelines for Examination
- NIPO Examination Guidelines (patentretningslinjene)
- EPO Boards of Appeal decisions (T 0488/13, T 0024/10, T 0899/91)

---

**Created**: 2026-04-27
**Author**: Patent Analysis System
**Status**: Production Ready
