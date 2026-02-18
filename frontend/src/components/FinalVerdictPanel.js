import React from 'react';
import { motion } from 'framer-motion';

const FinalVerdictPanel = ({ verdict, awarenessScore, onRestart }) => {
    // Check if this is a fasttrack verdict
    const isFastTrack = verdict?.mode === 'fasttrack';

    if (isFastTrack) {
        const { final_verdict, confidence, reasoning, key_findings } = verdict;
        const categoryClass = final_verdict === 'VERIFIED' ? 'true' : final_verdict === 'FAKE' ? 'false' : 'uncertain';
        const getScoreColor = (category) => {
            if (category === 'true' || final_verdict === 'VERIFIED') return '#10b981';
            if (category === 'false' || final_verdict === 'FAKE') return '#dc2626';
            return '#d4af37';
        };

        return (
            <motion.div
                className="panel"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
            >
                <div className="verdict-box">
                    <h2 style={{ color: '#d4af37', marginBottom: '0.5rem' }}>⚡ FAST-TRACK VERDICT</h2>
                    <div style={{ fontSize: '4rem', fontWeight: 'bold', color: getScoreColor(categoryClass) }}>
                        {confidence}%
                    </div>
                    <div style={{ fontSize: '1.5rem', marginBottom: '1rem', color: getScoreColor(categoryClass) }}>
                        {final_verdict}
                    </div>
                    <p>{reasoning}</p>
                </div>

                {key_findings && key_findings.length > 0 && (
                    <div style={{
                        marginTop: '2rem',
                        padding: '1.5rem',
                        background: 'rgba(212, 163, 115, 0.1)',
                        borderRadius: '8px',
                        border: '2px solid var(--color-oak)'
                    }}>
                        <h3 style={{ color: 'var(--color-oak)', marginTop: 0 }}>Key Findings:</h3>
                        <ul style={{ lineHeight: '1.8', marginTop: '1rem' }}>
                            {key_findings.map((finding, i) => (
                                <li key={i} style={{ marginBottom: '0.5rem' }}>{finding}</li>
                            ))}
                        </ul>
                    </div>
                )}

                <button onClick={onRestart} className="btn-oak" style={{ marginTop: '2rem' }}>
                    Start New Analysis
                </button>
            </motion.div>
        );
    }

    // Regular courtroom verdict
    const { score, category, individual_verdicts, summary } = verdict;

    // Calculate score color
    const getScoreColor = (s) => {
        if (s >= 60) return '#10b981'; // Green
        if (s <= 40) return '#dc2626'; // Red
        return '#d4af37'; // Gold/Yellow
    };

    return (
        <motion.div
            className="panel"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
        >
            <div className="verdict-box">
                <h2 style={{ color: '#d4af37', marginBottom: '0.5rem' }}>FINAL VERDICT</h2>
                <div style={{ fontSize: '4rem', fontWeight: 'bold', color: getScoreColor(score) }}>
                    {score}/100
                </div>
                <div style={{ fontSize: '1.5rem', marginBottom: '1rem', color: getScoreColor(score) }}>
                    {category}
                </div>
                <p style={{ color: '#f5e6d3' }}>{summary}</p>
            </div>

            {awarenessScore && (
                <div style={{
                    marginTop: '2rem',
                    padding: '1.5rem',
                    background: 'rgba(212, 163, 115, 0.2)',
                    borderRadius: '8px',
                    border: '2px solid var(--color-oak)'
                }}>
                    <h3 style={{ color: 'var(--color-text-dark)', marginTop: 0 }}>
                        Your Awareness Score: {awarenessScore.score}/10
                    </h3>
                    <p style={{ margin: 0, fontSize: '1rem', color: 'var(--color-text-dark)' }}>
                        {awarenessScore.feedback}
                    </p>
                </div>
            )}

            <h3 style={{ marginTop: '2rem', borderBottom: '2px solid var(--color-oak)' }}>Jury Breakdown</h3>
            <div className="evidence-grid">
                {individual_verdicts && individual_verdicts.map((j, i) => (
                    <div key={i} className="evidence-card" style={{ textAlign: 'left' }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: 'var(--color-oak)' }}>
                            Juror {j.juror_id} ({j.model})
                        </div>
                        <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                            Score: {j.confidence_score}
                        </div>
                        <p style={{ fontSize: '0.9rem' }}>{j.top_3_reasons && j.top_3_reasons[0]}</p>
                    </div>
                ))}
            </div>

            <button onClick={onRestart} className="btn-oak">
                Start New Trial
            </button>
        </motion.div>
    );
};

export default FinalVerdictPanel;
