"""
Emoji Processing Module
Converts emojis to textual representations for context building
"""

import re
import emoji

# Mapping of common emojis to emotional meanings (deduplicated and expanded)
EMOJI_MEANING_MAP = {
    # Happiness / Joy
    "😀": "broad grin, happiness, cheerfulness",
    "😁": "beaming face with smiling eyes, joy",
    "😂": "face with tears of joy, laughter",
    "🤣": "rolling on the floor laughing, extreme amusement",
    "😃": "grinning face with big eyes, happiness",
    "😄": "grinning face with smiling eyes, happiness",
    "😅": "grinning face with sweat, nervous happiness, relief",
    "😆": "grinning squinting face, joy, amusement",
    "😉": "winking face, playfulness, flirtation",
    "😊": "smiling face with smiling eyes, warmth, happiness",
    "😇": "smiling face with halo, innocence, angelic behavior",
    "🙂": "slightly smiling face, polite smile, possibly masking emotions",
    "😋": "face savoring food, enjoyment, satisfaction",
    
    # Love / Affection
    "😍": "heart eyes, love, adoration",
    "🥰": "smiling face with hearts, love, affection",
    "😘": "face blowing a kiss, affection, goodbye",
    "😗": "kissing face, affection",
    "😚": "kissing face with closed eyes, affection",
    "😙": "kissing face with smiling eyes, affection",
    "🥲": "smiling face with tear, bittersweet, touched",
    
    # Playful / Silly
    "😛": "tongue out face, playfulness, goofiness",
    "😜": "winking face with tongue, playfulness, silliness",
    "🤪": "zany face, craziness, silliness",
    "🙃": "upside down face, sarcasm, irony, hidden frustration",
    
    # Sadness
    "😔": "pensive face, sadness, disappointment",
    "😟": "worried face, anxiety, concern",
    "😕": "confused face, confusion, uncertainty",
    "🙁": "slightly frowning face, sadness, disappointment",
    "☹️": "frowning face, sadness, displeasure",
    "😲": "astonished face, shock, surprise",
    "😞": "disappointed face, sadness, sorrow",
    "😖": "confounded face, pain, distress",
    "😢": "crying face, sadness, sorrow",
    "😭": "loudly crying face, deep sadness, grief",
    "🥺": "pleading face, begging, sadness, puppy eyes",
    
    # Anger / Frustration
    "😤": "face with steam from nose, frustration, anger",
    "😠": "angry face, anger, rage",
    "😡": "pouting face, anger, fury",
    "🤬": "face with symbols on mouth, anger, swearing",
    "😒": "unamused face, disapproval, skepticism",
    
    # Fear / Surprise
    "😨": "fearful face, fear, shock",
    "😰": "anxious face with sweat, anxiety, fear",
    "😱": "screaming face, horror, extreme fear",
    "😳": "flushed face, embarrassment, shock",
    "🤯": "exploding head, shock, mind blown",
    
    # Disgust / Evil
    "😈": "smiling face with horns, mischief, evil",
    "👿": "angry face with horns, anger, malice",
    "💀": "skull, death, extreme reaction",
    "☠️": "skull and crossbones, danger",
    "💩": "pile of poo, disgust",
    "🤮": "face vomiting, disgust, nausea",
    "🤢": "nauseated face, sickness, disgust",
    
    # Neutral / Calm
    "😌": "relieved face, peace, contentment",
    "😐": "neutral face, no emotion, indifference",
    "😑": "expressionless face, annoyance, indifference",
    "🫤": "face with diagonal mouth, skepticism, uncertainty",
    
    # Awkward / Secret
    "😬": "grimacing face, awkwardness, discomfort",
    "🤐": "zipper-mouth face, secrecy, silence",
    "🤭": "face with hand over mouth, surprise, laughter",
    "🫢": "face with open eyes and hand over mouth, shock",
    "🤫": "shushing face, quiet, secrecy",
    "🤥": "lying face, dishonesty, deception",
    "😏": "smirking face, smugness, flirtation, sarcasm",
    
    # Tired / Sick
    "😪": "sleepy face, tiredness, boredom",
    "🤤": "drooling face, desire, anticipation",
    "😴": "sleeping face, tiredness, boredom",
    "😷": "face with medical mask, sickness, caution",
    "🤒": "face with thermometer, sickness",
    "🤕": "face with head-bandage, injury, pain",
    "🤧": "sneezing face, sickness, allergy",
    "🥵": "hot face, overheating, embarrassment",
    "🥶": "cold face, freezing, shock",
    "🥴": "woozy face, confusion, dizziness",
    "😵": "dizzy face, confusion, overwhelm",
    "🫠": "melting face, embarrassment, sarcasm, exhaustion",
    
    # Cool / Confident
    "🤠": "cowboy hat face, confidence, coolness",
    "🥳": "partying face, celebration, joy",
    "😎": "smiling face with sunglasses, coolness, confidence",
    "🤓": "nerd face, intelligence, awkwardness",
    "🧐": "face with monocle, skepticism, judgment",
    "🤔": "thinking face, contemplation, uncertainty",
    
    # Hearts
    "❤️": "red heart, love, passion",
    "🧡": "orange heart, warmth, care",
    "💛": "yellow heart, joy, friendship",
    "💚": "green heart, nature, growth, hope",
    "💙": "blue heart, sadness, calmness, loyalty",
    "💜": "purple heart, admiration, magic",
    "🖤": "black heart, darkness, sorrow, mischief",
    "🤍": "white heart, purity, peace",
    "🤎": "brown heart, warmth, earth",
    "💔": "broken heart, heartbreak, sadness",
    "💕": "two hearts, love, affection",
    "💞": "revolving hearts, love, mutual affection",
    "💓": "beating heart, strong emotion, passion",
    "💗": "growing heart, love, increasing affection",
    "💖": "sparkling heart, love, magic",
    "💘": "heart with arrow, love, cupid",
    "💝": "heart with ribbon, love, gift",
    "💟": "heart decoration, love, affection",
    "❤️‍🔥": "heart on fire, passionate love, intense desire",
    "❤️‍🩹": "mending heart, healing, recovery from heartbreak",
    
    # Gestures
    "👍": "thumbs up, approval, agreement",
    "👎": "thumbs down, disapproval, disagreement",
    "👏": "clapping hands, approval, celebration",
    "🙌": "raising hands, celebration, victory",
    "👋": "waving hand, goodbye, greeting",
    "🤝": "handshake, agreement, partnership",
    "🤲": "open hands, offering, openness",
    "🤟": "love you gesture, affection, friendship",
    "🙏": "folded hands, prayer, gratitude, please",
    "💪": "flexed biceps, strength, determination",
    
    # Celebration / Objects
    "🎉": "party popper, celebration, excitement, joy",
    "🎊": "confetti ball, celebration, festivity",
    "🎂": "birthday cake, celebration, happiness",
    "🌹": "rose, romance, love, beauty",
    "💐": "bouquet, romance, congratulations, love",
    "🔥": "fire, excitement, attraction, intensity",
    "⭐": "star, excellence, admiration",
    "🌟": "glowing star, excellence, magic",
    "✨": "sparkles, magic, excitement, positive",
    "💯": "hundred points, perfect, agreement, emphasis",
}

