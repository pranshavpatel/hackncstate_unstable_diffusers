import React from 'react';
import Character from './Character';

const EpochPanel = ({
    currentPhase, // 'prosecutor', 'defender'
    charActive,
    transcript,
    currentRound,
}) => {

    // Determine which character to show
    let role = 'jury';
    let position = 'center';

    if (currentPhase === 'prosecutor') {
        role = 'prosecutor';
        position = 'left';
    } else if (currentPhase === 'defender' || currentPhase === 'defendant') {
        role = 'defender';
        position = 'right';
    }

    // Get the text from the current transcript entry
    const activeText = (transcript && transcript.length > 0)
        ? transcript[transcript.length - 1].argument
        : "";

    return (
        <div style={{
            height: '350px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '1rem',
            position: 'relative'
        }}>
            <Character
                role={role}
                isActive={true}
                position={position}
                isStreaming={charActive}
                text={activeText}
            />
        </div>
    );
};

export default EpochPanel;
