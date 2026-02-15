# Project Structure

```
HackNCState/
│
├── 📄 README.md                          # Main documentation
├── 📄 PROJECT_SUMMARY.md                 # Detailed project summary
├── 📄 QUICK_REFERENCE.md                 # Quick command reference
├── 📄 .gitignore                         # Git ignore rules
├── 📄 docker-compose.yml                 # Full stack Docker setup
├── 🔧 setup.sh                           # Quick setup script
├── 📄 unreliable-narrator-vibe-coding-prompt.md  # Original requirements
│
├── 🐍 backend/                           # Python FastAPI Backend
│   ├── 📄 main.py                        # FastAPI server + SSE streaming
│   ├── 📄 workflow.py                    # LangGraph orchestration
│   ├── 📄 requirements.txt               # Python dependencies
│   ├── 📄 Dockerfile                     # Backend container
│   ├── 📄 .env.example                   # Environment template
│   ├── 📄 .env                           # Demo environment (needs real keys)
│   ├── 🔧 test_trial.py                  # Test script
│   │
│   ├── 📁 agents/                        # LangGraph Agent Nodes
│   │   ├── 📄 claim_extractor.py        # Extract atomic claims
│   │   ├── 📄 claim_triage.py           # Prioritize claims
│   │   ├── 📄 investigator.py           # Neutral evidence gathering
│   │   ├── 📄 prosecutor.py             # Argue misinformation
│   │   ├── 📄 defendant.py              # Argue legitimacy
│   │   ├── 📄 jury.py                   # Multi-model jury
│   │   ├── 📄 verdict.py                # Verdict aggregation
│   │   └── 📄 education.py              # Educational breakdown
│   │
│   ├── 📁 config/                        # Configuration
│   │   ├── 📄 settings.py               # Environment config
│   │   └── 📄 state.py                  # TrialState schema
│   │
│   └── 📁 utils/                         # Utilities
│       ├── 📄 blackboard.py             # Vector DB client
│       └── 📄 llm_clients.py            # Multi-model LLM wrapper
│
└── ⚛️  frontend/                         # React Frontend
    ├── 📄 package.json                   # Node dependencies
    ├── 📄 Dockerfile                     # Frontend container
    │
    ├── 📁 public/
    │   └── 📄 index.html                 # HTML template
    │
    └── 📁 src/
        ├── 📄 index.js                   # React entry point
        ├── 📄 App.js                     # Main app component
        ├── 📄 App.css                    # Global styles
        │
        └── 📁 components/
            └── 📄 Courtroom.js           # Courtroom trial display
```

## 📊 File Count Summary

- **Backend Python Files**: 15
- **Frontend React Files**: 5
- **Configuration Files**: 8
- **Documentation Files**: 4
- **Total Files**: 32+

## 🎯 Key Components

### Backend Architecture
```
FastAPI Server (main.py)
    ↓
LangGraph Workflow (workflow.py)
    ↓
┌─────────────────────────────────────┐
│  Agent Nodes (agents/)              │
│  - Claim Extractor                  │
│  - Investigator                     │
│  - Prosecutor ←→ Defendant          │
│  - Jury (Multi-Model)               │
│  - Verdict Aggregator               │
│  - Education Generator              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Infrastructure (utils/)            │
│  - Blackboard.io Vector DB          │
│  - Multi-Model LLM Clients          │
│    (Gemini, Claude, GPT-4o, Llama)  │
└─────────────────────────────────────┘
```

### Frontend Architecture
```
React App (App.js)
    ↓
Landing Page
    ↓
Submit Content
    ↓
Courtroom Component (Courtroom.js)
    ↓
SSE Stream Connection
    ↓
┌─────────────────────────────────────┐
│  Real-Time Display                  │
│  - Prosecutor Panel (Red)           │
│  - Defendant Panel (Green)          │
│  - Jury Panel (Gold)                │
│  - Verdict Reveal                   │
│  - Education Panel                  │
└─────────────────────────────────────┘
```

## 🔄 Data Flow

```
User Input
    ↓
Claim Extraction → Claims Array
    ↓
Investigation → Blackboard.io (investigator namespace)
    ↓
Trial Loop (5 rounds max)
    ├─ Prosecutor → Blackboard.io (prosecutor namespace)
    ├─ Defendant → Blackboard.io (defendant namespace)
    ├─ Jury Update → Blackboard.io (jury_notes/* namespaces)
    └─ Termination Check
    ↓
Jury Verdict (Parallel)
    ├─ Gemini Pro
    ├─ Claude Sonnet
    └─ Gemini Flash
    ↓
Verdict Aggregation
    ↓
Education + Report Generation
    ↓
Cleanup (Delete Blackboard.io collection)
    ↓
Display to User
```

## 🎨 Color Scheme

- **Background**: Dark gradient (#1a1a1a → #2d2d2d)
- **Primary Accent**: Gold (#d4af37)
- **Prosecutor**: Red (#c41e3a)
- **Defendant**: Green (#228b22)
- **Text**: Light gray (#e0e0e0)

## 🚀 Deployment Options

1. **Local Development**
   - Backend: `python main.py`
   - Frontend: `npm start`

2. **Docker Compose**
   - `docker-compose up --build`

3. **Separate Containers**
   - Backend: `docker build -t narrator-backend ./backend`
   - Frontend: `docker build -t narrator-frontend ./frontend`

## 📦 Dependencies

### Backend (Python)
- langgraph, langchain
- google-generativeai, anthropic, openai, together
- fastapi, uvicorn
- httpx, requests, beautifulsoup4
- python-dotenv, pydantic

### Frontend (React)
- react, react-dom
- framer-motion
- axios

## 🎓 Technologies Used

- **AI/ML**: Google Gemini, Claude, GPT-4o, Llama 3
- **Orchestration**: LangGraph
- **Vector DB**: Blackboard.io
- **Backend**: Python, FastAPI
- **Frontend**: React, Framer Motion
- **Streaming**: Server-Sent Events (SSE)
- **Containerization**: Docker, Docker Compose
