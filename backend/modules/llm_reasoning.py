"""
LLM Reasoning Module
Uses structured prompting to perform chain-of-thought emotion reasoning via Groq
"""

import os
import json
import logging
from groq import Groq
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()  # Load environment variables from .env file
logger = logging.getLogger(__name__)

class EmotionReasoner:
    """
    Performs structured reasoning for emotion detection using Groq LLMs
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize emotion reasoner
        
        Args:
            api_key: Groq API key (if not provided, uses GROQ_API_KEY env var)
            model: Groq LLM model to use (default: llama-3.3-70b-versatile for best reasoning)
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        
        # Initialize the Groq client
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("GROQ_API_KEY not found. Reasoner will fall back to heuristic analysis.")
        
        logger.info(f"EmotionReasoner initialized with model: {model}")
    
    def create_reasoning_prompt(self, context_string: str) -> str:
        """
        Create a structured prompt for chain-of-thought reasoning
        
        Args:
            context_string: Formatted multimodal context
        
        Returns:
            str: Complete prompt for LLM
        """
        
        prompt = f"""You are an expert emotional intelligence analyst with deep understanding of human emotions. 
Your task is to detect the TRUE emotion expressed through multiple modalities (text, emojis, and images) using step-by-step reasoning.

CRITICAL RULES:
- Do NOT default to "neutral" unless there is genuinely NO emotional signal at all.
- Positive statements like "he is the best", "I love this", "brought me flowers" are CLEARLY happiness or love — never classify these as neutral.
- Negative statements like "I hate this", "so frustrating", "terrible day" are CLEARLY anger or sadness — never classify these as neutral.
- Only use "neutral" for truly emotionless factual statements like "the sky is blue" or "it is 3pm".
- When text has clear emotional words (best, love, hate, awful, amazing, wonderful, terrible, etc.), the emotion is NOT neutral.

{context_string}

ANALYSIS INSTRUCTIONS:
Follow these steps EXACTLY:

STEP 1: TEXT EMOTION ANALYSIS
- Identify emotional keywords and phrases in the text
- Determine the dominant sentiment (positive, negative, or truly neutral)
- Consider tone, context, and implied meaning
- If someone says something positive about a person/thing, that indicates happiness/love/gratitude

STEP 2: EMOJI EMOTION ANALYSIS  
- For each emoji present, identify the emotion it conveys
- Note if emojis contradict the text (potential emotion masking)
- Consider emoji combinations and their collective meaning
- If no emojis are present, state that and rely more on text

STEP 3: IMAGE EMOTION ANALYSIS
- Analyze the scene, mood, and emotional cues in the image
- Consider body language, facial expressions, setting, colors
- If no image is provided, state that and rely on text/emoji signals

STEP 4: MULTIMODAL RESOLUTION
- Compare emotional signals across all available modalities
- Identify any conflicts between modalities
- When modalities agree, increase confidence
- When they conflict, consider which is most reliable (images > text > emoji for masking)
- Determine the single strongest emotional signal

STEP 5: CONFIDENCE ASSESSMENT
- Rate confidence from 0.0 to 1.0
- High confidence (0.8-1.0): All modalities agree, or text has strong clear emotional language
- Medium confidence (0.5-0.79): Some ambiguity or missing modalities
- Low confidence (0.3-0.49): Contradicting signals or very vague input

VALID EMOTIONS: happiness, sadness, anger, fear, surprise, disgust, love, neutral

OUTPUT FORMAT (respond with valid JSON only):
{{
    "step_1_text_analysis": "Your detailed text analysis",
    "step_2_emoji_analysis": "Your emoji analysis (or 'No emojis present')", 
    "step_3_image_analysis": "Your image analysis (or 'No image provided')",
    "step_4_resolution": "How you resolved signals across modalities",
    "step_5_confidence": "Your confidence reasoning",
    "final_emotion": "ONE of: happiness, sadness, anger, fear, surprise, disgust, love, neutral",
    "confidence_score": 0.85,
    "explanation": "A concise 1-2 sentence explanation of why this emotion was detected"
}}

