import React from 'react';
import { motion } from 'framer-motion';
import Character from './Character';

const InvestigationPanel = ({ evidence, onProceed, loading }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="panel"
        >
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '2rem' }}>
                <Character role="investigator" isActive={true} isStreaming={false} />
                <h2 style={{ marginTop: '1rem', color: 'var(--color-oak)' }}>Investigation Results</h2>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '2rem' }}>
                    <div style={{ fontSize: '3rem', animation: 'spin 1s linear infinite' }}>🔨</div>
                    <p style={{ marginTop: '1rem', color: 'var(--color-oak)' }}>Gathering evidence...</p>
                </div>
            ) : (
                <>
                    <div className="evidence-grid">
                        {evidence.map((item, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.2 }}
                                className="evidence-card"
                            >
                                <span className={`score-badge ${item.score >= 7 ? 'score-high' : item.score >= 4 ? 'score-med' : 'score-low'}`}>
                                    Reliability: {item.score}/10
                                </span>
                                <h4 style={{ margin: '0.5rem 0' }}>{item.source}</h4>
                                <p style={{ fontSize: '0.9rem', color: '#444' }}>{item.summary}</p>
                            </motion.div>
                        ))}
                    </div>

                    <button onClick={onProceed} className="btn-oak">
                        Proceed to Trial →
                    </button>
                </>
            )}

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </motion.div>
    );
};

export default InvestigationPanel;
