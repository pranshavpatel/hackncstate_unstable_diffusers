# Quick Reference Guide

## 🚀 Starting the Application

### Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```
Server runs on: http://localhost:8000

### Frontend
```bash
cd frontend
npm start
```
App runs on: http://localhost:3000

## 🔧 Common Commands

### Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Run Tests
```bash
cd backend
python test_trial.py
```

### Check API Status
```bash
curl http://localhost:8000/
```

## 📝 API Endpoints

### Start a Trial
```bash
POST http://localhost:8000/api/trial/start
Content-Type: application/json

{
  "content": "Your suspicious claim here",
  "input_type": "text"
}
```

### Stream Trial Progress
```bash
GET http://localhost:8000/api/trial/{case_id}/stream
```
Returns: Server-Sent Events (SSE) stream

### Submit Prediction
```bash
POST http://localhost:8000/api/trial/{case_id}/prediction
Content-Type: application/json

{
  "case_id": "uuid-here",
  "verdict": "real",  # or "fake"
  "confidence": "high"  # or "medium", "low"
}
```

### Get Trial Status
```bash
GET http://localhost:8000/api/trial/{case_id}/status
```

## 🎯 Test Claims

Use these for testing:

### Obvious Misinformation
```
"NASA confirmed that aliens exist on Mars last Tuesday and will make an official announcement next week."
```

### Ambiguous Claim
```
"A new study shows that drinking coffee can extend your lifespan by 10 years."
```

### Partially True
```
"The COVID-19 vaccine was developed in less than a year, which is unprecedented in vaccine history."
```

## 🔑 Environment Variables

Required in `backend/.env`:

```bash
# Minimum required
GOOGLE_API_KEY=your_key_here
BLACKBOARD_API_KEY=your_key_here

# Optional for jury diversity
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
TOGETHER_API_KEY=your_key_here
```

## 🐛 Troubleshooting

### "Module not found" error
```bash
cd backend
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or change port in backend/.env
PORT=8001
```

### Frontend can't connect to backend
1. Check backend is running: `curl http://localhost:8000/`
2. Check CORS settings in `backend/main.py`
3. Verify `API_BASE` in `frontend/src/App.js`

### API key errors
1. Check `.env` file exists in `backend/`
2. Verify keys are not wrapped in quotes
3. Ensure no spaces around `=` sign
4. Restart backend after changing `.env`

## 📊 Project Structure

```
HackNCState/
├── backend/              # Python FastAPI server
│   ├── agents/          # LangGraph agent nodes
│   ├── config/          # Settings and state
│   ├── utils/           # Helper utilities
│   ├── workflow.py      # Main LangGraph workflow
│   ├── main.py          # FastAPI server
│   └── .env             # Environment variables
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── App.js       # Main app
│   │   └── App.css      # Styles
│   └── package.json
└── README.md
```

## 🎨 Key Files to Modify

### Add a new agent
1. Create file in `backend/agents/`
2. Define async function with `TrialState` parameter
3. Add node to workflow in `backend/workflow.py`

### Modify UI
- Main layout: `frontend/src/App.js`
- Courtroom: `frontend/src/components/Courtroom.js`
- Styles: `frontend/src/App.css`

### Change LLM models
- Edit `backend/utils/llm_clients.py`
- Update jury members in `backend/workflow.py` (create_initial_state)

### Adjust trial parameters
- Max rounds: `backend/config/settings.py` (MAX_ROUNDS)
- Termination logic: `backend/agents/verdict.py` (termination_check)

## 💡 Tips

1. **Start simple**: Test with Gemini only first, add other models later
2. **Watch the logs**: Backend prints useful debug info
3. **Use the test script**: `python backend/test_trial.py` for quick testing
4. **Monitor API usage**: Each trial makes 10-20+ API calls
5. **Cache responses**: Consider caching for demo to avoid rate limits

## 🔗 Useful Links

- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Google Gemini API: https://ai.google.dev/
- FastAPI Docs: https://fastapi.tiangolo.com/
- React Docs: https://react.dev/
- Framer Motion: https://www.framer.com/motion/

## 📞 Getting Help

1. Check `README.md` for detailed setup
2. Review `PROJECT_SUMMARY.md` for architecture
3. Read the original prompt: `unreliable-narrator-vibe-coding-prompt.md`
4. Check backend logs for errors
5. Use browser DevTools for frontend issues
