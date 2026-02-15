import React from 'react';
import { motion } from 'framer-motion';

const AwarenessScore = ({ awarenessScore }) => {
    if (!awarenessScore || awarenessScore.score === undefined) {
        return null;
    }

    const score = awarenessScore.score || 0;
    const feedback = awarenessScore.feedback || "Keep practicing your fraud detection skills!";

    // Determine color based on score
    const getScoreColor = (score) => {
        if (score >= 8) return '#90ee90'; // Green
        if (score >= 5) return '#ffd700'; // Gold
        return '#ff6b7a'; // Red
    };

    const scoreColor = getScoreColor(score);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            style={{
                background: 'linear-gradient(135deg, rgba(75,0,130,0.2), rgba(138,43,226,0.2))',
                padding: '40px',
                borderRadius: '15px',
                border: '2px solid #9370db',
                marginTop: '40px',
                textAlign: 'center'
            }}
        >
            {/* Main Score Display */}
            <h2 style={{ color: '#dda0dd', fontSize: '2rem', marginBottom: '20px' }}>
                🧠 Your Awareness Score
            </h2>

            <div style={{
                fontSize: '5rem',
                fontWeight: 'bold',
                color: scoreColor,
                textShadow: `0 0 20px ${scoreColor}66`,
                marginBottom: '30px'
            }}>
                {score} / 10
            </div>

            {/* Educational Feedback */}
            <div style={{
                background: 'rgba(26,26,26,0.6)',
                padding: '30px',
                borderRadius: '10px',
                border: '1px solid #6a5acd',
                maxWidth: '800px',
                margin: '0 auto'
            }}>
                <div style={{
                    fontSize: '1.1rem',
                    color: '#dda0dd',
                    marginBottom: '15px',
                    fontWeight: 'bold'
                }}>
                    💡 How to Recognize Fraud
                </div>
                <p style={{
                    color: '#e0e0e0',
                    lineHeight: '1.8',
                    fontSize: '1.05rem',
                    margin: 0,
                    textAlign: 'left'
                }}>
                    {feedback}
                </p>
            </div>
        </motion.div>
    );
};

export default AwarenessScore;
