from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json

FASTTRACK_VERDICT_PROMPT = """You are an AI fact-checker delivering a verdict on submitted content.

Claims being evaluated:
{claims}

Investigation Evidence:
{investigator_evidence}

Base your judgment on EVIDENCE QUALITY and LOGICAL REASONING:
- Evidence Grounding (35%): Are claims backed by verified sources?
- Logical Validity (25%): Is the reasoning chain valid? Any fallacies?
- Factual Accuracy (25%): Do stated facts match the evidence?
- Source Quality (15%): Peer-reviewed > news > blog > social > anonymous

Deliver your verdict as JSON:
{{
  "confidence_score": 35,
  "verdict_category": "Likely False",
  "top_3_reasons": ["reason 1", "reason 2", "reason 3"],
  "key_evidence": "most decisive evidence"
}}

Score: 0-20=Confirmed Misinformation, 20-40=Likely False, 40-60=Uncertain, 60-80=Likely True, 80-100=Verified True
"""

async def fasttrack_verdict(state: TrialState) -> TrialState:
    """Generate instant verdict using only investigator evidence"""
    print("\n=== FAST-TRACK VERDICT ===")
    
    claims_text = "\n".join([f"- {c['text']}" for c in state.get("selected_claims", [])])
    
    # Get investigator evidence from blackboard
    investigator_evidence = await blackboard.query_namespace(
        state["case_id"], "investigator", "all evidence", top_k=10
    )
    
    prompt = FASTTRACK_VERDICT_PROMPT.format(
        claims=claims_text,
        investigator_evidence=str(investigator_evidence)
    )
    
    print("[Gemini API] Generating verdict...")
    try:
        response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
    except Exception as e:
        print(f"[Gemini API] Failed: {e}")
        print("[Groq API] Falling back to Groq...")
        try:
            response = await llm_clients.generate_groq(prompt, temperature=0.3)
        except Exception as e2:
            print(f"[Groq API] Failed: {e2}")
            response = '{"confidence_score": 50, "verdict_category": "Uncertain", "top_3_reasons": ["API error"], "key_evidence": "N/A"}'
    
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        verdict = json.loads(response[json_start:json_end])
    except:
        verdict = {
            "confidence_score": 50,
            "verdict_category": "Uncertain",
            "top_3_reasons": ["Unable to parse verdict"],
            "key_evidence": ""
        }
    
    print(f"Verdict: {verdict['verdict_category']} (Score: {verdict['confidence_score']})")
    
    state["aggregated_verdict"] = {
        "mode": "fasttrack",  # Critical for frontend to detect fasttrack mode
        "score": verdict["confidence_score"],
        "category": verdict["verdict_category"],
        "summary": " | ".join(verdict.get("top_3_reasons", [])),
        "individual_verdicts": [{
            "juror_id": "fasttrack",
            "model": "gemini-pro",
            "confidence_score": verdict["confidence_score"],
            "top_3_reasons": verdict.get("top_3_reasons", []),
            "key_evidence": verdict.get("key_evidence", "")
        }]
    }
    state["should_terminate"] = True
    
    print("=== FAST-TRACK COMPLETE ===\n")
    return state
