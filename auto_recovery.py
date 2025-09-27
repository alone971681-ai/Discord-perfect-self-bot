"""
Auto-recovery System for Discord Selfbot
This module handles automatic recovery from common errors and ensures 24/7 uptime
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

logger = logging.getLogger("AutoRecovery")

class AutoRecoverySystem:
    """
    Automatic recovery system for the Discord selfbot.
    Monitors the bot for crashes and restarts it when necessary.
    """
    
    def __init__(self, max_restarts=10, cooldown_period=3600):
        """
        Initialize the auto-recovery system.
        
        Args:
            max_restarts: Maximum number of restarts allowed in the cooldown period
            cooldown_period: Time period (in seconds) for restart count
        """
        self.max_restarts = max_restarts
        self.cooldown_period = cooldown_period
        self.restart_times = []
        self.bot_process = None
        self.monitor_thread = None
        self.running = False
        self.last_error = None
        
        # Create a semaphore for restart operations
        self.restart_lock = threading.Semaphore(1)
        
        # Register signal handlers for clean shutdown
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
    
    def start_bot(self):
        """Start the Discord selfbot process"""
        try:
            # Start the bot as a subprocess
            logger.info("Starting Discord selfbot process...")
            
            # Check if TOKEN is available
            if not os.environ.get('TOKEN'):
                logger.error("TOKEN environment variable not set! Cannot start bot.")
                return False
            
            self.bot_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            logger.info(f"Bot process started with PID: {self.bot_process.pid}")
            return True
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            self.last_error = traceback.format_exc()
            return False
    
    def monitor_bot(self):
        """Monitor the bot process and restart if it crashes"""
        while self.running:
            if self.bot_process is None:
                logger.warning("Bot process not found, attempting to start...")
                self.restart_bot()
                time.sleep(10)  # Wait before checking again
                continue
                
            # Check if process is still running
            returncode = self.bot_process.poll()
            if returncode is not None:
                logger.warning(f"Bot process exited with code: {returncode}")
                
                # Capture error output if available
                stderr = self.bot_process.stderr.read() if self.bot_process.stderr else None
                if stderr and stderr.strip():
                    logger.error(f"Bot error output: {stderr}")
                    self.last_error = stderr
                
                # Restart the bot
                self.restart_bot()
            
            # Process stdout for logging
            self._process_bot_output()
            
            # Check every 5 seconds
            time.sleep(5)
    
    def _process_bot_output(self):
        """Process and log bot output"""
        if not self.bot_process or not self.bot_process.stdout:
            return
            
        # Read any available output without blocking
        try:
            while True:
                line = self.bot_process.stdout.readline()
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    logger.info(f"Bot output: {line}")
        except Exception as e:
            logger.debug(f"Error reading bot output: {e}")
    
    def restart_bot(self):
        """Restart the bot with rate limiting to prevent excessive restarts"""
        # Use the semaphore to ensure only one restart happens at a time
        if not self.restart_lock.acquire(blocking=False):
            logger.debug("Restart already in progress, skipping")
            return
            
        try:
            # Check if we've exceeded restart limit
            current_time = time.time()
            self.restart_times = [t for t in self.restart_times if current_time - t < self.cooldown_period]
            
            if len(self.restart_times) >= self.max_restarts:
                logger.error(
                    f"Too many restarts ({len(self.restart_times)}) in the past {self.cooldown_period/3600} hours. "
                    f"Waiting before attempting another restart."
                )
                time.sleep(60)  # Forced cooldown
                return
                
            # Terminate existing process if it's running
            if self.bot_process:
                logger.info("Terminating existing bot process...")
                try:
                    self.bot_process.terminate()
                    self.bot_process.wait(timeout=5)
                except Exception as e:
                    logger.warning(f"Error terminating bot process: {e}")
                    try:
                        self.bot_process.kill()
                    except:
                        pass
            
            # Record this restart attempt
            self.restart_times.append(current_time)
            
            # Start the bot again
            logger.info(f"Restarting bot (Restart #{len(self.restart_times)} in cooldown period)")
            success = self.start_bot()
            
            if success:
                logger.info("Bot restarted successfully")
            else:
                logger.error("Failed to restart bot")
        finally:
            # Release the semaphore
            self.restart_lock.release()
    
    def start(self):
        """Start the auto-recovery system"""
        if self.running:
            logger.warning("Auto-recovery system already running")
            return
            
        logger.info("Starting auto-recovery system...")
        self.running = True
        
        # Start the bot
        self.start_bot()
        
        # Start the monitor thread
        self.monitor_thread = threading.Thread(target=self.monitor_bot, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Auto-recovery system started")
    
    def stop(self):
        """Stop the auto-recovery system and the bot"""
        if not self.running:
            return
            
        logger.info("Stopping auto-recovery system...")
        self.running = False
        
        # Stop the bot process
        if self.bot_process:
            try:
                self.bot_process.terminate()
                self.bot_process.wait(timeout=5)
            except Exception as e:
                logger.warning(f"Error terminating bot process: {e}")
                try:
                    self.bot_process.kill()
                except:
                    pass
        
        # Wait for monitor thread to end
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("Auto-recovery system stopped")
    
    def handle_shutdown(self, signum, frame):
        """Handle termination signals for clean shutdown"""
        logger.info(f"Received signal {signum}, shutting down cleanly...")
        self.stop()
        sys.exit(0)

    def get_status(self):
        """Get the current status of the auto-recovery system"""
        return {
            "running": self.running,
            "bot_running": self.bot_process is not None and self.bot_process.poll() is None,
            "restart_count": len(self.restart_times),
            "last_error": self.last_error,
            "last_restart": datetime.fromtimestamp(self.restart_times[-1]).strftime('%Y-%m-%d %H:%M:%S') if self.restart_times else None
        }

# Singleton instance
recovery_system = AutoRecoverySystem()

def start_recovery():
    """Start the auto-recovery system"""
    recovery_system.start()

def stop_recovery():
    """Stop the auto-recovery system"""
    recovery_system.stop()

def get_recovery_status():
    """Get the status of the auto-recovery system"""
    return recovery_system.get_status()

# For direct execution
if __name__ == "__main__":
    logger.info("Starting auto-recovery system in standalone mode")
    recovery_system.start()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(60)
            status = recovery_system.get_status()
            logger.info(f"Auto-recovery status: Bot running: {status['bot_running']}, Restart count: {status['restart_count']}")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        recovery_system.stop()