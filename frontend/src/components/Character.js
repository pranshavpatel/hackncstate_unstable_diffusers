import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

// Import images from src/images
import lawyerImg from '../images/lawyer.png';
import policeImg from '../images/police.png';
import juryImg from '../images/jury.png';
import userImg from '../images/user.png';

// Map roles to assigned images
const CHAR_IMAGES = {
    prosecutor: lawyerImg,
    defender: lawyerImg,
    defendant: lawyerImg,
    investigator: policeImg,
    jury: juryImg,
    user: userImg
};

const Character = ({ role, isActive, position = 'center', text, isStreaming }) => {
    const [displayedText, setDisplayedText] = useState('');
    const [hasEntered, setHasEntered] = useState(false);

    // Simple typewriter effect if text is provided and active
    useEffect(() => {
        if (isActive && text) {
            // If isStreaming is true, we might assume text is growing. 
            // Or we can just display 'text' directly if the parent handles the streaming accumulation.
            // If 'text' is the full final text, we might want to animate it.
            // For now, let's assume 'text' is updated by the parent as stream arrives, 
            // or we just show it. The prompt says "Word-by-word streaming: Use existing streaming hook/API".
            // If we receive the full text at once, we should animate it. 
            // If we receive it incrementally, we just set it.
            setDisplayedText(text);
        } else {
            setDisplayedText('');
        }
    }, [text, isActive]);

    // Mark as entered after initial animation
    useEffect(() => {
        if (isActive) {
            const timer = setTimeout(() => setHasEntered(true), 500);
            return () => clearTimeout(timer);
        } else {
            setHasEntered(false);
        }
    }, [isActive]);

    return (
        <motion.div
            className="character-container"
            style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                zIndex: isActive ? 10 : 1
            }}
            initial={{
                opacity: 0,
                scale: 0.5,
                y: 50
            }}
            animate={{
                opacity: 1,
                scale: isActive ? 1.3 : 1,
                x: isActive ? (position === 'left' ? 50 : position === 'right' ? -50 : 0) : 0,
                y: isActive && isStreaming ? [0, -2, 0] : 0, // Talking jitter
            }}
            transition={{
                opacity: { duration: 0.3 },
                scale: { type: 'spring', stiffness: 300, damping: 20 },
                x: { type: 'spring', stiffness: 300, damping: 20 },
                y: { repeat: (isActive && isStreaming) ? Infinity : 0, duration: 0.3 },
            }}
        >
            <img
                src={CHAR_IMAGES[role] || CHAR_IMAGES.investigator}
                className="w-32 h-32"
                alt={role}
                style={{
                    width: '128px',
                    height: '128px',
                    objectFit: 'contain',
                    filter: isActive ? 'drop-shadow(0 0 10px rgba(212, 163, 115, 0.5))' : 'none'
                }}
            />

            {/* Speech Bubble */}
            {isActive && displayedText && (
                <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                    style={{
                        position: 'absolute',
                        top: '-20px',
                        left: position === 'right' ? 'auto' : '100%',
                        right: position === 'right' ? '100%' : 'auto',
                        marginLeft: position === 'right' ? 0 : '1rem',
                        marginRight: position === 'right' ? '1rem' : 0,
                        background: 'var(--color-parchment)',
                        border: '2px solid var(--color-oak)',
                        borderRadius: '8px',
                        padding: '1rem',
                        width: '250px',
                        textAlign: 'left',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                        zIndex: 20
                    }}
                >
                    <p style={{ margin: 0, color: 'var(--color-text-main)', fontSize: '0.9rem' }}>
                        {displayedText}
                    </p>
                </motion.div>
            )}

            {/* Nameplate */}
            <div style={{
                marginTop: '10px',
                background: 'var(--color-oak)',
                color: 'white',
                padding: '4px 12px',
                borderRadius: '4px',
                fontSize: '0.8rem',
                fontWeight: 'bold',
                textTransform: 'capitalize'
            }}>
                {role}
            </div>
        </motion.div>
    );
};

export default Character;
