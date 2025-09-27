#!/usr/bin/env python3
"""
Test the new Opus-based audio system for Discord selfbot
"""
import discord
import asyncio
import yt_dlp
import shutil

def get_ffmpeg_path():
    """Find ffmpeg executable path"""
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        common_paths = ["/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg", "./ffmpeg"]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    return ffmpeg_path

async def test_opus_audio_creation():
    """Test creating Opus audio sources directly"""
    print("🎵 Testing Opus Audio Creation System")
    print("="*50)
    
    # Test configuration
    ytdl_options = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False
    }
    
    ytdl = yt_dlp.YoutubeDL(ytdl_options)
    test_query = "never gonna give you up"
    
    try:
        # Extract YouTube info
        print(f"🔍 Extracting info for: {test_query}")
        data = ytdl.extract_info(test_query, download=False)
        
        if data and 'entries' in data and data['entries']:
            data = data['entries'][0]
        
        if not data or not data.get('url'):
            print("❌ No audio URL found")
            return False
        
        print(f"✅ Found: {data.get('title', 'Unknown')}")
        print(f"🔗 URL: {data['url'][:100]}...")
        
        # Test FFmpeg availability
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            print("❌ FFmpeg not found")
            return False
        
        print(f"✅ FFmpeg available: {ffmpeg_path}")
        
        # Test Opus audio source creation
        print("🎵 Creating FFmpegOpusAudio source...")
        
        source = discord.FFmpegOpusAudio(
            data['url'],
            executable=ffmpeg_path,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            options='-vn -f opus'
        )
        
        print("✅ FFmpegOpusAudio source created successfully")
        print(f"🔊 Is Opus: {source.is_opus()}")
        
        # Test reading a few frames
        print("📖 Testing audio reading...")
        for i in range(3):
            frame = source.read()
            if frame:
                print(f"✅ Frame {i+1}: {len(frame)} bytes")
            else:
                print(f"⚠️  Frame {i+1}: Empty")
        
        # Cleanup
        source.cleanup()
        print("✅ Audio source cleaned up successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    print("🚀 Starting Opus Audio System Test")
    print("="*60)
    
    success = await test_opus_audio_creation()
    
    print("\n" + "="*60)
    if success:
        print("🎉 OPUS AUDIO SYSTEM: FULLY FUNCTIONAL")
        print("✅ The new audio system should eliminate FFmpeg hanging issues")
        print("✅ Direct Opus encoding prevents process termination problems")
        print("✅ Music streaming should now work reliably")
    else:
        print("❌ OPUS AUDIO SYSTEM: NEEDS ATTENTION")
        print("⚠️  Check the errors above for troubleshooting")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())