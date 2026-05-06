"""
Evaluation pipeline for MindMirror emotion analyzer.

Measures:
1. Emotion detection accuracy — does the model identify the right emotions?
2. Distortion detection precision — is it labeling distortions correctly?
3. LLM-as-judge quality score — how good is the analysis overall?

Ground truth labels were created manually by the developer.
"""

import json
from core.analyzer import analyze_entry
from core.llm import ask_llm

# Ground truth dataset — 10 labeled examples
# Created manually. In production this would be larger and validated by a psychologist.
GROUND_TRUTH = [
    {
        "text": "I completely bombed the interview. I always mess up when it matters most. I'm just not smart enough for these jobs.",
        "expected_emotions": ["shame", "hopeless", "anxious"],
        "expected_distortions": ["all-or-nothing thinking", "overgeneralization", "emotional reasoning"],
        "expected_valence": "negative",
        "expected_intensity_range": (7, 10)
    },
    {
        "text": "Had coffee with an old friend today. We laughed a lot. Feeling light and grateful.",
        "expected_emotions": ["happy", "grateful"],
        "expected_distortions": [],
        "expected_valence": "positive",
        "expected_intensity_range": (3, 6)
    },
    {
        "text": "My manager didn't say hi to me this morning. She must be angry with me. I probably did something wrong.",
        "expected_emotions": ["anxious", "worried"],
        "expected_distortions": ["mind reading", "personalization"],
        "expected_valence": "negative",
        "expected_intensity_range": (5, 8)
    },
    {
        "text": "I can't believe I forgot to call mom on her birthday. I'm the worst daughter ever. This ruined everything.",
        "expected_emotions": ["guilty", "shame"],
        "expected_distortions": ["all-or-nothing thinking", "catastrophizing"],
        "expected_valence": "negative",
        "expected_intensity_range": (6, 10)
    },
    {
        "text": "Finished a big project at work. My boss said it was good. I feel relieved but also a bit scared about the next one.",
        "expected_emotions": ["relieved", "anxious"],
        "expected_distortions": ["fortune telling"],
        "expected_valence": "mixed",
        "expected_intensity_range": (3, 6)
    },
    {
        "text": "I know I should exercise but I haven't in weeks. I'm so lazy and undisciplined. I'll never change.",
        "expected_emotions": ["shame", "hopeless"],
        "expected_distortions": ["should statements", "overgeneralization", "all-or-nothing thinking"],
        "expected_valence": "negative",
        "expected_intensity_range": (5, 8)
    },
    {
        "text": "Presentation went well today! People asked good questions. I think they actually liked it.",
        "expected_emotions": ["proud", "happy", "surprised"],
        "expected_distortions": [],
        "expected_valence": "positive",
        "expected_intensity_range": (5, 8)
    },
    {
        "text": "My friend seemed distant at dinner. She probably doesn't want to be friends anymore. People always leave eventually.",
        "expected_emotions": ["sad", "anxious", "lonely"],
        "expected_distortions": ["mind reading", "fortune telling", "overgeneralization"],
        "expected_valence": "negative",
        "expected_intensity_range": (6, 9)
    },
    {
        "text": "Normal day. Worked, had lunch, watched TV. Nothing special but nothing bad either.",
        "expected_emotions": ["neutral"],
        "expected_distortions": [],
        "expected_valence": "neutral",
        "expected_intensity_range": (1, 4)
    },
    {
        "text": "I feel so overwhelmed. There are too many things to do and I don't know where to start. What if I fail everything?",
        "expected_emotions": ["overwhelmed", "anxious"],
        "expected_distortions": ["catastrophizing", "fortune telling"],
        "expected_valence": "negative",
        "expected_intensity_range": (7, 10)
    },
]

JUDGE_SYSTEM = """You are an expert evaluator assessing AI-generated psychological analysis.
Respond only with a JSON object."""

JUDGE_PROMPT = """Rate the quality of this emotion analysis on a scale of 1-5.

Journal entry: "{text}"

AI Analysis:
- Emotions detected: {emotions}
- Cognitive distortions: {distortions}  
- Valence: {valence}
- Intensity: {intensity}/10
- Summary: {summary}

Return JSON:
{{
  "score": <integer 1-5>,
  "reasoning": "<one sentence explaining the score>",
  "most_accurate": "<what the model got right>",
  "missed": "<what the model missed or got wrong, or 'nothing significant'>"
}}

Scoring guide:
5 = Perfect: all emotions correct, distortions accurately identified
4 = Good: most emotions correct, minor misses on distortions  
3 = Acceptable: main emotion correct, some distortions missed
2 = Poor: significant emotions missed, distortions wrong
1 = Wrong: fundamentally misunderstood the emotional content"""


