# tests/test_audio_utils.py
import os
import pytest
from utils.audio_utils import extract_audio

# Define the path to the fixtures directory
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
# Define the path to a sample video file you must create for this test
SAMPLE_VIDEO_PATH = os.path.join(FIXTURE_DIR, 'sample_video.mp4')

@pytest.fixture
def temp_output_path(tmpdir):
    """A pytest fixture to create a temporary output file path."""
    return os.path.join(str(tmpdir), "output.wav")

@pytest.mark.skipif(not os.path.exists(SAMPLE_VIDEO_PATH), reason="Sample video fixture not found at tests/fixtures/sample_video.mp4")
def test_extract_audio_success_integration(temp_output_path):
    """
    Integration test: verifies successful audio extraction from a real video file.
    """
    result_path = extract_audio(SAMPLE_VIDEO_PATH, temp_output_path)
    
    assert result_path is not None
    assert result_path == temp_output_path
    assert os.path.exists(result_path)
    # Check that the file is not empty
    assert os.path.getsize(result_path) > 0

def test_extract_audio_video_not_found(temp_output_path):
    """
    Test that the function returns None when the input video file does not exist.
    """
    non_existent_path = "/path/to/non_existent_video.mp4"
    result = extract_audio(non_existent_path, temp_output_path)
    
    assert result is None
    assert not os.path.exists(temp_output_path)

def test_extract_audio_no_audio_track(mocker, temp_output_path):
    """
    Test the scenario where the video file has no audio track by mocking moviepy.
    """
    # Mock the VideoFileClip class
    mock_clip_instance = MagicMock()
    # Simulate a clip with no audio
    mock_clip_instance.audio = None
    
    # Patch the class in the audio_utils module
    mocker.patch('utils.audio_utils.VideoFileClip', return_value=mock_clip_instance)
    
    # The video path must exist for the initial check, so we can use a dummy file
    dummy_video_path = "dummy.mp4"
    mocker.patch('os.path.exists', return_value=True) # Mock os.path.exists to pass the first check
    
    result = extract_audio(dummy_video_path, temp_output_path)
    
    # Assertions
    assert result is None
    mock_clip_instance.close.assert_called_once() # Ensure resources are released
    assert not os.path.exists(temp_output_path)

def test_extract_audio_exception_on_write(mocker, temp_output_path):
    """
    Test that the function handles exceptions during the audio writing process.
    """
    # Mock the audio clip's write_audiofile method to raise an exception
    mock_audio_clip = MagicMock()
    mock_audio_clip.write_audiofile.side_effect = IOError("Disk full")
    
    # Mock the main VideoFileClip to return our mocked audio clip
    mock_video_clip_instance = MagicMock()
    mock_video_clip_instance.audio = mock_audio_clip
    
    mocker.patch('utils.audio_utils.VideoFileClip', return_value=mock_video_clip_instance)
    mocker.patch('os.path.exists', return_value=True)
    
    result = extract_audio("dummy.mp4", temp_output_path)
    
    # Assertions
    assert result is None
    mock_video_clip_instance.close.assert_called_once() # Ensure parent clip is closed
    assert not os.path.exists(temp_output_path)