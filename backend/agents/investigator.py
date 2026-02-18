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

INSTRUCTIONS
The response should be a normal JSON like the template given above. Don't give json response with triple back ticks.
"""

async def investigator(state: TrialState) -> TrialState:
    """Gather neutral baseline evidence using Gemini's grounding"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    evidence = []
    
    # NEW: If input is video, analyze for manipulation (minimal token usage)
    if state.get("input_type") == "video":
        print(f"[INVESTIGATOR] Running video forensics")
        try:
            # Reuse uploaded video file from claim extraction
            video_file = state.get("uploaded_video_file")
            if video_file:
                # print(f"[INVESTIGATOR] Reusing uploaded video file: {video_file.name}")
                # Analyze using existing file
                response = llm_clients.client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[video_file, """Briefly analyze this video for AI manipulation signs:
- Unnatural facial movements or lip-sync issues?
- Synthetic voice or audio artifacts?
- Visual glitches or inconsistencies?
Return: "AUTHENTIC" or "SUSPICIOUS: [brief reason]"
Keep response under 50 words."""],
                    config={'temperature': 0.3}
                )
                forensics = response.text
                print(f"[INVESTIGATOR] Video forensics result: {forensics}")
                evidence.append({
                    "source_url": "video_forensics_analysis",
                    "text": f"Video Forensics Analysis: {forensics}",
                    "credibility_score": 10,
                    "supports_claim": "SUSPICIOUS" not in forensics.upper(),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Clean up video file after forensics
                try:
                    llm_clients.client.files.delete(name=video_file.name)
                    # print(f"[INVESTIGATOR] Cleaned up video file: {video_file.name}")
                except:
                    pass
            else:
                print("[INVESTIGATOR] No uploaded video file found in state")
        except Exception as e:
            print(f"[INVESTIGATOR] Video forensics failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Use Gemini with Google Search grounding for web evidence
    prompt = INVESTIGATOR_PROMPT.format(claims=claims_text)
    
    # Gemini will search the web and cite real sources
    response = await llm_clients.generate_gemini_grounded(prompt)
    
    try:
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        web_evidence = json.loads(response[json_start:json_end])
        evidence.extend(web_evidence)
    except:
        # Fallback: create basic evidence structure
        evidence.append({
            "source_url": "web_search",
            "text": response[:500],
            "credibility_score": 5,
            "supports_claim": False,
            "timestamp": datetime.now().isoformat()
        })
    
    # Add timestamp to evidence that doesn't have it
    for e in evidence:
        if "timestamp" not in e:
            e["timestamp"] = datetime.now().isoformat()
    
    # Store in investigator namespace
    for e in evidence:
        await blackboard.store_evidence(state["case_id"], "investigator", e)
    
    state["investigator_evidence"] = evidence
    return state
