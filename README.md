# Multimodal Emotion Detection System

A complete end-to-end system that detects human emotions using a combination of Text, Emojis, and Images. This project leverages the **Chain-of-Thought (CoT)** reasoning capabilities of large language models (LLaMA 3.3 70B via Groq) alongside Vision-Language Models (BLIP) to logically deduce emotions, resolving complex cases like sarcasm and masked feelings.

---

## 🚀 Quick Start Guide

This project is divided into two parts: a **Python FastAPI Backend** and a **React.js Frontend**. You must run both servers simultaneously for the app to work.

### 1. Start the Backend Server
The backend handles the AI models, image captioning (BLIP), and the Groq API connection.

Open a new terminal window and run:

```bash
# Navigate to the project root (if not already there)
cd /path/to/multimodal_emotion_detection

# 1. Activate the virtual environment
# On macOS/Linux:
source backend/venv/bin/activate
# On Windows:
# .\backend\venv\Scripts\activate

# 2. Set up your environment variables
# Ensure you have a .env file inside the /backend directory with:
# GROQ_API_KEY=your_groq_api_key_here

# 3. Start the FastAPI server
python backend/main.py
```
*The backend server will start running on **http://localhost:8000**.*

---

### 2. Start the Frontend Server
The frontend is a React application that provides the User Interface.

Open a **second, separate terminal window** and run:

```bash
# Navigate to the frontend directory
cd /path/to/multimodal_emotion_detection/frontend

# 1. Install Node modules (only needed the first time)
npm install

# 2. Fix macOS permissions (Run this ONLY if npm start gives a 'Permission denied' error)
chmod +x node_modules/.bin/react-scripts
xattr -rd com.apple.quarantine node_modules

# 3. Start the React development server
npm start
```
*The frontend will automatically open in your browser at **http://localhost:3000**.*

---

## 📁 Project Structure

```
multimodal_emotion_detection/
│
├── backend/                  # Python FastAPI Backend
│   ├── modules/              # Core logic (context_builder, emoji_utils, image_utils)
│   ├── venv/                 # Python Virtual Environment
│   ├── main.py               # API Entry Point
│   ├── pipeline.py           # Orchestration Pipeline
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment Variables (Keep secure!)
│
├── frontend/                 # React.js Frontend
│   ├── public/               
│   ├── src/                  
│   │   ├── components/       # UI Components (InputForm, ResultCard)
│   │   ├── App.js            # Main React App
│   │   └── App.css           # Global Styles
│   └── package.json          # Node dependencies
│
├── report.tex                # Academic Project Report (LaTeX)
├── Presentation.pptx         # Project Presentation
├── PROJECT_REPORT.md         # Markdown version of the report
└── PROJECT_TECH_SUMMARY.md   # Tech Stack overview
```

## 🧠 Technologies Used
* **Frontend**: React.js, Vanilla CSS
* **Backend**: Python, FastAPI, Uvicorn
* **AI Models**: LLaMA 3.3 70B (via Groq API), BLIP Image Captioning (Hugging Face)
