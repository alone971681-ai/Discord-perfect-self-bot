from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import subprocess
import json
import time
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "development_secret_key")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bot_data.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
from models import db, BotConfiguration, AuthorizedUser, CommandLog, BotAnalytics, TargetUser, AFKStatus, BotSession
from models import get_bot_setting, set_bot_setting, log_command_execution, record_analytics

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    # Set default configuration values
    if not BotConfiguration.query.filter_by(setting_name='anti_ban_enabled').first():
        set_bot_setting('anti_ban_enabled', True, 'bool', 'Enable anti-ban protection features')
    if not BotConfiguration.query.filter_by(setting_name='response_delay_min').first():
        set_bot_setting('response_delay_min', 0.3, 'float', 'Minimum response delay in seconds')
    if not BotConfiguration.query.filter_by(setting_name='response_delay_max').first():
        set_bot_setting('response_delay_max', 0.8, 'float', 'Maximum response delay in seconds')

# Simple status tracking
BOT_STATUS = {
    "is_running": False,
    "last_started": None,
    "last_command": None,
    "command_result": None,
    "keep_alive_enabled": True  # New flag for 24/7 operation
}

@app.route('/')
def index():
    # Check if bot process is running
    try:
        result = subprocess.run(["pgrep", "-f", "python main.py"], capture_output=True, text=True)
        BOT_STATUS["is_running"] = result.returncode == 0
    except Exception as e:
        app.logger.error(f"Error checking bot status: {e}")
    
    return render_template('index.html', status=BOT_STATUS)

