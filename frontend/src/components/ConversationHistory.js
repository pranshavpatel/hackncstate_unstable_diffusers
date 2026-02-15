import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Import images
import lawyerImg from '../images/lawyer.png';
import policeImg from '../images/police.png';
import juryImg from '../images/jury.png';
import userImg from '../images/user.png';

const CHAR_IMAGES = {
    prosecutor: lawyerImg,
    defender: lawyerImg,
    defendant: lawyerImg, // Map defendant to lawyer too
    investigator: policeImg,
    jury: juryImg,
    user: userImg
};

const ConversationHistory = ({ transcript, currentRound, showJudgement, onJudge, awaitingJudgement }) => {
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [transcript, showJudgement]);

    return (
        <div className="transcript-container" ref={scrollRef}>
            <h3 style={{ color: 'var(--color-text-main)', marginBottom: '1rem', textAlign: 'center' }}>
                Court Transcript
            </h3>

            <AnimatePresence>
                {transcript.map((entry, index) => {
                    const role = entry.agent === 'defendant' ? 'defender' : entry.agent;
                    const icon = CHAR_IMAGES[role] || CHAR_IMAGES.investigator;

                    return (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`chat-bubble header-${entry.agent}`}
                            style={{
                                borderColor: entry.agent === 'prosecutor' ? 'var(--color-prosecutor)' :
                                    entry.agent === 'defender' || entry.agent === 'defendant' ? 'var(--color-defender)' :
                                        '#d4af37'
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
                                <img
                                    src={icon}
                                    alt={role}
                                    style={{ width: '32px', height: '32px', marginRight: '10px', borderRadius: '4px', objectFit: 'contain' }}
                                />
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <strong style={{ textTransform: 'capitalize' }}>
                                            {entry.agent === 'defendant' ? 'Defender' : entry.agent}
                                        </strong>
                                        <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>Round {entry.round}</span>
                                    </div>
                                </div>
                            </div>
                            <p style={{ margin: 0, lineHeight: 1.5 }}>{entry.argument}</p>
                        </motion.div>
                    );
                })}
            </AnimatePresence>

            {/* Inline Judgement UI */}
            {showJudgement && (
                <motion.div
                    className="judgement-inline"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <h4 style={{ color: 'var(--color-oak)', marginTop: 0, textAlign: 'center' }}>
                        The court pauses for your judgement.
                    </h4>
                    <p style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                        Based on the arguments so far, how do you perceive the claim?
                    </p>

                    <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                        {['Plausible', 'Misleading', 'Not Sure', 'Neutral'].map((option) => (
                            <button
                                key={option}
                                onClick={() => onJudge(option.toLowerCase())}
                                style={{
                                    padding: '10px 20px',
                                    borderRadius: '6px',
                                    border: '2px solid var(--color-oak)',
                                    background: 'white',
                                    color: 'var(--color-oak)',
                                    fontWeight: 'bold',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s'
                                }}
                                onMouseOver={(e) => {
                                    e.currentTarget.style.background = 'var(--color-oak)';
                                    e.currentTarget.style.color = 'white';
                                }}
                                onMouseOut={(e) => {
                                    e.currentTarget.style.background = 'white';
                                    e.currentTarget.style.color = 'var(--color-oak)';
                                }}
                            >
                                {option}
                            </button>
                        ))}
                    </div>
                </motion.div>
            )}

            {!showJudgement && awaitingJudgement && (
                <div style={{ textAlign: 'center', padding: '1rem', color: 'var(--color-oak)', fontStyle: 'italic', fontWeight: 'bold' }}>
                    Waiting for next speaker...
                </div>
            )}
        </div>
    );
};

export default ConversationHistory;
