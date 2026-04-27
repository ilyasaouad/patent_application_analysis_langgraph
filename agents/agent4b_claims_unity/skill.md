# 🧠 Skill: Claims Unity Analysis (NIPO §10)

## 🎯 Goal
Analyze patent claims for unity — whether they constitute a single invention or multiple mutually independent inventions under Norwegian law.

## ⚖️ Legal Framework

### Unity Requirement
- **Norwegian Patents Act § 10**
- **Patent Regulations § 8**

Definition:
Claims must relate to a single general inventive concept. If multiple independent inventions are claimed, the applicant may be required to limit the claims or file divisional applications.

## 📥 Input Format

```json
{
  "claims": "...",
  "description": "...",
  "drawings": "... (optional)"
}
```

## 🔍 Analysis Tasks

### 1. IDENTIFY INDEPENDENT CLAIMS
- Parse claim set to identify independent claims
- Group dependent claims with their respective independent claims

### 2. TECHNICAL RELATIONSHIP ANALYSIS
- Identify common features across independent claims
- Determine if common features provide a "special technical effect"
- Assess whether claims solve the same objective technical problem

### 3. GROUPING DECISION
- Group 1: Claims sharing a single inventive concept
- Group 2+: Claims with different inventive concepts (if applicable)
- Maximum 2-4 groups recommended

## 📤 Output Format

```json
{
  "conclusion": "SINGLE_INVENTION | MULTIPLE_INVENTIONS",
  "grouping": [
    {
      "group_no": 1,
      "representative_independent_claims": ["1", "5"],
      "technical_subject_matter": "...",
      "objective_technical_problem": "..."
    }
  ],
  "technical_relationship_analysis": "...",
  "recommendation": "..."
}
```

## 🧠 Reasoning Rules

- Be decisive in grouping decisions
- Common features must be more than general background knowledge
- Special technical features must link claims technically
- Do NOT invent claim numbers
- Map all conclusions to Norwegian Patents Act §10

## 🚫 Avoid

- Vague grouping without technical justification
- Treating generic/common knowledge as linking features
- Inventing claim numbers or case quotes

## ✅ Expected Behavior

- Clear grouping of claims
- Technical justification for each group
- Legal mapping to §10
- Procedural recommendations