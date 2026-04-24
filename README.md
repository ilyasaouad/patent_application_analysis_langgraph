# Patent Application Analyzer - LangGraph Project

## Project Overview

This project is a **LangGraph-based patent application analyzer** that processes patent documents (description, claims, and drawings) using AI agents to extract and analyze claims data.

### Use Case
Analyzes Norwegian patent applications from NIPO (Patentstyret) to:
- Extract text from patent documents (PDF/DOCX)
- Identify and process patent claims
- Generate rejection letters when claims are empty based on NIPO guidelines

---

## Project Structure

```
patent_application_anlayse_langgraph/
├── .env                    # API keys (LANGSMITH_API_KEY, etc.)
├── langgraph.json          # LangGraph Studio config
├── run_studio.bat        # Launch LangGraph Studio
├── visualize_graph.py   # Graph visualization script
├── graph_state.py       # LangGraph state definition
├── graph_workflow.py    # Graph node definitions
├── streamlit_app.py    # Streamlit web interface
├── agents/
│   ├── read_parse_document.py   # Document extraction agent
│   ├── extract_claims.py       # Claims analysis agent
│   └── empty_claims.py      # Empty claims handler
├── backend_text_extract/
│   ├── mineru_wrapper.py   # MinerU OCR wrapper
│   ├── docx_extractor.py  # DOCX extraction
│   ├── pdf_extractor.py   # PDF extraction
│   └── ...
└── resources/
    ├── guidelines/
    │   └── nipo_missing_claims_basis.md
    └── statement_examples/
        └── nipo_missing_claims_letter_example.md
```

---

## Graph Architecture

```
START
  │
  ▼
read_parse_document (extracts text from PDFs/DOCX)
  │
  ├─► claims_text empty ──► extract_claims (AI analysis)
  │                           │
  │                           ├─► claims_text empty ──► empty_claims (rejection letter)
  │                           │
  │                           └─► claims_text exists ──► END
  │
  └─► claims_text exists ──► END
```

### Nodes

| Node | Purpose |
|------|---------|
| `read_parse_document` | Extract text from PDF/DOCX files using MinerU |
| `extract_claims` | Analyze claims using AI |
| `empty_claims` | Generate formal rejection based on NIPO guidelines |

---

## How to Run

### Option 1: LangGraph Studio

```bash
# Set API key
set LANGSMITH_API_KEY=lsv2_pt_...

# Start Studio
langgraph dev --port 2024
```

Then open: https://smith.langchain.com/studio/

### Option 2: Streamlit App

```bash
streamlit run streamlit_app.py
```

Upload PDF/DOCX files through the web interface.

---

## API Keys Required

Add to `.env`:

```
LANGSMITH_API_KEY=lsv2_pt_...
LANGCHAIN_API_KEY=lsv2_pt_...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Current Status

- ✅ Graph structure defined
- ✅ LangGraph Studio working
- ✅ MinerU text extraction integrated
- ⚠️  Remote file access (files must be local or hosted)
- 🔄 Testing in progress

---

## Files

| File | Purpose |
|------|---------|
| `graph_state.py` | TypedDict for graph state |
| `graph_workflow.py` | Graph definition with conditional routing |
| `agents/read_parse_document.py` | First node - extract text |
| `agents/extract_claims.py` | Second node - analyze claims |
| `agents/empty_claims.py` | Third node - rejection handler |
| `backend_text_extract/mineru_wrapper.py` | OCR extraction wrapper |
| `resources/` | NIPO guidelines and templates |

---

## Built with

- [LangGraph](https://langchain.com/langgraph/) - Multi-agent orchestration
- [MinerU](https://mineru.ai/) - Document OCR extraction
- [Streamlit](https://streamlit.io/) - Web UI
- OpenAI/Anthropic - LLM for claims analysis