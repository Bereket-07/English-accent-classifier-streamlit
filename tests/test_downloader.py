# tests/test_downloader.py
import os
import pytest
from unittest.mock import patch, MagicMock
from utils.downloader import download_video

@pytest.fixture
def temp_dir(tmpdir):
    return str(tmpdir)

@patch('yt_dlp.YoutubeDL')
def test_download_video_success(mock_youtube_dl, temp_dir):
    """Test successful video download."""
    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {}
    mock_instance.prepare_filename.return_value = os.path.join(temp_dir, "video.mp4")
    mock_youtube_dl.return_value.__enter__.return_value = mock_instance
    
    url = "https://example.com/video.mp4"
    result_path = download_video(url, temp_dir)
    
    assert result_path is not None
    assert result_path.startswith(temp_dir)
    mock_instance.extract_info.assert_called_once_with(url, download=True)

@patch('yt_dlp.YoutubeDL')
def test_download_video_failure(mock_youtube_dl, temp_dir):
    """Test video download failure."""
    mock_instance = MagicMock()
    mock_instance.extract_info.side_effect = Exception("Download failed")
    mock_youtube_dl.return_value.__enter__.return_value = mock_instance
    
    url = "https://invalid.url/video.mp4"
    result_path = download_video(url, temp_dir)
    
    assert result_path is None

def test_download_no_url(temp_dir):
    """Test providing no URL."""
    result_path = download_video("", temp_dir)
    assert result_path is None