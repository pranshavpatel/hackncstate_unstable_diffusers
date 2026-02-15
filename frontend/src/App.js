import React, { useState } from 'react';
import axios from 'axios';
import Courtroom from './components/Courtroom';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [content, setContent] = useState('');
  const [caseId, setCaseId] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!content.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/trial/start`, {
        content: content,
        input_type: 'text'
      });
      
      setCaseId(response.data.case_id);
    } catch (error) {
      console.error('Error starting trial:', error);
      alert('Failed to start trial. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (caseId) {
    return (
      <div className="app">
        <Courtroom caseId={caseId} />
      </div>
    );
  }

  return (
    <div className="app">
      <div className="container">
        <div className="landing">
          <h1>The Unreliable Narrator</h1>
          <p>AI Courtroom for Misinformation Detection</p>
          <p style={{ fontSize: '1rem', color: '#888' }}>
            Submit suspicious content and watch AI agents battle it out in court
          </p>

          <div className="input-section">
            <h3 style={{ marginBottom: '20px', color: '#d4af37' }}>
              Submit Content for Trial
            </h3>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste a suspicious claim, article, or social media post here..."
            />
            <button 
              className="btn" 
              onClick={handleSubmit}
              disabled={loading || !content.trim()}
            >
              {loading ? 'Starting Trial...' : 'Start Trial'}
            </button>
          </div>

          <div style={{ marginTop: '60px', color: '#888' }}>
            <h3 style={{ color: '#d4af37', marginBottom: '20px' }}>How It Works</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', textAlign: 'left' }}>
              <div>
                <h4 style={{ color: '#d4af37' }}>1. Submit</h4>
                <p>Enter suspicious content you want fact-checked</p>
              </div>
              <div>
                <h4 style={{ color: '#d4af37' }}>2. Watch</h4>
                <p>AI agents debate in real-time courtroom trial</p>
              </div>
              <div>
                <h4 style={{ color: '#d4af37' }}>3. Learn</h4>
                <p>Multi-model jury delivers verdict with evidence</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
