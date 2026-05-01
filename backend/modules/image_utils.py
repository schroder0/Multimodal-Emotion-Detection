"""
Image Processing Module
Handles image caption generation and emotion inference from images
"""

import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import io
import base64
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Process images using BLIP model for captioning"""
    
    def __init__(self, device="cpu"):
        """Initialize BLIP model for image captioning"""
        self.device = device
        try:
            # Load BLIP processor and model
            self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.model = BlipForConditionalGeneration.from_pretrained(
                "Salesforce/blip-image-captioning-base"
            ).to(device)
            self.model.eval()
            logger.info(f"BLIP model loaded on device: {device}")
        except Exception as e:
            logger.error(f"Error loading BLIP model: {e}")
            self.processor = None
            self.model = None
    
    def generate_caption(self, image_input, max_length=50):
        """
        Generate a caption for an image
        Args:
            image_input: PIL Image object or file path
            max_length: maximum caption length
        Returns:
            str: Generated caption
        """
        try:
            if isinstance(image_input, str):
                image = Image.open(image_input).convert("RGB")
            else:
                if not isinstance(image_input, Image.Image):
                    # Try to convert from bytes
                    image = Image.open(io.BytesIO(image_input)).convert("RGB")
                else:
                    image = image_input.convert("RGB")
            
            if self.model is None or self.processor is None:
                logger.warning("Model not available, returning placeholder")
                return "Image uploaded successfully"
            
            # Process image and generate caption
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=max_length)
            
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return "Unable to process image"
    
    def get_image_emotions(self, caption):
        """
        Extract emotional cues from image caption
        Returns: dict with detected emotions and context
        """
        emotion_keywords = {
            "joy": ["smile", "laugh", "happy", "joy", "celebrate", "celebrate", "fun", "play"],
            "sadness": ["sad", "cry", "tears", "grief", "mourn", "alone", "lonely", "dark"],
            "anger": ["angry", "rage", "fight", "argue", "intense", "aggressive"],
            "fear": ["scared", "fear", "frightened", "horror", "danger"],
            "disgust": ["disgusted", "gross", "nasty", "filthy", "revolted"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "unexpected"],
            "neutral": ["sitting", "standing", "looking", "person", "people", "scene"],
        }
        
        caption_lower = caption.lower()
        detected_emotions = []
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in caption_lower:
                    detected_emotions.append(emotion)
                    break
        
        return {
            "caption": caption,
            "detected_emotions": list(set(detected_emotions)) if detected_emotions else ["neutral"],
            "emotion_context": f"Image shows: {caption}"
        }

def process_image(image_input, device="cpu"):
    """
    Convenience function to process a single image
    Args:
        image_input: PIL Image, file path, or bytes
        device: torch device
    Returns:
        dict with caption and emotion information
    """
    processor = ImageProcessor(device=device)
    caption = processor.generate_caption(image_input)
    emotions = processor.get_image_emotions(caption)
    
    return {
        "caption": caption,
        **emotions
    }

def decode_base64_image(base64_string):
    """
    Decode base64 string to PIL Image
    Args:
        base64_string: base64 encoded image
    Returns:
        PIL Image object
    """
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        return image
    except Exception as e:
        logger.error(f"Error decoding base64 image: {e}")
        return None

def encode_image_to_base64(image_input):
    """
    Encode image to base64 string
    Args:
        image_input: PIL Image or file path
    Returns:
        base64 encoded string
    """
    try:
        if isinstance(image_input, str):
            with open(image_input, "rb") as f:
                image_data = f.read()
        elif isinstance(image_input, Image.Image):
            buffer = io.BytesIO()
            image_input.save(buffer, format="PNG")
            image_data = buffer.getvalue()
        else:
            image_data = image_input
        
        return base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        return None