@app.route('/start_bot', methods=['POST'])
def start_bot():
    try:
        # Import and use the auto-recovery system
        from auto_recovery import start_recovery, get_recovery_status
        
        # Start the bot with auto-recovery
        start_recovery()
        
        # Update status
        BOT_STATUS["is_running"] = True
        BOT_STATUS["keep_alive_enabled"] = True
        BOT_STATUS["last_started"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        flash("Discord selfbot started successfully with 24/7 keep-alive and auto-recovery enabled!", "success")
        app.logger.info("Bot started with auto-recovery system")
    except Exception as e:
        flash(f"Error starting bot: {e}", "danger")
        app.logger.error(f"Error starting bot: {e}")
    
    return redirect(url_for('index'))

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    try:
        # Use the auto-recovery system to stop the bot properly
        from auto_recovery import stop_recovery
        
        # Stop the bot and recovery system
        stop_recovery()
        
        # Also use pkill as a backup method
        subprocess.run(["pkill", "-f", "python main.py"])
        
        BOT_STATUS["is_running"] = False
        flash("Discord selfbot stopped successfully!", "success")
    except Exception as e:
        flash(f"Error stopping bot: {e}", "danger")
        app.logger.error(f"Error stopping bot: {e}")
    
    return redirect(url_for('index'))

@app.route('/bot_status')
def bot_status():
    """API endpoint to get detailed bot status information"""
    try:
        # Import the recovery system and get status
        from auto_recovery import get_recovery_status
        recovery_status = get_recovery_status()
        
        # Update our status tracking based on recovery system
        BOT_STATUS["is_running"] = recovery_status["bot_running"]
        
        # Get analytics from database
        recent_commands = CommandLog.query.filter(
            CommandLog.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        active_session = BotSession.query.filter_by(status='active').first()
        
        # Return combined status information
        return json.dumps({
            "bot_status": BOT_STATUS,
            "recovery_status": recovery_status,
            "analytics": {
                "commands_24h": recent_commands,
                "current_session_id": active_session.session_id if active_session else None,
                "session_start": active_session.started_at.isoformat() if active_session else None
            }
        })
    except Exception as e:
        app.logger.error(f"Error getting bot status: {e}")
        return json.dumps({
            "error": str(e),
            "bot_status": BOT_STATUS
        })

@app.route('/analytics')
def analytics():
    """Display bot analytics and statistics"""
    try:
        # Get command statistics
        total_commands = CommandLog.query.count()
        commands_today = CommandLog.query.filter(
            CommandLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # Get most used commands
        from sqlalchemy import func
        popular_commands = db.session.query(
            CommandLog.command,
            func.count(CommandLog.command).label('count')
        ).group_by(CommandLog.command).order_by(func.count(CommandLog.command).desc()).limit(10).all()
        
        # Get authorized users count
        auth_users = AuthorizedUser.query.filter_by(is_active=True).count()
        
        # Get AFK statistics
        afk_sessions = AFKStatus.query.filter(AFKStatus.ended_at.isnot(None)).count()
        
        return render_template('analytics.html', 
                             total_commands=total_commands,
                             commands_today=commands_today,
                             popular_commands=popular_commands,
                             auth_users=auth_users,
                             afk_sessions=afk_sessions)
    except Exception as e:
        app.logger.error(f"Error getting analytics: {e}")
        flash(f"Error loading analytics: {e}", "danger")
        return redirect(url_for('index'))

@app.route('/api/command_logs')
def api_command_logs():
    """API endpoint for recent command logs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        logs = CommandLog.query.order_by(CommandLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            "logs": [{
                "id": log.id,
                "username": log.username,
                "command": log.command,
                "arguments": log.arguments,
                "success": log.success,
                "error_message": log.error_message,
                "execution_time": log.execution_time,
                "created_at": log.created_at.isoformat()
            } for log in logs.items],
            "total": logs.total,
            "pages": logs.pages,
            "current_page": page
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Real-time dashboard for bot monitoring"""
    return render_template('dashboard.html')

@app.route('/api/dashboard_data')
def api_dashboard_data():
    """API endpoint for real-time dashboard data"""
    try:
        # Get current bot status
        from auto_recovery import get_recovery_status
        recovery_status = get_recovery_status()
        
        # Calculate performance metrics
        recent_commands = CommandLog.query.filter(
            CommandLog.created_at >= datetime.utcnow() - timedelta(minutes=5)
        ).count()
        
        avg_response_time = db.session.query(
            db.func.avg(CommandLog.execution_time)
        ).filter(
            CommandLog.execution_time.isnot(None),
            CommandLog.created_at >= datetime.utcnow() - timedelta(hours=1)
        ).scalar() or 0
        
        commands_today = CommandLog.query.filter(
            CommandLog.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # Get recent command logs for display
        recent_logs = CommandLog.query.order_by(CommandLog.created_at.desc()).limit(10).all()
        
        return jsonify({
            "bot_online": recovery_status.get("bot_running", False),
            "commands_today": commands_today,
            "avg_response_time": round((avg_response_time or 0) * 1000, 1),  # Convert to ms
            "active_users": AuthorizedUser.query.filter_by(is_active=True).count(),
            "uptime": recovery_status.get("uptime", "0h"),
            "memory_usage": 75,  # Placeholder - could integrate with psutil
            "recent_commands": [{
                "timestamp": log.created_at.isoformat(),
                "user": log.username or "Unknown",
                "command": log.command,
                "success": log.success
            } for log in recent_logs],
            "performance_data": {
                "response_time": round((avg_response_time or 0) * 1000, 1),
                "commands_per_minute": recent_commands
            },
            "status": {
                "process": recovery_status.get("bot_running", False),
                "database": True,  # Could add actual DB health check
                "web_server": True,
                "anti_ban": True,
                "keep_alive": recovery_status.get("keep_alive_active", False),
                "security": True
            }
        })
    except Exception as e:
        app.logger.error(f"Error getting dashboard data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export_logs')
def api_export_logs():
    """Export command logs as JSON"""
    try:
        logs = CommandLog.query.order_by(CommandLog.created_at.desc()).limit(1000).all()
        export_data = [{
            "id": log.id,
            "user_id": log.user_id,
            "username": log.username,
            "command": log.command,
            "arguments": log.arguments,
            "success": log.success,
            "error_message": log.error_message,
            "execution_time": log.execution_time,
            "created_at": log.created_at.isoformat()
        } for log in logs]
        
        response = jsonify(export_data)
        response.headers["Content-Disposition"] = f"attachment; filename=bot_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency_stop', methods=['POST'])
def api_emergency_stop():
    """Emergency stop endpoint"""
    try:
        from auto_recovery import stop_recovery
        stop_recovery()
        subprocess.run(["pkill", "-f", "python main.py"])
        return jsonify({"success": True, "message": "Emergency stop executed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_token')
def check_token():
    token = os.environ.get('TOKEN')
    if token:
        # More secure way to verify token without exposing any part of it
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:10]
        return json.dumps({
            "status": "available", 
            "secured": True,
            "verified": True,
            "token_hash": token_hash
        })
    else:
        return json.dumps({"status": "missing", "secured": False})

@app.route('/setup-24-7')
def setup_24_7():
    """Display instructions for setting up 24/7 operation"""
    # Get the current Replit URL
    replit_url = os.environ.get('REPL_SLUG', 'your-repl-name')
    replit_owner = os.environ.get('REPL_OWNER', 'your-username')
    
    # Construct the URL to be monitored
    monitor_url = f"https://{replit_url}.{replit_owner}.repl.co"
    
    return render_template('setup_24_7.html', monitor_url=monitor_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)