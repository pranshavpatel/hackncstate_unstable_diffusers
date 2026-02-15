from langgraph.graph import StateGraph, END
from config.state import TrialState
from config.settings import Config
from agents.claim_extractor import claim_extractor
from agents.claim_triage import claim_triage
from agents.investigator import investigator
from agents.prosecutor import prosecutor_turn
from agents.defendant import defendant_turn
from agents.jury import jury_update, jury_verdict
from agents.verdict import verdict_aggregator, termination_check, score_calculator
from agents.education import education_generator, report_generator
from utils.blackboard import blackboard
import uuid

def create_initial_state(raw_input: str, input_type: str = "text") -> TrialState:
    """Create initial trial state"""
    case_id = str(uuid.uuid4())
    
    return {
        "case_id": case_id,
        "input_type": input_type,
        "raw_input": raw_input,
        "claims": [],
        "selected_claims": [],
        "investigator_evidence": [],
        "prosecutor_private_evidence": [],
        "defendant_private_evidence": [],
        "current_round": 1,
        "max_rounds": Config.MAX_ROUNDS,
        "trial_transcript": [],
        "prosecutor_revealed_evidence": [],
        "prosecutor_confidence": 50.0,
        "defendant_revealed_evidence": [],
        "defendant_confidence": 50.0,
        "user_interventions": [],
        "jury_members": [
            {"juror_id": 1, "model_name": "gemini-pro", "api_provider": "google", "current_lean": 50, "notes": {}},
            {"juror_id": 2, "model_name": "gemini-flash", "api_provider": "google", "current_lean": 50, "notes": {}},
            {"juror_id": 3, "model_name": "gemini-flash", "api_provider": "google", "current_lean": 50, "notes": {}},
        ],
        "should_terminate": False,
        "termination_reason": None,
        "user_prediction": None,
        "jury_verdicts": [],
        "aggregated_verdict": None,
        "user_score_delta": 0,
        "education_panel": None,
        "verdict_report": None
    }

async def setup_case(state: TrialState) -> TrialState:
    """Initialize Blackboard collection for case"""
    await blackboard.create_collection(state["case_id"])
    return state

async def cleanup_case(state: TrialState) -> TrialState:
    """Delete Blackboard collection"""
    await blackboard.delete_collection(state["case_id"])
    return state

def increment_round(state: TrialState) -> TrialState:
    """Increment round counter"""
    state["current_round"] += 1
    return state

def should_continue_trial(state: TrialState) -> str:
    """Conditional edge: continue trial or proceed to verdict"""
    if state["should_terminate"]:
        return "verdict"
    return "continue"

# Build the graph
def create_trial_graph():
    workflow = StateGraph(TrialState)
    
    # Add nodes
    workflow.add_node("setup", setup_case)
    workflow.add_node("claim_extractor", claim_extractor)
    workflow.add_node("claim_triage", claim_triage)
    workflow.add_node("investigator", investigator)
    workflow.add_node("prosecutor_turn", prosecutor_turn)
    workflow.add_node("defendant_turn", defendant_turn)
    workflow.add_node("jury_update", jury_update)
    workflow.add_node("termination_check", termination_check)
    workflow.add_node("increment_round", increment_round)
    workflow.add_node("jury_verdict", jury_verdict)
    workflow.add_node("verdict_aggregator", verdict_aggregator)
    workflow.add_node("score_calculator", score_calculator)
    workflow.add_node("education_generator", education_generator)
    workflow.add_node("report_generator", report_generator)
    workflow.add_node("cleanup", cleanup_case)
    
    # Define edges
    workflow.set_entry_point("setup")
    workflow.add_edge("setup", "claim_extractor")
    workflow.add_edge("claim_extractor", "claim_triage")
    workflow.add_edge("claim_triage", "investigator")
    workflow.add_edge("investigator", "prosecutor_turn")
    
    # Trial loop
    workflow.add_edge("prosecutor_turn", "defendant_turn")
    workflow.add_edge("defendant_turn", "termination_check")
    
    # Conditional: continue or end trial
    workflow.add_conditional_edges(
        "termination_check",
        should_continue_trial,
        {
            "continue": "increment_round",
            "verdict": "jury_verdict"
        }
    )
    workflow.add_edge("increment_round", "prosecutor_turn")
    
    # Verdict flow
    workflow.add_edge("jury_verdict", "verdict_aggregator")
    workflow.add_edge("verdict_aggregator", "score_calculator")
    workflow.add_edge("score_calculator", "education_generator")
    workflow.add_edge("education_generator", "report_generator")
    workflow.add_edge("report_generator", "cleanup")
    workflow.add_edge("cleanup", END)
    
    return workflow.compile()

# Create the compiled graph
trial_graph = create_trial_graph()
