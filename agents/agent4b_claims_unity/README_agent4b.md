# Agent 4B: Claims Unity Analysis

## Overview

Agent 4B performs **unity analysis** on patent claims under Norwegian Patents Act §10. It determines whether the claims constitute:
- A **single invention** (single general inventive concept), or
- **Multiple mutually independent inventions** requiring division

This analysis is critical for patent examination as it determines whether claims can be examined together or must be limited/divided.

## Architecture

```
agents/agent4b_claims_unity/
├── __init__.py                          # Package initialization
├── claims_unity_agent.py                # LangGraph agent wrapper
├── unity_prompts.py                     # Unity analysis prompts
├── resources/                           # Resources
│   ├── guidelines/
│   │   └── unity_guidelines.txt         # Unity examination guidelines
│   └── rejection_letter_template.md     # NIPO rejection letter template
└── skill.md                             # Skill documentation
```

## Files Description

### 1. `__init__.py`
**Purpose**: Package initialization and exports.

**Exports**:
- `claims_unity_agent` - Main agent function
- `run_claims_unity` - Standalone analysis function
- `UnityPrompts` - Prompt templates

**Usage**:
```python
from agents.agent4b_claims_unity import claims_unity_agent
```

---

### 2. `claims_unity_agent.py`
**Purpose**: LangGraph-compatible agent wrapper for claims unity analysis.

**Function**:

#### `claims_unity_agent(state)`
Main entry point for LangGraph integration.

**Parameters**:
- `state`: GraphState - Contains claims_text, description_text, drawings_text

**Workflow**:
1. Read claims from state or `output_text_documents/claims.md`
2. Initialize OllamaClient
3. Format unity analysis prompt with claims
4. Generate LLM analysis with JSON output
5. Parse and validate results
6. Generate human-readable report
7. **If multiple inventions**: Generate NIPO rejection letter
8. Save results to `claims_analyse_reports/unity_analyse/`

**Output Files**:
```
claims_analyse_reports/unity_analyse/
├── claims_unity_result.json              # Structured JSON results
├── claims_unity_report.md                # Analysis report
└── claims_unity_rejection_letter.md      # NIPO rejection letter (if applicable)
```

**Output Format**:
```json
{
  "status": "SUCCESS",
  "conclusion": "SINGLE_INVENTION" | "MULTIPLE_INVENTIONS",
  "status_reason": "Brief legal reasoning",
  "grouping": [
    {
      "group_no": 1,
      "representative_independent_claims": ["1", "5"],
      "included_dependent_claims": ["2", "3", "4"],
      "technical_subject_matter": "Seismic source system",
      "objective_technical_problem": "How to provide effective seismic energy",
      "special_technical_features": ["frequency modulation", "energy control"],
      "links_to_description": ["para 10", "fig 2"]
    }
  ],
  "common_features": ["seismic source"],
  "technical_relationship_analysis": "The common feature is general knowledge...",
  "legal_mapping": "Norwegian Patents Act §10 / Patent Regulations §8",
  "recommendation": "Limit to Group 1 or file divisional for Group 2",
  "confidence": "HIGH",
  "exemplar_analogies_used": [
    {
      "case_id": "T 1227/05",
      "quoted_excerpt": "...",
      "one_line_summary": "No single inventive concept with generic features",
      "mapping": "Applies here as common feature is known"
    }
  ],
  "rejection_letter": "After a preliminary review..."  // If MULTIPLE_INVENTIONS
}
```

---

### 3. `unity_prompts.py`
**Purpose**: LLM prompts for unity analysis with EPO exemplars.

**Key Components**:

#### `UNITY_SYSTEM`
System prompt for unity analysis with:
- Norwegian Patents Act §10 legal standard
- Patent Regulations §8 requirements
- EPO Board of Appeal exemplars (T 1227/05, T 0533/09, T 0140/11)
- Strict JSON output format with grouping structure
- Exemplar usage rules (analogy only, no fabrication)
- Overreach filter (softened conclusions)

**EPO Exemplars**:

**U1 — T 1227/05**: System and method claims with only generic common feature; no single inventive concept because common feature was known.

**U2 — T 0533/09**: Method and apparatus claims forming single inventive concept when apparatus contributes essential technical means solving same problem.

**U3 — T 0140/11**: Common feature must be more than general background knowledge; must provide special technical effect.

**Exemplar Usage Rules**:
- For analogy/in-context teaching only
- NOT binding authority
- Final mapping to Norwegian Patents Act §10
- Max 3 exemplars per response
- No fabrication of case quotes

#### `UNITY_USER`
User prompt template supplying:
- Claims text
- Description text
- Drawings text (optional)
- Preferred grouping hint (optional)

---

### 4. `resources/rejection_letter_template.md`
**Purpose**: Template for NIPO unity rejection letter.

**Structure**:
1. **Opening**: State claims concern mutually independent inventions
2. **Defects**: Reference Patent Regulations §8, Norwegian Patents Act §10
3. **Grouping**: List each group with representative claims
4. **Common Features**: Analyze why common feature doesn't link groups
5. **Technical Differences**: Show groups concern different technical features
6. **Objective Problems**: Different technical problems for each group
7. **Conclusion**: No technical relationship, mutually independent
8. **Instructions**: 3-month limit, divisional option

