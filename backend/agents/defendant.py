from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json

DEFENDANT_PROMPT = """You are the Defense Attorney. Argue that the content is LEGITIMATE.

Claims: {claims}
Evidence: {investigator_evidence}
Prosecutor's argument: {prosecutor_argument}

Provide a brief rebuttal (max 150 words) with:
1. Counter the prosecutor's main point
2. Present supporting evidence
3. Confidence score (0-100)

Return JSON:
{{
  "argument": "brief rebuttal",
  "confidence_score": 65,
  "evidence_to_reveal": [{{"source": "url", "text": "excerpt", "credibility_score": 7}}]
}}
"""

async def defendant_turn(state: TrialState) -> TrialState:
    """Generate defendant rebuttal"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    # Query investigator namespace
    investigator_context = await blackboard.query_namespace(
        state["case_id"], "investigator",
        "evidence supporting claims", top_k=5
    )
    
    # Query prosecutor namespace
    prosecutor_context = await blackboard.query_namespace(
        state["case_id"], "prosecutor",
        "prosecution arguments", top_k=3
    )
    
    # Get latest prosecutor argument
    prosecutor_arg = ""
    if state["trial_transcript"]:
        for t in reversed(state["trial_transcript"]):
            if t["agent"] == "prosecutor":
                prosecutor_arg = t["argument_text"]
                break
    
    prompt = DEFENDANT_PROMPT.format(
        claims=claims_text,
        investigator_evidence=str(investigator_context),
        prosecutor_argument=prosecutor_arg
    )
    
    response = await llm_clients.generate_gemini_pro(prompt, temperature=0.7)
    
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        result = json.loads(response[json_start:json_end])
    except:
        result = {"argument": response, "confidence_score": 50, "evidence_to_reveal": []}
    
    # Store revealed evidence in defendant namespace
    for evidence in result.get("evidence_to_reveal", []):
        await blackboard.store_evidence(state["case_id"], "defendant", evidence)
    
    # Update state
    state["defendant_confidence"] = result["confidence_score"]
    state["defendant_revealed_evidence"].extend(result.get("evidence_to_reveal", []))
    
    # Add to transcript
    state["trial_transcript"].append({
        "agent": "defendant",
        "round": state["current_round"],
        "argument_text": result["argument"],
        "confidence_score": result["confidence_score"],
        "evidence_revealed": result.get("evidence_to_reveal", [])
    })
    
    # Store in trial_transcript namespace
    await blackboard.store_evidence(state["case_id"], "trial_transcript", {
        "agent": "defendant",
        "round": state["current_round"],
        "text": result["argument"]
    })
    
    return state
