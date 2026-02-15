from config.state import TrialState
from utils.llm_clients import llm_clients
from utils.blackboard import blackboard
import json
import asyncio

JUROR_PROMPT = """You are Juror {juror_id} in a misinformation trial. You are evaluating whether submitted content is real or fake based on the evidence and arguments presented.

Claims being evaluated:
{claims}

Trial transcript so far:
{transcript}

Your previous notes:
{previous_notes}

Update your assessment:
- Current lean: 0 (definitely fake) to 100 (definitely real)
- Key evidence that influenced your lean
- Logical weaknesses you noticed in either side's arguments
- Unanswered questions you still have

Return ONLY a JSON object:
{{
  "current_lean": 45,
  "key_evidence": "description",
  "logical_weaknesses": "observations",
  "unanswered_questions": "questions"
}}
"""

VERDICT_PROMPT = """You are Juror {juror_id} delivering your final verdict in a misinformation trial.

Claims evaluated:
{claims}

All evidence and arguments:
{all_context}

Your notes throughout the trial:
{jury_notes}

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
  "key_evidence": "most decisive evidence",
  "dissent_note": "if you disagree with apparent consensus"
}}

Score: 0-20=Confirmed Misinformation, 20-40=Likely False, 40-60=Uncertain, 60-80=Likely True, 80-100=Verified True
"""

async def jury_update(state: TrialState) -> TrialState:
    """Update all jurors' private notes after each argument"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    # Get recent transcript
    recent_transcript = state["trial_transcript"][-3:] if len(state["trial_transcript"]) > 3 else state["trial_transcript"]
    transcript_text = "\n".join([f"{t['agent']}: {t['argument_text'][:300]}..." for t in recent_transcript])
    
    async def update_juror(juror):
        juror_id = juror["juror_id"]
        
        # Query juror's previous notes
        previous_notes = await blackboard.query_namespace(
            state["case_id"], f"jury_notes/juror_{juror_id}",
            "my previous assessment", top_k=1
        )
        
        prompt = JUROR_PROMPT.format(
            juror_id=juror_id,
            claims=claims_text,
            transcript=transcript_text,
            previous_notes=str(previous_notes) if previous_notes else "No previous notes"
        )
        
        # Use different models for different jurors
        if juror["model_name"] == "gemini-pro":
            response = await llm_clients.generate_gemini_pro(prompt, temperature=0.5)
        elif juror["model_name"] == "claude":
            response = await llm_clients.generate_claude(prompt, temperature=0.5)
        elif juror["model_name"] == "gemini-flash":
            response = await llm_clients.generate_gemini_flash(prompt, temperature=0.5)
        else:
            response = await llm_clients.generate_gemini_flash(prompt, temperature=0.5)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            notes = json.loads(response[json_start:json_end])
        except:
            notes = {"current_lean": 50, "key_evidence": "", "logical_weaknesses": "", "unanswered_questions": ""}
        
        # Store in private jury_notes namespace
        await blackboard.store_evidence(
            state["case_id"], 
            f"jury_notes/juror_{juror_id}",
            {"round": state["current_round"], "notes": notes}
        )
        
        juror["current_lean"] = notes["current_lean"]
        juror["notes"] = notes
    
    # Update all jurors in parallel
    await asyncio.gather(*[update_juror(j) for j in state["jury_members"]])
    
    return state

async def jury_verdict(state: TrialState) -> TrialState:
    """Generate final verdicts from all jurors"""
    claims_text = "\n".join([f"- {c['text']}" for c in state["selected_claims"]])
    
    # Get all public evidence
    investigator_evidence = await blackboard.query_namespace(state["case_id"], "investigator", "all evidence", top_k=10)
    prosecutor_evidence = await blackboard.query_namespace(state["case_id"], "prosecutor", "all arguments", top_k=10)
    defendant_evidence = await blackboard.query_namespace(state["case_id"], "defendant", "all arguments", top_k=10)
    
    all_context = f"Investigator: {investigator_evidence}\nProsecutor: {prosecutor_evidence}\nDefendant: {defendant_evidence}"
    
    async def get_verdict(juror):
        juror_id = juror["juror_id"]
        
        # Query juror's complete notes
        jury_notes = await blackboard.query_namespace(
            state["case_id"], f"jury_notes/juror_{juror_id}",
            "all my notes", top_k=10
        )
        
        prompt = VERDICT_PROMPT.format(
            juror_id=juror_id,
            claims=claims_text,
            all_context=all_context[:2000],
            jury_notes=str(jury_notes)
        )
        
        # Use different models
        if juror["model_name"] == "gemini-pro":
            response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
        elif juror["model_name"] == "claude":
            response = await llm_clients.generate_claude(prompt, temperature=0.3)
        elif juror["model_name"] == "gemini-flash":
            response = await llm_clients.generate_gemini_flash(prompt, temperature=0.3)
        elif juror["model_name"] == "gpt4":
            response = await llm_clients.generate_gpt4(prompt, temperature=0.3)
        else:
            response = await llm_clients.generate_gemini_flash(prompt, temperature=0.3)
        
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            verdict = json.loads(response[json_start:json_end])
        except:
            verdict = {
                "confidence_score": 50,
                "verdict_category": "Uncertain",
                "top_3_reasons": ["Unable to parse verdict"],
                "key_evidence": "",
                "dissent_note": ""
            }
        
        verdict["juror_id"] = juror_id
        verdict["model"] = juror["model_name"]
        return verdict
    
    # Get all verdicts in parallel
    verdicts = await asyncio.gather(*[get_verdict(j) for j in state["jury_members"]])
    
    state["jury_verdicts"] = verdicts
    return state
