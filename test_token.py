#!/usr/bin/env python3
"""
Token Test Script - Tests different token formats and connection methods
"""
import os
import sys
import asyncio

# Install discord.py-self if needed
try:
    import discord
    from discord.ext import commands
except ImportError:
    print("Installing discord.py-self...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "discord.py-self"])
    import discord
    from discord.ext import commands

async def test_connection():
    token = os.environ.get('TOKEN', '').strip()
    
    if not token:
        print("❌ No TOKEN found in environment")
        return False
        
    print(f"Testing token: {token[:20]}...{token[-10:]}")
    print(f"Token length: {len(token)}")
    print(f"Token parts: {len(token.split('.'))}")
    
    # Test 1: Regular selfbot connection
    print("\n🔄 Test 1: Standard selfbot connection")
    try:
        # Create a simple selfbot
        intents = discord.Intents.default()
        intents.message_content = True
        
        bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)
        
        @bot.event
        async def on_ready():
            print(f"✅ SUCCESS! Bot connected as: {bot.user}")
            print(f"User ID: {bot.user.id}")
            print(f"Account type: {'Bot' if bot.user.bot else 'User'}")
            await bot.close()
            return True
            
        await bot.start(token)
        return True
        
    except discord.LoginFailure as e:
        print(f"❌ Login failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    try:
        result = asyncio.run(test_connection())
        if result:
            print("\n✅ Token is valid and working!")
        else:
            print("\n❌ Token test failed")
            print("\nFor selfbots, you need a USER token, not a BOT token:")
            print("1. Go to Discord in your browser")
            print("2. Press F12 (Developer Tools)")
            print("3. Go to Network tab")
            print("4. Send a message in any channel")
            print("5. Look for 'messages' request")
            print("6. In Headers, find 'authorization' header")
            print("7. Copy the value (that's your USER token)")
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")

if __name__ == "__main__":
    main()