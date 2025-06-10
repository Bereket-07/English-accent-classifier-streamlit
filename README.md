# 🎙️ English Accent Classifier

A modular, production-ready Streamlit application that analyzes and classifies English accents from public video URLs using a pre-trained SpeechBrain model.

## Table of Contents

- [Overview](#overview)
- [Live Demo](#live-demo)
- [The Core Pipeline](#the-core-pipeline)
- [Technologies & Tools](#technologies--tools)
- [Folder Organization](#folder-organization)
- [System Requirements](#system-requirements)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides a user-friendly web interface to determine the English accent of a speaker in a video. By simply providing a public URL (from sources like YouTube), the application orchestrates a backend pipeline that downloads the video, isolates the audio track, and feeds it into a sophisticated deep learning model for classification. The results, including the predicted accent and the model's confidence, are then presented back to the user in a clean and intuitive dashboard.

The entire application is built with modularity and testability in mind, following best practices for pr![alt text]oduction-ready software.

## Live Demo

See the application in action! This short demo showcases the user interface and the end-to-end analysis process.



(image1.png)
(image2.png)
(image3.png)

## The Core Pipeline

The application follows a robust, multi-step process to analyze an accent:

1.  **URL Input**: The user provides a public video URL through the Streamlit interface.
2.  **Resilient Video Download**: A resilient downloader (`yt-dlp`) fetches the video, with built-in retries to handle network instabilities.
3.  **Audio Extraction**: The audio track is separated from the video file and converted into a standard `.wav` format using `moviepy`.
4.  **Accent Classification**: The extracted audio is fed into a pre-trained `SpeechBrain` model, which analyzes its acoustic features (not the words spoken) to predict the accent.
5.  **Results Visualization**: The top predictions and their confidence scores are displayed on the Streamlit dashboard using interactive charts and metrics.

## Technologies & Tools

This project leverages a modern stack of data science and web development libraries:

1.  **Programming Language**: [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=yellow)](https://www.python.org/)
2.  **Web Framework**: [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
3.  **AI / ML Model**: [![SpeechBrain](https://img.shields.io/badge/SpeechBrain-6C259D?style=for-the-badge&logo=pytorch&logoColor=white)](https://speechbrain.github.io/)
4.  **Audio Processing**: [![MoviePy](https://img.shields.io/badge/MoviePy-000000?style=for-the-badge&logo=python&logoColor=white)](https://zulko.github.io/moviepy/)
5.  **Video Downloading**: [![yt-dlp](https://img.shields.io/badge/yt--dlp-8921B2?style=for-the-badge)](https://github.com/yt-dlp/yt-dlp)
6.  **Numerical Computing**: [![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
7.  **Testing Framework**: [![Pytest](https://img.shields.io/badge/Pytest-0A9B53?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
8.  **Version Control**: [![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

## Folder Organization

The project is structured to separate concerns, making it clean, scalable, and easy to maintain.

```
📁rem_accent_checker/
│
├── app.py # 🎈 Main Streamlit application
├── 📜.gitignore
├── 📰README.md # 📖 You are here!
├── 🔋requirements.txt # 📦 Python dependencies
│
├── 📁.streamlit/
│ └── 📃config.toml # 🎨 Theming for the Streamlit app
│
├── 📁utils/ # 🛠️ Core logic modules
│ ├── 📜__init__.py
│ ├── 📁accent_id_model_clean/ # 🧠 Local SpeechBrain model files
│ ├── 📜audio_utils.py # 🎵 Audio extraction logic
│ ├── 📜classifier.py # 🤖 Accent classification logic
│ ├── 📜downloader.py # 📥 Video download logic
│ └── 📜logger.py # 📝 Logging configuration
│
└── ⌛tests/ # 🧪 Unit and integration tests
  ├── 📜test_audio_utils.py
  ├── 📜test_classifier.py
  └── 📜test_downloader.py
├── 📜__init__.py
├── 📁fixtures/ # 📎 Sample files for testing
│ ├── 🎥sample_video.mp4
│ └── 🔊sample_audio.wav

```


### Folder Structure: A Deep Dive

-   **`app.py`**: The entry point for the Streamlit application. It orchestrates the UI and calls the utility modules to perform the backend tasks.
-   **`.streamlit/config.toml`**: Contains theme configurations to give the app a polished, custom look.
-   **`utils/`**: This directory is the application's "engine room."
    -   **`accent_id_model_clean/`**: **Crucially**, this folder must contain the pre-trained SpeechBrain model files. The application loads the model locally from here.
    -   **`downloader.py`**: A robust module responsible for downloading video content from a given URL.
    -   **`audio_utils.py`**: Handles the technical task of extracting the raw audio waveform from the downloaded video file.
    -   **`classifier.py`**: Contains the `AccentClassifier` class, which loads the local SpeechBrain model and performs the inference on an audio file.
    -   **`logger.py`**: Sets up a standardized logger to provide clear, consistent output for debugging and monitoring.
-   **`tests/`**: Contains all automated tests.
    -   **`fixtures/`**: Holds small, sample media files (`.mp4`, `.wav`) used as inputs for the tests, ensuring they can run offline and are deterministic.
    -   **`test_*.py`**: Each utility module has a corresponding test file to verify its functionality in isolation.

## System Requirements

-   **Python 3.8+**
-   **`ffmpeg`**: This is a critical system-level dependency required by `moviepy` for audio and video processing.

    -   **On macOS (via Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    -   **On Debian/Ubuntu:**
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```
    -   **On Windows (via Chocolatey):**
        ```bash
        choco install ffmpeg
        ```

## Setup & Installation

Follow these steps to get the project running on your local machine.

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-username/rem_accent_checker.git
    cd rem_accent_checker
    ```

2.  **Create and activate a virtual environment** (highly recommended)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install all required Python packages**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Add the Model**: Ensure you have placed the `accent_id_model_clean` folder inside the `utils/` directory. The application will not run without it.

## Running the Application

Once the setup is complete, start the Streamlit server with this command:

```bash
streamlit run app.py