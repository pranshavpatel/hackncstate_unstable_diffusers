# THE UNRELIABLE NARRATOR — Comprehensive Vibe Coding Prompt

## PROJECT OVERVIEW

Build "The Unreliable Narrator" — a multi-agent AI courtroom simulation for misinformation detection. Users submit suspicious content (URLs, text, images, social media posts). The system extracts verifiable claims, then launches a full adversarial courtroom trial where AI agents argue whether the content is real or fake. A multi-model jury of 3-5 different AI models deliberates independently. Users participate as interactive jurors, predict verdicts, earn points, and learn media literacy through gamification.

**Core Philosophy**: We don't just detect misinformation — we teach people to detect it themselves. Every trial is a lesson. Every prediction is practice. Every shared verdict multiplies social impact.

**Problem Statement**: Projects within this track focus on handling misinformation, verifying social media content, battling social engineering, and detecting deceptive AI.

---

## TECH STACK

- **Primary LLM**: Google Gemini 2.5 Pro (all primary agents: Prosecutor, Defendant, Investigator, Claim Extraction, primary Juror)
- **Secondary LLMs for Jury Diversity**: Claude Sonnet (Anthropic API), GPT-4o (OpenAI API), Llama 3 (via Together AI / Groq), Gemini 2.5 Flash
- **Orchestration**: LangGraph (multi-agent workflow, turn management, state persistence, human-in-the-loop)
- **Vector Database**: Blackboard.io (ephemeral per-case evidence storage, RAG retrieval, web search capabilities)
- **Web Search**: Gemini built-in grounding with Google Search + Blackboard.io web search/retrieval
- **Fact-Checking**: Google Fact Check Tools API
- **Frontend**: React + Framer Motion (or Next.js) for real-time courtroom UI with streaming debate + gamification dashboard
- **Streaming**: Server-Sent Events (SSE) for real-time debate streaming
- **Auth & Persistence**: Firebase or Supabase (user accounts, scores, leaderboard — the ONLY persistent storage; everything else is ephemeral per case)
- **Image Analysis (optional)**: Google Cloud Vision API for image manipulation detection, OCR, reverse image search

---

## ARCHITECTURE — 6 PHASES

### PHASE 1: INTAKE & CLAIM EXTRACTION

**Step 1.1 — User Input**
- Accept: URL, raw text snippet, image upload, social media post link
- Auto-detect input type using Gemini 2.5 Flash (fast classification)
- For URLs: fetch full page content + metadata (publish date, author, domain age, domain reputation)
- For images: extract text via OCR + optionally run Error Level Analysis (ELA) for manipulation detection
- For social media posts: extract text, images, metadata, engagement metrics if available

**Step 1.2 — Claim Extraction**
- Use Gemini 2.5 Pro to break the input into atomic, independently verifiable claims
- Each claim is a single statement that can be fact-checked on its own
- Example: "NASA confirmed aliens exist on Mars last Tuesday" becomes:
  - Claim 1: NASA made a public announcement
  - Claim 2: The announcement concerned extraterrestrial life
  - Claim 3: The referenced location is Mars
  - Claim 4: This announcement occurred last Tuesday
- Output: structured JSON array of claims with text, category, and estimated verifiability score

**Step 1.3 — Claim Triage & Priority**
- Score each claim on: verifiability (can it be checked?), potential harm (how dangerous if false?), virality risk (how likely to spread?)
- High-priority claims get the full courtroom trial
- Low-priority or easily verifiable claims get a quick automated check
- Use Gemini 2.5 Flash for fast scoring
- Select the top 1-3 claims for the trial (keep it focused)

---

### PHASE 2: INVESTIGATION & BASELINE EVIDENCE

**Step 2.1 — Investigator Agent**
- Dedicated AI agent using Gemini 2.5 Pro
- Tools available to the Investigator:
  - Gemini grounded Google Search for real-time web search
  - Blackboard.io web search/retrieval capabilities
  - Google Fact Check Tools API to query existing fact-checks from established organizations
  - Reverse image search (for image-based claims)
  - Domain reputation checks (domain age, WHOIS data, known misinformation domains)
