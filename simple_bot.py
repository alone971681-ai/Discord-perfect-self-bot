#!/usr/bin/env python3
"""
Simple Discord Selfbot Test - Minimal working version
"""
import os
import sys
import subprocess

def install_discord_self():
    """Install discord.py-self if not already installed"""
    try:
        # Check if discord.py-self is installed
        import discord
        print("Discord package found, testing selfbot functionality...")
        return True
    except ImportError:
        print("Installing discord.py-self...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--break-system-packages", "discord.py-self"
            ])
            return True
        except Exception as e:
            print(f"Failed to install: {e}")
            return False

def test_token():
    """Test the Discord token connection"""
    if not install_discord_self():
        return False
    
    try:
        # Import after installation
        import discord
        from discord.ext import commands
        
        print("Testing Discord connection...")
        
        # Get token
        token = os.environ.get('TOKEN', '').strip()
        if not token:
            print("❌ No TOKEN found")
            return False
        
        print(f"Token length: {len(token)}")
        
        # Create minimal bot
        bot = commands.Bot(command_prefix="!", self_bot=True)
        
        @bot.event
        async def on_ready():
            print(f"✅ Bot connected as: {bot.user}")
            await bot.close()
        
        # Test connection
        bot.run(token, log_handler=None)
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_token()
    if success:
        print("✅ Token is working!")
    else:
        print("❌ Token test failed")
        print("Your token needs to be a USER token, not a BOT token")
        print("For selfbots, get your user token from Discord developer tools")