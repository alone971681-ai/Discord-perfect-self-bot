from flask import Flask
from threading import Thread
import logging
import os

# Create a separate keep-alive app to avoid conflicts
keep_alive_app = Flask('keep_alive')
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@keep_alive_app.route('/')
def home():
    """Root endpoint for the keep-alive server"""
    return "LTC Flash Discord Bot is alive! 24/7 operation enabled."

@keep_alive_app.route('/status')
def status():
    """API endpoint to check bot status"""
    # Return basic status information
    return {
        "status": "online",
        "message": "Discord LTC Flash Bot is running",
        "bot_type": "selfbot",
        "features": ["LTC Flash", "Drowning", "Debate", "Viggle AI Animation"]
    }

def setup_uptime_monitors():
    """
    Set up external uptime monitors to keep the bot running 24/7.
    This uses Replit's 'Always On' feature and we recommend adding an external
    service like UptimeRobot to ping the server regularly.
    """
    replit_url = os.environ.get('REPL_SLUG', 'your-repl-name')
    replit_owner = os.environ.get('REPL_OWNER', 'your-username')
    monitor_url = f"https://{replit_url}.{replit_owner}.repl.co"
    
    print("📌 Recommend setting up UptimeRobot to ping:", monitor_url)
    print("📋 For 24/7 uptime, set up a free UptimeRobot monitor at: https://uptimerobot.com")
    print("   Add your Replit URL as a monitor with a 5-minute check interval")

def run():
    """Run the Flask server for keep-alive"""
    # Use a different port to avoid conflicts with the main web app
    keep_alive_app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    """
    Creates and starts a web server that can be pinged to keep the bot alive.
    This is necessary for 24/7 operation on Replit.
    
    Important: To ensure your bot runs truly 24/7, even when you close Replit:
    1. Enable "Always On" in your Replit project settings
    2. Use an external service like UptimeRobot to ping your Replit URL
    """
    # Only start keep-alive server if we're running main.py directly, not through web interface
    if __name__ == "__main__" or "main.py" in str(os.environ.get('_', '')):
        t = Thread(target=run, daemon=True)
        t.start()
        print("✅ Keep-alive server started. Bot will now run 24/7.")
        setup_uptime_monitors()
    else:
        print("✅ Keep-alive server ready (will be managed by web interface).")

# Don't auto-start - let main.py call keep_alive() when needed
if __name__ == "__main__":
    keep_alive()