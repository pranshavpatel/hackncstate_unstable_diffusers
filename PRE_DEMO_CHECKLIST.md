# Pre-Demo Checklist

## ✅ Before You Start

### 1. API Keys Setup
- [ ] Get Google Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Get Blackboard.io API key (or prepare to mock it)
- [ ] (Optional) Get Anthropic API key for Claude
- [ ] (Optional) Get OpenAI API key for GPT-4o
- [ ] Add all keys to `backend/.env`
- [ ] Verify no quotes around keys in `.env`
- [ ] Restart backend after adding keys

### 2. Dependencies Installation
- [ ] Python 3.9+ installed: `python --version`
- [ ] Node.js 16+ installed: `node --version`
- [ ] Backend dependencies: `cd backend && pip install -r requirements.txt`
- [ ] Frontend dependencies: `cd frontend && npm install`
- [ ] No error messages during installation

### 3. Test Backend
- [ ] Start backend: `cd backend && python main.py`
- [ ] Backend runs without errors
- [ ] Visit http://localhost:8000 - should see {"message": "Unreliable Narrator API"}
- [ ] Check logs for any warnings
- [ ] Run test script: `python backend/test_trial.py` (optional)

### 4. Test Frontend
- [ ] Start frontend: `cd frontend && npm start`
- [ ] Frontend opens in browser automatically
- [ ] No console errors in browser DevTools
- [ ] Landing page displays correctly
- [ ] Input textarea is visible and functional

