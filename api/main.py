from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from core.analyzer import analyze_entry
from core.store import save_entry, search_entries, get_recent_entries, get_stats
from core.agent import generate_weekly_report

app = FastAPI(
    title="MindMirror API",
    description="AI-powered journal analysis for emotional pattern recognition",
    version="1.0.0"
)


# --- Request/Response Models ---

class JournalEntryRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000, 
                      description="The journal entry text to analyze")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Semantic search query")
    n_results: int = Field(default=5, ge=1, le=20)


# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "MindMirror API is running", "docs": "/docs"}


@app.post("/entry")
def create_entry(request: JournalEntryRequest):
    """
    Submit a journal entry for analysis.
    Returns emotion tags, distortions, and intensity score.
    """
    try:
        analysis = analyze_entry(request.text)
        entry_id = save_entry(request.text, analysis)
        
        return {
            "entry_id": entry_id,
            "analysis": analysis,
            "message": "Entry saved and analyzed successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/search")
def search(q: str, n: int = 5):
    """
    Semantic search over past journal entries.
    Example: /search?q=times I felt anxious about work
    """
    if len(q) < 3:
        raise HTTPException(status_code=400, detail="Query too short")
    
    results = search_entries(q, n_results=n)
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


@app.get("/stats")
def stats():
    """
    Get aggregate statistics: top emotions, distortions, valence distribution.
    Used for the patterns dashboard.
    """
    return get_stats()


@app.get("/entries/recent")
def recent_entries(days: int = 7):
    """Get the most recent journal entries."""
    entries = get_recent_entries(days=days)
    return {"entries": entries, "count": len(entries)}

@app.get("/report/weekly")
def weekly_report():
    """
    Generate a weekly insight report using the AI agent.
    Analyzes the last 7 days of entries for patterns and generates compassionate insights.
    """
    return generate_weekly_report()