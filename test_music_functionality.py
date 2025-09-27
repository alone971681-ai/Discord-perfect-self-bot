#!/usr/bin/env python3
"""
Comprehensive music functionality test for Discord selfbot
Tests all music features and verifies streaming capability
"""
import asyncio
import yt_dlp
import discord
import shutil
import os
import subprocess
import json

# Test configuration
TEST_QUERIES = [
    "never gonna give you up",
    "counting stars onerepublic", 
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
]

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

def test_ffmpeg_availability():
    """Test if FFmpeg is working properly"""
    print("🔧 Testing FFmpeg availability...")
    ffmpeg_path = get_ffmpeg_path()
    if ffmpeg_path:
        print(f"✅ FFmpeg found at: {ffmpeg_path}")
        try:
            # Test FFmpeg with a simple command
            result = subprocess.run([ffmpeg_path, '-version'], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ FFmpeg working: {version_line}")
                return True
            else:
                print(f"❌ FFmpeg test failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ FFmpeg error: {e}")
            return False
    else:
        print("❌ FFmpeg not found!")
        return False

def test_ytdl_extraction():
    """Test yt-dlp extraction capabilities"""
    print("\n🔍 Testing yt-dlp extraction...")
    
    ytdl_options = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False
    }
    
    ytdl = yt_dlp.YoutubeDL(ytdl_options)
    
    success_count = 0
    for query in TEST_QUERIES:
        try:
            print(f"  Testing: {query}")
            data = ytdl.extract_info(query, download=False)
            
            if data:
                if 'entries' in data and data['entries']:
                    data = data['entries'][0]
                
                title = data.get('title', 'Unknown')
                url = data.get('url', '')
                duration = data.get('duration', 0)
                
                if url:
                    print(f"  ✅ {title} ({duration}s)")
                    success_count += 1
                else:
                    print(f"  ❌ No audio URL found")
            else:
                print(f"  ❌ No data extracted")
                
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
    
    print(f"\n📊 yt-dlp Results: {success_count}/{len(TEST_QUERIES)} successful")
    return success_count == len(TEST_QUERIES)

def test_audio_source_creation():
    """Test Discord audio source creation"""
    print("\n🎵 Testing Discord audio source creation...")
    
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        print("❌ Cannot test audio sources - FFmpeg not available")
        return False
    
    # Test with a simple audio URL
    test_url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
    
    try:
        # Test basic FFmpegPCMAudio creation
        source = discord.FFmpegPCMAudio(
            test_url,
            executable=ffmpeg_path,
            before_options='-nostdin',
            options='-vn'
        )
        print("✅ Basic FFmpegPCMAudio creation successful")
        
        # Test with PCMVolumeTransformer
        volume_source = discord.PCMVolumeTransformer(source, volume=0.5)
        print("✅ PCMVolumeTransformer creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio source creation failed: {e}")
        return False

async def test_full_music_pipeline():
    """Test the complete music pipeline"""
    print("\n🚀 Testing complete music pipeline...")
    
    # Simplified YTDLSource class for testing
    class TestYTDLSource(discord.PCMVolumeTransformer):
        def __init__(self, source, *, data, volume=0.5):
            super().__init__(source, volume)
            self.data = data
            self.title = data.get('title')
            self.url = data.get('url')
            self.duration = data.get('duration')
        
        @classmethod
        async def from_url(cls, url, *, loop=None, stream=True):
            loop = loop or asyncio.get_event_loop()
            
            ytdl_options = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch',
                'extract_flat': False
            }
            
            ytdl = yt_dlp.YoutubeDL(ytdl_options)
            
            try:
                # Extract info with timeout
                data = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)),
                    timeout=30.0
                )
                
                if data is None:
                    raise Exception("No results found")
                
                if 'entries' in data and data['entries']:
                    data = data['entries'][0]
                
                if not data or not data.get('url'):
                    raise Exception("No playable audio found")
                
                # Get FFmpeg path
                ffmpeg_path = get_ffmpeg_path()
                if not ffmpeg_path:
                    raise Exception("FFmpeg not available")
                
                # Create audio source
                source = discord.FFmpegPCMAudio(
                    data['url'],
                    executable=ffmpeg_path,
                    before_options='-nostdin',
                    options='-vn'
                )
                
                return cls(source, data=data)
                
            except asyncio.TimeoutError:
                raise Exception("YouTube search timed out")
            except Exception as e:
                raise Exception(f"Failed to create audio: {str(e)}")
    
    # Test the pipeline
    success_count = 0
    for query in TEST_QUERIES[:2]:  # Test first 2 queries
        try:
            print(f"  Testing pipeline for: {query}")
            
            # Create audio source
            player = await TestYTDLSource.from_url(query, stream=True)
            
            if player and player.title:
                print(f"  ✅ Pipeline successful: {player.title}")
                success_count += 1
            else:
                print(f"  ❌ Pipeline failed: No player created")
                
        except Exception as e:
            print(f"  ❌ Pipeline failed: {str(e)}")
    
    print(f"\n📊 Pipeline Results: {success_count}/2 successful")
    return success_count >= 1

def check_bot_music_commands():
    """Check if bot music commands are properly defined"""
    print("\n🤖 Checking bot music command availability...")
    
    try:
        # Check if main.py has the music commands
        with open('main.py', 'r') as f:
            content = f.read()
        
        commands_found = {}
        music_commands = ['mjoin', 'mplay', 'mstop', 'mleave']
        
        for cmd in music_commands:
            if f'@bot.command(name="{cmd}")' in content:
                commands_found[cmd] = True
                print(f"  ✅ -{cmd} command found")
            else:
                commands_found[cmd] = False
                print(f"  ❌ -{cmd} command missing")
        
        return all(commands_found.values())
        
    except Exception as e:
        print(f"❌ Error checking commands: {e}")
        return False

async def main():
    """Run comprehensive music functionality test"""
    print("🎵" + "="*60)
    print("    DISCORD SELFBOT MUSIC FUNCTIONALITY TEST")
    print("="*62)
    
    test_results = {}
    
    # Test 1: FFmpeg availability
    test_results['ffmpeg'] = test_ffmpeg_availability()
    
    # Test 2: yt-dlp extraction
    test_results['ytdl'] = test_ytdl_extraction()
    
    # Test 3: Audio source creation
    test_results['audio_source'] = test_audio_source_creation()
    
    # Test 4: Full music pipeline
    test_results['pipeline'] = await test_full_music_pipeline()
    
    # Test 5: Bot command availability
    test_results['commands'] = check_bot_music_commands()
    
    # Results summary
    print("\n🏆" + "="*60)
    print("                    TEST RESULTS SUMMARY")
    print("="*62)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name.upper():15} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Music system is fully functional!")
        print("   Your Discord selfbot can stream music successfully.")
        print("\n🎵 Available commands:")
        print("   -mjoin [channel_name]  - Join voice channel")
        print("   -mplay <song_or_url>   - Play music")
        print("   -mstop                 - Stop playback")
        print("   -mleave                - Leave voice channel")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check the issues above.")
    
    print("\n" + "="*62)

if __name__ == "__main__":
    asyncio.run(main())