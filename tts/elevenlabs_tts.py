import aiohttp
import os
from config import ELEVENLABS_API_KEY, ELEVENLABS_API_URL
from text_processing.text_utils import clean_text_for_tts

async def generate_custom_tts(text):
    # Clean the text before sending it to the TTS API
    cleaned_text = clean_text_for_tts(text)
    # print(f"Cleaned text for TTS: {cleaned_text}")

    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'text': cleaned_text,
        'voice_settings': {
            'stability': 0.47,          # Balanced stability for smoothness
            'similarity_boost': 0.95,   # Enhanced similarity to the target voice
            'style': 0.60,              # Moderate style for natural expressiveness
            'use_speaker_boost': True   # Use speaker boost for better clarity
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            print(f"Sending request to ElevenLabs API: {ELEVENLABS_API_URL}")
            async with session.post(ELEVENLABS_API_URL, headers=headers, json=data) as response:
                print(f"Response status: {response.status}")
                if response.status == 200:
                    audio_data = await response.read()
                    audio_path = 'response.mp3'
                    with open(audio_path, 'wb') as f:
                        f.write(audio_data)
                    print(f"Audio file saved at: {audio_path}")
                    return audio_path
                else:
                    error_text = await response.text()
                    print(f"Failed to generate TTS. Response status: {response.status}, Error: {error_text}")
                    return None
    except aiohttp.ClientError as e:
        print(f"Error in TTS generation: {e}")
        return None
