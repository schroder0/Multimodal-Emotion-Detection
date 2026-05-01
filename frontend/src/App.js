import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultCard from './components/ResultCard';
import './App.css';

const emotionEmojis = {
  happiness: '\u{1F60A}',
  sadness: '\u{1F622}',
  anger: '\u{1F621}',
  fear: '\u{1F628}',
  surprise: '\u{1F632}',
  disgust: '\u{1F92E}',
  love: '\u{1F497}',
  neutral: '\u{1F610}',
  uncertain: '\u{1F914}',
};

function App() {
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const handleResultReceived = (analysisResult) => {
    setResult(analysisResult);

    // Add to history (keep last 10)
    const historyEntry = {
      id: Date.now(),
      emotion: analysisResult.emotion || 'uncertain',
      confidence: analysisResult.confidence || 0,
      text: analysisResult.context_summary?.multimodal_summary?.text_info || 'No text',
      timestamp: new Date().toLocaleTimeString(),
    };
    setHistory((prev) => [historyEntry, ...prev].slice(0, 10));

    // Scroll to result
    setTimeout(() => {
      const resultElement = document.querySelector('.result-card');
      if (resultElement) {
        resultElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100);
  };

  const handleHistoryClick = (entry) => {
    // Scroll back to top to see full context
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const clearHistory = () => {
    setHistory([]);
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>{'\u{1F3AD}'} Multimodal Emotion Detection</h1>
        </div>
      </header>

      <main className="app-main">
        <InputForm onResultReceived={handleResultReceived} />
        {result && <ResultCard result={result} />}

        {history.length > 0 && (
          <div className="history-section">
            <div className="history-header">
              <h3>{'\u{1F4CB}'} Analysis History</h3>
              <button className="clear-history-btn" onClick={clearHistory}>
                Clear
              </button>
            </div>
            <div className="history-list">
              {history.map((entry) => (
                <div
                  key={entry.id}
                  className="history-item"
                  onClick={() => handleHistoryClick(entry)}
                >
                  <span className="history-emoji">
                    {emotionEmojis[entry.emotion] || '\u{2753}'}
                  </span>
                  <div className="history-details">
                    <div className="history-text">{entry.text}</div>
                    <div className="history-meta">
                      <span
                        className="history-emotion-tag"
                        style={{
                          background: `var(--emotion-${entry.emotion}, var(--emotion-neutral))`,
                          color: '#000',
                        }}
                      >
                        {entry.emotion}
                      </span>
                      <span className="history-confidence">
                        {(entry.confidence * 100).toFixed(0)}% confidence
                      </span>
                      <span>{entry.timestamp}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
