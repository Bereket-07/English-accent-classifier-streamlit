# tests/test_classifier.py
import os
import pytest
import torch
from utils.classifier import AccentClassifier

# Define paths to fixtures
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
SAMPLE_AUDIO_PATH = os.path.join(FIXTURE_DIR, 'sample_audio.wav')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'utils', 'accent_id_model_clean')

@pytest.fixture(scope="module")
def classifier():
    """
    Fixture to load the AccentClassifier once for all tests in this module.
    This is an integration fixture that requires the model to be present.
    """
    if not os.path.isdir(MODEL_DIR):
        pytest.skip(f"Model directory not found at {MODEL_DIR}. Skipping integration tests.")
    
    try:
        return AccentClassifier()
    except Exception as e:
        pytest.fail(f"Failed to initialize AccentClassifier from '{MODEL_DIR}'. Error: {e}")

def test_classifier_initialization_fails_if_model_missing(mocker):
    """
    Unit test: Verifies that AccentClassifier raises FileNotFoundError if the model directory is missing.
    """
    # Mock os.path.isdir to simulate the model directory being absent
    mocker.patch('os.path.isdir', return_value=False)
    
    with pytest.raises(FileNotFoundError, match="Model directory not found"):
        AccentClassifier()

@pytest.mark.skipif(not os.path.exists(SAMPLE_AUDIO_PATH), reason="Sample audio fixture not found at tests/fixtures/sample_audio.wav")
def test_classify_audio_success(classifier, temp_dir):
    """
    Integration test: Classifies a real audio file and checks the output format.
    """
    # SpeechBrain requires an absolute path for its internal handling.
    # The fix in the source code handles chdir, but providing a full path is robust.
    # We'll copy the fixture to a temp dir to avoid issues with relative paths in tests.
    test_audio_path = os.path.join(temp_dir, 'test.wav')
    import shutil
    shutil.copy(SAMPLE_AUDIO_PATH, test_audio_path)
    
    results = classifier.classify_audio(test_audio_path, top_k=3)
    
    # Assertions on the output format
    assert isinstance(results, list)
    assert 0 < len(results) <= 3
    
    top_result = results[0]
    assert "label" in top_result
    assert "score" in top_result
    assert isinstance(top_result["label"], str)
    assert isinstance(top_result["score"], float)
    assert 0.0 <= top_result["score"] <= 1.0
    # Check that labels are title-cased and have spaces
    assert "_" not in top_result["label"]
    assert top_result["label"] == top_result["label"].title()


def test_classify_audio_file_not_found(classifier):
    """
    Test that classification returns an empty list if the audio file does not exist.
    """
    non_existent_path = "/path/to/non_existent_audio.wav"
    results = classifier.classify_audio(non_existent_path)
    assert results == []

def test_chdir_logic_restores_original_directory(classifier, mocker, temp_dir):
    """
    Test that the os.chdir logic correctly restores the current working directory,
    even if an error occurs during classification.
    """
    original_cwd = os.getcwd()
    
    # Mock the classifier's internal model to raise an exception
    mocked_internal_classifier = MagicMock()
    mocked_internal_classifier.classify_file.side_effect = Exception("Classification failed")
    classifier.classifier = mocked_internal_classifier
    
    test_audio_path = os.path.join(temp_dir, 'test.wav')
    with open(test_audio_path, 'w') as f: # create a dummy file to pass the `isfile` check
        f.write("dummy")

    # The function should catch the exception and return [], but the finally block must run
    results = classifier.classify_audio(test_audio_path)
    assert results == []
    
    # The most important assertion: did we return to the original directory?
    assert os.getcwd() == original_cwd
    
    # Restore the original classifier for other tests if necessary (though this is last)
    # This is not strictly needed due to test isolation but is good practice.
    del classifier.classifier