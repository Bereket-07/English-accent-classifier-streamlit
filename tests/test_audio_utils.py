# tests/test_audio_utils.py
import os
import pytest
from utils.audio_utils import extract_audio

# You must create a small video file at tests/fixtures/sample_video.mp4 for this test
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
SAMPLE_VIDEO_PATH = os.path.join(FIXTURE_DIR, 'sample_video.mp4') 

@pytest.fixture
def temp_output_path(tmpdir):
    return os.path.join(str(tmpdir), "output.wav")

@pytest.mark.skipif(not os.path.exists(SAMPLE_VIDEO_PATH), reason="Sample video fixture not found")
def test_extract_audio_success(temp_output_path):
    """Test successful audio extraction."""
    result_path = extract_audio(SAMPLE_VIDEO_PATH, temp_output_path)
    
    assert result_path is not None
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0

def test_extract_audio_file_not_found(temp_output_path):
    """Test audio extraction with a non-existent video file."""
    result_path = extract_audio("non_existent_video.mp4", temp_output_path)
    
    assert result_path is None
    assert not os.path.exists(temp_output_path)