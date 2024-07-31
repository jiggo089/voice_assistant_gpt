# OpenAI Audio Recorder and Assistant Interaction

This project demonstrates how to record audio, transcribe it using OpenAI's Whisper model, and interact with an OpenAI assistant. The assistant can also provide responses via text-to-speech.

## Prerequisites

- **Python 3.6+**
- **pyaudio**
- **wave**
- **openai**
- **dotenv**
- **typing-extensions**

## Setup

1. **Install Dependencies**:

    ```sh
    pip install pyaudio wave openai python-dotenv typing-extensions
    ```

2. **Setup OpenAI API Key**:

    - Create a `.env` file in the root directory of the project.
    - Add your OpenAI API key to the `.env` file:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key_here
    ```


