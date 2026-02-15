import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const Courtroom = ({ caseId }) => {
  const [trialState, setTrialState] = useState({
    phase: 'starting',
    currentRound: 0,
    transcript: [],
    verdict: null,
    education: null
  });

  useEffect(() => {
    let eventSource = null;
    let mounted = true;

    const connectStream = () => {
      eventSource = new EventSource(`http://localhost:8000/api/trial/${caseId}/stream`);

      eventSource.onmessage = (event) => {
        if (!mounted) return;
        const data = JSON.parse(event.data);
        
        if (data.phase === 'claim_extraction') {
          setTrialState(prev => ({ ...prev, phase: 'claims' }));
        } else if (data.phase === 'investigation') {
          setTrialState(prev => ({ ...prev, phase: 'investigation' }));
        } else if (data.phase === 'trial') {
          setTrialState(prev => ({
            ...prev,
            phase: 'trial',
            currentRound: data.round,
            transcript: [...prev.transcript, {
              agent: data.agent,
              round: data.round,
              argument: data.argument,
              confidence: data.confidence
            }]
          }));
        } else if (data.phase === 'verdict') {
          setTrialState(prev => ({ ...prev, phase: 'verdict', verdict: data.verdict }));
        } else if (data.phase === 'education') {
          setTrialState(prev => ({ ...prev, education: data.education }));
        } else if (data.phase === 'complete') {
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };
    };

    connectStream();

    return () => {
      mounted = false;
      if (eventSource) eventSource.close();
    };
  }, [caseId]);

  if (trialState.phase === 'starting' || trialState.phase === 'claims' || trialState.phase === 'investigation') {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Preparing the courtroom...</p>
        {trialState.phase === 'claims' && <p>Extracting claims...</p>}
        {trialState.phase === 'investigation' && <p>Gathering evidence...</p>}
      </div>
    );
  }

  if (trialState.phase === 'verdict' && trialState.verdict) {
    const { score, category, individual_verdicts, summary } = trialState.verdict;
    const categoryClass = score > 60 ? 'true' : score < 40 ? 'false' : 'uncertain';

    return (
      <div className="verdict-section">
        <h2>Trial Complete</h2>
        
        <div style={{ marginBottom: '40px', textAlign: 'left', background: 'rgba(45,45,45,0.9)', padding: '30px', borderRadius: '10px', border: '2px solid #d4af37' }}>
          <h3 style={{ color: '#d4af37', marginBottom: '20px' }}>📜 Full Trial Transcript</h3>
          {trialState.transcript.map((entry, i) => (
            <div key={i} style={{ marginBottom: '25px', borderLeft: entry.agent === 'prosecutor' ? '4px solid #c41e3a' : '4px solid #228b22', paddingLeft: '20px', background: 'rgba(26,26,26,0.5)', padding: '15px', borderRadius: '5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <strong style={{ color: entry.agent === 'prosecutor' ? '#ff6b7a' : '#90ee90', textTransform: 'capitalize', fontSize: '1.1rem' }}>
                  {entry.agent === 'prosecutor' ? '⚖️ Prosecutor' : '🛡️ Defense'} - Round {entry.round}
                </strong>
                <span style={{ color: '#d4af37', fontWeight: 'bold' }}>Confidence: {entry.confidence}%</span>
              </div>
              <p style={{ lineHeight: '1.8', color: '#e0e0e0', fontSize: '1.05rem' }}>{entry.argument}</p>
            </div>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }} style={{ background: 'rgba(45,45,45,0.9)', padding: '40px', borderRadius: '15px', border: '3px solid #d4af37' }}>
          <h2 style={{ color: '#d4af37', fontSize: '2.5rem' }}>⚖️ The Verdict</h2>
          <div className="verdict-score" style={{ fontSize: '4rem', margin: '20px 0', color: '#d4af37' }}>{score}/100</div>
          <div className={`verdict-category ${categoryClass}`} style={{ fontSize: '1.8rem', padding: '15px', borderRadius: '10px', marginBottom: '20px' }}>
            {category}
          </div>
          <p style={{ color: '#b0b0b0', fontSize: '1.1rem', marginBottom: '30px' }}>{summary}</p>
          
          <h3 style={{ color: '#d4af37', marginTop: '40px', marginBottom: '20px', fontSize: '1.8rem' }}>👥 Individual Jury Verdicts</h3>
          {individual_verdicts && individual_verdicts.length > 0 ? (
            <div className="individual-verdicts" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              {individual_verdicts.map((v, i) => (
                <div key={i} style={{ background: 'rgba(26,26,26,0.7)', padding: '25px', borderRadius: '10px', border: '2px solid #555' }}>
                  <h4 style={{ color: '#d4af37', fontSize: '1.3rem', marginBottom: '15px' }}>Juror {v.juror_id}</h4>
                  <p style={{ color: '#b0b0b0', marginBottom: '10px' }}><strong>Model:</strong> {v.model}</p>
                  <p style={{ fontSize: '1.5rem', color: '#d4af37', margin: '15px 0' }}><strong>Score:</strong> {v.confidence_score}/100</p>
                  <p style={{ color: '#e0e0e0', lineHeight: '1.6' }}><strong>Top Reason:</strong> {v.top_3_reasons && v.top_3_reasons[0]}</p>
                  {v.key_evidence && <p style={{ color: '#b0b0b0', marginTop: '10px', fontSize: '0.9rem' }}><strong>Key Evidence:</strong> {v.key_evidence}</p>}
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#888' }}>No individual verdicts available</p>
          )}

          {trialState.education && trialState.education.red_flags && (
            <div style={{ marginTop: '50px', textAlign: 'left', background: 'rgba(196,30,58,0.1)', padding: '30px', borderRadius: '10px', border: '2px solid #c41e3a' }}>
              <h3 style={{ color: '#ff6b7a', fontSize: '1.8rem', marginBottom: '20px' }}>🚩 What You Should Have Noticed</h3>
              <h4 style={{ color: '#ff6b7a', marginTop: '20px' }}>Red Flags:</h4>
              <ul style={{ color: '#e0e0e0', lineHeight: '1.8', fontSize: '1.05rem' }}>
                {trialState.education.red_flags.map((flag, i) => (
                  <li key={i} style={{ marginBottom: '10px' }}>{flag}</li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>
      </div>
    );
  }

  return (
    <div className="courtroom">
      <div className="courtroom-header">
        <h2>The Trial</h2>
        <div className="round-indicator">Round {trialState.currentRound} of 2</div>
      </div>

      <div style={{ background: 'rgba(45,45,45,0.9)', padding: '30px', borderRadius: '10px', marginBottom: '30px' }}>
        <h3 style={{ color: '#d4af37', marginBottom: '20px' }}>Trial Transcript</h3>
        {trialState.transcript.length === 0 ? (
          <p style={{ color: '#888' }}>Waiting for arguments...</p>
        ) : (
          trialState.transcript.map((entry, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ 
                marginBottom: '20px', 
                borderLeft: entry.agent === 'prosecutor' ? '3px solid #c41e3a' : '3px solid #228b22', 
                paddingLeft: '15px' 
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <strong style={{ color: entry.agent === 'prosecutor' ? '#ff6b7a' : '#90ee90', textTransform: 'capitalize' }}>
                  {entry.agent} - Round {entry.round}
                </strong>
                <span style={{ color: '#b0b0b0' }}>Confidence: {entry.confidence}%</span>
              </div>
              <p style={{ lineHeight: '1.6', color: '#d0d0d0' }}>{entry.argument}</p>
            </motion.div>
          ))
        )}
      </div>

      <div className="jury-panel">
        <h3>The Jury</h3>
        <div className="jurors">
          <div className="juror">
            <div className="juror-avatar">G</div>
            <div className="juror-name">Gemini Pro</div>
          </div>
          <div className="juror">
            <div className="juror-avatar">G</div>
            <div className="juror-name">Gemini Flash</div>
          </div>
          <div className="juror">
            <div className="juror-avatar">G</div>
            <div className="juror-name">Gemini Flash</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Courtroom;
