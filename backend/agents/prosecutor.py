from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json

PROSECUTOR_PROMPT = """You are the Prosecutor in a misinformation trial. Argue that the content is MISINFORMATION.

Claims: {claims}
Evidence: {investigator_evidence}
{previous_arguments}

Provide a brief argument (max 150 words) with:
1. Your main point against the claim
2. Key evidence
3. Confidence score (0-100)

Return JSON:
{{
  "argument": "brief argument",
  "confidence_score": 75,
  "evidence_to_reveal": [{{"source": "url", "text": "excerpt", "credibility_score": 8}}]
}}
"""

async def prosecutor_turn(state: TrialState) -> TrialState:
    """Generate prosecutor argument"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    # Query investigator namespace
    investigator_context = await blackboard.query_namespace(
        state["case_id"], "investigator", 
        "evidence against claims", top_k=5
    )
    
    # Query defendant namespace for rebuttals
    defendant_context = []
    if state["current_round"] > 1:
        defendant_context = await blackboard.query_namespace(
            state["case_id"], "defendant",
            "defense arguments", top_k=3
        )
    
    # Build previous arguments context
    previous_args = ""
    if state["trial_transcript"]:
        recent = state["trial_transcript"][-2:]
        previous_args = "\n".join([f"{t['agent']}: {t['argument_text'][:200]}..." for t in recent])
    
    prompt = PROSECUTOR_PROMPT.format(
        claims=claims_text,
        investigator_evidence=str(investigator_context),
        previous_arguments=f"\n\nPrevious arguments:\n{previous_args}" if previous_args else ""
    )
    
    response = await llm_clients.generate_gemini_pro(prompt, temperature=0.7)
    
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        result = json.loads(response[json_start:json_end])
    except:
        result = {"argument": response, "confidence_score": 50, "evidence_to_reveal": []}
    
    # Store revealed evidence in prosecutor namespace
    for evidence in result.get("evidence_to_reveal", []):
        await blackboard.store_evidence(state["case_id"], "prosecutor", evidence)
    
    # Update state
    state["prosecutor_confidence"] = result["confidence_score"]
    state["prosecutor_revealed_evidence"].extend(result.get("evidence_to_reveal", []))
    
    # Add to transcript
    state["trial_transcript"].append({
        "agent": "prosecutor",
        "round": state["current_round"],
        "argument_text": result["argument"],
        "confidence_score": result["confidence_score"],
        "evidence_revealed": result.get("evidence_to_reveal", [])
    })
    
    # Store in trial_transcript namespace
    await blackboard.store_evidence(state["case_id"], "trial_transcript", {
        "agent": "prosecutor",
        "round": state["current_round"],
        "text": result["argument"]
    })
    
    return state
