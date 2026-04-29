import json
import re
from core.llm import ask_llm

# These are the 10 most common CBT cognitive distortions
# Reference: Burns, D. (1980). Feeling Good: The New Mood Therapy
DISTORTIONS = [
    "all-or-nothing thinking",  # Seeing things in black and white
    "overgeneralization",        # One bad event = never-ending pattern
    "mental filter",             # Focusing only on negatives
    "disqualifying positives",   # Rejecting positive experiences
    "mind reading",              # Assuming others think negatively
    "fortune telling",           # Predicting bad outcomes
    "catastrophizing",           # Blowing things out of proportion
    "emotional reasoning",       # Feeling = fact ("I feel stupid, so I am")
    "should statements",         # Rigid rules about how things must be
    "personalization",           # Blaming yourself for external events
]

SYSTEM_PROMPT = f"""You are a compassionate clinical psychologist specializing in Cognitive Behavioral Therapy (CBT).
Your task is to analyze journal entries and identify emotional patterns and cognitive distortions.

Cognitive distortions you know about: {', '.join(DISTORTIONS)}

Always respond with valid JSON only. No explanation, no markdown, no extra text.
"""

ANALYSIS_PROMPT = """Analyze this journal entry and return a JSON object with exactly these fields:

Entry: "{entry}"

Return JSON with:
- "emotions": list of 1-4 emotion words (e.g. ["anxious", "overwhelmed", "hopeless"])
- "valence": one of "positive", "negative", "mixed", "neutral"  
- "intensity": integer 1-10 (how emotionally intense is this entry?)
- "distortions": list of cognitive distortions present (use exact names from the list, empty list if none)
- "themes": list of 1-3 life themes (e.g. ["work", "relationships", "self-worth"])
- "summary": one compassionate sentence summarizing the emotional state

Example output format:
{{
  "emotions": ["anxious", "overwhelmed"],
  "valence": "negative",
  "intensity": 7,
  "distortions": ["catastrophizing", "mind reading"],
  "themes": ["work", "self-worth"],
  "summary": "You seem to be carrying a heavy load of worry about how others perceive you at work."
}}"""


def analyze_entry(text: str) -> dict:
    """
    Analyze a journal entry and return structured psychological data.
    
    Args:
        text: The raw journal entry text
    
    Returns:
        Dictionary with emotions, valence, intensity, distortions, themes, summary
    """
    if not text or len(text.strip()) < 10:
        raise ValueError("Journal entry is too short to analyze.")
    
    prompt = ANALYSIS_PROMPT.format(entry=text)
    
    # Try up to 3 times if the LLM returns malformed JSON
    for attempt in range(3):
        try:
            response = ask_llm(prompt, system=SYSTEM_PROMPT, temperature=0.1)
            
            # Clean up response — sometimes LLM adds ```json fences
            cleaned = re.sub(r'```json|```', '', response).strip()
            
            result = json.loads(cleaned)
            
            # Validate required fields are present
            required = ["emotions", "valence", "intensity", "distortions", "themes", "summary"]
            for field in required:
                if field not in result:
                    raise ValueError(f"Missing field: {field}")
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == 2:
                # After 3 failures, return a safe default
                return {
                    "emotions": ["unidentified"],
                    "valence": "neutral",
                    "intensity": 5,
                    "distortions": [],
                    "themes": [],
                    "summary": "Unable to fully analyze this entry.",
                    "error": str(e)
                }
            continue


if __name__ == "__main__":
    # Test with example entries
    test_entries = [
        "I completely failed the presentation today. Everyone must think I'm incompetent. This always happens to me, I never do anything right.",
        "Had a really nice walk this morning. Felt peaceful and grateful for small things.",
        "My friend didn't reply to my message. She probably hates me now. I knew being too open was a mistake."
    ]
    
    for entry in test_entries:
        print(f"\nEntry: {entry[:60]}...")
        result = analyze_entry(entry)
        print(f"Emotions: {result['emotions']}")
        print(f"Distortions: {result['distortions']}")
        print(f"Intensity: {result['intensity']}/10")
        print(f"Summary: {result['summary']}")