# rem_accent_checker/utils/audio_utils.py
import os
from moviepy.editor import VideoFileClip
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)

def extract_audio(video_path: str, output_audio_path: str) -> Optional[str]:
    """
    Extracts audio from a video file and saves it as a WAV file.

    Args:
        video_path (str): The path to the input video file.
        output_audio_path (str): The path to save the output WAV file.

    Returns:
        Optional[str]: The path to the extracted audio file, or None on failure.
    """
    if not os.path.exists(video_path):
        logger.error(f"Video file not found at: {video_path}")
        return None
        
    try:
        logger.info(f"Extracting audio from {video_path}")
        video_clip = VideoFileClip(video_path)
        
        # Check if video has an audio track
        if video_clip.audio is None:
            logger.warning(f"The video at {video_path} has no audio track.")
            video_clip.close()
            return None
            
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_audio_path, codec='pcm_s16le', logger=None)
        
        video_clip.close()
        audio_clip.close()
        
        logger.info(f"Successfully extracted audio to: {output_audio_path}")
        return output_audio_path
    except Exception as e:
        logger.error(f"Failed to extract audio from {video_path}. Error: {e}")
        if 'video_clip' in locals() and video_clip:
            video_clip.close()
        return None