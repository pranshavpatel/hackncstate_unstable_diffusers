# MASTER PROMPT: Replicate Courtroom UI/UX in Main Project

## OBJECTIVE
Integrate this complete UI/UX design into the existing backend project while preserving all AI and backend functionalities.

---

## 1. VISUAL IDENTITY & THEME

### Color Palette (Light US Courtroom)
```css
Oak Wood: #d4a373
Parchment: #fefae0
Prosecutor Red: #dc2626
Defender Green: #10b981
```

### Background & Layout
- Use `court.png` as full-page background image
- Apply parchment overlay with 90% opacity and backdrop blur
- All panels: parchment background with 4px oak borders and shadow-2xl

---

## 2. CHARACTER ASSETS & USAGE

### Required Images (copy from /public/images/)
- `court.png` - Background
- `jury.png` - Jury members
- `lawyer.png` - Prosecutor & Defender
- `police.png` - Investigator
- `user.png` - User avatar

### Character Mapping
| Phase | Character | Image | Position |
|-------|-----------|-------|----------|
| Investigation | Investigator | police.png | Center |
| Prosecutor Turn | Prosecutor | lawyer.png | Left |
| Defender Turn | Defender | lawyer.png | Right |
| Jury Feedback | Jury | jury.png | Center |
| User Input | User | user.png | Panel icon |

---

## 3. ANIMATION SYSTEM (Framer Motion)

### Active Speaker Protocol
When a character speaks, implement:

```typescript
// Character.tsx component
<motion.div
  animate={{
    scale: isActive ? 1.3 : 1,
    x: isActive ? (position === 'left' ? 50 : position === 'right' ? -50 : 0) : 0,
    y: isActive ? [0, -2, 0] : 0, // Talking jitter
  }}
  transition={{
    scale: { type: 'spring', stiffness: 300, damping: 20 },
    x: { type: 'spring', stiffness: 300, damping: 20 },
    y: { repeat: isActive && !isComplete ? Infinity : 0, duration: 0.3 },
  }}
>
  <img src={characterImage} className="w-32 h-32" />
  
  {/* Speech Bubble */}
  {isActive && text && (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="absolute -top-4 left-full ml-4 bg-parchment border-2 border-oak rounded-lg p-4"
    >
      <p>{streamingText}</p>
    </motion.div>
  )}
</motion.div>
```

### Key Animation Features
1. **Step Forward**: Active speaker scales 1.3x, moves 50px toward center
2. **Talking Animation**: Y-axis jitter (2px) while text streams
3. **Speech Bubble**: Parchment bubble with oak border, anchored to character
4. **Word-by-word Streaming**: Use existing streaming hook/API

---

## 4. USER FLOW & STATE MANAGEMENT

### Flow Sequence (Button-Controlled)
```
INTAKE → INVESTIGATION → [5 EPOCHS] → FINAL_USER_VERDICT → FINAL_VERDICT
```

### Each Epoch Contains 4 Steps:
1. **EPOCH_PROSECUTOR**: Prosecutor argues → "Continue" button
2. **EPOCH_DEFENDER**: Defender rebuts → "Continue" button
3. **EPOCH_JURY**: Jury gives feedback → "Continue" button
4. **EPOCH_USER**: User inputs opinion (textarea) → "Next Round" button

### State Types Needed
```typescript
type ActState = 
  | 'INTAKE' 
  | 'INVESTIGATION' 
  | 'EPOCH_PROSECUTOR' 
  | 'EPOCH_DEFENDER'
  | 'EPOCH_JURY'
  | 'EPOCH_USER' 
  | 'FINAL_USER_VERDICT'
  | 'FINAL_VERDICT';

interface ConversationEntry {
  id: string;
  epoch: number;
  speaker: 'prosecutor' | 'defender' | 'jury' | 'user';
  text: string;
  timestamp: Date;
}
```

---

## 5. COMPONENT STRUCTURE

### Main Components to Create/Modify

#### 1. **Courtroom.tsx** (Main Orchestrator)
```tsx
<div style={{ backgroundImage: 'url(/images/court.png)' }}>
  <div className="bg-parchment/90 backdrop-blur-sm">
    <AnimatePresence mode="wait">
      {actState === 'INTAKE' && <IntakePanel />}
      {actState === 'INVESTIGATION' && <InvestigationPanel />}
      {actState.startsWith('EPOCH') && (
        <>
          <ConversationHistory />
          <EpochPanel />
        </>
      )}
      {actState === 'FINAL_USER_VERDICT' && <FinalVerdictPanel />}
      {actState === 'FINAL_VERDICT' && <FinalVerdictPanel />}
    </AnimatePresence>
  </div>
</div>
```

#### 2. **Character.tsx** (Reusable Animated Character)
- Props: `type`, `isActive`, `text`, `position`
- Handles: scaling, movement, talking animation, speech bubble
- See Animation System section above

#### 3. **IntakePanel.tsx**
- Display witness claim in parchment card
- Single button: "Begin Investigation →"
- Oak button styling with hover effects

#### 4. **InvestigationPanel.tsx**
- Show police character with speech bubble
- Display 3 evidence cards in grid (credibility scores 1-10)
- Color-code scores: ≥7 green, ≥4 yellow, <4 red
- Button: "Proceed to Trial →"

#### 5. **EpochPanel.tsx**
- Render active character based on state:
  - EPOCH_PROSECUTOR: lawyer.png (left)
  - EPOCH_DEFENDER: lawyer.png (right)
  - EPOCH_JURY: jury.png (center)
  - EPOCH_USER: user.png in panel + textarea
