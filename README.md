# 🪞 MindMirror

**AI-powered journaling with emotional pattern intelligence**

MindMirror is a private journaling application that uses large language models to analyze emotional patterns, identify cognitive distortions, and surface behavioral insights over time. Each journal entry is analyzed for emotions, tone, and intensity — then stored as a vector embedding to enable semantic search and longitudinal pattern tracking.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-F55036?style=flat-square)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Overview

Most journaling apps store your words but offer no reflection back. MindMirror combines a retrieval-augmented pipeline with CBT-based prompt engineering to turn raw journal text into structured psychological data — not as a diagnostic tool, but as a mirror for self-awareness.

**Core capabilities:**

- Emotion detection and cognitive distortion identification using LLM prompt chains
- Semantic search over past entries using sentence embeddings and vector retrieval
- Agentic weekly insight report that aggregates patterns and generates personalized observations
- Evaluation pipeline with LLM-as-judge scoring to measure analysis quality
- Fully local data storage — no journal content leaves your machine

---
## Demo

![Demo](assets/mindmirror-demo.gif)

---
## Architecture

```
User Input (Streamlit)
        │
        ▼
   FastAPI Backend
        │
        ├─── POST /entry ──────► Analyzer (LLaMA 3.1 via Groq)
        │                              │
        │                        Structured JSON
        │                     (emotions, distortions,
        │                      valence, intensity)
        │                              │
        │                        ChromaDB Store
        │                    (sentence-transformers
        │                     embedding + metadata)
        │
        ├─── GET /search ──────► Semantic retrieval from ChromaDB
        │
        ├─── GET /stats ───────► Aggregate pattern analysis
        │
        └─── GET /report ──────► Insight Agent
                                      │
                                 Retrieves last 7 entries
                                 Aggregates patterns
                                      │
                                 LLaMA 3.1 via Groq
                                      │
                                 Structured insight report
```

**Evaluation pipeline** (`eval/evaluator.py`) runs offline against a manually labeled dataset using LLM-as-judge scoring to measure emotion detection accuracy and distortion identification precision.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Groq API — LLaMA 3.1 8B Instant | Emotion analysis, distortion detection, report generation |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Local text embedding for semantic search |
| Vector DB | ChromaDB (persistent, local) | Entry storage and retrieval |
| Backend | FastAPI + Pydantic | REST API with input validation |
| Frontend | Streamlit | Journaling UI |
| Evaluation | Custom pipeline + LLM-as-judge | Offline quality measurement |

---

## Technical Design Decisions

**Groq over OpenAI.** Groq's LPU inference hardware delivers significantly lower latency than GPU-based providers. For a real-time journaling experience where users expect immediate feedback, this matters. LLaMA 3.1 8B on Groq is also free-tier, making the project fully reproducible at zero cost.

**ChromaDB over cloud vector stores.** ChromaDB runs in-process with no infrastructure overhead and persists to disk automatically. For a local-first personal app where data privacy is a core design principle, this is the right tradeoff — no data leaves the machine, no API keys for a vector service, instant setup.

**Local embeddings over embedding APIs.** `all-MiniLM-L6-v2` runs entirely offline on CPU, keeping journal content private. At ~80MB it is lightweight enough to not affect startup time, and achieves strong performance on semantic similarity for English text.

**Structured LLM output with retry logic.** The analyzer prompts the model to return JSON with an explicit field schema and CBT distortion taxonomy. The implementation includes a 3-attempt retry loop with regex-based JSON fence stripping to handle occasional malformed responses — more robust than a naive `json.loads()` call.

**LLM-as-judge evaluation.** Rather than requiring expensive human annotation for every metric, the evaluation pipeline uses a second LLM call as a judge, rating analysis quality 1–5 with reasoning. This is a standard pattern in production ML systems for scalable, automated quality measurement without per-sample ground truth labels.

---

## Evaluation Results

Evaluated on 10 manually labeled journal entries. Ground truth created using CBT distortion taxonomy (Burns, 1980).

