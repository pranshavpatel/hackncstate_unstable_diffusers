from typing import TypedDict, List, Dict, Optional

class TrialState(TypedDict):
    # Case metadata
    case_id: str
    input_type: str  # "url", "text", "image", "social_post"
    raw_input: str
    
    # Claim extraction
    claims: List[Dict]  # [{text, category, verifiability_score, priority}]
    selected_claims: List[Dict]  # Top claims chosen for trial
    
    # Investigation
    investigator_evidence: List[Dict]  # [{source_url, text, credibility_score, timestamp}]
    
    # Private agent arsenals (NOT in vector DB until revealed)
    prosecutor_private_evidence: List[Dict]
    defendant_private_evidence: List[Dict]
    
    # Trial state
    current_round: int
    max_rounds: int  # 5
    trial_transcript: List[Dict]  # [{agent, round, argument_text, confidence_score, evidence_revealed}]
    
    # Prosecutor state
    prosecutor_revealed_evidence: List[Dict]  # Evidence that has been stored in DB
    prosecutor_confidence: float  # 0-100, updated each round
    
    # Defendant state
    defendant_revealed_evidence: List[Dict]
    defendant_confidence: float
    
    # User interactions
    user_interventions: List[Dict]  # [{round, type, content, addressed_to}]
    
    # Jury state
    jury_members: List[Dict]  # [{model_name, api_provider, current_lean, notes}]
    
    # Termination
    should_terminate: bool
    termination_reason: Optional[str]  # "max_rounds", "convergence", "exhaustion", "confidence_collapse"
    
    # Verdict
    user_prediction: Optional[Dict]  # {verdict: "real"/"fake", confidence: "low"/"medium"/"high"}
    jury_verdicts: List[Dict]  # [{juror_id, model, score, top_3_reasons, key_evidence, dissent_note}]
    aggregated_verdict: Optional[Dict]  # {score, category, summary, dissenting_opinions}
    
    # Scoring
    user_score_delta: int
    education_panel: Optional[Dict]  # {red_flags, techniques, decisive_evidence, personalized_tips}
    verdict_report: Optional[Dict]  # Shareable report content
    
    # Awareness scoring
    user_judgements: List[str]  # Per-round judgements: ["plausible", "misleading", "not sure", "neutral"]
    awareness_score_result: Optional[Dict]  # {rounds: [...], summary: {..., final_score_out_of_10: X}}
