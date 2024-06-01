import aiohttp
import os
from config import ELEVENLABS_API_KEY, ELEVENLABS_API_URL
from text_processing.text_utils import clean_text_for_tts

async def generate_custom_tts(text):
    cleaned_text = clean_text_for_tts(text)

    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'text': cleaned_text,
        'voice_settings': {
            'stability': 0.47,
            'similarity_boost': 0.95,
            'style': 0.60,
            'use_speaker_boost': True
        }
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(ELEVENLABS_API_URL, headers=headers, json=data) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    audio_path = 'response.mp3'
                    with open(audio_path, 'wb') as f:
                        f.write(audio_data)
                    return audio_path
                else:
                    return None
    except aiohttp.ClientError as e:
        return None
