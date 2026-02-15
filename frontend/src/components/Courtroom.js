import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import IntakePanel from './IntakePanel';
import InvestigationPanel from './InvestigationPanel';
import EpochPanel from './EpochPanel';
import ConversationHistory from './ConversationHistory';
import FinalVerdictPanel from './FinalVerdictPanel';

const Courtroom = ({ caseId, originalContent }) => {
  // State machine following the exact flow requested
  const [actState, setActState] = useState('INTAKE');
  const [currentEpoch, setCurrentEpoch] = useState(0); // 0-indexed, so 0 = epoch 1

  // Data buffers from backend stream
  const [claim, setClaim] = useState(originalContent || 'Loading claim...');
  const [evidence, setEvidence] = useState([]);
  const [transcript, setTranscript] = useState([]);
  const [verdict, setVerdict] = useState(null);
  const [awarenessScore, setAwarenessScore] = useState(null);

  // Loading states for each phase
  const [investigationReady, setInvestigationReady] = useState(false);
  const [prosecutorReady, setProsecutorReady] = useState(false);
  const [defenderReady, setDefenderReady] = useState(false);
  const [verdictReady, setVerdictReady] = useState(false);

  // Conversation history for display
  const [conversationHistory, setConversationHistory] = useState([]);

  // Current data for active epoch
  const [currentSpeakerData, setCurrentSpeakerData] = useState(null);

  // Listen to backend SSE stream and buffer all data
  useEffect(() => {
    let eventSource = null;
    let mounted = true;

    const connectStream = () => {
      eventSource = new EventSource(`http://localhost:8000/api/trial/${caseId}/stream`);

      eventSource.onmessage = (event) => {
        if (!mounted) return;
        const data = JSON.parse(event.data);
        console.log('SSE Data received:', data);

        if (data.claim) {
          setClaim(data.claim);
        }

        if (data.phase === 'claim_extraction') {
          // Just note that claims are being extracted
        } else if (data.phase === 'investigation') {
          console.log('Investigation data:', data);
          if (data.evidence) {
            console.log('Setting evidence:', data.evidence);
            setEvidence(data.evidence);
            setInvestigationReady(true);
          }
          // Also check for sources field (in case backend uses different field name)
          if (data.sources) {
            console.log('Setting sources as evidence:', data.sources);
            setEvidence(data.sources);
            setInvestigationReady(true);
          }
          // Backend sends evidence_count instead of evidence array
          if (data.evidence_count !== undefined) {
            console.log('Evidence count received:', data.evidence_count);
            // Create placeholder evidence based on count
            const placeholderEvidence = Array.from({ length: data.evidence_count }, (_, i) => ({
              source: `Evidence Source ${i + 1}`,
              summary: 'Evidence analyzed and processed.',
              score: 7
            }));
            setEvidence(placeholderEvidence);
            setInvestigationReady(true);
          }
        } else if (data.phase === 'trial') {
          console.log('Trial data:', data);
          // Buffer trial arguments
          setTranscript(prev => {
            const exists = prev.some(e =>
              e.agent === data.agent &&
              e.round === data.round
            );
            if (exists) return prev;

            const newTranscript = [...prev, {
              agent: data.agent,
              round: data.round,
              argument: data.argument,
              confidence: data.confidence
            }];

            // Set ready flags based on what we received
            if (data.agent === 'prosecutor') {
              setProsecutorReady(true);
            } else if (data.agent === 'defendant') {
              setDefenderReady(true);
            }

            return newTranscript;
          });
        } else if (data.phase === 'verdict') {
          console.log('Verdict data:', data);
          setVerdict(data.verdict);
          setVerdictReady(true);
        } else if (data.phase === 'awareness_score') {
          console.log('Awareness score data:', data);
          if (data.awareness_score) {
            setAwarenessScore(data.awareness_score);
          }
        } else if (data.phase === 'complete') {
          eventSource.close();
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
      };
    };

    connectStream();

    return () => {
      mounted = false;
      if (eventSource) eventSource.close();
    };
  }, [caseId]);

  // Debug effect
  useEffect(() => {
    console.log('Evidence updated:', evidence);
    console.log('Investigation ready:', investigationReady);
  }, [evidence, investigationReady]);

  // Check if current state can proceed
  const canProceed = () => {
    switch (actState) {
      case 'INVESTIGATION':
        return investigationReady && evidence.length > 0;
      case 'EPOCH_PROSECUTOR':
        const prosecutorEntry = transcript.find(t =>
          t.agent === 'prosecutor' && t.round === currentEpoch + 1
        );
        return prosecutorEntry !== undefined;
      case 'EPOCH_DEFENDER':
        const defenderEntry = transcript.find(t =>
          (t.agent === 'defendant' || t.agent === 'defender') && t.round === currentEpoch + 1
        );
        return defenderEntry !== undefined;
      case 'FINAL_VERDICT':
        return verdictReady && verdict !== null;
      default:
        return true; // INTAKE and EPOCH_USER don't need backend data
    }
  };

  // Advance to next state
  const handleContinue = () => {
    if (!canProceed()) return; // Don't proceed if data not ready

    switch (actState) {
      case 'INTAKE':
        // Skip investigation, go directly to trial
        setCurrentEpoch(0);
        setActState('EPOCH_PROSECUTOR');
        break;
      case 'INVESTIGATION':
        setCurrentEpoch(0);
        setActState('EPOCH_PROSECUTOR');
        break;
      case 'EPOCH_PROSECUTOR':
        setActState('EPOCH_DEFENDER');
        break;
      case 'EPOCH_DEFENDER':
        setActState('EPOCH_USER');
        break;
      case 'EPOCH_USER':
        if (currentEpoch < 1) {
          setCurrentEpoch(currentEpoch + 1);
          setActState('EPOCH_PROSECUTOR');
        } else {
          setActState('FINAL_USER_VERDICT');
        }
        break;
      case 'FINAL_USER_VERDICT':
        setActState('FINAL_VERDICT');
        break;
      default:
        break;
    }
  };

  // Submit user judgement for current round
  const handleUserJudgement = async (judgement) => {
    try {
      await fetch(`http://localhost:8000/api/trial/${caseId}/judgement`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId, judgement })
      });

      setConversationHistory(prev => [...prev, {
        agent: 'user',
        round: currentEpoch + 1,
        argument: `User judgement: ${judgement}`,
        confidence: null
      }]);

      handleContinue();
    } catch (error) {
      console.error('Error submitting judgement:', error);
    }
  };

  // Get current speaker's data based on state
  useEffect(() => {
    if (actState === 'EPOCH_PROSECUTOR' || actState === 'EPOCH_DEFENDER') {
      const agent = actState === 'EPOCH_PROSECUTOR' ? 'prosecutor' : 'defendant';
      const round = currentEpoch + 1;

      const entry = transcript.find(t => t.agent === agent && t.round === round);
      if (entry) {
        setCurrentSpeakerData(entry);

        setConversationHistory(prev => {
          const exists = prev.some(e => e.agent === agent && e.round === round);
          if (!exists) {
            return [...prev, entry];
          }
          return prev;
        });
      }
    }
  }, [actState, currentEpoch, transcript]);

  // Loading spinner component
  const LoadingSpinner = ({ message = 'Processing...' }) => (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '2rem'
    }}>
      <div style={{
        fontSize: '3rem',
        animation: 'spin 1s linear infinite'
      }}>
        🔨
      </div>
      <p style={{ marginTop: '1rem', color: 'var(--color-oak)', fontWeight: 'bold' }}>
        {message}
      </p>
    </div>
  );

  return (
    <div className="courtroom-bg">
      <div className="overlay">
        <AnimatePresence mode="wait">

          {actState === 'INTAKE' && (
            <IntakePanel
              key="intake"
              claim={claim}
              onStartInvestigation={handleContinue}
            />
          )}

          {actState === 'INVESTIGATION' && (
            <InvestigationPanel
              key="investigation"
              evidence={evidence}
              onProceed={handleContinue}
              loading={!investigationReady}
            />
          )}

          {actState.startsWith('EPOCH') && (
            <div key="epoch" className="panel" style={{ maxWidth: '1200px' }}>
              <ConversationHistory
                transcript={conversationHistory}
                currentRound={currentEpoch + 1}
                showJudgement={actState === 'EPOCH_USER'}
                onJudge={handleUserJudgement}
                awaitingJudgement={false}
              />

              {(actState === 'EPOCH_PROSECUTOR' || actState === 'EPOCH_DEFENDER') && (
                <>
                  {currentSpeakerData ? (
                    <EpochPanel
                      currentPhase={actState === 'EPOCH_PROSECUTOR' ? 'prosecutor' : 'defender'}
                      charActive={false}
                      transcript={[currentSpeakerData]}
                      currentRound={currentEpoch + 1}
                    />
                  ) : (
                    <LoadingSpinner />
                  )}
                </>
              )}

              {actState !== 'EPOCH_USER' && (
                <button
                  onClick={handleContinue}
                  className="btn-oak"
                  style={{ marginTop: '2rem' }}
                  disabled={!canProceed()}
                >
                  {canProceed() ? 'Continue →' : 'Loading...'}
                </button>
              )}
            </div>
          )}

          {actState === 'FINAL_USER_VERDICT' && (
            <div key="final-user-verdict" className="panel">
              <h2 style={{ textAlign: 'center', marginBottom: '2rem', color: 'var(--color-oak)' }}>
                Your Final Verdict
              </h2>
              <p style={{ textAlign: 'center', marginBottom: '2rem' }}>
                Based on all the evidence and arguments, what is your verdict?
              </p>
              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                <button
                  onClick={() => { handleContinue(); }}
                  className="btn-oak"
                  style={{ background: '#dc2626', width: 'auto', padding: '1rem 3rem' }}
                >
                  FAKE
                </button>
                <button
                  onClick={() => { handleContinue(); }}
                  className="btn-oak"
                  style={{ background: '#10b981', width: 'auto', padding: '1rem 3rem' }}
                >
                  REAL
                </button>
              </div>
            </div>
          )}

          {actState === 'FINAL_VERDICT' && (
            <>
              {verdict ? (
                <FinalVerdictPanel
                  key="verdict"
                  verdict={verdict}
                  awarenessScore={awarenessScore}
                  onRestart={() => window.location.reload()}
                />
              ) : (
                <div className="panel">
                  <LoadingSpinner />
                </div>
              )}
            </>
          )}

        </AnimatePresence>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Courtroom;