- Show "Continue →" button (or "Next Round →" for user)
- Display round counter: "Round X/5"

#### 6. **ConversationHistory.tsx**
- Display all past conversations sequentially
- Each entry shows: character icon, speaker label, round number, text
- Border-left color-coded by speaker
- Staggered fade-in animations

#### 7. **FinalVerdictPanel.tsx**
- **FINAL_USER_VERDICT state**: Show 2 buttons (FAKE vs REAL)
- **FINAL_VERDICT state**: 
  - Show 3 jury members with individual scores
  - Display weighted verdict calculation
  - Show user correctness (green/red)
  - Educational feedback section
  - "Start New Trial" button

---

## 6. INTEGRATION WITH EXISTING BACKEND

### Replace Dummy Data With Real API Calls

#### Investigation Phase
```typescript
// Replace DUMMY_EVIDENCE with:
const evidence = await investigatorAgent.gatherEvidence(witnessText);
evidence.forEach(e => addEvidence(e));
```

#### Epoch Arguments
```typescript
// Replace PROSECUTOR_ARGS[epoch] with:
const prosecutorArg = await prosecutorAgent.generateArgument(
  witnessText, 
  evidenceCards, 
  conversationHistory
);
```

#### Jury Feedback
```typescript
// Replace JURY_FEEDBACK[epoch] with:
const juryFeedback = await juryAgent.provideFeedback(
  conversationHistory,
  currentEpoch
);
```

#### Final Verdict
```typescript
// Replace hardcoded scores with:
const juryScores = await Promise.all(
  jurors.map(j => j.agent.calculateScore(fullTranscript))
);
const weighted = calculateWeightedVerdict(juryScores, jurors);
```

### Streaming Integration
```typescript
// If backend supports streaming:
const stream = await prosecutorAgent.streamArgument(...);
for await (const chunk of stream) {
  setStreamingText(prev => prev + chunk);
}
```

---

## 7. STYLING GUIDELINES

### Button Styles
```tsx
className="w-full bg-oak text-white font-bold py-4 rounded-lg text-lg 
           hover:bg-amber-700 transition-colors shadow-lg"
```

### Panel Styles
```tsx
className="bg-parchment rounded-lg border-4 border-oak p-8 shadow-2xl"
```

### Evidence Card Styles
```tsx
className="bg-parchment p-6 rounded-lg border-4 border-oak/30 
           hover:border-oak transition-colors shadow-lg"
```

### Conversation Entry Styles
```tsx
className="bg-parchment/80 p-4 rounded-lg border-l-4 border-{speaker-color} shadow"
```

---

## 8. KEY FEATURES TO PRESERVE

### Educational Features
- ✅ Full conversation transcript saved sequentially
- ✅ Educational feedback with rubric after final verdict
- ✅ Visual indicators for credibility scores
- ✅ Jury transparency (individual scores + weighted aggregation)

### User Experience
- ✅ Button-controlled flow (no auto-progression)
- ✅ Word-by-word text streaming
- ✅ Smooth Framer Motion transitions
- ✅ Character animations during speech
- ✅ Color-coded speakers
- ✅ Responsive design

### Technical
- ✅ TypeScript strict typing
- ✅ Zustand state management (or adapt to existing state)
- ✅ Weighted jury verdict calculation: `w_i = r_i / (Σ r_j)`
- ✅ 5 epochs with 4 steps each

---

## 9. IMPLEMENTATION CHECKLIST

### Phase 1: Setup
- [ ] Copy images to public/images/
- [ ] Update Tailwind config with oak/parchment colors
- [ ] Install framer-motion if not present

### Phase 2: Core Components
- [ ] Create Character.tsx with animation logic
- [ ] Update Courtroom.tsx with background and state routing
- [ ] Create/update all panel components

### Phase 3: Integration
- [ ] Replace dummy data with real API calls
- [ ] Connect streaming to Character speech bubbles
- [ ] Wire up state management to existing backend
- [ ] Test all 5 epochs flow

### Phase 4: Polish
- [ ] Verify all animations work smoothly
- [ ] Test responsive design
- [ ] Ensure conversation history persists
- [ ] Validate educational feedback displays correctly

---

## 10. CRITICAL NOTES

1. **Preserve Backend Logic**: Only replace UI layer, keep all AI agent logic intact
2. **Streaming**: Character talking animation should sync with text streaming
3. **State Flow**: User must click button at every step (no auto-progression)
4. **Conversation History**: Must persist and display all exchanges sequentially
5. **Weighted Verdict**: Use existing jury reliability weights in calculation
6. **Character Positioning**: Prosecutor=left, Defender=right, Jury/Police=center
7. **Speech Bubbles**: Must be anchored to character and move with them
8. **5 Epochs**: Hardcoded to exactly 5 rounds before final verdict

---

## 11. FILE REFERENCES

Key files to reference from this prototype:
- `/src/components/Character.tsx` - Animation logic
- `/src/components/EpochPanel.tsx` - Epoch flow structure
- `/src/components/ConversationHistory.tsx` - Transcript display
- `/src/types/trial.ts` - TypeScript interfaces
- `/src/lib/store.ts` - State management pattern
- `/tailwind.config.js` - Color palette

---

## FINAL OUTPUT REQUIREMENTS

The integrated UI must:
1. Look identical to this prototype
2. Use real AI backend instead of dummy data
3. Maintain button-controlled user flow
4. Display animated characters with speech bubbles
5. Show full conversation transcript
6. Provide educational feedback at end
7. Support 5 epochs with 4 steps each
8. Calculate weighted jury verdicts
9. Be fully responsive and accessible
10. Preserve all existing backend functionality
