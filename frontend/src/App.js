import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Courtroom from './components/Courtroom';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [content, setContent] = useState('');
  const [inputType, setInputType] = useState('text');
  const [selectedFile, setSelectedFile] = useState(null);
  const [caseId, setCaseId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('courtroom'); // 'courtroom' or 'fasttrack'

  // Auto-detect URLs in text input
  useEffect(() => {
    if (inputType === 'text' && content.trim().startsWith('http')) {
      console.log('Auto-detected URL, switching to URL mode');
      setInputType('url');
    }
  }, [content, inputType]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const handleSubmit = async () => {
    if (inputType === 'video' || inputType === 'image') {
      if (!selectedFile) {
        alert(`Please select ${inputType === 'video' ? 'a video' : 'an image'} file`);
        return;
      }
      await handleFileUpload();
    } else {
      if (!content.trim()) {
        alert('Please enter content');
        return;
      }
      await handleTextOrUrlSubmit();
    }
  };

  const handleTextOrUrlSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/trial/start`, {
        content: content,
        input_type: inputType,
        mode: mode
      });

      setCaseId(response.data.case_id);
    } catch (error) {
      console.error('Error starting trial:', error);
      alert('Failed to start trial. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('input_type', inputType);
      formData.append('mode', mode);

      const response = await axios.post(`${API_BASE}/api/trial/start-with-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setCaseId(response.data.case_id);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (caseId) {
    return (
      <div className="app">
        <Courtroom caseId={caseId} originalContent={content} />
      </div>
    );
  }

  return (
    <div className="app">
      <div className="container">
        <div className="landing">
          <h1>The Unreliable Narrator</h1>
          <p>AI Courtroom for Misinformation Detection</p>
          <p style={{ fontSize: '1rem', color: '#4a4a4a', fontWeight: '500' }}>
            Submit suspicious content and watch AI agents battle it out in court
          </p>

          <div className="input-section">
            <h3 style={{ marginBottom: '20px', color: '#1a1a1a', fontWeight: 'bold' }}>
              Submit Content for Trial
            </h3>

            {/* Mode Toggle */}
            <div style={{ marginBottom: '30px', textAlign: 'center' }}>
              <div style={{ 
                display: 'inline-flex', 
                backgroundColor: '#1a1a1a', 
                borderRadius: '12px', 
                padding: '4px',
                border: '2px solid #333'
              }}>
                <button
                  onClick={() => setMode('courtroom')}
                  style={{
                    padding: '12px 30px',
                    fontSize: '1rem',
                    borderRadius: '8px',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    backgroundColor: mode === 'courtroom' ? '#d4af37' : 'transparent',
                    color: mode === 'courtroom' ? '#000' : '#fff',
                    fontWeight: mode === 'courtroom' ? 'bold' : 'normal'
                  }}
                >
                  ⚖️ Courtroom Simulation
                </button>
                <button
                  onClick={() => setMode('fasttrack')}
                  style={{
                    padding: '12px 30px',
                    fontSize: '1rem',
                    borderRadius: '8px',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    backgroundColor: mode === 'fasttrack' ? '#d4af37' : 'transparent',
                    color: mode === 'fasttrack' ? '#000' : '#fff',
                    fontWeight: mode === 'fasttrack' ? 'bold' : 'normal'
                  }}
                >
                  ⚡ Fast-Track Verdict
                </button>
              </div>
              <p style={{ marginTop: '10px', fontSize: '0.9rem', color: '#888' }}>
                {mode === 'courtroom' 
                  ? '🎭 Watch AI agents debate in real-time (slower, detailed)' 
                  : '⚡ Get instant verdict with AI analysis (faster)'}
              </p>
            </div>

            {/* Input Type Selector */}
            <div style={{ marginBottom: '20px', display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
              <button
                className={inputType === 'text' ? 'btn-input-type active' : 'btn-input-type'}
                onClick={() => { setInputType('text'); setSelectedFile(null); }}
              >
                📝 Text
              </button>
              <button
                className={inputType === 'url' ? 'btn-input-type active' : 'btn-input-type'}
                onClick={() => { setInputType('url'); setSelectedFile(null); }}
              >
                🔗 URL
              </button>
              <button
                className={inputType === 'image' ? 'btn-input-type active' : 'btn-input-type'}
                onClick={() => { setInputType('image'); setSelectedFile(null); }}
              >
                🖼️ Image
              </button>
              <button
                className={inputType === 'video' ? 'btn-input-type active' : 'btn-input-type'}
                onClick={() => { setInputType('video'); setSelectedFile(null); }}
              >
                🎥 Video
              </button>
            </div>

            {/* Input Fields */}
            {(inputType === 'text' || inputType === 'url') && (
              <textarea
                placeholder={inputType === 'text' ? 'Enter suspicious text...' : 'Enter URL...'}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                style={{
                  width: '100%',
                  minHeight: '150px',
                  padding: '15px',
                  marginBottom: '20px',
                  borderRadius: '8px',
                  border: '2px solid #333',
                  backgroundColor: '#1a1a1a',
                  color: '#fff',
                  fontSize: '1rem',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
              />
            )}

            {(inputType === 'image' || inputType === 'video') && (
              <div style={{ marginBottom: '20px' }}>
                <input
                  type="file"
                  accept={inputType === 'image' ? 'image/*' : 'video/*'}
                  onChange={handleFileChange}
                  style={{
                    width: '100%',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '2px solid #333',
                    backgroundColor: '#1a1a1a',
                    color: '#fff',
                    cursor: 'pointer'
                  }}
                />
                {selectedFile && (
                  <p style={{ marginTop: '10px', color: '#d4af37', fontSize: '0.9rem' }}>
                    Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                  </p>
                )}
              </div>
            )}

            <button
              className="btn"
              onClick={handleSubmit}
              disabled={loading || ((inputType === 'text' || inputType === 'url') && !content.trim()) || ((inputType === 'video' || inputType === 'image') && !selectedFile)}
            >
              {loading ? (mode === 'fasttrack' ? 'Analyzing...' : 'Starting Trial...') : (mode === 'fasttrack' ? '⚡ Get Instant Verdict' : '⚖️ Start Trial')}
            </button>
          </div>

          <div style={{ marginTop: '60px', color: '#2d2d2d' }}>
            <h3 style={{ color: '#1a1a1a', marginBottom: '20px', fontWeight: 'bold' }}>How It Works</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', textAlign: 'left' }}>
              <div>
                <h4 style={{ color: 'var(--color-oak)', fontWeight: 'bold' }}>1. Submit</h4>
                <p>Enter text, paste a URL, or upload an image/video</p>
              </div>
              <div>
                <h4 style={{ color: 'var(--color-oak)', fontWeight: 'bold' }}>2. Watch</h4>
                <p>AI agents debate in real-time courtroom trial</p>
              </div>
              <div>
                <h4 style={{ color: 'var(--color-oak)', fontWeight: 'bold' }}>3. Learn</h4>
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
