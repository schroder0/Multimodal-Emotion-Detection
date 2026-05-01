"""
FastAPI Server for Multimodal Emotion Detection
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64

from pipeline import EmotionDetectionPipeline

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multimodal Emotion Detection API",
    description="Detects emotions from text, emojis, and images using LLM reasoning",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
DEVICE = os.getenv("DEVICE", "cpu")
USE_LLM = os.getenv("USE_LLM", "true").lower() == "true"

try:
    pipeline = EmotionDetectionPipeline(device=DEVICE, use_llm=USE_LLM)
    logger.info(f"Pipeline initialized successfully. Device: {DEVICE}, UseLLM: {USE_LLM}")
except Exception as e:
    logger.error(f"Error initializing pipeline: {e}")
    pipeline = None

@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "message": "Multimodal Emotion Detection API",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    if pipeline is None:
        return {
            "status": "unhealthy",
            "message": "Pipeline not initialized"
        }, 503
    
    return {
        "status": "healthy",
        "device": DEVICE,
        "use_llm": USE_LLM
    }

@app.post("/analyze")
async def analyze_emotion(
    text: str = Form(""),
    image: UploadFile = File(None)
):
    """
    Analyze emotion from multimodal input
    
    Args:
        text: Input text (may contain emojis)
        image: Optional image file
    
    Returns:
        JSON with emotion, reasoning, and confidence
    """
    
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        # Validate input
        if not text and image is None:
            raise HTTPException(status_code=400, detail="Please provide text or an image")
        
        logger.info(f"Received analysis request. Text length: {len(text)}, Image: {image is not None}")
        
        # Process image if provided
        image_data = None
        if image:
            try:
                contents = await image.read()
                image_data = Image.open(io.BytesIO(contents)).convert("RGB")
                logger.info(f"Image processed: {image_data.size}")
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
        
        # Run analysis pipeline
        result = pipeline.analyze(text=text, image=image_data)
        
        return JSONResponse(status_code=200, content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-base64")
async def analyze_emotion_base64(
    data: dict
):
    """
    Analyze emotion from multimodal input with base64 encoded image
    
    Args:
        data: JSON with 'text' and optional 'image' (base64 encoded)
    
    Returns:
        JSON with emotion, reasoning, and confidence
    """
    
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        text = data.get("text", "")
        image_base64 = data.get("image", None)
        
        if not text and not image_base64:
            raise HTTPException(status_code=400, detail="Please provide text or an image")
        
        logger.info(f"Received base64 analysis request. Text length: {len(text)}, Image: {image_base64 is not None}")
        
        # Process image if provided
        image_data = None
        if image_base64:
            try:
                image_bytes = base64.b64decode(image_base64)
                image_data = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                logger.info(f"Image processed: {image_data.size}")
            except Exception as e:
                logger.error(f"Error processing base64 image: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
        
        # Run analysis pipeline
        result = pipeline.analyze(text=text, image=image_data)
        
        return JSONResponse(status_code=200, content=result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/examples")
async def get_examples():
    """Get example emotion detections"""
    return {
        "examples": [
            {
                "input": {
                    "text": "I'm fine 🙂",
                    "image_description": "person sitting alone in dark room"
                },
                "expected_output": {
                    "emotion": "sadness",
                    "reason": "Text appears neutral but emoji suggests masking emotions. Image shows loneliness."
                }
            },
            {
                "input": {
                    "text": "Just got promoted! 🎉",
                    "image_description": "person at office with colleagues"
                },
                "expected_output": {
                    "emotion": "happiness",
                    "reason": "Text and emoji both indicate celebration. Image shows social context supporting joy."
                }
            },
            {
                "input": {
                    "text": "This is so frustrating 😤",
                    "image_description": "person throwing objects"
                },
                "expected_output": {
                    "emotion": "anger",
                    "reason": "Text, emoji, and image all consistently show anger."
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
