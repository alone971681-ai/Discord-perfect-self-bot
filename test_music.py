#!/usr/bin/env python3
"""
Test script for Discord music functionality
"""
import asyncio
import yt_dlp
import discord
import shutil
import os

# FFMPEG Configuration
def get_ffmpeg_path():
    """Find ffmpeg executable path"""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        # Try common paths
        common_paths = ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "./ffmpeg"]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    return ffmpeg_path

# YouTube-DL Configuration
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        try:
            print(f"🔍 Extracting info for: {url}")
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
            
            if data is None:
                raise Exception("Failed to extract video information from YouTube")
            
            if 'entries' in data and data['entries']:
                # Take first item from a playlist
                data = data['entries'][0]
                print(f"📋 Selected from playlist: {data.get('title', 'Unknown')}")
            
            if data is None:
                raise Exception("No playable content found in the search results")
            
            # Get the audio URL for streaming
            audio_url = data.get('url')
            if not audio_url:
                raise Exception("Could not extract audio URL from YouTube")
            
            print(f"🎵 Found audio: {data.get('title', 'Unknown')}")
            
            # Check if ffmpeg is available
            ffmpeg_path = get_ffmpeg_path()
            if not ffmpeg_path:
                raise Exception("FFmpeg not found. Please install FFmpeg to play music.")
            
            print(f"🔧 Using FFmpeg at: {ffmpeg_path}")
            
            # Create FFmpeg PCM Audio source
            ffmpeg_source = discord.FFmpegPCMAudio(
                audio_url,
                executable=ffmpeg_path,
                before_options=ffmpeg_options['before_options'],
                options=ffmpeg_options['options']
            )
            
            print("✅ Successfully created FFmpeg audio source")
            return cls(ffmpeg_source, data=data)
        except Exception as e:
            error_msg = f"Error creating audio source: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)

async def test_music_functionality():
    """Test the music functionality without actually playing"""
    test_queries = [
        "never gonna give you up",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "counting stars"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing query: {query}")
        print(f"{'='*50}")
        
        try:
            # Test the YTDLSource creation
            player = await YTDLSource.from_url(query, stream=True)
            
            print(f"✅ SUCCESS for '{query}'")
            print(f"   Title: {player.title}")
            print(f"   Uploader: {player.uploader}")
            print(f"   Duration: {player.duration}s")
            print(f"   Audio URL available: {'Yes' if player.data.get('url') else 'No'}")
            
        except Exception as e:
            print(f"❌ FAILED for '{query}': {e}")

if __name__ == "__main__":
    print("🎵 Testing Discord Music Functionality")
    print("=" * 50)
    
    # Test FFmpeg
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        print(f"✅ FFmpeg found at: {ffmpeg_path}")
    else:
        print("❌ FFmpeg not found!")
        exit(1)
    
    # Run the async test
    asyncio.run(test_music_functionality())
    
    print("\n" + "=" * 50)
    print("🎵 Music functionality test complete!")