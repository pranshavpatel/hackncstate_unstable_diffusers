from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json
from datetime import datetime

INVESTIGATOR_PROMPT = """You are the Court Investigator in a misinformation trial. Your role is NEUTRAL evidence gathering.
You do NOT take sides. You search for ALL relevant evidence — both supporting and contradicting the claims.

Claims to investigate:
{claims}

For each piece of evidence you find, provide:
- source_url: The URL of the source
- text: Relevant excerpt from the source
- credibility_score: 1-10 rating based on domain reputation, author credentials, editorial standards
- supports_claim: true/false - does this evidence support or contradict the claim?

Return ONLY a JSON array of evidence in this exact format:
[{{"source_url": "url", "text": "excerpt", "credibility_score": 8, "supports_claim": true}}]

Be thorough. The trial depends on the quality of your investigation.
"""

async def investigator(state: TrialState) -> TrialState:
    """Gather neutral baseline evidence"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    # Web search for evidence
    search_results = []
    for claim in state["selected_claims"]:
        results = await blackboard.web_search(claim["text"], top_k=3)
        search_results.extend(results)
    
    # Generate investigation report
    prompt = INVESTIGATOR_PROMPT.format(claims=claims_text)
    response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
    
    try:
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        evidence = json.loads(response[json_start:json_end])
    except:
        evidence = []
    
    # Add timestamp to evidence
    for e in evidence:
        e["timestamp"] = datetime.now().isoformat()
    
    # Store in investigator namespace
    for e in evidence:
        await blackboard.store_evidence(state["case_id"], "investigator", e)
    
    state["investigator_evidence"] = evidence
    return state
