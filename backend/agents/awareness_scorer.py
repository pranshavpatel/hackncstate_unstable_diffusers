from config.state import TrialState
from utils.llm_clients import llm_clients
import json

# Static rubric for awareness scoring
AWARENESS_RUBRIC = """
Evaluate the user's overall awareness of misinformation based on their per-round judgements.

**Your Goal**: Provide a single awareness score (1-10) that reflects how well the user recognized fraud/misinformation.

**Scoring Guidelines**:
- 9-10: Excellent - Consistently identified misleading arguments and weak evidence
- 7-8: Good - Generally recognized fraud indicators with minor lapses
- 5-6: Fair - Some awareness but missed key red flags
- 3-4: Needs Improvement - Frequently missed obvious fraud indicators
- 1-2: Poor - Did not recognize most fraud signals

**Focus on**: Did the user spot manipulation techniques, weak evidence, logical fallacies, and misleading claims?
"""

SCORING_PROMPT = """You are evaluating a user's awareness of misinformation during a trial.

**Trial Transcript** (what the user saw):
{conversation}

**User's Judgements** (after each round):
{user_judgements}

**Jury's Final Verdict**:
{jury_verdict}

**Rubric**:
{rubric}

**Your Task**:
1. **Compare** the user's judgements with the jury's final verdict
2. **Evaluate** how well the user detected fraud/misinformation
3. **Assign** a score from 1-10 based on alignment:
   - If jury said "Likely False" or "Verified False" and user said "misleading" → HIGH score (8-10)
   - If jury said "Likely False" and user said "not sure" → LOW score (3-5)
   - If jury said "Likely False" and user said "plausible" → VERY LOW score (1-2)
   - If jury said "Verified True" and user said "plausible" → HIGH score (8-10)
   - If jury said "Verified True" and user said "not sure" → MEDIUM score (5-6)
   - If jury said "Verified True" and user said "misleading" → VERY LOW score (1-2)

4. **Provide** specific, educational feedback about what they missed

Return STRICT JSON (no markdown, no triple backticks):
{{
  "score": <number from 1-10 based on alignment with jury verdict>,
  "feedback": "<specific feedback about their performance vs the correct verdict>"
}}

Be HONEST in scoring. If the user was wrong or uncertain when they should have been confident, give a LOW score.
"""

async def awareness_scorer(state: TrialState) -> TrialState:
    """Score user's awareness based on their per-round judgements"""
    
    # If no judgements, skip scoring
    if not state.get("user_judgements"):
        state["awareness_score_result"] = {
            "score": 0,
            "feedback": "No judgements were provided during the trial."
        }
        return state
    
    # Build conversation transcript
    conversation = []
    trial_transcript = state.get("trial_transcript")
    if trial_transcript:
        for entry in trial_transcript:
            conversation.append(
                f"Round {entry['round']} - {entry['agent'].upper()}: {entry['argument_text']}"
            )
    conversation_text = "\n\n".join(conversation) if conversation else "No trial transcript available"
    
    # Format user judgements
    judgements_text = "\n".join([
        f"Round {i+1}: {judgement}"
        for i, judgement in enumerate(state["user_judgements"])
    ])
    
    # Format jury verdict
    verdict = state.get("aggregated_verdict", {})
    jury_verdict_text = f"""
    Category: {verdict.get('category', 'Unknown')}
    Score: {verdict.get('score', 'N/A')}/100
    Summary: {verdict.get('summary', 'No summary available')}
    """
    
    # Build prompt
    prompt = SCORING_PROMPT.format(
        conversation=conversation_text,
        user_judgements=judgements_text,
        jury_verdict=jury_verdict_text,
        rubric=AWARENESS_RUBRIC
    )
    
    # Call LLM
    try:
        response = await llm_clients.generate_gemini_flash(prompt, temperature=0.3)
        
        # Parse JSON response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start == -1 or json_end == 0:
            raise ValueError("No JSON found in response")
        
        result = json.loads(response[json_start:json_end])
        
        # Validate structure
        if "score" not in result or "feedback" not in result:
            raise ValueError("Missing required fields in response")
        
        # Clamp score to 1-10 range
        score = max(1, min(10, int(result["score"])))
        
        state["awareness_score_result"] = {
            "score": score,
            "feedback": result["feedback"]
        }
        
    except Exception as e:
        print(f"[AWARENESS_SCORER] Error: {e}")
        # Fallback to default score
        state["awareness_score_result"] = {
            "score": 5,
            "feedback": "Unable to calculate awareness score due to processing error. Keep practicing fraud detection skills!"
        }
    
    return state