**Generated when**: `conclusion == "MULTIPLE_INVENTIONS"`

**Output location**: `claims_analyse_reports/unity_analyse/claims_unity_rejection_letter.md`

---

### 5. `skill.md`
**Purpose**: Agent skill documentation.

Documents:
- Unity requirement (Norwegian Patents Act §10)
- Technical relationship analysis
- Grouping methodology
- Special technical features
- Single general inventive concept

---

## Analysis Logic

### Unity Assessment
**Legal Standard**: Claims must relate to a single general inventive concept (Norwegian Patents Act §10 / Patent Regulations §8).

**Analysis Steps**:
1. **Parse Claims**: Extract independent and dependent claims
2. **Identify Groups**: Group claims by technical subject matter
3. **Find Common Features**: Identify features shared across groups
4. **Assess Technical Relationship**:
   - Is common feature more than general knowledge?
   - Does it provide special technical effect?
   - Do groups solve same objective technical problem?
5. **Determine Conclusion**:
   - SINGLE_INVENTION: Groups linked by special technical feature
   - MULTIPLE_INVENTIONS: No linking feature, groups independent

### Grouping Methodology

**Group Structure**:
```
Group 1:
- Representative Independent Claims: 1, 5
- Dependent Claims: 2-4, 6-10
- Technical Subject: System/apparatus
- Technical Problem: How to structure the system

Group 2:
- Representative Independent Claims: 13, 20
- Dependent Claims: 14-19, 21-25
- Technical Subject: Method/process
- Technical Problem: How to perform the method
```

**Grouping Rules**:
- Limit to 2-4 groups (concise)
- Each group must have clear technical subject
- Groups must be mutually exclusive technically
- Be decisive in grouping decisions

### Technical Relationship Analysis

**Key Questions**:
1. What is the common technical feature?
2. Is it general background knowledge?
3. Does it provide special technical effect?
4. Do groups solve the same technical problem?
5. Are the technical features corresponding?

**Decision Tree**:
```
Common feature exists?
  ├── NO → MULTIPLE_INVENTIONS
  └── YES → Is it special technical feature?
        ├── NO → MULTIPLE_INVENTIONS
        └── YES → Same technical problem?
              ├── NO → MULTIPLE_INVENTIONS
              └── YES → SINGLE_INVENTION
```

### Confidence Levels
- **HIGH**: Clear multiple inventions or clear single concept
- **MEDIUM**: Some ambiguity in grouping or relationship
- **LOW**: Complex case requiring manual review

## Rejection Letter Generation

**When Generated**: Only when `conclusion == "MULTIPLE_INVENTIONS"`

**Content Includes**:
- Reference to Norwegian Patents Act §10
- Grouping of claims into independent inventions
- Analysis of common features (why they don't link)
- Technical differences between groups
- Different objective technical problems
- Instructions to limit claims within 3 months
- Option to file divisional applications

**Example Output**:
```markdown
# NIPO Unity Rejection Letter

After a preliminary review, we have found that the claims concern several 
mutually independent inventions that may not be protected in the same 
application, ref. Norwegian Patents Act, Section 10.

## Grouping

Group 1: Claims 1-12 (System for seismic source)
Group 2: Claims 13-25 (Method of generating seismic wave)

## Analysis

The common feature "seismic source" is general knowledge and cannot 
constitute a special technical feature linking the groups...

## Instructions

Limit the application within 3 months or file divisional applications...
```

## Integration with Streamlit

Tab 5 in `streamlit_app_next_agents.py`:

```python
from agents.agent4b_claims_unity.claims_unity_agent import claims_unity_agent

with tab5:
    st.subheader("Claims Unity Analysis")
    if st.button("Run Unity Analysis"):
        result = claims_unity_agent(state)
        # Display:
        # - Conclusion (SINGLE_INVENTION / MULTIPLE_INVENTIONS)
        # - Confidence level
        # - Number of groups
        # - Group details (expandable)
        # - Common features
        # - Technical relationship analysis
        # - Rejection letter (if applicable)
```

## Dependencies

- **Ollama**: LLM for unity analysis (model: gpt-oss:120b-cloud)
- **agents.claims_analyse_libs**: Shared libraries
  - `core.OllamaClient`
  - `utils.parse_json_safe`, `utils.truncate_text`

## Error Handling

- Missing claims: Returns error with instructions
- LLM failure: Returns error status
- Invalid JSON: Uses fallback parsing
- Parsing errors: Reports low confidence

## Output Directory

```
claims_analyse_reports/unity_analyse/
```

## Legal Framework

- Norwegian Patents Act §10 (Unity of Invention)
- Patent Regulations §8 (Technical Relationship)
- EPO Guidelines Part C, Chapter III, 6.2
- EPO Boards of Appeal: T 1227/05, T 0533/09, T 0140/11

## References

- NIPO Examination Guidelines (patentretningslinjene)
- EPO Guidelines for Examination, Part C
- Patent Regulations, Chapter 5 (Divisional Applications)

---

**Created**: 2026-04-27
**Author**: Patent Analysis System
**Status**: Production Ready
