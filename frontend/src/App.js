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
        input_type: inputType
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
                onClick={() => { setInputType('image'); setContent(''); }}
              >
                🖼️ Image
              </button>
              <button
                className={inputType === 'video' ? 'btn-input-type active' : 'btn-input-type'}
                onClick={() => { setInputType('video'); setContent(''); }}
              >
                🎥 Video
              </button>
            </div>

            {/* Text Input */}
            {inputType === 'text' && (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste a suspicious claim, article, or social media post here..."
              />
            )}

            {/* URL Input */}
            {inputType === 'url' && (
              <input
                type="url"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste a news article URL here..."
                style={{
                  width: '100%',
                  padding: '15px',
                  fontSize: '1rem',
                  borderRadius: '8px',
                  border: '2px solid #333',
                  backgroundColor: '#1a1a1a',
                  color: '#fff',
                  marginBottom: '20px'
                }}
              />
            )}

            {/* Image Upload */}
            {inputType === 'image' && (
              <div style={{ marginBottom: '20px' }}>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  style={{
                    width: '100%',
                    padding: '15px',
                    fontSize: '1rem',
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

            {/* Video Upload */}
            {inputType === 'video' && (
              <div style={{ marginBottom: '20px' }}>
                <input
                  type="file"
                  accept="video/*"
                  onChange={handleFileChange}
                  style={{
                    width: '100%',
                    padding: '15px',
                    fontSize: '1rem',
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
              {loading ? 'Starting Trial...' : 'Start Trial'}
            </button>
          </div>

          <div style={{ marginTop: '60px', color: '#888' }}>
            <h3 style={{ color: '#d4af37', marginBottom: '20px' }}>How It Works</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', textAlign: 'left' }}>
              <div>
                <h4 style={{ color: '#d4af37' }}>1. Submit</h4>
                <p>Enter text, paste a URL, or upload an image/video</p>
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