- The Investigator is NEUTRAL — it gathers all available evidence without taking sides
- It searches for: corroborating sources, contradicting sources, fact-check results, source credibility data, historical context

**Step 2.2 — Evidence → Blackboard.io (investigator namespace)**
- All baseline evidence is embedded and stored in the Blackboard.io vector database
- Stored under the `investigator` namespace within the case collection
- This becomes the PUBLIC COURT RECORD — accessible by all agents, all jurors, and the user
- Each piece of evidence includes: source URL, source credibility score, relevant text excerpt, retrieval timestamp
- This is the shared foundation that both sides will build their arguments on

---

### PHASE 3: PRIVATE RESEARCH (PRE-TRIAL)

**Step 3.1 — Prosecutor Private Research**
- The Prosecutor agent (Gemini 2.5 Pro) independently researches the claims
- It can: query the investigator namespace via RAG, perform additional web searches, query fact-check databases
- Goal: build the strongest possible case that the content is MISINFORMATION
- All research results are held in the agent's PRIVATE MEMORY — NOT yet stored in the vector DB
- The Prosecutor decides strategically which evidence to reveal and when (see Phase 4)

**Step 3.2 — Defendant Private Research**  
- The Defendant agent (Gemini 2.5 Pro, possibly with different temperature/system prompt for variety) independently researches
- Same tools and access as the Prosecutor
- Goal: build the strongest possible case that the content is LEGITIMATE
- Must genuinely steel-man the content's legitimacy — not just weakly oppose
- All research held privately until strategically revealed during the trial

---

### PHASE 4: THE COURTROOM TRIAL (STRATEGIC EVIDENCE REVEAL)

This is the core of the application. The trial unfolds in real-time, streamed to the user via SSE.

#### Blackboard.io Vector Database Namespace Architecture (EPHEMERAL — per case)

Each case creates an ISOLATED collection in Blackboard.io with a unique `case_id`. The collection contains 5 namespaces:

1. **`investigator`** — Baseline evidence gathered pre-trial. Read access: ALL agents + jury + user. Write access: Investigator agent only. Timing: populated before trial begins.

2. **`prosecutor`** — Prosecution's evidence, revealed strategically across rounds. Write access: Prosecutor agent only. Read access: ALL agents + jury + user, BUT only AFTER evidence is formally "presented to the court" (i.e., stored in this namespace). The Prosecutor does NOT dump all evidence at once — they choose what to reveal each round.

3. **`defendant`** — Defense's evidence, same strategic reveal mechanic. Write access: Defendant agent only. Same read access rules as prosecutor namespace.

4. **`jury_notes`** — Private running notes for each juror. Sub-namespaces: `jury_notes/juror_1`, `jury_notes/juror_2`, etc. Write/Read access: PRIVATE per juror — no other agent or juror can see these. Updated after EVERY argument. Contains: current lean (prosecution vs defense, 0-100), key evidence that swayed them, logical weaknesses spotted, unanswered questions.

5. **`trial_transcript`** — Complete chronological record of all arguments, rebuttals, and user interjections. Read access: ALL agents + jury + user. Write access: System (appended automatically after each argument). Allows any agent to RAG-query the full trial history (e.g., "What has the prosecutor already argued about source credibility?") — prevents repetition and enables targeted rebuttals.

**CRITICAL: The entire collection is DELETED after the verdict is delivered. No data persists between cases. The only persistent data is user scores on the leaderboard (stored in Firebase/Supabase, NOT Blackboard.io).**

#### Trial Flow

**Step 4.1 — Prosecutor Opens (Round 1)**
- The Prosecutor presents their opening argument, arguing the content is FAKE/MISINFORMATION
- Must cite specific evidence from the investigator namespace
- Uses structured legal reasoning: state the claim → present evidence against it → identify logical fallacies → source credibility issues → factual contradictions
- STRATEGICALLY SELECTS which evidence from their private research to reveal — only the selected evidence is stored in the `prosecutor` namespace and becomes visible to all
- Example: Prosecutor has 8 pieces of evidence total, reveals 3 strongest in Round 1, saves 5 for rebuttals
- Each argument receives a confidence score (0-100) based on evidence quality (see Confidence Weighting below)
- The argument text is automatically appended to the `trial_transcript` namespace

