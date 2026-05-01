"""
Context Builder Module
Combines all modalities (text, emoji, image) into structured context for LLM reasoning
"""

import json

# Quick sentiment keywords for pre-assessment hint
POSITIVE_WORDS = {
    "love", "best", "great", "amazing", "wonderful", "happy", "joy", "excited",
    "beautiful", "fantastic", "awesome", "brilliant", "excellent", "perfect",
    "grateful", "thankful", "blessed", "proud", "delighted", "celebrate",
    "promotion", "flowers", "gift", "won", "success", "smile", "laugh"
}

NEGATIVE_WORDS = {
    "hate", "worst", "terrible", "awful", "sad", "angry", "frustrated",
    "depressed", "miserable", "lonely", "pain", "cry", "tears", "grief",
    "scared", "fear", "anxious", "nervous", "disgusted", "furious",
    "annoyed", "upset", "hurt", "broken", "lost", "hopeless", "betrayed"
}


def _quick_sentiment(text):
    """
    Quick sentiment pre-assessment based on keyword presence.
    Returns a hint string for the LLM.
    """
    words = set(text.lower().split())
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)
    
    if pos_count > 0 and neg_count == 0:
        return f"STRONG POSITIVE (matched {pos_count} positive keyword(s): {', '.join(words & POSITIVE_WORDS)})"
    elif neg_count > 0 and pos_count == 0:
        return f"STRONG NEGATIVE (matched {neg_count} negative keyword(s): {', '.join(words & NEGATIVE_WORDS)})"
    elif pos_count > 0 and neg_count > 0:
        return f"MIXED SIGNALS (positive: {', '.join(words & POSITIVE_WORDS)} | negative: {', '.join(words & NEGATIVE_WORDS)})"
    else:
        return "NO STRONG KEYWORDS DETECTED — rely on overall context and tone"


def build_multimodal_context(text_data, emoji_data, image_data=None):
    """
    Build comprehensive context from multiple modalities
    
    Args:
        text_data: dict with text information
        emoji_data: dict with emoji information
        image_data: dict with image information (optional)
    
    Returns:
        dict: Structured context for LLM
    """
    
    context = {
        "text_analysis": {
            "raw_text": text_data.get("original_text", ""),
            "clean_text": text_data.get("clean_text", ""),
            "length": len(text_data.get("clean_text", "")),
            "sentiment_hint": _quick_sentiment(text_data.get("clean_text", ""))
        },
        "emoji_analysis": {
            "count": emoji_data.get("emojis_found", 0),
            "meanings": emoji_data.get("emoji_meanings", []),
            "interpretation": emoji_data.get("emoji_context", "")
        }
    }
    
    if image_data:
        context["image_analysis"] = {
            "caption": image_data.get("caption", ""),
            "detected_emotions": image_data.get("detected_emotions", []),
            "interpretation": image_data.get("emotion_context", "")
        }
    else:
        context["image_analysis"] = {
            "caption": "No image provided",
            "detected_emotions": [],
            "interpretation": "No image data available"
        }
    
    return context

def format_context_for_llm(multimodal_context):
    """
    Format context into a readable string for LLM prompt
    
    Args:
        multimodal_context: dict with multimodal information
    
    Returns:
        str: Formatted context string
    """
    
    sentiment_hint = multimodal_context['text_analysis'].get('sentiment_hint', 'N/A')
    
    context_string = f"""
MULTIMODAL CONTEXT FOR EMOTION ANALYSIS:

1. TEXT ANALYSIS:
   - Raw text: "{multimodal_context['text_analysis']['raw_text']}"
   - Clean text (without emojis): "{multimodal_context['text_analysis']['clean_text']}"
   - Text length: {multimodal_context['text_analysis']['length']} characters
   - Quick sentiment pre-assessment: {sentiment_hint}

2. EMOJI ANALYSIS:
   - Number of emojis: {multimodal_context['emoji_analysis']['count']}
   - Emoji meanings: {', '.join(multimodal_context['emoji_analysis']['meanings']) if multimodal_context['emoji_analysis']['meanings'] else 'None'}
   - Interpretation: {multimodal_context['emoji_analysis']['interpretation']}

3. IMAGE ANALYSIS:
   - Image caption: "{multimodal_context['image_analysis']['caption']}"
   - Detected emotions in image: {', '.join(multimodal_context['image_analysis']['detected_emotions']) if multimodal_context['image_analysis']['detected_emotions'] else 'None'}
   - Interpretation: {multimodal_context['image_analysis']['interpretation']}

END OF CONTEXT
"""
    return context_string.strip()

def build_conflict_resolution_prompt(multimodal_context):
    """
    Build a prompt specifically for resolving conflicts between modalities
    
    Args:
        multimodal_context: dict with multimodal information
    
    Returns:
        str: Prompt for conflict resolution
    """
    
    prompt = f"""
You are analyzing emotions expressed through multiple modalities. Sometimes, these modalities conflict.

CONTEXT:
{format_context_for_llm(multimodal_context)}

TASK: Analyze potential conflicts between modalities:

1. Does the text emotion match the emoji emotion?
2. Does the text emotion match the image emotion?
3. Does the emoji emotion match the image emotion?
4. Which modality is likely most truthful? (Consider: is the emoji masking? Is the image context different?)

Based on this analysis, determine the most likely TRUE emotion.
"""
    return prompt.strip()

def create_analysis_summary(multimodal_context):
    """
    Create a summary of the multimodal analysis
    
    Args:
        multimodal_context: dict with multimodal information
    
    Returns:
        dict: Summary dictionary
    """
    
    text = multimodal_context['text_analysis']['clean_text']
    emojis = multimodal_context['emoji_analysis']['count']
    image_caption = multimodal_context['image_analysis']['caption']
    
    summary = {
        "has_text": bool(text),
        "has_emojis": emojis > 0,
        "has_image": image_caption != "No image provided",
        "text_present": text != "",
        "emoji_count": emojis,
        "image_emotions_detected": multimodal_context['image_analysis']['detected_emotions'],
        "multimodal_summary": {
            "text_info": f"Text: '{text[:100]}...'" if len(text) > 100 else f"Text: '{text}'",
            "emoji_info": f"{emojis} emoji(s) detected" if emojis > 0 else "No emojis",
            "image_info": f"Image shows: {image_caption}"
        }
    }
    
    return summary

def export_context_json(multimodal_context, filepath=None):
    """
    Export context as JSON for logging/debugging
    
    Args:
        multimodal_context: dict with multimodal information
        filepath: optional file path to save JSON
    
    Returns:
        str: JSON string
    """
    
    json_str = json.dumps(multimodal_context, indent=2)
    
    if filepath:
        try:
            with open(filepath, 'w') as f:
                f.write(json_str)
        except Exception as e:
            print(f"Error saving context to file: {e}")
    
    return json_str
