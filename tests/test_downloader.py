# tests/test_downloader.py
import os
import pytest
from unittest.mock import MagicMock, call
from yt_dlp.utils import DownloadError
from utils.downloader import download_video

@pytest.fixture
def temp_dir(tmpdir):
    """A pytest fixture to create a temporary directory for test artifacts."""
    return str(tmpdir)

def test_download_no_url(temp_dir):
    """
    Test that the function correctly handles being called with an empty or None URL.
    """
    assert download_video("", temp_dir) is None
    assert download_video(None, temp_dir) is None

def test_download_video_success(mocker, temp_dir):
    """
    Test the successful download scenario by mocking yt-dlp.
    """
    # Mock the yt-dlp YoutubeDL class
    mock_ydl_instance = MagicMock()
    # Configure the mock to simulate a successful download
    mock_ydl_instance.extract_info.return_value = {'title': 'test_video', 'ext': 'mp4'}
    mock_ydl_instance.prepare_filename.return_value = os.path.join(temp_dir, "test_video.mp4")

    # The `with` statement calls __enter__, so we mock that return value
    mock_ydl_context_manager = MagicMock()
    mock_ydl_context_manager.__enter__.return_value = mock_ydl_instance
    
    # Patch the class in the downloader module
    mocker.patch('utils.downloader.yt_dlp.YoutubeDL', return_value=mock_ydl_context_manager)

    url = "https://www.youtube.com/watch?v=test"
    result_path = download_video(url, temp_dir)

    # Assertions
    assert result_path == os.path.join(temp_dir, "test_video.mp4")
    mock_ydl_instance.extract_info.assert_called_once_with(url, download=True)

def test_download_video_failure_downloaderror(mocker, temp_dir):
    """
    Test the download failure scenario where yt-dlp raises a DownloadError.
    """
    mock_ydl_instance = MagicMock()
    # Configure the mock to simulate a failure
    mock_ydl_instance.extract_info.side_effect = DownloadError("Video unavailable")

    mock_ydl_context_manager = MagicMock()
    mock_ydl_context_manager.__enter__.return_value = mock_ydl_instance
    mocker.patch('utils.downloader.yt_dlp.YoutubeDL', return_value=mock_ydl_context_manager)

    url = "https://www.youtube.com/watch?v=private_video"
    result_path = download_video(url, temp_dir)

    # Assertion
    assert result_path is None

def test_progress_callback_is_used(mocker, temp_dir):
    """
    Test that the progress callback is correctly passed to yt-dlp's options.
    """
    mock_callback = MagicMock()
    
    # We only need to check if YoutubeDL was initialized with the right options
    mock_youtube_dl = mocker.patch('utils.downloader.yt_dlp.YoutubeDL')

    url = "https://www.youtube.com/watch?v=test"
    download_video(url, temp_dir, progress_callback=mock_callback)

    # Check that YoutubeDL was called with an options dictionary
    # that contains a 'progress_hooks' list with our callback.
    assert mock_youtube_dl.call_count == 1
    args, kwargs = mock_youtube_dl.call_args
    # The options dict is the first positional argument
    options = args[0]
    assert 'progress_hooks' in options
    assert options['progress_hooks'] == [mock_callback]