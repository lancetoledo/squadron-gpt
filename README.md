
# Squadron GPT

Squadron GPT is a sassy, sarcastic Discord bot designed to engage users with a playful, sharp-witted manner. It tailors conversations to the personalities and interests of the user's friends, offering unique interactions based on predefined data.

## Features

- **Relationship Inquiry**: Detects and provides information about relationships between friends.
- **Friend Inquiry**: Retrieves data about friends.
- **General Inquiry**: Handles general questions and provides responses based on the context.
- **Feedback Handling**: Detects feedback messages and stores them for future review.
- **Text-to-Speech (TTS)**: Uses ElevenLabs API to generate custom TTS responses.
- **Voice Channel Integration**: Joins and leaves voice channels to play TTS responses.
- **GPT-4 API Integration**: Uses OpenAI's GPT-4 API for generating responses.
- **Music Streaming**: Streams music from YouTube, SoundCloud, and Bandcamp.

## Directory Structure

```plaintext
squadron-gpt/
├── commands/
│   └── command_handlers.py
├── data/
│   └── (JSON files containing personal data)
├── events/
│   └── message_events.py
├── models/
│   └── (spaCy models)
├── tts/
│   └── elevenlabs_tts.py
├── utils/
│   ├── context_management.py
│   ├── feedback_utils.py
│   ├── file_utils.py
│   └── text_utils.py
├── .env
├── config.py
├── discord_client.py
├── main.py
├── nltk_setup.py
├── spacy_setup.py
└── train_spacy_model.py
```

## Setup Guide

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- A Discord account and a Discord bot token
- OpenAI API key
- ElevenLabs API key and voice ID

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/squadron-gpt.git
    cd squadron-gpt
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the `.env` file**:
    Create a `.env` file in the root directory of your project and add the following variables:
    ```dotenv
    OPENAI_API_KEY=your-openai-api-key
    ELEVENLABS_API_KEY=your-elevenlabs-api-key
    ELEVENLABS_VOICE_ID=your-elevenlabs-voice-id
    DISCORD_BOT_TOKEN=your-discord-bot-token
    SPACY_MODEL=en_core_web_sm
    RELATIONSHIP_MODEL=models/best_relationship_inquiry_model
    NLTK_DATA=punkt,averaged_perceptron_tagger,maxent_ne_chunker,words
    RELATIONSHIPS_DATA1=Lance_Relationships_Detailed.json
    RELATIONSHIPS_DATA2=Navi_Relationships_Detailed.json
    FRIEND_DATA1=squadron1.json
    FRIEND_DATA2=squadron2.json
    STATIC_FRIEND_DATA=[{"name": "Christian"}, {"name": "Justine"}, {"name": "Bob"}]
    DISCORD_TO_REAL_NAME={"noobmaster69": "Korg", "thechosenone": "Neo"}
    ```

5. **Download NLTK data**:
    ```bash
    python -m nltk.downloader punkt averaged_perceptron_tagger maxent_ne_chunker words
    ```

6. **Train spaCy model (if needed)**:
    ```bash
    python train_spacy_model.py
    ```

### Running the Bot

1. **Run the main script**:
    ```bash
    python main.py
    ```

### Bot Commands

- **Join Voice Channel**: `!join`
- **Leave Voice Channel**: `!leave`
- **Play Music**: `!play <url>`

### Handling Sensitive Data

To prevent sensitive data from being pushed to GitHub:

1. **Use `.env` for sensitive variables**:
    - Store your API keys, tokens, and personal data filenames in the `.env` file.

2. **Update `.gitignore**:
    - Ensure your `.gitignore` file includes entries for `.env` and `data/` directory:
    ```gitignore
    .env
    data/
    ```

### Example Data Structure

For `static_friend_data` and `discord_to_real_name`, structure your data in `.env` as follows:

```dotenv
STATIC_FRIEND_DATA=[{"name": "Christian"}, {"name": "Justine"}, {"name": "Bob"}]
DISCORD_TO_REAL_NAME={"noobmaster69": "Korg","thechosenone": "Neo"}
```

### Contributing

Contributions are welcome! Please fork the repository and create a pull request.

### License

This project is licensed under the MIT License.

---

Now you are ready to engage with your friends on Discord with Squadron GPT! If you have any questions or run into issues, feel free to open an issue in the repository.
