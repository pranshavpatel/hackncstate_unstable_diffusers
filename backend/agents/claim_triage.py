from config.state import TrialState

async def claim_triage(state: TrialState) -> TrialState:
    """Score and prioritize claims for trial"""
    claims = state["claims"]
    
    # Sort by priority score (descending)
    sorted_claims = sorted(claims, key=lambda x: x.get("priority", 0), reverse=True)
    
    # Select top 1-3 claims
    state["selected_claims"] = sorted_claims[:3]
    
    return state
