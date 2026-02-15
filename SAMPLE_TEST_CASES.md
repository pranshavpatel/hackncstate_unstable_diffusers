# Sample Test Cases

Use these test cases to demonstrate the system:

## 1. Obvious Misinformation (Easy)

### Claim
```
NASA confirmed that aliens exist on Mars last Tuesday and will make an official announcement next week.
```

### Expected Outcome
- **Verdict**: Confirmed Misinformation (0-20)
- **Key Evidence**: No NASA announcements, no credible sources
- **Red Flags**: Specific false date, appeal to authority, sensationalism

---

## 2. Partially True (Medium)

### Claim
```
The COVID-19 vaccine was developed in less than a year, which is unprecedented in vaccine history and proves it's unsafe.
```

### Expected Outcome
- **Verdict**: Likely False (20-40)
- **Key Evidence**: Timeline is true, but conclusion is false
- **Red Flags**: Logical fallacy (correlation ≠ causation), misleading context

---

## 3. Ambiguous Health Claim (Medium)

### Claim
```
A new study shows that drinking coffee can extend your lifespan by 10 years.
```

### Expected Outcome
- **Verdict**: Uncertain / Mixed (40-60)
- **Key Evidence**: Studies exist but results vary, claim is exaggerated
- **Red Flags**: Vague attribution ("a study"), absolute claims, missing context

---

## 4. Political Misinformation (Hard)

### Claim
```
The 2020 US election had widespread voter fraud with millions of illegal votes cast, according to multiple state investigations.
```

### Expected Outcome
- **Verdict**: Confirmed Misinformation (0-20)
- **Key Evidence**: Multiple court cases dismissed, no evidence found
- **Red Flags**: False authority claims, debunked conspiracy theory

---

## 5. Scientific Misrepresentation (Hard)

### Claim
```
5G cell towers cause COVID-19 by weakening the immune system through electromagnetic radiation.
```

### Expected Outcome
- **Verdict**: Confirmed Misinformation (0-20)
- **Key Evidence**: No scientific basis, virus vs. radiation confusion
- **Red Flags**: Conspiracy theory, scientific impossibility, fear-mongering

---

## 6. Out-of-Context Truth (Tricky)

### Claim
```
Bill Gates said he wants to reduce the world's population through vaccines.
```

### Expected Outcome
- **Verdict**: Likely False (20-40)
- **Key Evidence**: Quote taken out of context (he meant reducing child mortality leads to lower birth rates)
- **Red Flags**: Context manipulation, quote mining, conspiracy framing

---

## 7. Recent News (Timely)

### Claim
```
A major tech company just announced they're laying off 50% of their workforce due to AI replacing human workers.
```

### Expected Outcome
- **Verdict**: Uncertain (40-60) or Likely False (20-40)
- **Key Evidence**: Depends on current news, likely exaggerated
- **Red Flags**: Vague attribution, sensational numbers, fear-mongering

---

## 8. Celebrity Misinformation (Easy)

### Claim
```
Elon Musk announced he's giving away free Bitcoin to anyone who sends him cryptocurrency first.
```

### Expected Outcome
- **Verdict**: Confirmed Misinformation (0-20)
- **Key Evidence**: Classic crypto scam, no official announcements
- **Red Flags**: Too good to be true, common scam pattern, impersonation

---

## 9. Historical Revisionism (Medium)

### Claim
```
The moon landing in 1969 was faked in a Hollywood studio, as proven by the flag waving in the footage.
```

### Expected Outcome
- **Verdict**: Confirmed Misinformation (0-20)
- **Key Evidence**: Extensively debunked, flag movement explained by physics
- **Red Flags**: Conspiracy theory, cherry-picked evidence, scientific misunderstanding

---

## 10. Legitimate News (Control)

### Claim
```
The James Webb Space Telescope captured the deepest infrared image of the universe in 2022, showing galaxies from over 13 billion years ago.
```

### Expected Outcome
- **Verdict**: Verified True (80-100)
- **Key Evidence**: Official NASA announcements, peer-reviewed data, multiple sources
- **Red Flags**: None - legitimate scientific achievement

---

## Testing Strategy

### For Demo
1. Start with **#1 (NASA aliens)** - clear misinformation, dramatic
2. Show **#10 (JWST)** - legitimate news, shows system isn't biased
3. End with **#6 (Bill Gates)** - tricky context manipulation, educational

### For Testing
- Use **#1, #5, #8** to test obvious misinformation detection
- Use **#2, #3, #7** to test nuanced reasoning
- Use **#10** to verify system doesn't over-flag legitimate news

### Expected Trial Dynamics

**Obvious Misinformation (#1, #5, #8)**
- Prosecutor: High confidence (80-95%)
- Defendant: Low confidence (10-25%)
- Jury: Strong consensus (0-20 score)
- Rounds: 2-3 (defendant concedes early)

**Ambiguous Claims (#2, #3, #7)**
- Prosecutor: Medium confidence (50-70%)
- Defendant: Medium confidence (40-60%)
- Jury: Mixed verdict (40-60 score)
- Rounds: 4-5 (full debate)

**Legitimate News (#10)**
- Prosecutor: Low confidence (20-40%)
- Defendant: High confidence (75-90%)
- Jury: Strong consensus (80-100 score)
- Rounds: 2-3 (prosecutor concedes)

---

## API Test Commands

### Test Case 1 (NASA Aliens)
```bash
curl -X POST http://localhost:8000/api/trial/start \
  -H "Content-Type: application/json" \
  -d '{
    "content": "NASA confirmed that aliens exist on Mars last Tuesday and will make an official announcement next week.",
    "input_type": "text"
  }'
```

### Test Case 10 (JWST - Legitimate)
```bash
curl -X POST http://localhost:8000/api/trial/start \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The James Webb Space Telescope captured the deepest infrared image of the universe in 2022, showing galaxies from over 13 billion years ago.",
    "input_type": "text"
  }'
```

---

## Expected Performance

- **Processing Time**: 30-90 seconds per trial
- **API Calls**: 10-20 per trial
- **Accuracy**: 80-90% on obvious cases, 60-70% on ambiguous cases
- **Educational Value**: High - shows reasoning process

---

## Tips for Demo

1. **Pre-load test case**: Have it ready to paste
2. **Explain as it runs**: Narrate what's happening
3. **Highlight key moments**: 
   - Claim extraction
   - Evidence gathering
   - Confidence scores changing
   - Jury deliberation
   - Verdict reveal
4. **Show education panel**: Point out red flags
5. **Emphasize social impact**: "Every trial is a lesson"
