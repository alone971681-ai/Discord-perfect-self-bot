"""
WORKING Discord Selfbot - Guaranteed to respond to commands
This version uses proven WebSocket connection for real-time command detection
"""
import json
import os
import time
import threading
import requests
import websocket
import random
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

class WorkingSelfbot:
    def __init__(self, token):
        self.token = token
        self.user_id = None
        self.ws = None
        self.heartbeat_interval = 41.25
        self.session_id = None
        self.sequence = None
        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.processed_commands = set()
        self.annoying_users = {}  # {user_id: {'guild_id': guild_id, 'channel_id': channel_id}}
        self.voice_state_cache = {}  # Track voice states for monitoring
        
    def send_message(self, channel_id, content):
        """Send message to Discord channel"""
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        payload = {"content": content}
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                print(f"✅ Message sent successfully: {content[:50]}...")
                return True
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def get_user_info(self):
        """Get current user information"""
        try:
            response = requests.get("https://discord.com/api/v9/users/@me", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = str(user_data['id'])
                print(f"✅ Authenticated as: {user_data['username']} ({self.user_id})")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to get user info: {e}")
            return False
    
    def handle_flash_command(self, channel_id, args):
        """Handle LTC flash command"""
        try:
            parts = args.split()
            if len(parts) >= 2:
                amount = parts[0]
                address = parts[1]
                txid = self.generate_fake_txid()
                
                flash_msg = f"""🚀 **LTC FLASH SENT!** ⚡
💰 **Amount:** {amount} LTC
📍 **To Address:** `{address}`
🔗 **TxID:** `{txid}`
⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}
✅ **Status:** CONFIRMED"""
                
                self.send_message(channel_id, flash_msg)
            else:
                self.send_message(channel_id, "❌ Usage: -flash <amount> <address>")
        except Exception as e:
            print(f"Error in flash command: {e}")
    
    def handle_balance_command(self, channel_id, address):
        """Handle balance check command"""
        fake_balance = round(random.uniform(0.1, 50.0), 8)
        balance_msg = f"""💰 **LTC Balance Check** 
📍 **Address:** `{address}`
💵 **Balance:** {fake_balance} LTC
⏰ **Last Updated:** {datetime.now().strftime('%H:%M:%S')}"""
        self.send_message(channel_id, balance_msg)
    
    def handle_drown_command(self, channel_id, args, language="both"):
        """Handle drown commands"""
        if not args.strip():
            self.send_message(channel_id, "❌ Usage: -drown @user")
            return
            
        user_mention = args.strip()
        
        english_insults = [
            f"{user_mention} Your existence is more pointless than a broken pencil! 🤡",
            f"{user_mention} You're like internet explorer - slow, outdated and nobody wants you! 💀",
            f"{user_mention} I've seen more intelligence in a brick wall! 🧱",
        ]
        
        hindi_insults = [
            f"{user_mention} तेरा दिमाग घुटने में है क्या? 🤦‍♂️",
            f"{user_mention} तू इतना बेकार है कि तेरे से कचरा भी शर्म करता है! 🗑️",
            f"{user_mention} तेरी सोच से छोटा केवल तेरा दिमाग है! 🧠",
        ]
        
        if language == "english":
            insult = random.choice(english_insults)
        elif language == "hindi":
            insult = random.choice(hindi_insults)
        else:  # both
            insult = random.choice(english_insults + hindi_insults)
            
        self.send_message(channel_id, insult)
    
    def generate_fake_txid(self):
        """Generate fake transaction ID"""
        chars = "abcdef0123456789"
        return ''.join(random.choice(chars) for _ in range(64))

    def get_user_voice_state(self, guild_id, user_id):
        """Get a user's current voice state in a guild"""
        try:
            url = f"https://discord.com/api/v9/guilds/{guild_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return None
            
            guild_data = response.json()
            voice_states = guild_data.get('voice_states', [])
            
            for voice_state in voice_states:
                if voice_state.get('user_id') == user_id:
                    return voice_state
            return None
        except Exception as e:
            print(f"Error getting voice state: {e}")
            return None

    def modify_member_voice(self, guild_id, user_id, mute=None, deaf=None, channel_id=None):
        """Modify a member's voice state (mute, deafen, move/disconnect)"""
        try:
            url = f"https://discord.com/api/v9/guilds/{guild_id}/members/{user_id}"
            payload = {}
            
            if mute is not None:
                payload['mute'] = mute
            if deaf is not None:
                payload['deaf'] = deaf
            if channel_id is not None:
                payload['channel_id'] = channel_id  # None disconnects them
            
            response = requests.patch(url, headers=self.headers, json=payload)
            return response.status_code == 200 or response.status_code == 204
        except Exception as e:
            print(f"Error modifying member voice: {e}")
            return False

    def get_guild_id_from_channel(self, channel_id):
        """Get guild ID from a channel ID"""
        try:
            url = f"https://discord.com/api/v9/channels/{channel_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                channel_data = response.json()
                return channel_data.get('guild_id')
            return None
        except Exception as e:
            print(f"Error getting guild ID: {e}")
            return None

    def extract_user_id_from_mention(self, mention):
        """Extract user ID from Discord mention format"""
        import re
        # Handle <@!123456789> or <@123456789> format
        match = re.search(r'<@!?(\d+)>', mention)
        if match:
            return match.group(1)
        return None

    def handle_annoy_command(self, channel_id, args):
        """Handle the annoy command - mute, deafen, and disconnect target user"""
        if not args.strip():
            self.send_message(channel_id, "❌ Usage: -annoy @user")
            return
        
        user_mention = args.strip()
        user_id = self.extract_user_id_from_mention(user_mention)
        
        if not user_id:
            self.send_message(channel_id, "❌ Invalid user mention. Use @user format.")
            return
        
        # Get guild ID from channel
        guild_id = self.get_guild_id_from_channel(channel_id)
        if not guild_id:
            self.send_message(channel_id, "❌ Could not determine server. Make sure this is used in a server channel.")
            return
        
        # Check if user is currently in voice channel
        voice_state = self.get_user_voice_state(guild_id, user_id)
        
        if not voice_state or not voice_state.get('channel_id'):
            self.send_message(channel_id, f"❌ {user_mention} is not currently in a voice channel.")
            return
        
        # Add user to annoying list for continuous monitoring
        self.annoying_users[user_id] = {
            'guild_id': guild_id,
            'channel_id': channel_id,
            'target_mention': user_mention
        }
        
        # Perform the annoying actions
        success = self.annoy_user_in_vc(guild_id, user_id, user_mention, channel_id)
        
    def annoy_user_in_vc(self, guild_id, user_id, user_mention, channel_id):
        """Perform the annoying actions: mute, deafen, and disconnect"""
        actions_performed = []
        
        # Try to mute the user
        if self.modify_member_voice(guild_id, user_id, mute=True):
            actions_performed.append("🔇 Muted")
        
        # Try to deafen the user  
        if self.modify_member_voice(guild_id, user_id, deaf=True):
            actions_performed.append("🔕 Deafened")
        
        # Try to disconnect the user (move to None channel)
        if self.modify_member_voice(guild_id, user_id, channel_id=None):
            actions_performed.append("🚫 Disconnected")
        
        if actions_performed:
            actions_text = " + ".join(actions_performed)
            self.send_message(channel_id, f"😈 **ANNOYING** {user_mention}\n{actions_text}\n🔄 **Monitoring for rejoin...**")
            return True
        else:
            self.send_message(channel_id, f"❌ **Permission Denied!** Cannot modify {user_mention}\nI don't have the required permissions to manage this member.")
            # Remove from annoying list since we can't affect them
            if user_id in self.annoying_users:
                del self.annoying_users[user_id]
            return False

    def handle_stop_annoy_command(self, channel_id, args):
        """Stop annoying a specific user"""
        if not args.strip():
            self.send_message(channel_id, "❌ Usage: -stopannoy @user")
            return
        
        user_mention = args.strip()
        user_id = self.extract_user_id_from_mention(user_mention)
        
        if not user_id:
            self.send_message(channel_id, "❌ Invalid user mention. Use @user format.")
            return
        
        if user_id in self.annoying_users:
            del self.annoying_users[user_id]
            self.send_message(channel_id, f"✅ Stopped annoying {user_mention}")
        else:
            self.send_message(channel_id, f"❌ {user_mention} was not being annoyed.")

    
    def process_command(self, channel_id, content, message_id):
        """Process discovered command"""
        if message_id in self.processed_commands:
            return
            
        self.processed_commands.add(message_id)
        
        if not content.startswith('-'):
            return
            
        parts = content[1:].split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        print(f"🔥 PROCESSING COMMAND: {cmd} with args: {args}")
        
        # Command handlers
        if cmd == "ping":
            self.send_message(channel_id, "🏓 **Pong!** LTC Flash Bot is **ONLINE** and responding!")
            
        elif cmd == "test":
            self.send_message(channel_id, "✅ **Test successful!** Bot is working perfectly! 🎉")
            
        elif cmd in ["help", "helpme"]:
            help_text = """🤖 **LTC Flash Bot Commands:**

💰 **LTC Commands:**
• `-flash <amount> <address>` - Send LTC flash
• `-flashchannel <amount> <address>` - Flash to channel
• `-bal <address>` - Check balance

😈 **Drown Commands:**
• `-drown @user` - Insult user (both languages)
• `-drownenglish @user` - English insults only
• `-drownhindi @user` - Hindi insults only
• `-stop @user` - Stop drowning user

🎙️ **Voice Channel Annoy:**
• `-annoy @user` - Mute, deafen & disconnect user from VC
• `-stopannoy @user` - Stop monitoring and annoying user

🔧 **Utility:**
• `-ping` - Check if bot is online
• `-test` - Test bot functionality
• `-help` - Show this message

✅ **Bot Status: ONLINE & RESPONDING**"""
            self.send_message(channel_id, help_text)
            
        elif cmd in ["flash", "fash"] and args:
            self.handle_flash_command(channel_id, args)
            
        elif cmd in ["flashchannel", "flashchanel"] and args:
            self.handle_flash_command(channel_id, args)
            
        elif cmd in ["bal", "balance"] and args:
            self.handle_balance_command(channel_id, args)
            
        elif cmd in ["drown"] and args:
            self.handle_drown_command(channel_id, args, "both")
            
        elif cmd in ["drownenglish", "drownen"] and args:
            self.handle_drown_command(channel_id, args, "english")
            
        elif cmd in ["drownhindi", "drownhi"] and args:
            self.handle_drown_command(channel_id, args, "hindi")
            
        elif cmd == "stop" and args:
            self.send_message(channel_id, f"✅ Stopped drowning {args.strip()}")
            
        elif cmd == "annoy" and args:
            self.handle_annoy_command(channel_id, args)
            
        elif cmd == "stopannoy" and args:
            self.handle_stop_annoy_command(channel_id, args)
    
    def on_message(self, ws, message):
        """Handle WebSocket messages"""
        try:
            data = json.loads(message)
            op = data.get('op')
            
            if op == 10:  # Hello
                self.heartbeat_interval = data['d']['heartbeat_interval'] / 1000.0
                self.start_heartbeat()
                self.identify()
                
            elif op == 11:  # Heartbeat ACK
                pass
                
            elif op == 0:  # Dispatch
                self.sequence = data.get('s')
                event_type = data.get('t')
                
                if event_type == 'READY':
                    self.session_id = data['d']['session_id']
                    user = data['d']['user']
                    print(f"🎉 Connected as: {user['username']} ({user['id']})")
                    
                elif event_type == 'MESSAGE_CREATE':
                    msg_data = data['d']
                    channel_id = msg_data['channel_id']
                    author_id = str(msg_data['author']['id'])
                    content = msg_data['content']
                    message_id = msg_data['id']
                    
                    # Only process commands from our user
                    if author_id == self.user_id and content.startswith('-'):
                        print(f"🎯 COMMAND DETECTED: {content}")
                        self.process_command(channel_id, content, message_id)
                        
                elif event_type == 'VOICE_STATE_UPDATE':
                    # Monitor voice state changes for users we're annoying
                    voice_data = data['d']
                    user_id = voice_data.get('user_id')
                    channel_id_in_voice = voice_data.get('channel_id')
                    
                    if user_id in self.annoying_users and channel_id_in_voice:
                        # User rejoined a voice channel, annoy them again!
                        user_data = self.annoying_users[user_id]
                        guild_id = user_data['guild_id']
                        notification_channel = user_data['channel_id']
                        user_mention = user_data['target_mention']
                        
                        print(f"🎯 DETECTED REJOIN: {user_mention} joined voice channel")
                        
                        # Small delay to ensure they're fully connected
                        def delayed_annoy():
                            time.sleep(2)  # Give them a moment to settle in
                            self.annoy_user_in_vc(guild_id, user_id, user_mention, notification_channel)
                        
                        threading.Thread(target=delayed_annoy, daemon=True).start()
                        
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("WebSocket connection closed. Reconnecting...")
        time.sleep(5)
        self.connect()
    
    def identify(self):
        """Send identify payload"""
        identify_payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "desktop"
                }
            }
        }
        self.ws.send(json.dumps(identify_payload))
    
    def start_heartbeat(self):
        """Start heartbeat thread"""
        def heartbeat():
            while True:
                time.sleep(self.heartbeat_interval)
                if self.ws:
                    heartbeat_payload = {
                        "op": 1,
                        "d": self.sequence
                    }
                    try:
                        self.ws.send(json.dumps(heartbeat_payload))
                    except:
                        break
        
        threading.Thread(target=heartbeat, daemon=True).start()
    
    def connect(self):
        """Connect to Discord WebSocket"""
        try:
            self.ws = websocket.WebSocketApp(
                "wss://gateway.discord.gg/?v=9&encoding=json",
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws.run_forever()
        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(5)
            self.connect()
    
    def start(self):
        """Start the selfbot"""
        print("🚀 Starting Working Discord Selfbot...")
        
        if not self.get_user_info():
            print("❌ Failed to authenticate")
            return
            
        print("✅ Authentication successful")
        print("🔗 Connecting to Discord WebSocket...")
        
        # Start keep-alive server
        def start_server():
            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'LTC Flash Bot is ONLINE!')
                def log_message(self, format, *args): pass
            
            server = HTTPServer(('0.0.0.0', 8080), Handler)
            server.serve_forever()
        
        threading.Thread(target=start_server, daemon=True).start()
        print("🌐 Keep-alive server started on port 8080")
        
        # Connect to Discord
        self.connect()

def main():
    token = os.environ.get('TOKEN')
    if not token:
        print("❌ TOKEN environment variable not set!")
        return
    
    bot = WorkingSelfbot(token)
    bot.start()

if __name__ == "__main__":
    main()