**Step 4.2 — Defendant Rebuts (Round 1)**
- The Defendant responds, arguing the content is REAL/LEGITIMATE
- MUST directly address the Prosecutor's points before presenting own evidence
- RAG-queries the `prosecutor` namespace to find weaknesses in the prosecution's revealed evidence
- RAG-queries the `investigator` namespace for supporting baseline evidence
- Reveals selected counter-evidence from their private research → stored in `defendant` namespace
- Provides corroborating sources, contextual explanations, identifies where prosecution's evidence is weak
- Also receives a confidence score
- Argument appended to `trial_transcript`

**Step 4.3 — User Intervention Window (After Each Round)**
- After each complete round (Prosecutor turn + Defendant turn), the user gets a window to:
  - (a) Ask a specific question to either agent: "Prosecutor, what about this source?" or "Defendant, how do you explain this contradiction?"
  - (b) Introduce new evidence: "I found this article that says..." (the system searches for and embeds the user's evidence)
  - (c) Challenge a specific argument: "Your source is from 2019, this claim is about 2026"
  - (d) Skip / Pass (no intervention)
- User questions/evidence are stored in the `trial_transcript` namespace
- The addressed agent MUST respond to the user's input in their next turn
- This is implemented as a LangGraph human-in-the-loop node

**Step 4.4 — Jury Memory Update (After EACH Argument)**
- After every single argument (not just at the end of a round), each juror independently:
  - RAG-queries all public namespaces (investigator, prosecutor, defendant, trial_transcript)
  - Updates their private `jury_notes` sub-namespace with: current lean score, evidence that swayed them, logical weaknesses spotted
  - This running memory ensures the final verdict reflects the ENTIRE trial, not just recency bias
- All 5 jurors update in parallel (LangGraph parallel nodes)

**Step 4.5 — Multi-Round Rebuttals (Rounds 2-5)**
- The Prosecutor and Defendant continue alternating, with each round:
  - RAG-querying the opponent's namespace to find new weaknesses
  - Revealing NEW evidence from their private arsenal
  - Directly countering the opponent's previous arguments
- Each round must introduce NEW arguments or directly counter previous points — NO REPETITION ALLOWED
- The system enforces novelty via a similarity check: compare new argument embeddings against previous arguments in `trial_transcript`
- User intervention window available after each complete round

**Step 4.6 — Debate Termination Check (After Each Round)**
- After each complete round, check if the debate should end. The debate ends when ANY of these triggers fire:
  1. **Max rounds reached**: Hard cap at **5 rounds**
  2. **Argument convergence**: Both sides' latest arguments are too similar to their previous arguments (cosine similarity > 0.85 between consecutive arguments from the same side, computed via Blackboard.io embeddings)
  3. **Evidence exhaustion**: Neither side cited any NEW evidence in the last round
  4. **Confidence collapse**: One side's confidence score drops below 15% (effective concession)
- Implemented as a LangGraph conditional edge after the jury update node
- If no termination trigger fires, loop back to the next Prosecutor turn

#### Confidence & Logic Weighting for Arguments

Every argument from both sides is scored on SUBSTANCE, not rhetoric. This prevents an eloquent model from winning on style alone:

- **Evidence Grounding (35%)**: How many claims are backed by verified, retrievable sources? An argument citing 3 verified sources scores higher than one citing none.
- **Logical Validity (25%)**: Is the reasoning chain valid? No logical fallacies (ad hominem, straw man, appeal to authority, etc.)? Formal logical structure?
- **Factual Accuracy (25%)**: Are the stated facts cross-referenced against the evidence dossier in the investigator namespace? Do they match?
- **Source Quality (15%)**: Source hierarchy: peer-reviewed research > official government/institutional sources > established news organizations > blogs/opinion pieces > social media posts > anonymous sources

Scoring is enforced via structured output from Gemini 2.5 — the model evaluates each argument against this rubric and outputs a breakdown.

---

### PHASE 5: JURY DELIBERATION & VERDICT

**Step 5.1 — User Locks Prediction**
- BEFORE the jury reveals its verdict, the user must commit to their prediction
- User selects: Real or Fake
- User selects confidence level: Low, Medium, or High
- This prediction is locked and cannot be changed after submission
- This is the core gamification mechanic — it forces the user to COMMIT to a judgment

**Step 5.2 — Multi-Model Jury Deliberation (Independent, Parallel)**
- Each juror is a DIFFERENT AI model (this is critical — diversity of models = diversity of judgment = fewer blind spots):
  - **Juror 1**: Gemini 2.5 Pro (analytical, evidence-focused reasoning)
  - **Juror 2**: Claude Sonnet (nuanced, contextual reasoning)
  - **Juror 3**: Gemini 2.5 Flash (fast pattern recognition)
  - **Juror 4**: GPT-4o (broad knowledge base)
  - **Juror 5**: Llama 3 via Together AI/Groq (open-source perspective, different training biases)
- For a 3-member jury MVP: use Gemini Pro, Claude Sonnet, and Gemini Flash (or GPT-4o)
- Each juror independently:
  - RAG-queries ALL public namespaces (investigator, prosecutor, defendant, trial_transcript)
  - RAG-queries their OWN private `jury_notes` sub-namespace (their running memory from throughout the trial)
  - Produces a verdict with:
    - Confidence score (0-100 on the fake↔real spectrum)
    - Top 3 reasons for their verdict
    - The single strongest piece of evidence that swayed them
    - Dissenting note if they disagree with what seems to be the apparent consensus
- All jurors deliberate simultaneously (LangGraph parallel nodes with barrier sync before aggregation)
- Verdicts are revealed SIMULTANEOUSLY — no juror sees another's verdict before producing their own (prevents groupthink)

**Step 5.3 — Aggregated Verdict**
- Weighted average of all juror confidence scores
- Verdict categories on the confidence spectrum:
  - **Verified True (80-100)**: Strong evidence supports legitimacy
  - **Likely True (60-80)**: Preponderance of evidence suggests legitimate
  - **Uncertain / Mixed (40-60)**: Evidence is conflicting or insufficient
  - **Likely False (20-40)**: Preponderance of evidence suggests misinformation
  - **Confirmed Misinformation (0-20)**: Strong evidence confirms this is false
- Display: overall score, each juror's individual score and reasoning, highlight any dissenting opinions (these are often the most interesting and educational)
- Generate a summary of the key arguments from both sides

---

### PHASE 6: SCORING, EDUCATION & CLEANUP

**Step 6.1 — User Score Calculation**
- Compare user's prediction against jury verdict:
  - Correct prediction: **+10 points**
  - Correct prediction + high confidence: **+25 points**
  - User asked a question during trial that demonstrably swayed the jury (appeared in a juror's reasoning): **+10 bonus points**
  - Wrong prediction: **-5 points**
  - Wrong prediction + high confidence: **-15 points**
- Update user's cumulative score in Firebase/Supabase
- Update leaderboard rankings

**Step 6.2 — Educational Breakdown ("What You Should Have Noticed")**
- After the verdict is revealed, show an educational panel:
  - Red flags that were present in the content (emotional language, fake authority, missing sources, date manipulation, out-of-context images, etc.)
  - Common manipulation techniques identified
  - Which evidence was most decisive and why
  - What the user could look for next time
- Generated by Gemini 2.5 Flash summarizing the trial transcript
- Personalized: track which types of misinformation fool the user most over time

**Step 6.3 — Verdict Report Generation**
- Generate a clean, shareable verdict card/report containing:
  - The original claim
  - Key evidence for and against
  - Jury verdict with confidence score and reasoning
  - Sources cited
  - Designed for social media sharing — when someone encounters the same misinformation, they can share this report
- Generated by Gemini 2.5 Flash

**Step 6.4 — Vector DB Deletion**
- **CRITICAL**: Delete the ENTIRE case collection from Blackboard.io
- `blackboard.delete_collection(case_id)`
- All namespaces (investigator, prosecutor, defendant, jury_notes/*, trial_transcript) are purged
- No evidence, arguments, or notes persist between cases
- Clean slate for the next trial
- The only persistent data across cases is: user accounts, scores, leaderboard (in Firebase/Supabase)

---

## GAMIFICATION & SOCIAL IMPACT FEATURES

### Leaderboard System
- Global leaderboard with all-time and weekly/monthly rankings
- Sort by: total points, accuracy percentage, streak length
- Show user's rank, points, accuracy rate, total cases judged

### Achievement Badges
- **Accuracy Streaks**: 5, 10, 25 correct predictions in a row
- **Category Mastery**: High accuracy across specific domains (politics, health, science, celebrity, technology)
- **Active Juror**: Asked X questions during trials that influenced the verdict
- **Fact Fighter**: Shared X verdict reports on social media
- **Community Champion**: Referred X friends who completed their first trial

### Media Literacy Score
- Personal dashboard tracking improvement over time
- Breakdown by misinformation category — shows which types fool the user most
- Monthly "Media Literacy Score" that tracks overall improvement
- Suggests areas to focus on based on weakness patterns

### Social Features
- **Shareable Verdict Cards**: Clean, evidence-based cards for social media sharing when you spot misinformation
- **Community Impact Counter**: Real-time display: "Together, our users have identified X pieces of misinformation and educated Y people"
- **Weekly Challenges**: Curated cases of real misinformation. Topic-specific challenges during high-misinfo events (elections, health crises, major news events)
- **Friend Challenges**: Send a suspicious article to a friend. Both watch the trial independently, make predictions, compare results.
- **Red Flag Education**: After each verdict, teach specific manipulation techniques that were used

---

## LANGGRAPH NODE ARCHITECTURE

```
StateGraph(TrialState)
│
├── claim_extractor        → Extract atomic claims from input (Gemini 2.5 Pro)
├── claim_triage           → Score and prioritize claims (Gemini 2.5 Flash)
├── investigator           → Web search + fact-check + store in Blackboard.io investigator namespace
├── prosecutor_research    → Private research, results held in agent state (not DB)
├── defendant_research     → Private research, results held in agent state (not DB)
│
│   ┌─── TRIAL LOOP ───────────────────────────────────┐
│   │                                                    │
│   ├── prosecutor_turn    → Generate argument + reveal  │
│   │                        selected evidence to         │
│   │                        prosecutor namespace         │
│   ├── defendant_turn     → RAG query opponent +        │
│   │                        generate rebuttal + reveal   │
│   │                        counter-evidence to          │
│   │                        defendant namespace          │
│   ├── user_input         → Human-in-the-loop node      │
│   │                        (question/evidence/skip)     │
│   ├── jury_update        → Parallel: all 5 jurors      │
│   │                        update private notes         │
│   ├── termination_check  → Conditional edge:           │
│   │                        max 5 rounds OR              │
│   │                        convergence OR               │
│   │                        exhaustion OR                │
│   │                        confidence collapse          │
│   │                        → loop back OR proceed       │
│   └───────────────────────────────────────────────────┘
│
├── user_prediction        → Lock user's prediction (human-in-the-loop)
├── jury_verdict           → Parallel: 5 models deliberate independently
│                            → Barrier sync before aggregation
├── verdict_aggregator     → Weighted average + category + dissent detection
├── score_calculator       → Compare user prediction vs verdict → update points
├── education_generator    → "What You Should Have Noticed" panel (Gemini Flash)
├── report_generator       → Shareable verdict card (Gemini Flash)
└── cleanup                → DELETE entire Blackboard.io collection for this case_id
```

### LangGraph State Schema

```python
class TrialState(TypedDict):
    # Case metadata
    case_id: str
    input_type: str  # "url", "text", "image", "social_post"
    raw_input: str
    
    # Claim extraction
    claims: list[dict]  # [{text, category, verifiability_score, priority}]
    selected_claims: list[dict]  # Top claims chosen for trial
    
    # Investigation
    investigator_evidence: list[dict]  # [{source_url, text, credibility_score, timestamp}]
    
    # Private agent arsenals (NOT in vector DB until revealed)
    prosecutor_private_evidence: list[dict]
    defendant_private_evidence: list[dict]
    
    # Trial state
    current_round: int
    max_rounds: int  # 5
    trial_transcript: list[dict]  # [{agent, round, argument_text, confidence_score, evidence_revealed}]
    
    # Prosecutor state
    prosecutor_revealed_evidence: list[dict]  # Evidence that has been stored in DB
    prosecutor_confidence: float  # 0-100, updated each round
    
    # Defendant state
    defendant_revealed_evidence: list[dict]
    defendant_confidence: float
    
    # User interactions
    user_interventions: list[dict]  # [{round, type, content, addressed_to}]
    
    # Jury state
    jury_members: list[dict]  # [{model_name, api_provider, current_lean, notes}]
    
    # Termination
    should_terminate: bool
    termination_reason: str  # "max_rounds", "convergence", "exhaustion", "confidence_collapse"
    
    # Verdict
    user_prediction: dict  # {verdict: "real"/"fake", confidence: "low"/"medium"/"high"}
    jury_verdicts: list[dict]  # [{juror_id, model, score, top_3_reasons, key_evidence, dissent_note}]
    aggregated_verdict: dict  # {score, category, summary, dissenting_opinions}
    
    # Scoring
    user_score_delta: int
    education_panel: dict  # {red_flags, techniques, decisive_evidence, personalized_tips}
    verdict_report: dict  # Shareable report content
```

---

## RAG QUERY PATTERNS (Blackboard.io)

### Prosecutor Turn
```
1. RAG-query `defendant` namespace → "weaknesses in defense arguments"
2. RAG-query `investigator` namespace → "source credibility issues for [claim]"
3. RAG-query `trial_transcript` namespace → "what has the defense already conceded?"
4. Select evidence from private arsenal to reveal
5. Generate argument with Gemini 2.5 Pro using retrieved context
6. Store ONLY revealed evidence in `prosecutor` namespace
7. Append argument to `trial_transcript` namespace
```

### Defendant Turn
```
1. RAG-query `prosecutor` namespace → "prosecution claims that lack source verification"
2. RAG-query `investigator` namespace → "evidence supporting legitimacy of [claim]"
3. RAG-query `trial_transcript` namespace → "what has the prosecution argued that I haven't addressed?"
4. Select counter-evidence from private arsenal to reveal
5. Generate rebuttal with Gemini 2.5 Pro using retrieved context
6. Store ONLY revealed evidence in `defendant` namespace
7. Append argument to `trial_transcript` namespace
```

### Jury Update (Each Juror, After Each Argument)
```
1. RAG-query ALL public namespaces (investigator, prosecutor, defendant, trial_transcript)
2. RAG-query OWN private `jury_notes/juror_N` namespace → "my previous lean and reasoning"
3. Update lean score, note compelling evidence, flag logical issues
4. Store updated notes in `jury_notes/juror_N` namespace
```

### Jury Final Deliberation (Each Juror)
```
1. RAG-query ALL public namespaces → full evidence picture
2. RAG-query OWN `jury_notes/juror_N` → complete trial memory
3. Generate independent verdict: score (0-100), top 3 reasons, key evidence, dissent note
4. Output structured verdict (do NOT store — collection about to be deleted)
```

### User Question Handling
```
1. User submits question/evidence → stored in `trial_transcript` namespace
2. Addressed agent's next turn: RAG-query `trial_transcript` for user's input
3. Agent must directly address user's question before proceeding with regular argument
```

---

## FRONTEND REQUIREMENTS

### Core Pages/Views

1. **Landing Page**: Explain the concept, show community impact stats, CTA to start a trial or submit content
2. **Input Page**: Submit content (URL, text, image upload). Show claim extraction in progress.
3. **Courtroom View** (the main experience):
   - Split-screen or alternating view: Prosecutor side (red) vs Defendant side (green)
   - Arguments stream in real-time via SSE — text appears word by word or paragraph by paragraph for drama
   - Evidence board panel showing what's in the vector DB (grows each round as evidence is revealed)
   - Jury panel showing juror avatars with subtle "lean" indicators that shift after each argument
   - User intervention input — appears between rounds with options to ask questions, submit evidence, or skip
   - Round counter and termination status
4. **Verdict Reveal**: 
   - User prediction lock-in screen (before reveal)
   - Dramatic verdict reveal — show each juror's individual score, then aggregate
   - Highlight dissenting opinions
   - Score calculation animation (points earned/lost)
5. **Education Panel**: "What You Should Have Noticed" — red flags, techniques, tips
6. **Verdict Report**: Shareable card with key findings and sources
7. **Dashboard/Profile**: 
   - User stats: total points, accuracy rate, streak, category breakdown
   - Media Literacy Score over time
   - Badge collection
8. **Leaderboard**: Global rankings, weekly/monthly, filterable
9. **Challenge Hub**: Weekly challenges, friend challenges, community cases

### UX Priorities
- The courtroom drama is the hero moment — it must feel cinematic and immersive
- Real-time streaming of arguments is essential (SSE)
- The evidence board growing each round should be visually satisfying
- Verdict reveal should have dramatic pacing (slight delays, reveal one juror at a time)
- Mobile-responsive — people will share and use this on phones
- Dark theme with courtroom-inspired aesthetic (think: dark wood tones, judicial gold accents, clean typography)

---

## AGENT SYSTEM PROMPTS

### Investigator Agent
```
You are the Court Investigator in a misinformation trial. Your role is NEUTRAL evidence gathering.
You do NOT take sides. You search for ALL relevant evidence — both supporting and contradicting the claims.
For each piece of evidence you find, assess and record:
- Source URL and publication date
- Source credibility (rate 1-10 based on: domain reputation, author credentials, editorial standards)
- Relevance to the specific claims being investigated
- Any potential biases in the source
Be thorough. The trial depends on the quality of your investigation.
```

### Prosecutor Agent
```
You are the Prosecutor in a misinformation trial. Your role is to build the STRONGEST possible case that the submitted content is MISINFORMATION or FAKE.
You must:
1. Cite specific evidence from the court record (investigator findings)
2. Use structured legal reasoning: state the claim → present evidence against it → identify logical fallacies → highlight source credibility issues
3. Be strategic about which evidence you reveal each round — save strong evidence for rebuttals
4. Directly address the Defendant's arguments in your rebuttals
5. Address any user questions directed to you
6. Your arguments must be grounded in EVIDENCE and LOGIC, not rhetoric
7. Assign yourself a confidence score (0-100) for how strong your case is after each argument
If at any point you believe the content may actually be legitimate, you must still argue your position but your confidence score should reflect your actual assessment.
```

### Defendant Agent
```
You are the Defense Attorney in a misinformation trial. Your role is to build the STRONGEST possible case that the submitted content is LEGITIMATE and TRUE.
You must:
1. Genuinely steel-man the content's legitimacy — do not weakly oppose
2. Directly address EVERY point the Prosecutor makes before presenting your own arguments
3. Provide corroborating sources, proper context, and alternative explanations
4. Be strategic about revealing evidence — counter the Prosecutor's strongest points with your strongest evidence
5. Address any user questions directed to you
6. Identify where the Prosecutor's evidence is weak, outdated, or taken out of context
7. Assign yourself a confidence score (0-100) after each argument
If at any point you believe the content may actually be misinformation, you must still argue your position but your confidence score should reflect your actual assessment.
```

### Juror Agent (Template — customize per model)
```
You are Juror [N] in a misinformation trial. You are evaluating whether submitted content is real or fake based on the evidence and arguments presented.
After each argument, update your assessment:
- Current lean: 0 (definitely fake) to 100 (definitely real)
- Key evidence that influenced your lean
- Logical weaknesses you noticed in either side's arguments
- Unanswered questions you still have
When delivering your final verdict, you must:
1. State your confidence score (0-100 on the fake↔real spectrum)
2. Provide your top 3 reasons
3. Identify the single most decisive piece of evidence
4. Note if you disagree with what appears to be the consensus
Base your judgment on EVIDENCE QUALITY and LOGICAL REASONING, not on which side was more eloquent.
Scoring rubric for evaluating arguments:
- Evidence Grounding (35%): Are claims backed by verified sources?
- Logical Validity (25%): Is the reasoning chain valid? Any fallacies?
- Factual Accuracy (25%): Do stated facts match the evidence dossier?
- Source Quality (15%): Peer-reviewed > news > blog > social > anonymous
```

---

## API KEYS NEEDED

1. **Google Gemini API Key** — All primary agents + built-in Google Search grounding
2. **Blackboard.io API Key** — Vector DB + web search/retrieval
3. **Google Fact Check Tools API Key** — Verified fact-check database queries
4. **Anthropic API Key** — Claude Sonnet as jury member
5. **OpenAI API Key** — GPT-4o as jury member
6. **Together AI or Groq API Key** — Llama 3 inference as jury member
7. **Firebase or Supabase Key** — User auth, scores, leaderboard persistence
8. **Google Cloud Vision API Key** *(optional)* — Image analysis for image-based cases

---

## HACKATHON BUILD PRIORITY

### Day 1: Core Trial Loop
1. Set up LangGraph workflow with TrialState
2. Implement Investigator → Prosecutor → Defendant loop with Gemini 2.5 Pro
3. Connect Blackboard.io: create/delete collections, namespace CRUD, basic RAG queries
4. Hardcode: 5 max rounds, basic termination (max rounds only)
5. Test with a known misinformation case end-to-end in terminal

### Day 2: Jury + Frontend
1. Add 3-member jury (Gemini Pro, Claude Sonnet, Gemini Flash) with parallel deliberation
2. Build the streaming courtroom UI (React + SSE)
3. Add user prediction input (lock before verdict reveal)
4. Add user intervention window (basic question input between rounds)
5. Implement strategic evidence reveal mechanic (prosecutor/defendant choose what to reveal)

### Day 3: Polish + Gamification
1. Scoring system and leaderboard
2. "What You Should Have Noticed" education panel
3. Shareable verdict cards
4. Dramatic verdict reveal animation
5. Add remaining termination triggers (convergence, exhaustion, confidence collapse)
6. Mobile responsiveness pass

### Demo Strategy
- Have a live misinformation case ready (recent, recognizable)
- Let the judges/audience submit it
- Watch the courtroom unfold in real-time
- Show the evidence board growing with each round
- The dramatic verdict reveal is your moment — build suspense
- Show the educational breakdown — demonstrate the social impact angle
- Show the leaderboard — demonstrate engagement/gamification

---

## IMPORTANT IMPLEMENTATION NOTES

1. **Ephemeral DB is non-negotiable**: Every case must create and destroy its own Blackboard.io collection. No cross-case data leakage. This is a privacy and cost feature.

2. **Strategic reveal is the secret sauce**: The prosecutor and defendant must NOT reveal all evidence at once. Their private research is held in LangGraph state, and they choose what to "present to the court" each round. Only presented evidence goes into the vector DB.

3. **Jury diversity matters**: Using different models for jurors is not a gimmick — each model has different training data, reasoning patterns, and blind spots. This genuinely produces better verdicts than any single model.

4. **User interaction makes it immersive**: The user intervention window between rounds is what turns this from a demo into a product. Let users feel like they're participating in the trial.

5. **Evidence grounding over rhetoric**: The confidence weighting rubric (35% evidence, 25% logic, 25% accuracy, 15% source quality) must be enforced. Without it, the most eloquent model "wins" regardless of truth.

6. **Stream everything**: Arguments should stream in real-time via SSE. The courtroom drama effect is the #1 demo moment. Don't batch — stream word by word or sentence by sentence.

7. **The educational angle is the social impact story**: The point system, leaderboard, and "What You Should Have Noticed" panel are what make this a social impact project, not just a tech demo. Users learn to detect misinformation themselves.
