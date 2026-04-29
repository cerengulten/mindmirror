import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime
import uuid

# Load embedding model once at module level (saves time on repeated imports)
# all-MiniLM-L6-v2 is small (~80MB), fast, and very good for English text
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB — stores data in a local folder called .chroma/
# This persists between runs (unlike in-memory storage)
chroma_client = chromadb.PersistentClient(path=".chroma")
collection = chroma_client.get_or_create_collection(
    name="journal_entries",
    metadata={"hnsw:space": "cosine"}  # cosine similarity for semantic search
)


def save_entry(text: str, analysis: dict) -> str:
    """
    Save a journal entry with its embedding and metadata to ChromaDB.
    
    Args:
        text: The raw journal entry text
        analysis: The dict returned by analyzer.analyze_entry()
    
    Returns:
        The unique ID of the saved entry
    """
    entry_id = str(uuid.uuid4())
    embedding = EMBEDDING_MODEL.encode(text).tolist()
    
    # Metadata must be flat (no nested dicts/lists) for ChromaDB
    # Convert lists to comma-separated strings
    metadata = {
        "date": datetime.now().isoformat(),
        "valence": analysis.get("valence", "neutral"),
        "intensity": analysis.get("intensity", 5),
        "emotions": ", ".join(analysis.get("emotions", [])),
        "distortions": ", ".join(analysis.get("distortions", [])),
        "themes": ", ".join(analysis.get("themes", [])),
        "summary": analysis.get("summary", ""),
    }
    
    collection.add(
        ids=[entry_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )
    
    return entry_id


def search_entries(query: str, n_results: int = 5) -> list[dict]:
    """
    Semantic search over past journal entries.
    
    Args:
        query: Natural language search query (e.g. "times I felt anxious about work")
        n_results: How many results to return
    
    Returns:
        List of dicts, each with 'text', 'metadata', 'distance' (lower = more similar)
    """
    if collection.count() == 0:
        return []
    
    query_embedding = EMBEDDING_MODEL.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count())
    )
    
    entries = []
    for i in range(len(results["ids"][0])):
        entries.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })
    
    return entries


def get_recent_entries(days: int = 7) -> list[dict]:
    """
    Get the most recent N entries (for weekly report generation).
    
    Returns all entries sorted by date, most recent first.
    """
    if collection.count() == 0:
        return []
    
    # Get all entries (for small personal journal this is fine)
    results = collection.get(include=["documents", "metadatas"])
    
    entries = []
    for i in range(len(results["ids"])):
        entries.append({
            "id": results["ids"][i],
            "text": results["documents"][i],
            "metadata": results["metadatas"][i]
        })
    
    # Sort by date, most recent first
    entries.sort(key=lambda x: x["metadata"]["date"], reverse=True)
    
    return entries[:days * 1]  # Assume ~1 entry per day


def get_stats() -> dict:
    """
    Get aggregate statistics across all entries.
    Used for the patterns dashboard.
    """
    if collection.count() == 0:
        return {"total_entries": 0}
    
    results = collection.get(include=["metadatas"])
    
    emotion_counts = {}
    distortion_counts = {}
    valence_counts = {"positive": 0, "negative": 0, "mixed": 0, "neutral": 0}
    intensities = []
    
    for meta in results["metadatas"]:
        # Count emotions
        for emotion in meta.get("emotions", "").split(", "):
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Count distortions
        for distortion in meta.get("distortions", "").split(", "):
            if distortion:
                distortion_counts[distortion] = distortion_counts.get(distortion, 0) + 1
        
        # Count valences
        valence = meta.get("valence", "neutral")
        valence_counts[valence] = valence_counts.get(valence, 0) + 1
        
        # Track intensity
        intensities.append(meta.get("intensity", 5))
    
    return {
        "total_entries": collection.count(),
        "top_emotions": sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        "top_distortions": sorted(distortion_counts.items(), key=lambda x: x[1], reverse=True)[:5],
        "valence_distribution": valence_counts,
        "avg_intensity": round(sum(intensities) / len(intensities), 1) if intensities else 0,
    }


if __name__ == "__main__":
    from core.analyzer import analyze_entry
    
    # Test: save a few entries and search them
    test_entries = [
        "I feel like a failure after today's meeting. Nobody respects my ideas.",
        "Had a great run this morning. Feeling energized and optimistic.",
        "Couldn't stop thinking about my exam. What if I fail everything?",
        "My partner and I had a small argument. I'm worried it means something bad.",
    ]
    
    print("Saving test entries...")
    for entry_text in test_entries:
        analysis = analyze_entry(entry_text)
        entry_id = save_entry(entry_text, analysis)
        print(f"  Saved: {entry_text[:50]}... (id: {entry_id[:8]}...)")
    
    print("\nSearching for 'feeling like a failure'...")
    results = search_entries("feeling like a failure", n_results=3)
    for r in results:
        print(f"  [{r['distance']:.3f}] {r['text'][:60]}...")
    
    print("\nStats:")
    stats = get_stats()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Top emotions: {stats['top_emotions']}")
    print(f"  Avg intensity: {stats['avg_intensity']}")