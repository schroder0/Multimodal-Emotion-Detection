# Multimodal Emotion Detection: Project Overview

This document explains the entire technology stack, the exact pipeline flow, and how the different pieces of this project fit together. 

## Technology Stack
The project is split into a React frontend and a Python FastAPI backend.

### Frontend
- **React.js**: The core framework used to build the user interface.
- **Axios**: Used to make HTTP POST requests from the React frontend to the Python backend.
- **Vanilla CSS**: Custom styling with a dark navy theme (no external CSS frameworks like Tailwind are used).

### Backend
- **FastAPI**: The Python web framework serving the API endpoints. Selected for its high performance and built-in asynchronous support.
- **Uvicorn**: The ASGI server used to run the FastAPI application.
- **Groq API**: The cloud service used to run the large language model. It runs models much faster than traditional GPUs.
- **LLaMA 3.3 70B (via Groq)**: The specific Large Language Model used to perform the complex "chain-of-thought" emotional reasoning.
- **Transformers (Hugging Face)**: Used specifically for the BLIP model (Bootstrapped Language-Image Pre-training) to analyze images.
- **Pillow (PIL)**: Used for loading and processing images before they are passed to the AI models.

---

## Overall Pipeline Flow

When a user types text (with emojis) and uploads an image in the frontend, here is the exact step-by-step flow of what happens under the hood:

### 1. The Request (Frontend → Backend)
The React app (`InputForm.js`) packages the text string and the image file into a `FormData` object and sends it via an HTTP POST request to the backend's `/analyze` endpoint.

### 2. Data Extraction (`pipeline.py`)
The backend receives the data and immediately separates the processing into three distinct modalities:

*   **Text & Emojis (`emoji_utils.py`)**: 
    *   It scans the text for any emojis. 
    *   If found, it looks them up in a dictionary (e.g., `😊` = "smiling face with smiling eyes, warmth, happiness"). 
    *   It separates the raw text from the emojis, creating two clean data sources: pure text, and a list of emoji meanings.
*   **Images (`image_utils.py`)**: 
    *   If an image was uploaded, it is passed through the **BLIP** vision model.
    *   BLIP generates a text caption describing what is in the image (e.g., "A person sitting alone in a dark room").
    *   The caption is scanned for emotional keywords (e.g., "dark", "alone" = sadness).

### 3. Context Assembly (`context_builder.py`)
The system takes the three outputs (Clean Text, Emoji Meanings, Image Caption) and combines them into one structured JSON string. It also does a quick "sentiment pre-assessment" to give the LLM a hint if strongly positive or negative words are present.

### 4. Chain-of-Thought Reasoning (`llm_reasoning.py`)
This is the core "brain" of the project. The structured context is sent to the **LLaMA 3.3 70B model via Groq**. The model is prompted with strict instructions to perform "Chain-of-Thought" reasoning:
1.  **Step 1:** Analyze the text alone.
2.  **Step 2:** Analyze the emojis alone.
3.  **Step 3:** Analyze the image caption alone.
4.  **Step 4:** Resolve any conflicts (e.g., if the text says "I'm fine" but the image shows someone crying, the model must deduce that the person is hiding their sadness).
5.  **Step 5:** Determine the final emotion and assign a confidence score.

*(Note: If the Groq API fails or the key is missing, the system automatically falls back to a basic keyword-counting heuristic method).*

### 5. The Response (Backend → Frontend)
The backend takes the LLM's final JSON output (which includes the detected emotion, the confidence percentage, and the full step-by-step reasoning) and sends it back to the React app.

### 6. UI Update (`ResultCard.js`)
The React app receives the response and updates the UI. The result card animates in, showing the dominant emotion color, the exact confidence score, and the collapsible step-by-step reasoning details. The result is also saved to the "Analysis History" panel.
