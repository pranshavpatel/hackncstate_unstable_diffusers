import React from 'react';
import { motion } from 'framer-motion';

const IntakePanel = ({ claim, onStartInvestigation }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="panel"
            style={{ textAlign: 'center' }}
        >
            <h2 style={{ color: 'var(--color-text-main)', marginBottom: '1.5rem' }}>Court Intake</h2>

            <div style={{
                background: 'rgba(255,255,255,0.5)',
                padding: '2rem',
                borderRadius: '8px',
                fontSize: '1.25rem',
                fontStyle: 'italic',
                marginBottom: '2rem',
                borderLeft: '4px solid var(--color-oak)'
            }}>
                "{claim}"
            </div>

            <p style={{ marginBottom: '2rem', color: 'var(--color-oak)', fontWeight: 'bold' }}>
                The court will now proceed to trial.
            </p>

            <button onClick={onStartInvestigation} className="btn-oak">
                Begin Trial →
            </button>
        </motion.div>
    );
};

export default IntakePanel;
