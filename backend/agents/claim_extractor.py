from config.state import TrialState
from utils.llm_clients import llm_clients
import json

CLAIM_EXTRACTOR_PROMPT = """You are a claim extraction specialist. Break down the following content into atomic, independently verifiable claims.

Content: {content}

For each claim, provide:
1. text: The exact claim statement
2. category: The type of claim (factual, opinion, prediction, etc.)
3. verifiability_score: 0-100 score on how verifiable this claim is
4. priority: 0-100 score on importance (based on potential harm if false and virality risk)

Return ONLY a JSON array of claims in this exact format:
[{{"text": "claim text", "category": "factual", "verifiability_score": 85, "priority": 90}}]
"""

async def claim_extractor(state: TrialState) -> TrialState:
    """Extract atomic claims from input content"""
    prompt = CLAIM_EXTRACTOR_PROMPT.format(content=state["raw_input"])
    response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
    
    try:
        # Extract JSON from response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        claims = json.loads(response[json_start:json_end])
    except:
        claims = [{"text": state["raw_input"], "category": "factual", "verifiability_score": 50, "priority": 50}]
    
    state["claims"] = claims
    return state
