#!/bin/bash

# Start Web and Bot with Auto-Recovery
# This script starts both the Flask web server and the Discord bot with auto-recovery

echo "=================================================================================="
echo "🚀 Starting LTC Flash Bot System with Web Interface and Auto-Recovery"
echo "=================================================================================="

# Export required environment variables if not already set
# This will be used by both the web server and the bot
if [ -z "$PORT" ]; then
  export PORT=5000
  echo "⚙️ Setting default port: $PORT"
fi

# Check if TOKEN is set
if [ -z "$TOKEN" ]; then
  echo "❌ ERROR: Discord TOKEN environment variable is not set!"
  echo "   Please set your Discord token in Replit secrets or environment variables."
  echo "   This is required for the bot to function."
  exit 1
fi

# Start the Flask web server in the background
echo "🌐 Starting Flask web server..."
gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload wsgi:application &
WEB_PID=$!
echo "✅ Web server started with PID: $WEB_PID"

# Give the web server a moment to start
sleep 2

# Start the bot with auto-recovery
echo "🤖 Starting Discord selfbot with auto-recovery..."
python start_bot_with_recovery.py &
BOT_PID=$!
echo "✅ Bot started with PID: $BOT_PID"

echo "=================================================================================="
echo "📋 System Information:"
echo "   - Web Interface: http://localhost:$PORT"
echo "   - Web Server PID: $WEB_PID"
echo "   - Bot Launcher PID: $BOT_PID"
echo ""
echo "📋 For true 24/7 operation when Replit is closed:"
echo "   1. Enable 'Always On' in your Replit project settings"
echo "   2. Set up a free UptimeRobot monitor (https://uptimerobot.com)"
echo "      to ping your Replit URL every 5 minutes"
echo "   3. Visit http://localhost:$PORT/setup-24-7 for detailed setup instructions"
echo "=================================================================================="

# Keep the main process running and handle clean shutdown
function cleanup() {
  echo "🛑 Shutting down services..."
  
  # Kill bot process
  if ps -p $BOT_PID > /dev/null; then
    echo "   Stopping bot with PID: $BOT_PID"
    kill -15 $BOT_PID
  fi
  
  # Kill web server process
  if ps -p $WEB_PID > /dev/null; then
    echo "   Stopping web server with PID: $WEB_PID"
    kill -15 $WEB_PID
  fi
  
  # Wait for graceful shutdown
  sleep 2
  
  # Force kill if still running
  if ps -p $BOT_PID > /dev/null; then
    kill -9 $BOT_PID
  fi
  
  if ps -p $WEB_PID > /dev/null; then
    kill -9 $WEB_PID
  fi
  
  echo "✅ All services stopped"
  exit 0
}

# Handle clean shutdown on SIGINT and SIGTERM
trap cleanup SIGINT SIGTERM

echo "🔄 System is running. Press Ctrl+C to stop all services."

# Monitor child processes
while true; do
  # Check if web server is still running
  if ! ps -p $WEB_PID > /dev/null; then
    echo "⚠️ Web server process exited unexpectedly. Restarting..."
    gunicorn --bind 0.0.0.0:$PORT --reuse-port --reload wsgi:application &
    WEB_PID=$!
    echo "✅ Web server restarted with PID: $WEB_PID"
  fi
  
  # Check if bot launcher is still running
  if ! ps -p $BOT_PID > /dev/null; then
    echo "⚠️ Bot launcher process exited unexpectedly. Restarting..."
    python start_bot_with_recovery.py &
    BOT_PID=$!
    echo "✅ Bot launcher restarted with PID: $BOT_PID"
  fi
  
  sleep 30
done