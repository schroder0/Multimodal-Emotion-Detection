import React, { useState } from 'react';
import './ResultCard.css';

const ResultCard = ({ result }) => {
  const [expandedSections, setExpandedSections] = useState({
    text: true,
    emoji: true,
    image: true,
    resolution: false,
    confidence: false,
  });

  if (!result) {
    return null;
  }

  // Emotion color mapping
  const emotionColors = {
    happiness: 'var(--emotion-happiness)',
    sadness: 'var(--emotion-sadness)',
    anger: 'var(--emotion-anger)',
    fear: 'var(--emotion-fear)',
    surprise: 'var(--emotion-surprise)',
    disgust: 'var(--emotion-disgust)',
    love: 'var(--emotion-love)',
    neutral: 'var(--emotion-neutral)',
    uncertain: 'var(--emotion-uncertain)',
  };

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

  const emotion = result.emotion || 'uncertain';
  const emotionColor = emotionColors[emotion] || 'var(--emotion-neutral)';
  const emotionEmoji = emotionEmojis[emotion] || '\u{2753}';
  const confidence = parseFloat(result.confidence) || 0;
  const confidencePercent = Math.round(confidence * 100);

  const toggleSection = (key) => {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const detailSections = [
    {
      key: 'text',
      icon: '\u{1F4DD}',
      title: 'Text Analysis',
      content: result.reasoning_details?.text_analysis,
    },
    {
      key: 'emoji',
      icon: '\u{1F60A}',
      title: 'Emoji Analysis',
      content: result.reasoning_details?.emoji_analysis,
    },
    {
      key: 'image',
      icon: '\u{1F5BC}',
      title: 'Image Analysis',
      content: result.reasoning_details?.image_analysis,
    },
    {
      key: 'resolution',
      icon: '\u{1F504}',
      title: 'Multimodal Resolution',
      content: result.reasoning_details?.multimodal_resolution,
    },
    {
      key: 'confidence',
      icon: '\u{1F4CA}',
      title: 'Confidence Reasoning',
      content: result.reasoning_details?.confidence_reasoning,
    },
  ];

  return (
    <div className="result-card">
      {/* Emotion Header */}
      <div className="result-header">
        <div className="emotion-display" style={{ '--emotion-clr': emotionColor }}>
          <span className="emotion-emoji">{emotionEmoji}</span>
          <span className="emotion-text">{emotion.toUpperCase()}</span>
        </div>
        <div className="confidence-display">
          <span className="confidence-label">Confidence</span>
          <span className="confidence-value" style={{ color: emotionColor }}>
            {confidencePercent}%
          </span>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${confidencePercent}%`,
                background: emotionColor,
              }}
            />
          </div>
        </div>
      </div>

      {/* Main Reasoning */}
      <div className="result-reasoning">
        <h3>{'\u{1F9E0}'} Analysis Summary</h3>
        <p className="reason-text">{result.reason}</p>
      </div>

      {/* Detailed Analysis — Collapsible Sections */}
      {result.reasoning_details && (
        <div className="reasoning-details">
          <h3>Detailed Chain-of-Thought</h3>
          {detailSections.map(
            (section) =>
              section.content && (
                <div
                  key={section.key}
                  className={`detail-section ${expandedSections[section.key] ? 'expanded' : 'collapsed'}`}
                >
                  <button
                    className="detail-toggle"
                    onClick={() => toggleSection(section.key)}
                    type="button"
                  >
                    <span className="detail-toggle-left">
                      <span className="detail-icon">{section.icon}</span>
                      <span className="detail-title">{section.title}</span>
                    </span>
                    <span className={`chevron ${expandedSections[section.key] ? 'chevron-open' : ''}`}>
                      {'\u{25B6}'}
                    </span>
                  </button>
                  {expandedSections[section.key] && (
                    <div className="detail-content">
                      <p>{section.content}</p>
                    </div>
                  )}
                </div>
              )
          )}
        </div>
      )}

      {/* Context Summary */}
      {result.context_summary && (
        <div className="context-summary">
          <h3>Input Summary</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-icon">{'\u{1F4DD}'}</span>
              <span>{result.context_summary.has_text ? 'Text provided' : 'No text'}</span>
            </div>
            <div className="summary-item">
              <span className="summary-icon">{'\u{1F60A}'}</span>
              <span>{result.context_summary.emoji_count} emoji(s)</span>
            </div>
            <div className="summary-item">
              <span className="summary-icon">{'\u{1F5BC}'}</span>
              <span>{result.context_summary.has_image ? 'Image provided' : 'No image'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
