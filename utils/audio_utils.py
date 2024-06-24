import os
import discord
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import asyncio
from elevenlabs import generate, save

async def generate_custom_tts(text: str) -> str:
    audio = generate(
        text=text,
        voice="Antoni",
        model="eleven_monolingual_v1"
    )
    
    file_name = f"temp_audio_{os.urandom(4).hex()}.mp3"
    save(audio, file_name)
    return file_name

async def play_audio(ctx, audio_path: str):
    voice_client = ctx.guild.voice_client
    if not voice_client:
        return

    def after_playing(error):
        if error:
            print(f"Error in playback: {error}")
        else:
            print("Playback finished.")
        asyncio.run_coroutine_threadsafe(cleanup(audio_path), ctx.bot.loop)

    source = PCMVolumeTransformer(FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=audio_path))
    source.volume = 1.0
    voice_client.play(source, after=after_playing)

    while voice_client.is_playing():
        await asyncio.sleep(1)

async def cleanup(audio_path: str):
    try:
        os.remove(audio_path)
        print(f"Temporary audio file {audio_path} removed.")
    except Exception as e:
        print(f"Error removing temporary audio file: {e}")