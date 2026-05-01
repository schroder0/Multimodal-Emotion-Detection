import React, { useState, useRef } from 'react';
import axios from 'axios';
import './InputForm.css';

const InputForm = ({ onResultReceived }) => {
  const [text, setText] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastSubmittedText, setLastSubmittedText] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleTextChange = (e) => {
    setText(e.target.value);
    setError(null);
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      processImageFile(file);
    }
  };

  const processImageFile = (file) => {
    if (!file.type.startsWith('image/')) {
      setError('Please upload a valid image file');
      return;
    }
    setImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
    setError(null);
  };

  const handleClearImage = () => {
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      processImageFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!text.trim() && !image) {
      setError('Please enter text or upload an image');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('text', text);
      if (image) {
        formData.append('image', image);
      }

      const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      onResultReceived(response.data);
      // Save submitted text for display, keep text in input
      setLastSubmittedText(text);
      // Clear image only (text persists until user changes it)
      setImage(null);
      setImagePreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Error:', err);
      setError(
        err.response?.data?.detail ||
        err.response?.data?.error ||
        'Failed to analyze emotion. Please check that the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  };

  const charCount = text.length;

  return (
    <div className="input-form-container">
      <div className="input-form">
        <div className="form-title-row">
          <h2>Analyze Your Emotion</h2>
          {lastSubmittedText && (
            <div className="last-submitted">
              <span className="last-submitted-label">Last analyzed:</span>
              <span className="last-submitted-text">"{lastSubmittedText.substring(0, 50)}{lastSubmittedText.length > 50 ? '...' : ''}"</span>
            </div>
          )}
        </div>
        
        {error && (
          <div className="error-message">
            <span className="error-icon">{'\u{26A0}'}</span>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Text Input */}
          <div className="form-group">
            <div className="label-row">
              <label htmlFor="text-input">Enter Text (with emojis)</label>
              <span className={`char-counter ${charCount > 500 ? 'char-warn' : ''}`}>
                {charCount}/500
              </span>
            </div>
            <textarea
              id="text-input"
              value={text}
              onChange={handleTextChange}
              placeholder="E.g., I'm so happy today! 🎉 or This makes me really angry 😤"
              rows={4}
              maxLength={500}
              disabled={loading}
            />
          </div>

          {/* Image Upload — Drag & Drop Zone */}
          <div className="form-group">
            <label htmlFor="image-input">Upload Image (optional)</label>
            <div
              className={`drop-zone ${isDragging ? 'drop-zone-active' : ''} ${imagePreview ? 'drop-zone-has-image' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => !loading && fileInputRef.current?.click()}
            >
              {imagePreview ? (
                <div className="image-preview">
                  <img src={imagePreview} alt="Selected" />
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); handleClearImage(); }}
                    disabled={loading}
                    className="clear-btn"
                  >
                    {'\u{2715}'} Remove
                  </button>
                </div>
              ) : (
                <div className="drop-zone-content">
                  <span className="drop-icon">{'\u{1F4F7}'}</span>
                  <span className="drop-text">
                    {isDragging ? 'Drop image here' : 'Drag & drop an image or click to browse'}
                  </span>
                </div>
              )}
              <input
                ref={fileInputRef}
                id="image-input"
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                disabled={loading}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="submit-btn"
          >
            {loading ? (
              <span className="loading-content">
                <span className="spinner"></span>
                Analyzing...
              </span>
            ) : (
              <span>{'\u{2728}'} Analyze Emotion</span>
            )}
          </button>
        </form>

        {/* Info Section */}
        <div className="info-section">
          <h3>How it works</h3>
          <ul>
            <li>Enter text with emojis to describe your mood</li>
            <li>Optionally upload an image for deeper context</li>
            <li>AI analyzes all modalities with chain-of-thought reasoning</li>
            <li>Receive detailed emotion detection with explanations</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default InputForm;
