import yt_dlp as youtube_dl
import requests
import re

# Options for yt-dlp to format the audio extraction
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Options for FFmpeg to process the audio
ffmpeg_options = {
    'options': '-vn'
}

# Initialize yt-dlp with the specified options
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Function to get audio URL from SoundCloud
async def get_soundcloud_audio(search):
    print("Using SoundCloud for the search term")
    with ytdl as ydl:
        info = ydl.extract_info(f"scsearch1:{search}", download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title']

# Function to get audio URL from Bandcamp
async def get_bandcamp_audio(search):
    print("Using Bandcamp for the search term")
    with ytdl as ydl:
        info = ydl.extract_info(f"bcsearch:{search}", download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title']

# Function to get audio URL from YouTube
async def get_youtube_audio(search):
    print("Using YouTube for the search term")
    with ytdl as ydl:
        info = ydl.extract_info(search, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title']

# Function to get the appropriate audio URL based on the provided URL or search term
async def get_audio_url(search):
    audio_url, title = None, None
    
    try:
        audio_url, title = await get_soundcloud_audio(search)
    except Exception as e:
        print(f"SoundCloud failed: {e}")
    
    if not audio_url:
        try:
            audio_url, title = await get_bandcamp_audio(search)
        except Exception as e:
            print(f"Bandcamp failed: {e}")

    if not audio_url:
        try:
            audio_url, title = await get_youtube_audio(search)
        except Exception as e:
            print(f"YouTube failed: {e}")

    return audio_url, title
