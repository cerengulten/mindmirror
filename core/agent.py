from core.store import get_recent_entries
from core.llm import ask_llm
from collections import Counter

REPORT_SYSTEM = """You are a compassionate AI wellness coach trained in Cognitive Behavioral Therapy.
You analyze patterns in a person's journal entries and provide gentle, actionable insights.
You never diagnose. You never prescribe. You help people notice patterns and reflect.
Always be warm, non-judgmental, and constructive.
Respond only in valid JSON."""

REPORT_PROMPT = """Based on this week's journal data, generate a compassionate weekly insight report.

Summary of this week:
- Total entries: {total_entries}
- Most common emotions: {top_emotions}
- Most common cognitive distortions: {top_distortions}
- Average emotional intensity: {avg_intensity}/10
- Emotional tone breakdown: {valence_breakdown}

Recent entry summaries:
{summaries}

Return a JSON object with exactly these fields:
{{
  "dominant_theme": "One sentence describing the main emotional theme of this week",
  "pattern_to_notice": "One specific pattern worth reflecting on, described compassionately",
  "suggestion": "One small, concrete, actionable suggestion for the coming week",
  "encouragement": "One warm sentence of encouragement based on what you noticed",
  "intensity_trend": "one of: improving, worsening, stable"
}}"""


def generate_weekly_report() -> dict:
    """
    Generate a weekly insight report based on recent journal entries.
    Uses an LLM agent to analyze patterns and produce structured insights.
    
    Returns:
        Dictionary with dominant_theme, pattern_to_notice, suggestion, encouragement, intensity_trend
    """
    entries = get_recent_entries(days=7)
    
    if not entries:
        return {
            "dominant_theme": "No entries yet this week.",
            "pattern_to_notice": "Start journaling to see patterns emerge.",
            "suggestion": "Write your first entry today — even a few sentences helps.",
            "encouragement": "Every journey begins with a single step.",
            "intensity_trend": "stable"
        }
    
    # Aggregate data from entries
    all_emotions = []
    all_distortions = []
    intensities = []
    valences = []
    summaries = []
    
    for entry in entries:
        meta = entry["metadata"]
        
        emotions = [e.strip() for e in meta.get("emotions", "").split(",") if e.strip()]
        all_emotions.extend(emotions)
        
        distortions = [d.strip() for d in meta.get("distortions", "").split(",") if d.strip()]
        all_distortions.extend(distortions)
        
        intensities.append(int(meta.get("intensity", 5)))
        valences.append(meta.get("valence", "neutral"))
        
        if meta.get("summary"):
            summaries.append(f"- {meta['summary']}")
    
    # Build prompt context
    top_emotions = [f"{e} ({c}x)" for e, c in Counter(all_emotions).most_common(3)]
    top_distortions = [f"{d} ({c}x)" for d, c in Counter(all_distortions).most_common(3)]
    valence_breakdown = dict(Counter(valences))
    avg_intensity = round(sum(intensities) / len(intensities), 1)
    
    prompt = REPORT_PROMPT.format(
        total_entries=len(entries),
        top_emotions=", ".join(top_emotions) or "none detected",
        top_distortions=", ".join(top_distortions) or "none detected",
        avg_intensity=avg_intensity,
        valence_breakdown=valence_breakdown,
        summaries="\n".join(summaries[:5])  # Limit to 5 to keep prompt short
    )
    
    import json, re
    response = ask_llm(prompt, system=REPORT_SYSTEM, temperature=0.4)
    cleaned = re.sub(r'```json|```', '', response).strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "dominant_theme": "Could not generate report.",
            "pattern_to_notice": "Try adding more entries.",
            "suggestion": "Write consistently for a week to see insights.",
            "encouragement": "You are doing great by showing up.",
            "intensity_trend": "stable"
        }