Remember: Output ONLY valid JSON. Choose exactly ONE emotion for 'final_emotion'. Do NOT default to neutral when clear emotional signals exist.
"""
        return prompt.strip()
    
    def reason_about_emotion(self, context_string: str) -> Dict:
        """
        Use LLM to reason about emotion with chain-of-thought
        
        Args:
            context_string: Formatted multimodal context
        
        Returns:
            dict: LLM reasoning result
        """
        
        if not self.client:
            logger.error("Groq API key not set. Using fallback reasoning.")
            return self._fallback_reasoning(context_string)
        
        try:
            prompt = self.create_reasoning_prompt(context_string)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are an expert emotional intelligence analyst. "
                            "You detect emotions accurately from text, emojis, and images. "
                            "You NEVER default to 'neutral' when clear emotional signals exist. "
                            "Positive words like 'best', 'love', 'amazing', 'wonderful' indicate happiness or love. "
                            "Negative words like 'hate', 'terrible', 'angry', 'sad' indicate negative emotions. "
                            "Always respond with valid JSON."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"} 
            )
            
            response_text = response.choices[0].message.content
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                result = self._extract_json_from_response(response_text)
            
            # Validate the result has required fields
            result = self._validate_result(result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return self._fallback_reasoning(context_string)
    
    def _validate_result(self, result: Dict) -> Dict:
        """
        Validate and clean up the LLM result
        
        Args:
            result: Raw LLM result dict
        
        Returns:
            dict: Validated result with all required fields
        """
        valid_emotions = {"happiness", "sadness", "anger", "fear", "surprise", "disgust", "love", "neutral", "uncertain"}
        
        # Normalize the final_emotion field
        emotion = result.get("final_emotion", "uncertain").lower().strip()
        if emotion not in valid_emotions:
            # Try to map common variations
            emotion_map = {
                "happy": "happiness", "sad": "sadness", "angry": "anger",
                "scared": "fear", "afraid": "fear", "surprised": "surprise",
                "disgusted": "disgust", "loving": "love", "affection": "love",
                "joy": "happiness", "rage": "anger", "grief": "sadness",
                "excitement": "happiness", "grateful": "happiness", "gratitude": "happiness"
            }
            emotion = emotion_map.get(emotion, "uncertain")
        
        result["final_emotion"] = emotion
        
        # Ensure confidence is a valid float
        try:
            confidence = float(result.get("confidence_score", 0.5))
            result["confidence_score"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            result["confidence_score"] = 0.5
        
        # Ensure all step fields exist
        for key in ["step_1_text_analysis", "step_2_emoji_analysis", "step_3_image_analysis", 
                     "step_4_resolution", "step_5_confidence", "explanation"]:
            if key not in result:
                result[key] = ""
        
        return result
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """
        Try to extract JSON from LLM response if it's not pure JSON
        """
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            try:
                json_str = response_text[start_idx:end_idx+1]
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        return {
            "final_emotion": "uncertain",
            "confidence_score": 0.5,
            "explanation": response_text,
            "step_1_text_analysis": "Unable to parse structured response",
            "step_2_emoji_analysis": "Unable to parse structured response",
            "step_3_image_analysis": "Unable to parse structured response",
            "step_4_resolution": "Unable to parse structured response",
            "step_5_confidence": "Unable to parse structured response"
        }
    
    def _fallback_reasoning(self, context_string: str) -> Dict:
        """
        Fallback reasoning when API is unavailable
        Uses improved keyword-based emotion detection
        """
        logger.info("Using fallback heuristic reasoning")
        
        context_lower = context_string.lower()
        
        emotion_keywords = {
            "happiness": [
                "happy", "joy", "smile", "laugh", "celebrate", "fun", "great", "love",
                "wonderful", "amazing", "awesome", "best", "excellent", "fantastic",
                "beautiful", "brilliant", "delighted", "excited", "thrilled", "glad",
                "pleased", "grateful", "thankful", "blessed", "cheerful", "proud",
                "flowers", "gift", "promoted", "won", "success", "achievement"
            ],
            "love": [
                "love", "adore", "cherish", "sweetheart", "darling", "heart",
                "romantic", "affection", "caring", "devoted", "passionate",
                "flowers", "kiss", "hug", "miss you", "forever", "soulmate"
            ],
            "sadness": [
                "sad", "cry", "tears", "grief", "alone", "lonely", "dark", "blue",
                "sorry", "depressed", "heartbroken", "miserable", "unhappy", "down",
                "lost", "empty", "hopeless", "pain", "suffering", "mourning"
            ],
            "anger": [
                "angry", "rage", "mad", "furious", "hate", "upset", "annoyed",
                "frustrated", "irritated", "livid", "outraged", "disgusted",
                "terrible", "worst", "stupid", "idiot", "unfair", "betrayed"
            ],
            "fear": [
                "scared", "fear", "frightened", "anxiety", "nervous", "worry",
                "terrified", "panic", "dread", "horror", "alarmed", "uneasy",
                "afraid", "phobia", "danger", "threat", "creepy"
            ],
            "surprise": [
                "surprised", "shocked", "amazed", "wow", "unexpected",
                "astonished", "stunned", "bewildered", "unbelievable",
                "incredible", "omg", "whoa", "no way", "really"
            ],
            "disgust": [
                "disgusted", "gross", "nasty", "yuck", "revolting",
                "sickening", "repulsive", "awful", "vile", "foul"
            ],
        }
        
        emotion_scores = {emotion: 0 for emotion in emotion_keywords}
        emotion_scores["neutral"] = 0
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                count = context_lower.count(keyword)
                if count > 0:
                    emotion_scores[emotion] += count * 1.5
        
        # If no emotion keywords found, it's neutral
        if sum(emotion_scores.values()) == 0:
            emotion_scores["neutral"] = 1
        
        final_emotion = max(emotion_scores, key=emotion_scores.get)
        max_score = emotion_scores[final_emotion]
        confidence = min(0.9, max(0.4, max_score / 5.0))
        
        return {
            "step_1_text_analysis": f"Keyword analysis of text content",
            "step_2_emoji_analysis": f"Emoji meanings extracted and analyzed",
            "step_3_image_analysis": f"Image emotions analyzed via captioning",
            "step_4_resolution": f"Combined all modality signals — strongest: {final_emotion}",
            "step_5_confidence": f"Confidence based on keyword match strength: {max_score:.1f}",
            "final_emotion": final_emotion,
            "confidence_score": confidence,
            "explanation": f"Detected {final_emotion} based on analysis of text, emojis, and image context."
        }


def create_structured_reasoning_request(multimodal_context: Dict) -> str:
    from .context_builder import format_context_for_llm
    
    context_string = format_context_for_llm(multimodal_context)
    reasoner = EmotionReasoner()
    return reasoner.create_reasoning_prompt(context_string)