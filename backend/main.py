from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio
import os
from pathlib import Path
from workflow import trial_graph, create_initial_state
from config.settings import Config
from utils.tts_service import tts_service

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
    mode: str = "courtroom"  # "courtroom" or "fasttrack"

class PredictionInput(BaseModel):
    case_id: str
    verdict: str  # "real" or "fake"
    confidence: str  # "low", "medium", "high"

class JudgementInput(BaseModel):
    case_id: str
    judgement: str  # "plausible", "misleading", "not sure", "neutral"

# Store active trials in memory (for demo purposes)
active_trials = {}
# Store judgment queues for synchronization
judgment_queues = {}  # case_id -> asyncio.Queue

@app.get("/")
async def root():
    return {"message": "Unreliable Narrator API", "status": "running"}

@app.post("/api/trial/start")
async def start_trial(trial_input: TrialInput):
    """Start a new trial"""
    try:
        state = create_initial_state(trial_input.content, trial_input.input_type)
        state["mode"] = trial_input.mode
        case_id = state["case_id"]
        active_trials[case_id] = {"state": state, "status": "started", "streaming": False}
        judgment_queues[case_id] = asyncio.Queue()  # Initialize judgment queue
        return {"case_id": case_id, "status": "started", "message": "Trial initialized", "mode": trial_input.mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trial/start-with-file")
async def start_trial_with_file(
    input_type: str = Form(...),
    mode: str = Form("courtroom"),
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
        state["mode"] = mode
        case_id = state["case_id"]
        active_trials[case_id] = {"state": state, "status": "started", "streaming": False, "uploaded_file": file_path}
        judgment_queues[case_id] = asyncio.Queue()  # Initialize judgment queue
        
        return {"case_id": case_id, "status": "started", "message": "Trial initialized with uploaded file", "mode": mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trial/{case_id}/audio/{filename}")
async def serve_audio(case_id: str, filename: str):
    """Serve TTS audio files"""
    try:
        # Security: validate filename to prevent directory traversal
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        cache_dir = Path("/tmp/unreliable_narrator_tts_cache")
        file_path = cache_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            str(file_path),
            media_type="audio/mpeg",
            headers={"Cache-Control": "public, max-age=3600"}
        )
    except HTTPException:
        raise
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
            mode = state.get("mode", "courtroom")
            
            # Fast-track mode: skip courtroom simulation
            if mode == "fasttrack":
                from agents.claim_extractor import claim_extractor
                from agents.claim_triage import claim_triage
                from agents.investigator import investigator
                from agents.fasttrack_verdict import fasttrack_verdict
                
                yield f"data: {json.dumps({'phase': 'claim_extraction', 'status': 'running'})}\n\n"
                state = await claim_extractor(state)
                
                yield f"data: {json.dumps({'phase': 'claim_triage', 'status': 'running'})}\n\n"
                state = await claim_triage(state)
                
                yield f"data: {json.dumps({'phase': 'investigation', 'status': 'running'})}\n\n"
                state = await investigator(state)
                
                yield f"data: {json.dumps({'phase': 'fasttrack', 'status': 'analyzing'})}\n\n"
                result_state = await fasttrack_verdict(state)
                verdict = result_state.get('aggregated_verdict')
                
                yield f"data: {json.dumps({'phase': 'verdict', 'verdict': verdict})}\n\n"
                yield f"data: {json.dumps({'phase': 'complete', 'status': 'finished'})}\n\n"
                
                active_trials[case_id]["state"] = result_state
                return
            
            # Courtroom mode: manual round-by-round execution with judgment checkpoints
            from agents.claim_extractor import claim_extractor
            from agents.claim_triage import claim_triage
            from agents.investigator import investigator
            from agents.prosecutor import prosecutor_turn
            from agents.defendant import defendant_turn
            from agents.jury import jury_update
            from agents.verdict import termination_check, verdict_aggregator, score_calculator
            from agents.jury import jury_verdict
            from agents.awareness_scorer import awareness_scorer
            from agents.education import education_generator, report_generator
            from utils.blackboard import blackboard
            
            # Setup
            await blackboard.create_collection(state["case_id"])
            
            # Claim extraction
            yield f"data: {json.dumps({'phase': 'claim_extraction', 'status': 'running'})}\n\n"
            state = await claim_extractor(state)
            yield f"data: {json.dumps({'phase': 'claim_extraction', 'claims': state.get('claims', [])})}\n\n"
            
            # Claim triage
            state = await claim_triage(state)
            
            # Investigation
            yield f"data: {json.dumps({'phase': 'investigation', 'status': 'running'})}\n\n"
            state = await investigator(state)
            yield f"data: {json.dumps({'phase': 'investigation', 'evidence_count': len(state.get('investigator_evidence', []))})}\n\n"
            
            # Trial rounds loop
            judgment_queue = judgment_queues.get(case_id)
            if not judgment_queue:
                raise RuntimeError(f"Judgment queue not found for case {case_id}")
            
            while not state.get("should_terminate", False):
                current_round = state.get("current_round", 1)
                
                # Prosecutor turn
                state = await prosecutor_turn(state)
                transcript = state.get('trial_transcript', [])
                if transcript:
                    latest = transcript[-1]
                    audio_path = await tts_service.generate_speech(latest['argument_text'], 'prosecutor')
                    audio_url = tts_service.get_audio_url(audio_path, case_id) if audio_path else None
                    yield f"data: {json.dumps({'phase': 'trial', 'agent': 'prosecutor', 'round': current_round, 'argument': latest['argument_text'], 'confidence': latest['confidence_score'], 'audio_url': audio_url})}\n\n"
                
                # Defendant turn
                state = await defendant_turn(state)
                transcript = state.get('trial_transcript', [])
                if transcript:
                    latest = transcript[-1]
                    audio_path = await tts_service.generate_speech(latest['argument_text'], 'defendant')
                    audio_url = tts_service.get_audio_url(audio_path, case_id) if audio_path else None
                    yield f"data: {json.dumps({'phase': 'trial', 'agent': 'defendant', 'round': current_round, 'argument': latest['argument_text'], 'confidence': latest['confidence_score'], 'audio_url': audio_url})}\n\n"
                
                # CHECKPOINT: Wait for user judgment
                yield f"data: {json.dumps({'phase': 'awaiting_judgment', 'round': current_round})}\n\n"
                
                try:
                    # Wait for judgment with 5 minute timeout
                    judgement = await asyncio.wait_for(judgment_queue.get(), timeout=300.0)
                    print(f"[JUDGMENT] Received for round {current_round}: {judgement}")
                except asyncio.TimeoutError:
                    print(f"[JUDGMENT] Timeout waiting for judgment in round {current_round}, using 'neutral'")
                    judgement = "neutral"
                
                # Store judgment in state
                state["user_judgements"].append(judgement)
                active_trials[case_id]["state"] = state
                
                # Check termination
                state = termination_check(state)
                
                # If continuing, increment round
                if not state.get("should_terminate", False):
                    state["current_round"] += 1
            
            # Jury deliberation and verdict
            yield f"data: {json.dumps({'phase': 'deliberation', 'status': 'jury_deliberating'})}\n\n"
            state = await jury_verdict(state)
            
            state = verdict_aggregator(state)
            verdict = state.get('aggregated_verdict')
            yield f"data: {json.dumps({'phase': 'verdict', 'verdict': verdict})}\n\n"
            
            state = score_calculator(state)
            
            # Awareness scoring
            state = await awareness_scorer(state)
            awareness = state.get('awareness_score_result')
            yield f"data: {json.dumps({'phase': 'awareness_score', 'awareness_score': awareness})}\n\n"
            
            # Education
            state = await education_generator(state)
            education = state.get('education_panel')
            yield f"data: {json.dumps({'phase': 'education', 'education': education})}\n\n"
            
            state = await report_generator(state)
            
            # Cleanup
            await blackboard.delete_collection(state["case_id"])
            
            active_trials[case_id]["state"] = state
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
    
    if case_id not in judgment_queues:
        raise HTTPException(status_code=404, detail="Judgment queue not found")
    
    # Validate judgement
    valid_judgements = ["plausible", "misleading", "not sure", "neutral"]
    user_judgement = judgement.judgement.lower().strip()
    
    # Coerce invalid judgements to "neutral"
    if user_judgement not in valid_judgements:
        user_judgement = "neutral"
    
    # Put judgment into the queue to signal streaming process
    await judgment_queues[case_id].put(user_judgement)
    print(f"[JUDGMENT] Queued judgment for case {case_id}: {user_judgement}")
    
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
