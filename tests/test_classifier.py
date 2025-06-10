# tests/test_classifier.py
import os
import pytest
from utils.classifier import AccentClassifier

# This is an integration test and requires network access to download the model.
# It also requires a sample audio file at tests/fixtures/sample_audio.wav
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
SAMPLE_AUDIO_PATH = os.path.join(FIXTURE_DIR, 'sample_audio.wav') 

@pytest.fixture(scope="module")
def classifier():
    """Fixture to load the classifier once for all tests in this module."""
    try:
        return AccentClassifier()
    except Exception:
        pytest.fail("Failed to initialize AccentClassifier. Check network connection or model ID.")

@pytest.mark.skipif(not os.path.exists(SAMPLE_AUDIO_PATH), reason="Sample audio fixture not found")
def test_classify_audio_returns_correct_format(classifier):
    """Test that classification returns the expected data structure."""
    results = classifier.classify_audio(SAMPLE_AUDIO_PATH, top_k=3)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert len(results) <= 3
    
    for item in results:
        assert "label" in item
        assert "score" in item
        assert isinstance(item["label"], str)
        assert isinstance(item["score"], float)
        assert 0.0 <= item["score"] <= 1.0

def test_classify_audio_file_not_found(classifier):
    """Test classification with a non-existent audio file."""
    results = classifier.classify_audio("non_existent_audio.wav")
    assert results == []