### 5. End-to-End Test
- [ ] Submit a test claim (use Sample Test Case #1)
- [ ] Courtroom loads without errors
- [ ] Arguments stream in real-time
- [ ] Prosecutor and Defendant panels update
- [ ] Jury panel is visible
- [ ] Verdict displays after trial
- [ ] No errors in browser console or backend logs

---

## 🎯 Demo Preparation

### 1. Content Ready
- [ ] Choose 2-3 test cases from `SAMPLE_TEST_CASES.md`
- [ ] Have them ready to copy-paste
- [ ] Test each one beforehand to know expected outcome
- [ ] Prepare backup test case in case of API issues

### 2. Presentation Points
- [ ] Understand the problem: misinformation detection + education
- [ ] Know the innovation: adversarial AI courtroom
- [ ] Memorize key features: multi-agent, strategic reveal, multi-model jury
- [ ] Practice explaining the flow: intake → investigation → trial → verdict
- [ ] Prepare social impact story: "Every trial is a lesson"

### 3. Technical Setup
- [ ] Laptop fully charged or plugged in
- [ ] Stable internet connection
- [ ] Browser zoom at 100% for demo
- [ ] Close unnecessary tabs and applications
- [ ] Disable notifications
- [ ] Have backup plan if API rate limits hit

### 4. Backup Plans
- [ ] Screenshots of successful trial run
- [ ] Video recording of full trial (optional)
- [ ] Slide deck explaining architecture (optional)
- [ ] Code walkthrough prepared if demo fails

---

## 🚀 Demo Flow

### Opening (30 seconds)
- [ ] Introduce the problem: "Misinformation spreads faster than truth"
- [ ] State the solution: "AI courtroom that teaches media literacy"
- [ ] Hook: "Watch AI agents battle it out in real-time"

### Live Demo (2-3 minutes)
- [ ] Show landing page
- [ ] Paste test claim (NASA aliens)
- [ ] Explain: "System extracts claims and gathers evidence"
- [ ] Point out: "Prosecutor argues it's fake, Defendant argues it's real"
- [ ] Highlight: "Watch confidence scores change as evidence is revealed"
- [ ] Show: "Multi-model jury deliberates independently"
- [ ] Reveal: "Verdict with evidence and reasoning"
- [ ] Emphasize: "Educational breakdown shows red flags"

### Technical Explanation (1-2 minutes)
- [ ] Architecture: LangGraph multi-agent workflow
- [ ] Innovation: Strategic evidence reveal (not all at once)
- [ ] Diversity: Multi-model jury prevents bias
- [ ] Privacy: Ephemeral storage, deleted after verdict
- [ ] Scalability: Each trial is independent

### Social Impact (30 seconds)
- [ ] "Every trial teaches media literacy"
- [ ] "Shareable verdicts combat viral misinformation"
- [ ] "Gamification encourages repeated engagement"
- [ ] "Community learning through leaderboards"

### Q&A Preparation
- [ ] How accurate is it? "80-90% on obvious cases, improves with more models"
- [ ] How fast is it? "30-90 seconds per trial"
- [ ] What about costs? "Optimized with strategic reveal, ~10-20 API calls per trial"
- [ ] Can it handle images? "Architecture supports it, not yet implemented"
- [ ] What makes it unique? "First adversarial courtroom + educational angle"

---

## 🐛 Common Issues & Fixes

### Backend won't start
```bash
# Check Python version
python --version  # Need 3.9+

# Reinstall dependencies
cd backend
pip install --upgrade -r requirements.txt

# Check .env file
cat .env  # Verify keys are present
```

### Frontend won't connect
```bash
# Verify backend is running
curl http://localhost:8000/

# Check CORS in backend/main.py
# Verify API_BASE in frontend/src/App.js
```

### API rate limits
```bash
# Use fewer jury models (just Gemini)
# Edit backend/workflow.py - reduce jury_members to 1

# Add delays between API calls
# Edit agents to add: await asyncio.sleep(1)
```

### Streaming not working
```bash
# Check browser supports SSE
# Try different browser (Chrome recommended)
# Check network tab in DevTools for /stream endpoint
```

---

## 📊 Success Metrics

### Minimum Viable Demo
- [ ] Trial completes end-to-end
- [ ] Arguments display in real-time
- [ ] Verdict is reasonable and evidence-based
- [ ] No crashes or errors

### Good Demo
- [ ] Multiple test cases work
- [ ] Confidence scores change realistically
- [ ] Jury shows diversity of opinions
- [ ] Educational panel provides insights

### Excellent Demo
- [ ] All features work smoothly
- [ ] Audience can submit their own claims
- [ ] Live Q&A with working system
- [ ] Clear social impact story

---

## 🎓 Key Talking Points

### Problem
"Misinformation spreads 6x faster than truth on social media. Traditional fact-checking is too slow and doesn't teach people to think critically."

### Solution
"An AI courtroom where agents debate in real-time, a multi-model jury delivers verdicts, and users learn media literacy through gamification."

### Innovation
1. **Adversarial AI**: Prosecutor vs Defendant ensures both sides are heard
2. **Strategic Reveal**: Agents don't show all evidence at once - creates drama and prevents information overload
3. **Multi-Model Jury**: Different AI models have different biases - consensus is more reliable
4. **Educational**: Every trial teaches red flags and manipulation techniques
5. **Ephemeral**: Privacy-first, no data persistence between cases

### Impact
"We're not just detecting misinformation - we're teaching people to detect it themselves. Every trial is a lesson. Every prediction is practice. Every shared verdict multiplies social impact."

---

## 📝 Post-Demo Notes

After the demo, document:
- [ ] What worked well
- [ ] What could be improved
- [ ] Questions asked
- [ ] Feedback received
- [ ] Ideas for future features

---

## 🏆 Final Confidence Check

Before going on stage:
- [ ] I can explain the problem clearly
- [ ] I can demonstrate the solution live
- [ ] I understand the technical architecture
- [ ] I can articulate the social impact
- [ ] I have backup plans if something fails
- [ ] I'm excited to show this!

---

## 🎉 You're Ready!

Remember:
- **Breathe**: You've built something amazing
- **Tell a story**: Problem → Solution → Impact
- **Show passion**: Your excitement is contagious
- **Have fun**: Enjoy the moment!

Good luck! 🚀
