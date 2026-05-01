"""
Main Pipeline Module
Orchestrates the complete multimodal emotion detection pipeline
"""

import logging
from modules.emoji_utils import build_emoji_context
from modules.image_utils import ImageProcessor, decode_base64_image
from modules.context_builder import (
    build_multimodal_context,
    format_context_for_llm,
    create_analysis_summary
)
from modules.llm_reasoning import EmotionReasoner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDetectionPipeline:
    """
    Complete multimodal emotion detection pipeline
    """
    
    def __init__(self, device="cpu", use_llm=True):
        """
        Initialize the pipeline
        
        Args:
            device: torch device for image processing
            use_llm: whether to use LLM for reasoning
        """
        self.device = device
        self.use_llm = use_llm
        self.image_processor = ImageProcessor(device=device)
        self.emotion_reasoner = EmotionReasoner() if use_llm else None
        logger.info(f"Pipeline initialized with device: {device}, use_llm: {use_llm}")
    
    def analyze(self, text="", image=None):
        """
        Main pipeline method to analyze emotion from multimodal input
        
        Args:
            text: input text (may contain emojis)
            image: PIL Image object or base64 encoded string
        
        Returns:
            dict: Analysis result with emotion, reasoning, confidence
        """
        
        logger.info("Starting emotion analysis pipeline")
        
        # Step 1: Process text and extract emojis
        logger.info("Step 1: Processing text and emojis")
        emoji_data = build_emoji_context(text)
        text_data = {
            "original_text": text,
            "clean_text": emoji_data["clean_text"]
        }
        
        # Step 2: Process image if provided
        image_data = None
        if image is not None:
            logger.info("Step 2: Processing image")
            try:
                # Handle base64 encoded image
                if isinstance(image, str):
                    image = decode_base64_image(image)
                
                if image:
                    caption = self.image_processor.generate_caption(image)
                    image_data = self.image_processor.get_image_emotions(caption)
                else:
                    logger.warning("Failed to decode image")
                    image_data = {
                        "caption": "Unable to process image",
                        "detected_emotions": [],
                        "emotion_context": "Image processing failed"
                    }
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                image_data = {
                    "caption": "Error processing image",
                    "detected_emotions": [],
                    "emotion_context": f"Error: {str(e)}"
                }
        else:
            logger.info("No image provided")
            image_data = {
                "caption": "No image provided",
                "detected_emotions": [],
                "emotion_context": "No image data"
            }
        
        # Step 3: Build multimodal context
        logger.info("Step 3: Building multimodal context")
        multimodal_context = build_multimodal_context(text_data, emoji_data, image_data)
        context_string = format_context_for_llm(multimodal_context)
        
        # Step 4: LLM reasoning
        logger.info("Step 4: Performing LLM reasoning")
        if self.use_llm and self.emotion_reasoner:
            reasoning_result = self.emotion_reasoner.reason_about_emotion(context_string)
        else:
            reasoning_result = self._simple_heuristic_analysis(multimodal_context)
        
        # Step 5: Compile final result
        logger.info("Step 5: Compiling final result")
        final_result = {
            "emotion": reasoning_result.get("final_emotion", "uncertain"),
            "confidence": reasoning_result.get("confidence_score", 0.5),
            "reason": reasoning_result.get("explanation", "Unable to determine emotion"),
            "reasoning_details": {
                "text_analysis": reasoning_result.get("step_1_text_analysis", ""),
                "emoji_analysis": reasoning_result.get("step_2_emoji_analysis", ""),
                "image_analysis": reasoning_result.get("step_3_image_analysis", ""),
                "multimodal_resolution": reasoning_result.get("step_4_resolution", ""),
                "confidence_reasoning": reasoning_result.get("step_5_confidence", "")
            },
            "context_summary": create_analysis_summary(multimodal_context)
        }
        
        logger.info(f"Analysis complete. Emotion: {final_result['emotion']}, Confidence: {final_result['confidence']}")
        return final_result
    
    def _simple_heuristic_analysis(self, multimodal_context):
        """
        Improved heuristic analysis without LLM
        
        Args:
            multimodal_context: dict with multimodal information
        
        Returns:
            dict: Analysis result
        """
        
        text = multimodal_context['text_analysis']['clean_text'].lower()
        emojis = multimodal_context['emoji_analysis']['meanings']
        image_emotions = multimodal_context['image_analysis']['detected_emotions']
        
        # Expanded keyword matching
        emotion_keywords = {
            "happiness": [
                "happy", "great", "wonderful", "amazing", "awesome", "best",
                "excellent", "fantastic", "beautiful", "brilliant", "delighted",
                "excited", "thrilled", "glad", "pleased", "grateful", "thankful",
                "blessed", "cheerful", "proud", "celebrate", "promoted", "won",
                "success", "achievement", "perfect", "incredible"
            ],
            "love": [
                "love", "adore", "cherish", "sweetheart", "darling", "heart",
                "romantic", "affection", "caring", "devoted", "passionate",
                "flowers", "kiss", "hug", "miss", "forever", "soulmate",
                "brought flowers", "beautiful"
            ],
            "sadness": [
                "sad", "unhappy", "down", "depressed", "cry", "tears",
                "grief", "alone", "lonely", "miserable", "heartbroken",
                "lost", "empty", "hopeless", "pain", "suffering", "sorry"
            ],
            "anger": [
                "angry", "mad", "hate", "furious", "frustrated", "irritated",
                "livid", "outraged", "annoyed", "terrible", "worst", "stupid",
                "unfair", "betrayed", "rage"
            ],
            "fear": [
                "scared", "fear", "frightened", "anxiety", "nervous", "worry",
                "terrified", "panic", "dread", "horror", "afraid", "danger"
            ],
            "surprise": [
                "surprised", "shocked", "amazed", "wow", "unexpected",
                "astonished", "stunned", "unbelievable", "incredible", "omg"
            ],
            "disgust": [
                "disgusted", "gross", "nasty", "yuck", "revolting",
                "sickening", "repulsive", "awful", "vile"
            ],
        }
        
        emotion_scores = {emotion: 0 for emotion in emotion_keywords}
        emotion_scores["neutral"] = 0
        
        # Text analysis — check for keyword matches
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    emotion_scores[emotion] += 2
        
        # Image emotion analysis
        for img_emotion in image_emotions:
            if img_emotion in emotion_scores:
                emotion_scores[img_emotion] += 1.5
        
        # Emoji analysis
        for emoji_meaning in emojis:
            meaning_lower = emoji_meaning.lower()
            if any(w in meaning_lower for w in ["happy", "smile", "joy", "grin", "laugh", "celebration"]):
                emotion_scores["happiness"] += 1
            if any(w in meaning_lower for w in ["love", "heart", "kiss", "affection", "adoration"]):
                emotion_scores["love"] += 1
            if any(w in meaning_lower for w in ["sad", "tear", "cry", "grief", "disappointment"]):
                emotion_scores["sadness"] += 1
            if any(w in meaning_lower for w in ["anger", "rage", "fury", "frustration", "steam"]):
                emotion_scores["anger"] += 1
            if any(w in meaning_lower for w in ["fear", "scared", "frightened", "anxious"]):
                emotion_scores["fear"] += 1
            if any(w in meaning_lower for w in ["surprise", "shock", "astonish"]):
                emotion_scores["surprise"] += 1
            if any(w in meaning_lower for w in ["disgust", "vomit", "nausea"]):
                emotion_scores["disgust"] += 1
        
        # Determine final emotion
        total = sum(emotion_scores.values())
        if total == 0:
            emotion_scores["neutral"] = 1
        
        final_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[final_emotion]
        confidence = min(0.9, max(0.35, max_score / 5.0))
        
        return {
            "step_1_text_analysis": f"Analyzed text: '{text[:80]}{'...' if len(text) > 80 else ''}'",
            "step_2_emoji_analysis": f"Found {len(emojis)} emoji(s) with emotional signals",
            "step_3_image_analysis": f"Image emotions detected: {', '.join(image_emotions) if image_emotions else 'none'}",
            "step_4_resolution": f"Combined all modality signals — strongest emotion: {final_emotion}",
            "step_5_confidence": f"Confidence score: {confidence:.2f} (based on signal strength: {max_score:.1f})",
            "final_emotion": final_emotion,
            "confidence_score": confidence,
            "explanation": f"Detected {final_emotion} based on heuristic analysis of text, emojis, and image context."
        }
