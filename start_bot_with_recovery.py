#!/usr/bin/env python3
"""
Start Discord Selfbot with Auto-Recovery
This script starts the Discord selfbot with automatic error recovery and 24/7 uptime support.
"""

import os
import sys
import time
import logging
import argparse
from auto_recovery import start_recovery, stop_recovery, get_recovery_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logger = logging.getLogger("Launcher")

def check_environment():
    """Check if required environment variables are set"""
    token = os.environ.get('TOKEN')
    if not token:
        logger.error("❌ ERROR: Discord TOKEN environment variable is not set!")
        logger.error("Please set your Discord token in Replit secrets or environment variables.")
        logger.error("This is required for the bot to function.")
        return False
    return True

def display_info():
    """Display information about 24/7 operation"""
    logger.info("=" * 60)
    logger.info("🤖 Discord LTC Flash Selfbot with 24/7 Auto-Recovery")
    logger.info("=" * 60)
    logger.info("📋 For true 24/7 operation when Replit is closed:")
    logger.info("1. Enable 'Always On' in your Replit project settings")
    logger.info("2. Set up a free UptimeRobot monitor (https://uptimerobot.com)")
    logger.info("   to ping your Replit URL every 5 minutes")
    logger.info("=" * 60)

def main():
    """Main function to start the bot with recovery"""
    parser = argparse.ArgumentParser(description="Start Discord selfbot with auto-recovery")
    parser.add_argument("--web-only", action="store_true", help="Start only the web server, not the bot")
    args = parser.parse_args()
    
    display_info()
    
    if args.web_only:
        logger.info("Starting in web-only mode (bot will be started through web interface)")
        # Just import app and keep the script running
        try:
            from app import app
            logger.info("Web server is running. Discord bot can be started through the web interface.")
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            return
    else:
        # Check if environment is properly set up
        if not check_environment():
            return
            
        # Start the bot with auto-recovery
        logger.info("Starting Discord selfbot with auto-recovery...")
        start_recovery()
        
        try:
            # Keep the script running and log status periodically
            while True:
                time.sleep(60)
                status = get_recovery_status()
                if status['bot_running']:
                    logger.info("✅ Bot is running (Restart count: %d)", status['restart_count'])
                else:
                    logger.warning("⚠️ Bot appears to be down, recovery system should restart it shortly")
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down...")
            stop_recovery()

if __name__ == "__main__":
    main()