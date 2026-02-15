from config.state import TrialState
from typing import Dict

def verdict_aggregator(state: TrialState) -> TrialState:
    """Aggregate jury verdicts into final verdict"""
    verdicts = state["jury_verdicts"]
    
    if not verdicts:
        state["aggregated_verdict"] = {
            "score": 50,
            "category": "Uncertain",
            "summary": "No verdicts available",
            "dissenting_opinions": []
        }
        return state
    
    # Calculate weighted average
    total_score = sum(v["confidence_score"] for v in verdicts)
    avg_score = total_score / len(verdicts)
    
    # Determine category
    if avg_score >= 80:
        category = "Verified True"
    elif avg_score >= 60:
        category = "Likely True"
    elif avg_score >= 40:
        category = "Uncertain / Mixed"
    elif avg_score >= 20:
        category = "Likely False"
    else:
        category = "Confirmed Misinformation"
    
    # Collect dissenting opinions (jurors >20 points from average)
    dissenting = [v for v in verdicts if abs(v["confidence_score"] - avg_score) > 20]
    
    # Generate summary
    summary = f"The jury reached a verdict of '{category}' with an average confidence score of {avg_score:.1f}/100. "
    summary += f"{len(verdicts)} jurors deliberated independently."
    
    state["aggregated_verdict"] = {
        "score": round(avg_score, 1),
        "category": category,
        "summary": summary,
        "dissenting_opinions": dissenting,
        "individual_verdicts": verdicts
    }
    
    return state

def termination_check(state: TrialState) -> TrialState:
    """Check if trial should terminate"""
    # Max rounds reached
    if state["current_round"] >= state["max_rounds"]:
        state["should_terminate"] = True
        state["termination_reason"] = "max_rounds"
        return state
    
    # Confidence collapse (one side below 15%)
    if state["prosecutor_confidence"] < 15:
        state["should_terminate"] = True
        state["termination_reason"] = "confidence_collapse"
        return state
    
    if state["defendant_confidence"] < 15:
        state["should_terminate"] = True
        state["termination_reason"] = "confidence_collapse"
        return state
    
    # Evidence exhaustion (no new evidence in last round)
    if len(state["trial_transcript"]) >= 4:
        last_two_rounds = state["trial_transcript"][-4:]
        new_evidence_count = sum(len(t.get("evidence_revealed", [])) for t in last_two_rounds)
        if new_evidence_count == 0:
            state["should_terminate"] = True
            state["termination_reason"] = "exhaustion"
            return state
    
    state["should_terminate"] = False
    return state

def score_calculator(state: TrialState) -> TrialState:
    """Calculate user score based on prediction accuracy"""
    if not state.get("user_prediction") or not state.get("aggregated_verdict"):
        state["user_score_delta"] = 0
        return state
    
    user_pred = state["user_prediction"]["verdict"]  # "real" or "fake"
    user_conf = state["user_prediction"]["confidence"]  # "low", "medium", "high"
    jury_score = state["aggregated_verdict"]["score"]
    
    # Determine if prediction was correct
    # jury_score > 50 means "real", < 50 means "fake"
    jury_verdict = "real" if jury_score > 50 else "fake"
    correct = (user_pred == jury_verdict)
    
    # Calculate points
    if correct:
        if user_conf == "high":
            points = 25
        else:
            points = 10
    else:
        if user_conf == "high":
            points = -15
        else:
            points = -5
    
    state["user_score_delta"] = points
    return state
