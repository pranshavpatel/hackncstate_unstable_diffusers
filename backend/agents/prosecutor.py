from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json

PROSECUTOR_PROMPT = """You are the Prosecutor in a misinformation trial. Argue that the content is MISINFORMATION.

Claims: {claims}
Evidence: {investigator_evidence}
{previous_arguments}
{first_round_argument}

Provide a brief argument (max 150 words) with:
1. Your main point against the claim
2. Key evidence
3. HONEST confidence score (0-100) - Be realistic. If evidence is weak or circumstantial, score lower. Only score 80+ if you have multiple verified sources directly contradicting the claim.

Confidence guidelines:
- 90-100: Multiple verified sources directly prove it's false
- 70-89: Strong evidence suggests it's false
- 50-69: Some evidence against, but not conclusive
- 30-49: Weak evidence, mostly speculation
- 0-29: Very little evidence, claim might be true

Return JSON:
{{
  "argument": "brief argument",
  "confidence_score": <identified score>,
  "evidence_to_reveal": [{{"source": "url", "text": "excerpt", "credibility_score": <identified score>}}]
}}

INSTRUCTIONS
The response should be a normal JSON like the template given above. Don't give json response with triple back ticks.
For each round, you should have a different argument which adds to your initial reasoning and strengthens your case.
DO NOT repeat the same points from your first round argument. Build upon it with NEW evidence and reasoning.
Be specific. Include dates, names, numbers. No vague statements.
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
    
    # Extract first round prosecutor argument
    first_round_arg = ""
    if state["current_round"] > 1:
        for t in state["trial_transcript"]:
            if t["agent"] == "prosecutor" and t["round"] == 1:
                first_round_arg = t["argument_text"]
                break
    
    prompt = PROSECUTOR_PROMPT.format(
        claims=claims_text,
        investigator_evidence=str(investigator_context),
        previous_arguments=f"\n\nPrevious arguments:\n{previous_args}" if previous_args else "",
        first_round_argument=f"\n\nYour first round argument (DO NOT REPEAT):\n{first_round_arg}" if first_round_arg else ""
    )
    
    response = await llm_clients.generate_gemini_pro(prompt, temperature=0.7)
    
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        result = json.loads(response[json_start:json_end])
    except:
        result = {"argument": response, "confidence_score": 50, "evidence_to_reveal": []}
    
    # Store revealed evidence in prosecutor namespace
    print(f"\n[PROSECUTOR] Revealing {len(result.get('evidence_to_reveal', []))} pieces of evidence:")
    for evidence in result.get("evidence_to_reveal", []):
        print(f"  - Source: {evidence.get('source', 'N/A')}")
        print(f"    Text: {evidence.get('text', 'N/A')[:100]}...")
        print(f"    Credibility: {evidence.get('credibility_score', 'N/A')}/10")
        store_result = await blackboard.store_evidence(state["case_id"], "prosecutor", evidence)
        print(f"    Store result: {store_result}")
    print()
    
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