| Metric | Score |
|---|---|
| Emotion detection overlap | 0.433 |
| Distortion detection overlap | 0.7 |
| Valence classification accuracy | 1.0 |
| Intensity range accuracy | 0.9 |
| LLM judge average score | 4.0 / 5.0 |
| Model | LLaMA 3.1 8B via Groq |
| Embedding model | all-MiniLM-L6-v2 |

> Run `python eval/evaluator.py` to reproduce. Results are saved to `eval/results.json`.

---

## Project Structure

```
mindmirror/
│
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI — all endpoints
│
├── core/
│   ├── __init__.py
│   ├── llm.py               # Groq API connector
│   ├── analyzer.py          # Emotion + distortion analysis chain
│   ├── store.py             # ChromaDB operations
│   └── agent.py             # Weekly insight agent
│
├── eval/
│   ├── __init__.py
│   ├── evaluator.py         # Evaluation pipeline
│   └── results.json         # Evaluation output
│
├── app.py                   # Streamlit UI
├── .env                     # API keys (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Free Groq API key — [console.groq.com](https://console.groq.com) (no credit card required)

### Installation

```bash
git clone https://github.com/cerengulten/mindmirror.git
cd mindmirror

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Running

Start both processes in separate terminals:

```bash
# Terminal 1 — API
uvicorn api.main:app --reload

# Terminal 2 — UI
streamlit run app.py
```

- Streamlit UI: [http://localhost:8501](http://localhost:8501)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/entry` | Submit a journal entry for analysis |
| `GET` | `/search?q=&n=` | Semantic search over past entries |
| `GET` | `/stats` | Aggregate emotion and distortion statistics |
| `GET` | `/entries/recent?days=` | Retrieve recent entries |
| `GET` | `/report/weekly` | Generate weekly insight report |
| `DELETE` | `/entry/{id}` | Delete a specific journal entry |

**Example:**

```bash
curl -X POST http://localhost:8000/entry \
  -H "Content-Type: application/json" \
  -d '{"text": "I completely failed the presentation. I always mess things up when it matters."}'
```

```json
{
  "entry_id": "abc123...",
  "analysis": {
    "emotions": ["shame", "hopeless"],
    "valence": "negative",
    "intensity": 8,
    "distortions": ["overgeneralization", "all-or-nothing thinking"],
    "themes": ["work", "self-worth"],
    "summary": "You seem to be holding yourself to a very harsh standard after a difficult moment."
  }
}
```

---

## Running the Evaluation

```bash
python eval/evaluator.py
```

Analyzes 10 labeled entries, computes overlap metrics against ground truth, and scores with LLM-as-judge. Runtime is approximately 5–10 minutes. Results are saved to `eval/results.json`.

---

## Future Development

- **Multi-user support** with authentication and isolated data stores per user
- **Longitudinal trend visualization** — intensity and valence charts over time using Plotly
- **Azure deployment** — containerized backend on Azure App Service with Blob Storage for persistence
- **Multilingual support** — extending analysis to Italian and Turkish entries using multilingual embedding models
- **Voice-to-text input** using Whisper API for hands-free journaling
- **Export** — generate a personal PDF report covering a selected date range
- **Scheduled reports** — weekly insight email delivery via SendGrid

---

## Privacy

Journal data is stored locally in a ChromaDB instance (`.chroma/` folder) and never transmitted to any external service except the Groq API for LLM inference. The `.chroma/` directory is excluded from version control via `.gitignore`. To run this project, you supply your own API key — no data is shared with the repository author.

---

## Disclaimer

MindMirror is a personal reflection and self-awareness tool. It is not a medical device, clinical service, or substitute for professional mental health support. Cognitive distortion labels are applied using CBT frameworks for educational purposes only and do not constitute a diagnosis of any kind.

If you are experiencing mental health difficulties, please reach out to a qualified professional.

---

## Author

**Ceren Yilmaz Gülten** — AI/ML Engineer

Specialized in LLMs, retrieval-augmented generation, semantic search, and NLP systems. MSc from University of Padova with thesis on contrastive learning for semantic search.

[LinkedIn](https://www.linkedin.com/in/ceren-yilmaz-gulten-/) · [GitHub](https://github.com/cerengulten)

---

## License

MIT License — see [LICENSE](LICENSE) for details.