def calculate_overlap(predicted: list, expected: list) -> float:
    """
    Calculate what fraction of expected items were found in predicted.
    E.g. expected=["anxious", "sad"], predicted=["anxious", "worried"] → 0.5
    """
    if not expected:
        return 1.0 if not predicted else 0.0
    
    predicted_lower = [p.lower() for p in predicted]
    expected_lower = [e.lower() for e in expected]
    
    hits = sum(1 for e in expected_lower if any(e in p or p in e for p in predicted_lower))
    return hits / len(expected_lower)


def run_evaluation() -> dict:
    """Run the full evaluation pipeline and return results."""
    print("Running MindMirror Evaluation Pipeline")
    print("=" * 50)
    
    results = []
    emotion_scores = []
    distortion_scores = []
    valence_correct = 0
    intensity_correct = 0
    judge_scores = []
    
    for i, sample in enumerate(GROUND_TRUTH):
        print(f"\nEvaluating sample {i+1}/{len(GROUND_TRUTH)}...")
        
        # Get model prediction
        prediction = analyze_entry(sample["text"])
        
        # Emotion overlap score
        emotion_score = calculate_overlap(
            prediction.get("emotions", []),
            sample["expected_emotions"]
        )
        emotion_scores.append(emotion_score)
        
        # Distortion overlap score
        distortion_score = calculate_overlap(
            prediction.get("distortions", []),
            sample["expected_distortions"]
        )
        distortion_scores.append(distortion_score)
        
        # Valence exact match
        valence_match = prediction.get("valence") == sample["expected_valence"]
        if valence_match:
            valence_correct += 1
        
        # Intensity in expected range
        intensity = prediction.get("intensity", 5)
        lo, hi = sample["expected_intensity_range"]
        intensity_match = lo <= intensity <= hi
        if intensity_match:
            intensity_correct += 1
        
        # LLM-as-judge score
        import re
        judge_prompt = JUDGE_PROMPT.format(
            text=sample["text"],
            emotions=prediction.get("emotions", []),
            distortions=prediction.get("distortions", []),
            valence=prediction.get("valence"),
            intensity=prediction.get("intensity"),
            summary=prediction.get("summary", "")
        )
        judge_response = ask_llm(judge_prompt, system=JUDGE_SYSTEM, temperature=0.1)
        cleaned = re.sub(r'```json|```', '', judge_response).strip()
        
        try:
            judge_result = json.loads(cleaned)
            judge_score = judge_result.get("score", 3)
        except:
            judge_score = 3
            judge_result = {"score": 3, "reasoning": "Parse error"}
        
        judge_scores.append(judge_score)
        
        sample_result = {
            "sample_id": i + 1,
            "text_preview": sample["text"][:60] + "...",
            "emotion_overlap": round(emotion_score, 2),
            "distortion_overlap": round(distortion_score, 2),
            "valence_correct": valence_match,
            "intensity_in_range": intensity_match,
            "judge_score": judge_score,
            "judge_reasoning": judge_result.get("reasoning", ""),
        }
        results.append(sample_result)
        
        print(f"  Emotion overlap: {emotion_score:.0%} | Distortion overlap: {distortion_score:.0%} | Judge: {judge_score}/5")
    
    # Final metrics
    final_metrics = {
        "total_samples": len(GROUND_TRUTH),
        "avg_emotion_overlap": round(sum(emotion_scores) / len(emotion_scores), 3),
        "avg_distortion_overlap": round(sum(distortion_scores) / len(distortion_scores), 3),
        "valence_accuracy": round(valence_correct / len(GROUND_TRUTH), 3),
        "intensity_accuracy": round(intensity_correct / len(GROUND_TRUTH), 3),
        "avg_judge_score": round(sum(judge_scores) / len(judge_scores), 2),
        "model_used": "llama-3.1-8b-instant via Groq",
        "embedding_model": "all-MiniLM-L6-v2",
    }
    
    print("\n" + "=" * 50)
    print("EVALUATION RESULTS")
    print("=" * 50)
    for k, v in final_metrics.items():
        print(f"  {k}: {v}")
    
    # Save to file
    output = {"metrics": final_metrics, "per_sample": results}
    with open("eval/results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n✓ Results saved to eval/results.json")
    return output


if __name__ == "__main__":
    run_evaluation()