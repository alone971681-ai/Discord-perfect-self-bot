#!/usr/bin/env python3
"""
Install discord.py-self properly for selfbot functionality
"""
import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Command: {cmd}")
        print(f"Output: {result.stdout}")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Exception running {cmd}: {e}")
        return False

def main():
    print("Installing discord.py-self for selfbot functionality...")
    
    # Uninstall any existing discord packages
    print("1. Removing existing discord packages...")
    run_command("pip uninstall -y discord.py discord")
    
    # Install discord.py-self
    print("2. Installing discord.py-self...")
    success = run_command("pip install discord.py-self")
    
    if success:
        print("3. Verifying installation...")
        try:
            import discord
            print(f"Discord version: {discord.__version__}")
            
            # Test selfbot creation
            from discord.ext import commands
            intents = discord.Intents.default()
            bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)
            print("✅ Selfbot creation successful!")
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
    else:
        print("❌ Installation failed")

if __name__ == "__main__":
    main()