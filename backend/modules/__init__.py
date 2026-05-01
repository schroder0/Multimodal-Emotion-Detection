"""
Modules package for multimodal emotion detection
"""

from .emoji_utils import build_emoji_context, extract_emojis, convert_emojis_to_meaning
from .image_utils import ImageProcessor, process_image, decode_base64_image
from .context_builder import build_multimodal_context, format_context_for_llm
from .llm_reasoning import EmotionReasoner

__all__ = [
    'build_emoji_context',
    'extract_emojis',
    'convert_emojis_to_meaning',
    'ImageProcessor',
    'process_image',
    'decode_base64_image',
    'build_multimodal_context',
    'format_context_for_llm',
    'EmotionReasoner',
]
