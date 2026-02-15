from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
import os
from workflow import trial_graph, create_initial_state
from config.settings import Config

app = FastAPI(title="Unreliable Narrator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrialInput(BaseModel):
    content: str
    input_type: str = "text"

class PredictionInput(BaseModel):
    case_id: str
    verdict: str  # "real" or "fake"
    confidence: str  # "low", "medium", "high"

class JudgementInput(BaseModel):
    case_id: str
    judgement: str  # "plausible", "misleading", "not sure", "neutral"

# Store active trials in memory (for demo purposes)
active_trials = {}

@app.get("/")
async def root():
    return {"message": "Unreliable Narrator API", "status": "running"}

@app.post("/api/trial/start")
async def start_trial(trial_input: TrialInput):
    """Start a new trial"""
    try:
        state = create_initial_state(trial_input.content, trial_input.input_type)
        case_id = state["case_id"]
        active_trials[case_id] = {"state": state, "status": "started", "streaming": False}
        return {"case_id": case_id, "status": "started", "message": "Trial initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trial/start-with-file")
async def start_trial_with_file(
    input_type: str = Form(...),
    file: UploadFile = File(...)
):
    """Start trial with uploaded file (video)"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "/tmp/unreliable_narrator_uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file with unique name
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        print(f"[FILE UPLOAD] Saving {file.filename} to {file_path}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        print(f"[FILE UPLOAD] Saved {len(content)} bytes")
        
        # Create initial state with file path
        state = create_initial_state(file_path, input_type)
        case_id = state["case_id"]
        active_trials[case_id] = {"state": state, "status": "started", "streaming": False, "uploaded_file": file_path}
        
        return {"case_id": case_id, "status": "started", "message": "Trial initialized with uploaded file"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trial/{case_id}/stream")
async def stream_trial(case_id: str):
    """Stream trial progress via SSE"""
    if case_id not in active_trials:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    if active_trials[case_id].get("streaming"):
        raise HTTPException(status_code=409, detail="Already streaming")
    
    active_trials[case_id]["streaming"] = True
    
    async def event_generator():
        try:
            state = active_trials[case_id]["state"]
            yield f"data: {json.dumps({'phase': 'claim_extraction', 'status': 'running'})}\n\n"
            await asyncio.sleep(0.5)
            
            async for event in trial_graph.astream(state):
                node_name = list(event.keys())[0]
                node_state = event[node_name]
                
                if node_name == "claim_extractor":
                    yield f"data: {json.dumps({'phase': 'claim_extraction', 'claims': node_state.get('claims', [])})}\n\n"
                elif node_name == "investigator":
                    yield f"data: {json.dumps({'phase': 'investigation', 'evidence_count': len(node_state.get('investigator_evidence', []))})}\n\n"
                elif node_name == "prosecutor_turn":
                    transcript = node_state.get('trial_transcript', [])
                    if transcript:
                        latest = transcript[-1]
                        yield f"data: {json.dumps({'phase': 'trial', 'agent': 'prosecutor', 'round': node_state['current_round'], 'argument': latest['argument_text'], 'confidence': latest['confidence_score']})}\n\n"
                elif node_name == "defendant_turn":
                    transcript = node_state.get('trial_transcript', [])
                    if transcript:
                        latest = transcript[-1]
                        yield f"data: {json.dumps({'phase': 'trial', 'agent': 'defendant', 'round': node_state['current_round'], 'argument': latest['argument_text'], 'confidence': latest['confidence_score']})}\n\n"
                elif node_name == "jury_verdict":
                    yield f"data: {json.dumps({'phase': 'deliberation', 'status': 'jury_deliberating'})}\n\n"
                elif node_name == "verdict_aggregator":
                    verdict = node_state.get('aggregated_verdict')
                    yield f"data: {json.dumps({'phase': 'verdict', 'verdict': verdict})}\n\n"
                elif node_name == "awareness_scorer":
                    awareness = node_state.get('awareness_score_result')
                    yield f"data: {json.dumps({'phase': 'awareness_score', 'awareness_score': awareness})}\n\n"
                elif node_name == "education_generator":
                    education = node_state.get('education_panel')
                    yield f"data: {json.dumps({'phase': 'education', 'education': education})}\n\n"
                
                active_trials[case_id]["state"] = node_state
                await asyncio.sleep(0.1)
            
            yield f"data: {json.dumps({'phase': 'complete', 'status': 'finished'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            active_trials[case_id]["streaming"] = False
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/trial/{case_id}/prediction")
async def submit_prediction(case_id: str, prediction: PredictionInput):
    """Submit user prediction"""
    if case_id not in active_trials:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Update state with prediction
    active_trials[case_id]["state"]["user_prediction"] = {
        "verdict": prediction.verdict,
        "confidence": prediction.confidence
    }
    
    return {"status": "prediction_recorded"}

@app.post("/api/trial/{case_id}/judgement")
async def submit_judgement(case_id: str, judgement: JudgementInput):
    """Submit user judgement for a round"""
    if case_id not in active_trials:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Validate judgement
    valid_judgements = ["plausible", "misleading", "not sure", "neutral"]
    user_judgement = judgement.judgement.lower().strip()
    
    # Coerce invalid judgements to "neutral"
    if user_judgement not in valid_judgements:
        user_judgement = "neutral"
    
    # Store in state
    active_trials[case_id]["state"]["user_judgements"].append(user_judgement)
    
    return {"status": "judgement_recorded", "judgement": user_judgement}

@app.get("/api/trial/{case_id}/status")
async def get_trial_status(case_id: str):
    """Get current trial status"""
    if case_id not in active_trials:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    state = active_trials[case_id]["state"]
    
    return {
        "case_id": case_id,
        "current_round": state.get("current_round", 0),
        "max_rounds": state.get("max_rounds", 5),
        "should_terminate": state.get("should_terminate", False),
        "verdict": state.get("aggregated_verdict"),
        "score_delta": state.get("user_score_delta", 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=Config.PORT)
