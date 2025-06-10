# rem_accent_checker/app.py
import streamlit as st
import tempfile
import os
import pandas as pd
import re
from typing import Dict, Any, Optional
from utils.downloader import download_video
from utils.audio_utils import extract_audio
from utils.classifier import AccentClassifier
from utils.logger import get_logger

# Setup logger
logger = get_logger(__name__)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="English Accent Classifier",
    page_icon="🎙️",
    layout="centered"
)

# --- NEW: Helper function to normalize YouTube URLs ---
def get_clean_youtube_url(url: str) -> Optional[str]:
    """
    Takes various YouTube URL formats and returns a standard, embeddable URL.
    Handles:
    - youtu.be/VIDEO_ID
    - youtube.com/watch?v=VIDEO_ID
    - youtube.com/shorts/VIDEO_ID
    - And removes extra parameters like ?si=..., &t=...
    """
    # Regex to find the 11-character video ID from common YouTube URL patterns
    match = re.search(r"(?:v=|\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})", url)
    if match:
        video_id = match.group(1)
        # Return the standard, clean URL format
        return f"https://www.youtube.com/watch?v={video_id}"
    return None # Return None if no valid YouTube ID is found

# --- Model Caching ---
@st.cache_resource
def load_classifier():
    """Loads the accent classifier model, cached for performance."""
    try:
        classifier = AccentClassifier()
        return classifier
    except Exception as e:
        st.error(f"Fatal Error: Could not load the classification model. Please check logs. Error: {e}")
        return None

# --- Main Application UI ---
def main():
    """Main function to run the Streamlit app interface."""
    st.title("🎙️ English Accent Classifier")
    st.markdown("Enter a public video URL to analyze the speaker's English accent.")

    classifier = load_classifier()
    if not classifier:
        st.stop()

    if 'video_url' not in st.session_state:
        st.session_state.video_url = ""

    st.text_input(
        "Public Video URL",
        placeholder="e.g., https://www.youtube.com/watch?v=your_video_id",
        key="video_url",
        help="Paste a URL and see the video preview below."
    )

    # --- MODIFIED: Live Video Preview with URL Normalization ---
    if st.session_state.video_url:
        # First, try to clean it as a YouTube URL
        clean_url = get_clean_youtube_url(st.session_state.video_url)
        
        if clean_url:
            # If we got a clean YouTube URL, display it. This is the most reliable way.
            st.video(clean_url)
        else:
            # If it's not a recognizable YouTube URL, try to display it directly.
            # This will handle direct .mp4 links.
            try:
                st.video(st.session_state.video_url)
            except Exception:
                # Only show a warning if both attempts fail.
                st.warning("Could not display video preview. Please ensure it's a valid YouTube or direct video URL.")

    # The form now only contains the submit button
    with st.form(key="analysis_form"):
        submit_button = st.form_submit_button(label="Analyze Accent")

    if submit_button:
        if st.session_state.video_url:
            process_video(st.session_state.video_url, classifier)
        else:
            st.warning("Please enter a video URL first.")

#
# The rest of the file (process_video, display_results) remains exactly the same.
#
def process_video(url: str, classifier: AccentClassifier):
    # ... (No changes here)
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            st.info("Starting analysis...")
            progress_bar = st.progress(0.0)
            progress_text = st.empty()

            def streamlit_progress_hook(d: Dict[str, Any]):
                if d['status'] == 'downloading':
                    percent_str = d.get('_percent_str', '0.0%').strip().replace('%', '')
                    try:
                        progress_value = float(percent_str) / 100.0
                    except ValueError:
                        progress_value = 0.0
                        logger.warning(f"Could not parse percent string: {percent_str}")
                    
                    eta_str = d.get('_eta_str', 'N/A')
                    progress_bar.progress(progress_value)
                    progress_text.text(f"Step 1/3: Downloading... {progress_value:.0%} (ETA: {eta_str})")
                
                elif d['status'] == 'finished':
                    progress_bar.progress(1.0)
                    progress_text.text("✅ Download complete! Moving to next step...")

            video_path = download_video(
                url, temp_dir, progress_callback=streamlit_progress_hook
            )
            
            progress_text.empty()
            progress_bar.empty()

            if not video_path:
                st.error("Could not download the video. Please check if the URL is public and valid.")
                return
            
            with st.spinner("Step 2/3: Extracting audio..."):
                audio_filename = f"{os.path.basename(video_path)}.wav"
                audio_path = extract_audio(video_path, os.path.join(temp_dir, audio_filename))
            if not audio_path:
                st.error("Failed to extract audio. The video might not have an audio track.")
                return

            with st.spinner("Step 3/3: Analyzing accent..."):
                results = classifier.classify_audio(audio_path, top_k=5)
            if not results:
                st.warning("Could not classify accent. Audio may be too short or silent.")
                return
            
            display_results(results)

    except Exception as e:
        logger.error(f"An unexpected error occurred in the processing pipeline: {e}")
        st.error("An unexpected error occurred. Please try a different video.")

def display_results(results: list):
    # ... (No changes here)
    st.success("Analysis Complete!")
    top_result = results[0]
    st.metric(label="Predicted Accent", value=top_result["label"])
    st.progress(top_result["score"])
    st.write(f"Confidence: {top_result['score']:.2%}")
    st.subheader("Top Predictions")
    chart_data = pd.DataFrame(results).rename(columns={"label": "Accent", "score": "Confidence"})
    chart_data['Confidence'] *= 100
    st.bar_chart(chart_data.set_index('Accent'))
    with st.expander("How does this work?"):
        st.markdown(...) # Same explanation as before

if __name__ == "__main__":
    main()