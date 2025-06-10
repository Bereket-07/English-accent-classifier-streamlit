# rem_accent_checker/utils/classifier.py
import os
import torch
from speechbrain.inference import EncoderClassifier
from typing import Dict, List, Any
from .logger import get_logger

logger = get_logger(__name__)

class AccentClassifier:
    """
    A class to handle accent classification using a local SpeechBrain model.
    """
    def __init__(self):
        """
        Initializes the classifier by loading the local SpeechBrain model.
        """
        model_dir = os.path.join(os.path.dirname(__file__), "accent_id_model_clean")
        
        if not os.path.isdir(model_dir):
            error_msg = f"Model directory not found at '{model_dir}'. Please ensure it is in 'utils/accent_id_model_clean'."
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
            
        try:
            logger.info(f"Loading SpeechBrain model from: {model_dir}")
            self.classifier = EncoderClassifier.from_hparams(source=model_dir, savedir=model_dir)
            self.ind2lab = self.classifier.hparams.label_encoder.ind2lab
            logger.info("SpeechBrain model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SpeechBrain model. Error: {e}")
            raise RuntimeError(f"Could not initialize AccentClassifier: {e}")

    def classify_audio(self, audio_path: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Classifies the accent from an audio file.

        Args:
            audio_path (str): The full, absolute path to the audio file (.wav).
            top_k (int): The number of top predictions to return.

        Returns:
            A list of dictionaries with 'label' and 'score'.
        """
        if not os.path.isfile(audio_path):
            logger.error(f"Audio file not found for classification: {audio_path}")
            return []
            
        # --- START: ROBUST PATH HANDLING FIX FOR WINDOWS ---
        original_cwd = os.getcwd()  # Save the current working directory
        audio_dir = os.path.dirname(audio_path)
        audio_filename = os.path.basename(audio_path)
        
        try:
            os.chdir(audio_dir)  # Temporarily change to the audio file's directory
            logger.info(f"Classifying audio file: {audio_filename} (from directory: {audio_dir})")
            
            # Now, classify using only the filename. SpeechBrain will look in the current directory.
            out_prob, score, index, text_lab = self.classifier.classify_file(audio_filename)
            
            # --- END: ROBUST PATH HANDLING FIX ---

            probabilities = out_prob.squeeze()
            top_k_scores, top_k_indices = torch.topk(probabilities, k=top_k)

            results = []
            for i in range(top_k):
                label_index = top_k_indices[i].item()
                label_score = top_k_scores[i].item()
                label_name = self.ind2lab[label_index]
                
                results.append({
                    "label": label_name.replace("_", " ").title(),
                    "score": label_score,
                })
            
            logger.info(f"Classification successful. Top prediction: {results[0]['label']} ({results[0]['score']:.2f})")
            return results

        except Exception as e:
            logger.error(f"An error occurred during SpeechBrain classification: {e}")
            return []
        finally:
            os.chdir(original_cwd) # IMPORTANT: Always change back to the original directory