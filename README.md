# The Unreliable Narrator

AI-powered courtroom simulation for misinformation detection. Submit suspicious content and watch AI agents battle it out in a dramatic trial, with a multi-model jury delivering the final verdict.

## 🎯 Features

- **Multi-Agent Courtroom**: Prosecutor and Defendant AI agents argue in real-time
- **Strategic Evidence Reveal**: Agents strategically reveal evidence across multiple rounds
- **Multi-Model Jury**: 3-5 different AI models deliberate independently (Gemini, Claude, GPT-4o, Llama)
- **Real-Time Streaming**: Watch arguments unfold live via Server-Sent Events
- **Educational Breakdown**: Learn what red flags to look for in misinformation
- **Ephemeral Vector DB**: Each case creates isolated evidence storage, deleted after verdict

## 🏗️ Architecture

### Backend (Python + LangGraph)
- **LangGraph**: Multi-agent workflow orchestration
- **Google Gemini 2.5**: Primary LLM for all agents
- **Blackboard.io**: Ephemeral vector database with namespace isolation
- **FastAPI**: REST API + SSE streaming
- **Multi-Model Support**: Claude, GPT-4o, Llama 3 for jury diversity

### Frontend (React)
- **React 18**: Modern UI with hooks
- **Framer Motion**: Smooth animations for courtroom drama
- **SSE Client**: Real-time trial streaming
- **Responsive Design**: Mobile-friendly courtroom interface

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- API Keys (see `.env.example`)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# Run the server
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will start on `http://localhost:3000`

## 🔑 Required API Keys

Add these to `backend/.env`:

1. **Google Gemini API** (Required)
   - Get from: https://makersuite.google.com/app/apikey
   - Used for: All primary agents (Prosecutor, Defendant, Investigator, Jurors)

2. **Blackboard.io API** (Required)
   - Get from: https://blackboard.io
   - Used for: Vector database, web search, RAG queries

3. **Anthropic API** (Optional - for jury diversity)
   - Get from: https://console.anthropic.com/
   - Used for: Claude Sonnet as jury member

4. **OpenAI API** (Optional - for jury diversity)
   - Get from: https://platform.openai.com/api-keys
   - Used for: GPT-4o as jury member

5. **Together AI API** (Optional - for jury diversity)
   - Get from: https://api.together.xyz/
   - Used for: Llama 3 as jury member

## 🚀 Usage

1. Start the backend server: `python backend/main.py`
2. Start the frontend: `npm start` in the `frontend` directory
3. Open `http://localhost:3000` in your browser
4. Paste suspicious content (text, URL, or claim)
5. Click "Start Trial" and watch the courtroom drama unfold
6. See the multi-model jury verdict with evidence breakdown

## 📊 Trial Flow

```
User Input → Claim Extraction → Investigation → Trial Loop → Jury Verdict → Education
                                                    ↓
                                    Prosecutor ↔ Defendant
                                    (5 rounds max, strategic evidence reveal)
                                                    ↓
                                    Jury updates after each argument
                                                    ↓
                                    Termination check (max rounds, convergence, etc.)
```

## 🎮 Demo Example

Try this sample misinformation claim:

```
"NASA confirmed that aliens exist on Mars last Tuesday and will make an official announcement next week."
```

Watch as:
1. Claims are extracted and prioritized
2. Investigator gathers neutral evidence
3. Prosecutor argues it's misinformation
4. Defendant steel-mans the legitimacy
5. Jury of 3 AI models deliberates independently
6. Final verdict reveals the truth with evidence

## 🏛️ Blackboard.io Namespace Architecture

Each trial creates an isolated collection with 5 namespaces:

- `investigator`: Baseline neutral evidence (read: all, write: investigator only)
- `prosecutor`: Prosecution's revealed evidence (strategic reveal)
- `defendant`: Defense's revealed evidence (strategic reveal)
- `jury_notes/juror_N`: Private notes per juror (private to each juror)
- `trial_transcript`: Complete chronological record (read: all, write: system)

**All data is deleted after the verdict** - no persistence between cases.

## 🎯 Hackathon Build Priority

### Day 1: Core Trial Loop ✅
- [x] LangGraph workflow with TrialState
- [x] Investigator → Prosecutor → Defendant loop
- [x] Blackboard.io integration with namespaces
- [x] Basic termination (max 5 rounds)

### Day 2: Jury + Frontend ✅
- [x] 3-member jury with parallel deliberation
- [x] Streaming courtroom UI with SSE
- [x] Strategic evidence reveal mechanic
- [x] Real-time argument display

### Day 3: Polish + Features
- [ ] User prediction input (before verdict)
- [ ] Scoring system and leaderboard
- [ ] "What You Should Have Noticed" education panel
- [ ] Shareable verdict cards
- [ ] Additional termination triggers
- [ ] Mobile responsiveness

## 🛠️ Tech Stack

- **Backend**: Python, LangGraph, FastAPI, Google Gemini, Anthropic Claude, OpenAI GPT-4o
- **Frontend**: React, Framer Motion, Axios
- **Database**: Blackboard.io (ephemeral vector DB)
- **Streaming**: Server-Sent Events (SSE)
- **Deployment**: Docker-ready (optional)

## 📝 Project Structure

```
HackNCState/
├── backend/
│   ├── agents/           # LangGraph agent nodes
│   │   ├── claim_extractor.py
│   │   ├── claim_triage.py
│   │   ├── investigator.py
│   │   ├── prosecutor.py
│   │   ├── defendant.py
│   │   ├── jury.py
│   │   ├── verdict.py
│   │   └── education.py
│   ├── config/
│   │   ├── settings.py   # Environment config
│   │   └── state.py      # TrialState schema
│   ├── utils/
│   │   ├── blackboard.py # Vector DB client
│   │   └── llm_clients.py # Multi-model LLM wrapper
│   ├── workflow.py       # LangGraph orchestration
│   ├── main.py          # FastAPI server
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── Courtroom.js
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   └── package.json
└── README.md
```

## 🎨 Design Philosophy

- **Courtroom Drama**: Cinematic, immersive experience with real-time streaming
- **Evidence-Based**: Arguments scored on evidence quality, not rhetoric
- **Educational**: Every trial teaches media literacy skills
- **Privacy-First**: Ephemeral storage, no data persistence between cases
- **Multi-Model**: Jury diversity prevents single-model bias

## 🐛 Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (need 3.9+)
- Verify API keys in `.env`
- Install dependencies: `pip install -r requirements.txt`

**Frontend won't connect:**
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify `API_BASE` in `App.js` matches backend URL

**No jury verdicts:**
- Check that at least Gemini API key is configured
- Other jury models (Claude, GPT-4o) are optional but enhance diversity

## 📄 License

MIT License - Built for HackNCState 2024

## 🙏 Acknowledgments

- Google Gemini for primary LLM capabilities
- Blackboard.io for ephemeral vector database
- LangGraph for multi-agent orchestration
- Anthropic, OpenAI, Together AI for jury model diversity
