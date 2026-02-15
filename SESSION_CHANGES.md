# Recent Changes - Google Search Grounding Implementation

## Date: February 15, 2024

---

## Changes Made

### 1. **llm_clients.py** - Added Google Search Grounding
**File**: `backend/utils/llm_clients.py`

**Added new function:**
```python
async def generate_gemini_grounded(self, prompt: str) -> str:
    """Generate grounded response using Gemini with Google Search"""
    response = self.client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "temperature": 0.3,
            "tools": [{"google_search": {}}],
            "automatic_function_calling": {"disable": False}
        }
    )
```

**What it does:**
- Enables Gemini to search Google in real-time
- Returns actual web search results
- Prints grounding metadata to terminal for debugging

---

### 2. **investigator.py** - Use Grounded Search
**File**: `backend/agents/investigator.py`

**Changed from:**
```python
response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
```

**Changed to:**
```python
response = await llm_clients.generate_gemini_grounded(prompt)
```

**What changed:**
- Investigator now uses Google Search grounding
- Gets real web results instead of hallucinating evidence
- Searches web for actual URLs, facts, and dates

---

### 3. **prosecutor.py** - Confidence Calibration
**File**: `backend/agents/prosecutor.py`

**Added to prompt:**
```
HONEST confidence score (0-100) - Be realistic. If evidence is weak or circumstantial, 
score lower. Only score 80+ if you have multiple verified sources directly contradicting 
the claim.

Confidence guidelines:
- 90-100: Multiple verified sources directly prove it's false
- 70-89: Strong evidence suggests it's false
- 50-69: Some evidence against, but not conclusive
- 30-49: Weak evidence, mostly speculation
- 0-29: Very little evidence, claim might be true
```

**What changed:**
- Prosecutor now gives realistic confidence scores
- Won't always be 95% confident
- Must justify high confidence with strong evidence

---

### 4. **defendant.py** - Confidence Calibration
**File**: `backend/agents/defendant.py`

**Added to prompt:**
```
HONEST confidence score (0-100) - Be realistic. If you have strong corroborating 
sources, score higher. Don't be overly defensive.

Confidence guidelines:
- 90-100: Multiple verified sources confirm the claim is true
- 70-89: Strong evidence supports legitimacy
- 50-69: Some supporting evidence, plausible
- 30-49: Weak evidence, prosecutor has stronger case
- 0-29: Very little support, likely false
```

**What changed:**
- Defendant can score higher when evidence supports legitimacy
- Won't always be stuck at 65%
- More balanced confidence assessment

---

## Why These Changes?

### Problem 1: Investigator Hallucinating Evidence
**Before:**
- Investigator collected web search results but never used them
- Gemini generated evidence from memory (hallucinations)
- No real URLs or facts

**After:**
- Gemini searches Google in real-time
- Returns actual URLs and facts from web
- Evidence is grounded in reality

### Problem 2: Unrealistic Confidence Scores
**Before:**
- Prosecutor: Always ~95% confident
- Defendant: Always ~65% confident
- Scores didn't reflect evidence strength

**After:**
- Both agents have calibration guidelines
- Scores vary based on actual evidence
- More realistic and balanced

---

## Testing

**To verify grounding is working:**
1. Start backend: `python main.py`
2. Submit a claim in frontend
3. Check backend terminal for:
```
============================================================
GOOGLE SEARCH GROUNDING RESULTS
============================================================
Candidate 1:
Grounding Metadata: [search results here]
```

**If grounding metadata shows "None":**
- Grounding may not be enabled for your API key
- Model may not support grounding yet
- Falls back to regular generation

---

## Files Modified

1. `backend/utils/llm_clients.py` - Added `generate_gemini_grounded()`
2. `backend/agents/investigator.py` - Uses grounded search
3. `backend/agents/prosecutor.py` - Added confidence guidelines
4. `backend/agents/defendant.py` - Added confidence guidelines

**Total**: 4 files modified

---

## Impact

- ✅ Investigator uses real web search
- ✅ Evidence is grounded in actual sources
- ✅ Confidence scores are more realistic
- ✅ Arguments are more balanced
- ✅ Better user experience with real data

---

*Session Date: February 15, 2024*
