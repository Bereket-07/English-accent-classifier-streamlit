# rem_accent_checker/utils/downloader.py
import os
import sys
import yt_dlp
from typing import Optional, Callable, Dict, Any
from .logger import get_logger

logger = get_logger(__name__)

def download_video(
    url: str,
    output_dir: str,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
) -> Optional[str]:
    """
    Downloads a video from a public URL, with retries for network resilience.
    """
    if not url:
        logger.error("No URL provided.")
        return None

    def hook(d: Dict[str, Any]):
        if progress_callback:
            progress_callback(d)

    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': output_template,
        'quiet': True,
        'progress_hooks': [hook],
        'source_address': '0.0.0.0',
        'nocolor': True,
        # --- FINAL FIX: Add retries for network resilience ---
        # This tells yt-dlp to retry downloading a fragment 10 times if it fails.
        # This is essential for handling temporary network glitches like DNS errors.
        'fragment_retries': 10,
        'retries': 10,
    }

    try:
        logger.info(f"Attempting to download video from URL: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            logger.info(f"Successfully downloaded video to: {filename}")
            return filename
            
    except yt_dlp.utils.DownloadError as e:
        logger.warning(f"Could not download video. It may be private, unavailable, or a network issue occurred. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during download: {e}")
        return None

# Standalone testing block can remain the same
if __name__ == '__main__':
    # ...
    pass 