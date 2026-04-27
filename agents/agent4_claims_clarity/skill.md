# 🧠 Skill: Patent Legal Analysis (EPO + NIPO)

## 🎯 Goal
Analyze patent documents (**claims, description, drawings**) and determine:

- Enablement (Art. 83 EPC / §8 Patentloven)
- Clarity (Art. 84 EPC)
- Support (Art. 84 EPC)

Output structured results to assist a patent examiner.

---

## ⚖️ Legal Framework

### Enablement
- EPC Art. 83
- Norwegian Patent Act § 8  
Definition:  
The invention must be disclosed clearly and completely enough for a skilled person to carry it out.

---

### Clarity
- EPC Art. 84  
Definition:  
Claims must be clear, precise, and unambiguous.

---

### Support
- EPC Art. 84  
Definition:  
Claims must be supported by the description.

---

## 📥 Input Format

```json
{
  "claims": "...",
  "description": "...",
  "drawings": "... (optional text or extracted labels)"
}
```

---

## 🔍 Analysis Tasks

### 1. ENABLEMENT CHECK
Evaluate whether the description enables the claims.

Check for:
- Missing technical parameters (e.g., ranges, values)
- Lack of implementation details
- Functional language without mechanism
- No working examples

---

### 2. CLARITY CHECK (CLAIMS ONLY)
Evaluate claims for:
- Vague terms (“optimal”, “configured to”)
- Undefined terms
- Overly broad functional language
- Lack of structural limitations

---

### 3. SUPPORT CHECK (CLAIMS ↔ DESCRIPTION)
Evaluate:
- Are all claim elements described?
- Are embodiments covering claim scope?
- Are drawings referenced and explained?
- Are claim features broader than description?

---

## 📤 Output Format

```json
{
  "enablement": {
    "status": "ENABLED | NOT_ENABLED",
    "issues": [],
    "missing_elements": []
  },
  "clarity": {
    "status": "CLEAR | UNCLEAR",
    "issues": []
  },
  "support": {
    "status": "SUPPORTED | NOT_SUPPORTED",
    "issues": []
  },
  "overall_assessment": {
    "risk_level": "LOW | MEDIUM | HIGH",
    "summary": ""
  }
}
```

---

## 🧠 Reasoning Rules

- Be strict (examiner-level)
- Prefer technical deficiencies over style
- Do NOT assume missing information
- If something is not explicitly described → treat as missing
- Focus on reproducibility

---

## 🚫 Avoid

- General summaries
- Marketing language
- Guessing missing details

---

## ✅ Expected Behavior

- Highlight legal violations clearly
- Map issues to Enablement / Clarity / Support
- Provide actionable feedback
