from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json
from datetime import datetime

INVESTIGATOR_PROMPT = """You are the Court Investigator in a misinformation trial. Your role is NEUTRAL evidence gathering.

Claims to investigate:
{claims}

Search the web for REAL, CURRENT information about these claims. For each piece of evidence:
- Find actual URLs from credible sources (news sites, official sites, fact-checkers)
- Extract specific facts, dates, quotes
- Rate source credibility (1-10)
- Note if it supports or contradicts the claim

Return ONLY a JSON array:
[{{"source_url": "actual_url", "text": "specific excerpt with facts/dates", "credibility_score": 8, "supports_claim": true}}]

Be specific. Include dates, names, numbers. No vague statements.
"""

async def investigator(state: TrialState) -> TrialState:
    """Gather neutral baseline evidence using Gemini's grounding"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    # Use Gemini with Google Search grounding
    prompt = INVESTIGATOR_PROMPT.format(claims=claims_text)
    
    # Gemini will search the web and cite real sources
    response = await llm_clients.generate_gemini_grounded(prompt)
    
    try:
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        evidence = json.loads(response[json_start:json_end])
    except:
        # Fallback: create basic evidence structure
        evidence = [{
            "source_url": "web_search",
            "text": response[:500],
            "credibility_score": 5,
            "supports_claim": False,
            "timestamp": datetime.now().isoformat()
        }]
    
    # Add timestamp to evidence
    for e in evidence:
        if "timestamp" not in e:
            e["timestamp"] = datetime.now().isoformat()
    
    # Store in investigator namespace
    for e in evidence:
        await blackboard.store_evidence(state["case_id"], "investigator", e)
    
    state["investigator_evidence"] = evidence
    return state
