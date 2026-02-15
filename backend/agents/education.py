from config.state import TrialState
from utils.llm_clients import llm_clients
import json

EDUCATION_PROMPT = """Based on this misinformation trial, generate an educational breakdown for the user.

Claims: {claims}
Verdict: {verdict}
Trial highlights: {transcript_summary}

Identify:
1. red_flags: What warning signs were present in the content?
2. techniques: What manipulation techniques were used?
3. decisive_evidence: What evidence was most important?
4. personalized_tips: What should the user look for next time?

Return ONLY JSON:
{{
  "red_flags": ["flag1", "flag2"],
  "techniques": ["technique1", "technique2"],
  "decisive_evidence": "description",
  "personalized_tips": ["tip1", "tip2"]
}}
"""

REPORT_PROMPT = """Generate a shareable verdict report card for social media.

Original claim: {claim}
Verdict: {verdict_category} ({score}/100)
Key evidence for: {evidence_for}
Key evidence against: {evidence_against}

Create a concise, shareable summary (max 280 characters) and a detailed report.

Return JSON:
{{
  "social_summary": "short summary",
  "detailed_report": "full report",
  "sources": ["url1", "url2"]
}}
"""

async def education_generator(state: TrialState) -> TrialState:
    """Generate educational breakdown"""
    claims_text = "\n".join([c["text"] for c in state["selected_claims"]])
    verdict = state["aggregated_verdict"]
    
    # Summarize transcript
    transcript_summary = "\n".join([
        f"{t['agent']}: {t['argument_text'][:200]}..."
        for t in state["trial_transcript"][-4:]
    ])
    
    prompt = EDUCATION_PROMPT.format(
        claims=claims_text,
        verdict=verdict["category"],
        transcript_summary=transcript_summary
    )
    
    response = await llm_clients.generate_gemini_flash(prompt, temperature=0.5)
    
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        education = json.loads(response[json_start:json_end])
    except:
        education = {
            "red_flags": ["Unable to generate"],
            "techniques": [],
            "decisive_evidence": "",
            "personalized_tips": []
        }
    
    state["education_panel"] = education
    return state

async def report_generator(state: TrialState) -> TrialState:
    """Generate shareable verdict report"""
    claim = state["selected_claims"][0]["text"] if state["selected_claims"] else "Unknown claim"
    verdict = state["aggregated_verdict"]
    
    # Collect evidence
    evidence_for = []
    evidence_against = []
    for t in state["trial_transcript"]:
        if t["agent"] == "defendant":
            evidence_for.append(t["argument_text"][:100])
        elif t["agent"] == "prosecutor":
            evidence_against.append(t["argument_text"][:100])
    
    prompt = REPORT_PROMPT.format(
        claim=claim,
        verdict_category=verdict["category"],
        score=verdict["score"],
        evidence_for="; ".join(evidence_for[:2]),
        evidence_against="; ".join(evidence_against[:2])
    )
    
    response = await llm_clients.generate_gemini_flash(prompt, temperature=0.5)
    
    try:
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        report = json.loads(response[json_start:json_end])
    except:
        report = {
            "social_summary": f"Verdict: {verdict['category']}",
            "detailed_report": verdict["summary"],
            "sources": []
        }
    
    state["verdict_report"] = report
    return state