def extract_emojis(text):
    """
    Extract all emojis from text
    Returns: list of emoji characters
    """
    emoji_list = []
    for char in text:
        if char in emoji.EMOJI_DATA:
            emoji_list.append(char)
    return emoji_list

def convert_emojis_to_meaning(text):
    """
    Convert emojis in text to their emotional meanings
    Returns: text with emoji meanings inserted and cleaned text
    """
    emojis_found = extract_emojis(text)
    emoji_meanings = []
    
    for em in emojis_found:
        if em in EMOJI_MEANING_MAP:
            emoji_meanings.append(f"{em}: {EMOJI_MEANING_MAP[em]}")
        else:
            # Fallback for unknown emojis
            try:
                meaning = emoji.demojize(em).replace(":", " ").strip()
                emoji_meanings.append(f"{em}: {meaning}")
            except:
                emoji_meanings.append(f"{em}: unknown emoji")
    
    # Remove emojis from text to get clean text
    clean_text = ''.join(char for char in text if char not in emoji.EMOJI_DATA)
    
    return clean_text, emoji_meanings

def build_emoji_context(text):
    """
    Build structured emoji context from text
    Returns: dict with emoji information
    """
    clean_text, emoji_meanings = convert_emojis_to_meaning(text)
    
    context = {
        "original_text": text,
        "clean_text": clean_text.strip(),
        "emojis_found": len(emoji_meanings),
        "emoji_meanings": emoji_meanings,
        "emoji_context": " | ".join(emoji_meanings) if emoji_meanings else "No emojis found"
    }
    
    return context
