#!/bin/bash

# Master startup script for LTC Flash Discord Selfbot
# This script determines the best way to start the application

# Check if running in Replit
if [ -n "$REPL_ID" ] || [ -n "$REPL_SLUG" ]; then
  # Running in Replit environment
  echo "Detected Replit environment"
  
  # Check if TOKEN is set
  if [ -z "$TOKEN" ]; then
    echo "==========================================================================="
    echo "⚠️ WARNING: Discord TOKEN environment variable is not set!"
    echo "   Starting in web-only mode so you can set your TOKEN through the web UI."
    echo "==========================================================================="
    
    # Start only the web server (the bot can be started from the web UI)
    exec gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload wsgi:application
  else
    # Start both web server and bot with the combined script
    echo "Discord TOKEN is configured. Starting full system..."
    exec ./start_web_and_bot.sh
  fi
else
  # Not running in Replit
  echo "Not running in Replit environment"
  echo "Starting in standard mode..."
  
  # Check if we're running the bot or web server
  if [ "$1" = "web" ]; then
    echo "Starting web server only..."
    exec gunicorn --bind 0.0.0.0:5000 --reuse-port --reload wsgi:application
  elif [ "$1" = "bot" ]; then
    echo "Starting bot with auto-recovery only..."
    exec python start_bot_with_recovery.py
  else
    # Default: start both
    echo "Starting complete system (bot + web server)..."
    exec ./start_web_and_bot.sh
  fi
fi