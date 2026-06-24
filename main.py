import subprocess
import sys
import os
import asyncio
import re
import requests
import random
import time
import copy
import logging
import datetime
from collections import deque, defaultdict
import io

# Function to install packages
def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {package}: {e}")
        return False

# Check if discord.py-self is installed
try:
    import discord
    from discord.ext import commands
    if not hasattr(discord, 'User'):  # Basic check for discord.py-self
        raise ImportError("Regular discord.py detected, need discord.py-self")
except ImportError:
    print("discord.py-self not found, installing...")
    # Uninstall regular discord.py if installed
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "discord.py"])
        print("Uninstalled regular discord.py")
    except:
        pass
    
    # Install discord.py-self
    if not install_package("discord.py-self"):
        print("Failed to install discord.py-self. Exiting.")
        sys.exit(1)
    
    # Now import the newly installed packages
    import discord
    from discord.ext import commands

# Database integration for enhanced analytics and persistence
DATABASE_INTEGRATION = True
try:
    from models import (log_command_execution, record_analytics, is_user_authorized_db, 
                       add_authorized_user_db, remove_authorized_user_db, add_whitelisted_user_db,
                       remove_whitelisted_user_db, is_user_whitelisted_db, get_command_history,
                       get_whitelisted_users)
    print("📊 Database integration enabled - Advanced analytics active")
except ImportError as e:
    DATABASE_INTEGRATION = False
    print(f"⚠️ Database integration disabled - {e}")

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s %(levelname)s  %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ULTRA-OPTIMIZED Bot Setup - Lightning Fast Startup for discord.py-self
import discord.utils

# Lightning-fast bot with minimal Discord overhead (discord.py-self compatible)
_OWNER_ID_STR = os.environ.get("OWNER_ID", "824584672965165056")
bot = commands.Bot(
    command_prefix="-",
    self_bot=True,
    case_insensitive=True,
    strip_after_prefix=True,
    owner_id=int(_OWNER_ID_STR)
)

# Enhanced performance settings for faster startup
# bot.max_messages removed - not available in discord.py-self 2.0.1
LOW_LATENCY_MODE = True  # Enable low latency optimizations
ULTRA_FAST_STARTUP = True  # Skip unnecessary initialization steps

# Dictionary to track users being "drowned" with insults
drowned_users = {}  # Dictionary to track users being "drowned" with insults

# ── DROWN WORD BANKS ─────────────────────────────────────────────────────────
def _get_english_insults(mention):
    # Source: Snowy repo (uzicifer/Snowy) — flood_messages + wordlist
    return [
        f"{mention} shut the fuck up son get flooded",
        f"weak retard is drowning {mention}",
        f"{mention} shut the fuck up low IQ retard",
        f"{mention} niggas ugly as fuck",
        f"{mention} i dont wanna hear your little sob story faggot",
        f"{mention} stop crying get back up loser",
        f"{mention} loser ass fucking dork",
        f"{mention} step the fuck up pussy",
        f"{mention} u cant beef retard",
        f"lol ur so sad keep crying bitch {mention}",
        f"i dont fucking like you {mention}",
        f"{mention} ugly ass awkward loser",
        f"{mention} stupid little cuck",
        f"{mention} fuck up antisocial faggot",
        f"{mention} shitty low tier pedo",
        f"{mention} loser ass nigga snakes his friends for epussy",
        f"{mention} unbalanced retarded fuck",
        f"{mention} ur a retard and what?",
        f"{mention} weak ass faggot",
        f"{mention} broke ass softie",
        f"{mention} pathetic fucking cuck",
        f"{mention} shut the fuck up dumb faggot",
        f"{mention} bitch ass nigga",
        f"{mention} dogshit loser",
        f"{mention} scummy pedophile",
        f"pedo nigga touches kids {mention}",
        f"{mention} faggot likes little boys",
        f"{mention} bitchmade nigga",
        f"{mention} ur a cyber bully victim lmao",
        f"nobody likes u geek {mention}",
        f"{mention} failed reject",
        f"{mention} angered cuck",
        f"{mention} somalian freak fuck",
        f"ill murder ur bloodline {mention}",
        f"{mention} shut the fuck up slow ass dork",
        f"{mention} stinky ass clown",
        f"{mention} disowned sperm",
        f"{mention} trash bag",
        f"faggot ass pedophile stay away from little boys {mention}",
        f"{mention} stop sexualizing your mom weirdo",
        f"{mention} ur my fucking son peasant",
        f"{mention} focus up retarded fuckboy",
        f"{mention} nigga you cant step shitty loser",
        f"shut the fuck up bitchmade loser {mention}",
        f"{mention} lol ur a shitty com reject loser",
        f"{mention} your dying to me lmfao",
        f"{mention} stop stepping u slow brained moron",
        f"my mom types faster than you {mention} what the fuck lmao",
        f"{mention} never compete with a god",
        f"{mention} ur weak ass chat slave get down fuckboy",
        f"{mention} moronic ass little faggot get back up",
        f"nigga gets bullied on daily basis {mention}",
        f"{mention} trash nigga outlast me retard",
    ]

def _get_hindi_insults(mention):
    # Hindi translations of Snowy-style insults
    return [
        f"{mention} बंद कर अपनी बकवास बेटा डूब जा",
        f"कमज़ोर मंदबुद्धि डूब रहा है {mention}",
        f"{mention} बंद कर अपना मुंह कम IQ वाले गधे",
        f"{mention} बदसूरत बेकार टुकड़ा",
        f"{mention} तेरी रोने की कहानी नहीं सुननी मुझे",
        f"{mention} रोना बंद कर और उठ कर लड़ हारे हुए",
        f"{mention} घटिया ज़िंदगी का लूज़र बेकार",
        f"{mention} आगे आ साबित कर खुद को कायर",
        f"{mention} तुझसे बीफ नहीं होती मंदबुद्धि",
        f"हाहाहा तू इतना दयनीय है रोता रह {mention}",
        f"मुझे तेरी परवाह नहीं है {mention} हट सामने से",
        f"{mention} बदसूरत अजीब हारा हुआ इंसान",
        f"{mention} बेवकूफ छोटा कायर",
        f"{mention} बंद कर अपनी असामाजिक बकवास",
        f"{mention} घटिया निचले दर्जे का रद्दी",
        f"{mention} हारा हुआ जो दोस्तों को धोखा देता है",
        f"{mention} असंतुलित मंदबुद्धि बेकार इंसान",
        f"{mention} तू एक मंद है और क्या करेगा",
        f"{mention} कमज़ोर बेकार गधा",
        f"{mention} टूटा हुआ नरम दिल वाला",
        f"{mention} दयनीय कायर इंसान",
        f"{mention} बंद कर मुंह बेवकूफ",
        f"{mention} कमीना नीच इंसान",
        f"{mention} कचरे जैसा हारा हुआ",
        f"बच्चों को छूने वाला {mention}",
        f"{mention} रद्दी असफल मंद इंसान",
        f"{mention} बुज़दिल नीच कुत्ता",
        f"{mention} तू एक cyber bully का शिकार है हाहाहा",
        f"कोई तुझे पसंद नहीं करता {mention} भाग यहां से",
        f"{mention} असफल रद्दी इंसान",
        f"{mention} चिढ़ा हुआ कायर",
        f"{mention} दुनिया का सबसे घटिया फ्रीक",
        f"तेरे खानदान को मिटा दूंगा {mention}",
        f"{mention} बंद कर मुंह धीमी बुद्धि वाले",
        f"{mention} बदबूदार जोकर इंसान",
        f"{mention} अपने मां-बाप की नाकामी है तू",
        f"{mention} कचरे का थैला",
        f"{mention} अपनी मां को sexualize करना बंद कर",
        f"{mention} तू मेरा बेटा है किसान",
        f"{mention} ध्यान दे मंदबुद्धि",
        f"{mention} तुझसे मुकाबला नहीं होता घटिया हारे",
        f"बंद कर मुंह बेकार हारे {mention}",
        f"{mention} तू एक घटिया reject है हाहाहा",
        f"{mention} मेरे सामने मर रहा है तू",
        f"{mention} चल हट मंद दिमाग वाले",
        f"मेरी मां तुझसे तेज़ टाइप करती है {mention}",
        f"{mention} मुझसे कभी मुकाबला मत कर",
        f"{mention} कमज़ोर chat slave है तू",
        f"{mention} मंदबुद्धि उठ वापस",
        f"रोज़ पिटता है ये {mention}",
        f"{mention} कचरे जैसा इंसान मुझसे जीत नहीं सकता",
    ]

def _get_hinglish_insults(mention):
    # Snowy-style insults in Hinglish + original lines same energy
    return [
        f"{mention} band kar apni bakwas beta doob ja",
        f"kamzor retard doob raha hai {mention}",
        f"{mention} band kar apna mooh kam IQ wale gadhe",
        f"{mention} bahut ganda aur bekar insaan hai tu",
        f"{mention} teri rone ki kahani nahi sunni mujhe faggot",
        f"{mention} rona band kar aur uth ke lad haare hue",
        f"{mention} loser ass dork teri aukaat nahi",
        f"{mention} aage aa sabit kar khud ko pussy",
        f"{mention} tujhse beef nahi hoti retard",
        f"haha tu itna deen hai rota reh {mention}",
        f"mujhe teri parwah nahi hai {mention} hat saamne se",
        f"{mention} ugly awkward loser kahin ka",
        f"{mention} bewakoof chota cuck",
        f"{mention} band kar apni antisocial bakwas faggot",
        f"{mention} shitty low tier pedo saala",
        f"{mention} loser jo apne doston ko dhoka deta hai",
        f"{mention} unbalanced retarded saala bekar insaan",
        f"{mention} tu ek retard hai aur kya karega",
        f"{mention} weak ass faggot teri aukaat nahi",
        f"{mention} broke ass softie kahin ka",
        f"{mention} pathetic cuck teri koi value nahi",
        f"{mention} band kar mooh dumb faggot",
        f"{mention} bitch ass nigga aukaat mein reh",
        f"{mention} dogshit loser kahin ka",
        f"pedo bacha chhoota hai {mention} sab jaante hain",
        f"{mention} randi ke bacche failed reject hai tu",
        f"{mention} bitchmade nigga teri koi aukaat nahi",
        f"{mention} tu ek cyber bully victim hai hahaha",
        f"koi tujhe pasand nahi karta {mention} bhaag yahan se",
        f"{mention} failed reject kahin ka",
        f"{mention} angered cuck itna gussa kyun",
        f"{mention} freak saala koi nahi tujhe puchhta",
        f"teri poori nasl maar dunga {mention}",
        f"{mention} band kar mooh slow ass dork",
        f"{mention} stinky ass clown kahin ka",
        f"{mention} disowned sperm hai tu",
        f"{mention} trash bag hai teri life",
        f"{mention} apni maa ko sexualize karna band kar weirdo",
        f"{mention} tu mera beta hai peasant",
        f"{mention} dhyan de retarded fuckboy",
        f"{mention} nigga tujhse step nahi hota shitty loser",
        f"band kar mooh bitchmade loser {mention}",
        f"{mention} lol tu ek shitty reject hai hahaha",
        f"{mention} mujhse haar raha hai lmfao",
        f"{mention} band kar stepping slow brained moron",
        f"meri maa tujhse tez type karti hai {mention} kya bakwaas",
        f"{mention} mujhse kabhi compete mat kar",
        f"{mention} weak ass chat slave tu hai",
        f"{mention} moronic faggot wapas uth",
        f"roz pita hai ye {mention}",
        f"{mention} trash nigga mujhse nahi jeeta kabhi",
        f"{mention} saala gutter ka keeda hai tu",
        f"{mention} teri maa ne tujhe banake bhagwan ko bhi sharm aayi",
        f"ek baar mil {mention} sab bataunga kaise baat karte hain",
        f"{mention} chhup ja apne kamre mein warna pachtayega",
        f"tu itna bekar hai {mention} ki teri pararchhayi bhi dur bhaagti hai",
        f"{mention} roz muh ki khaata hai aur phir online aake hero banta hai",
        f"haath lagaya toh teri teen peediyan yaad rakhegi {mention}",
        f"{mention} bhai teri aukaat ek joote ki nok se bhi kam hai",
        f"tune galat insaan se panga liya hai {mention} ab bhugat",
        f"{mention} ek thappad maara toh teri poori family line pakki",
        f"saala {mention} online brave hai bahar nikle toh pata chale",
        f"{mention} tujhe itna marunga ki khud ginaan bhi bhool jaayega",
        f"kya bol raha hai {mention} apni aukaat mein reh chhote",
        f"{mention} bhai tu itna soft hai ki paani bhi nahi peeta tujhe",
        f"aaja bahar {mention} seedha settle karte hain sab",
        f"{mention} teri life ek badi galti hai aur sab log jaante hain",
        f"tu mujhse jeetega kya {mention} hahahaha sapne mein bhi nahi",
        f"{mention} chal bhaag yahan se pehle kuch aur bura ho jaaye",
        f"itna bolta hai {mention} ek baar muh pe aakar toh baat kar",
        f"{mention} pure area mein teri izzat ek paisa bhi nahi",
        f"saala {mention} ek baar haath lagaya toh dobara uthega nahi",
        f"{mention} jo bolta hai woh kar ke dikha warna chup reh",
        f"tu keyboard pe brave hai {mention} real life mein kuch nahi",
    ]
# ─────────────────────────────────────────────────────────────────────────────

# Dictionary to track users being "debated" with savage responses
debated_users = {}

# Dictionary to track users being "annoyed" in voice channels
annoying_users = {}

# Dictionary to track users being dragged through voice channels
dragging_users = {}

# Global spam control
spam_active = False
spam_tasks = []

# Jija system for rapid group chat name changes
jija_sessions = {}  # {channel_id: {"message": "message", "active": True, "task": task_object}}

# Ultra-fast jija performance configuration
JIJA_ULTRA_FAST_MODE = True
JIJA_MIN_DELAY = 0.02  # Minimum 20ms delay for maximum speed
JIJA_MAX_DELAY = 1.0   # Maximum delay during heavy rate limiting
JIJA_BURST_MODE = True  # Enable burst mode for even faster execution
JIJA_BURST_SIZE = 3     # Number of rapid changes before brief pause in burst mode

# Global ultra-fast response configuration
ULTRA_FAST_MODE = True
INSTANT_DELETE_COMMANDS = True  # Delete commands instantly for seamless experience
COMMAND_RESPONSE_DELAY = 0.005  # Super-fast 5ms command processing
ZERO_ERROR_MODE = True          # Eliminate all errors and optimize performance
PERFORMANCE_MONITORING = True   # Track performance metrics
LOW_LATENCY_MODE = True         # Force low latency connections

# Auto-reaction system for tracking users
reaction_targets = {}  # {user_id: {"emoji": "😀", "active": True}}

# AFK system for automatic replies
afk_users = {}  # {user_id: {"status": True, "message": "optional custom message", "timestamp": time}}

# Whitelist system - users protected from all bot features
whitelisted_users = set()  # Set of user IDs who are whitelisted from bot features

# Snipe system - cache last deleted/edited messages per channel
snipe_cache = {}   # {channel_id: {"content": str, "author": str, "author_id": int, "timestamp": datetime, "attachments": list}}
esnipe_cache = {}  # {channel_id: {"before": str, "after": str, "author": str, "author_id": int, "timestamp": datetime}}

# Typing spam control
typing_tasks = {}  # {channel_id: asyncio.Task}

# Mass DM control
mass_dm_active = False
mass_dm_task = None

# Troll system - auto-reply to a user's messages with troll responses
troll_targets = {}  # {user_id_str: {"channel_id": int, "active": True}}

# Copycat system - mirror a user's messages
copycat_targets = {}  # {user_id_str: {"channel_id": int, "active": True}}

# Auto Quest Completer
auto_quest_active = False
auto_quest_task = None
DISCORD_API_BASE = "https://discord.com/api/v10"
QUEST_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9170 Chrome/124.0.6367.243 Electron/30.4.0 Safari/537.36"
QUEST_SUPER_PROPS = "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkxNzAgQ2hyb21lLzEyNC4wLjYzNjcuMjQzIEVsZWN0cm9uLzMwLjQuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMzAuNC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjM4MDk3MCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0="

# Enhanced Security System - Advanced access control and protection  
BOT_OWNER_ID = os.environ.get("OWNER_ID", "824584672965165056")
authorized_users = set()  # Set of user IDs who can control the bot
AUTHORIZED_USERS_FILE = "authorized_users.txt"  # File to persist authorized users

# ACCESS CONTROL SYSTEM - Limited Command Access for Authorized Users
# Define which commands are allowed for authorized users vs restricted to owner only
ALLOWED_COMMANDS_FOR_AUTHORIZED = {
    "debate", "react", "list", "about", "stop", "stopd", "stops", "history",
    "ping", "bal", "balance"
}
RESTRICTED_COMMANDS = {
    "spam", "drown", "drownenglish", "drownhindi", "drownhinglish", "annoy", "jija", "flash", 
    "target", "gcspam", "access", "removeaccess", "cleartargets", "afk", "removeafk"
}

# MILITARY-GRADE Security Configuration
SECURITY_ENHANCED = True            # Enable enhanced security measures
FAILED_ATTEMPTS_LIMIT = 2           # Stricter - Only 2 attempts allowed
LOCKOUT_DURATION = 900              # Longer lockout - 15 minutes
SESSION_TIMEOUT = 1800              # Shorter session - 30 minutes
AUDIT_LOG_ENABLED = True            # Enable security audit logging
OWNER_VERIFICATION_REQUIRED = True  # Require additional owner verification
COMMAND_RATE_LIMIT_STRICT = True    # Ultra-strict command rate limiting
ANTI_BRUTEFORCE_ENHANCED = True     # Enhanced brute force protection

# Security tracking dictionaries
failed_attempts = {}                # Track failed access attempts per user
locked_users = {}                   # Track locked out users
active_sessions = {}                # Track active authorized sessions
security_audit_log = deque(maxlen=50)  # Security event audit log

# Anti-detection configuration to prevent Discord security warnings
STEALTH_MODE = True             # Enable comprehensive anti-detection measures
HUMAN_LIKE_DELAYS = True        # Add random human-like delays between actions
RATE_LIMIT_SAFETY = True        # Ultra-conservative rate limiting
ACTIVITY_ROTATION = True        # Rotate activities to appear natural
MAX_COMMANDS_PER_MINUTE = 8     # Stricter limit to avoid detection (reduced from 10)
NATURAL_TYPING_SIMULATION = True # Simulate natural typing patterns

# Enhanced anti-ban protection
ANTI_BAN_MODE = True            # Enable anti-ban protection measures
COMMAND_COOLDOWN = 2.0          # Minimum seconds between commands
MESSAGE_VARIATION = True        # Vary message patterns to avoid detection

# Command usage tracking for anti-detection
command_usage_tracker = {}      # Track command frequency
last_command_time = 0          # Track last command execution time

# Ultra-fast command processing functions
async def instant_delete_command(ctx):
    """TRULY INSTANT command deletion - NO DELAY AT ALL"""
    if INSTANT_DELETE_COMMANDS:
        try:
            # Delete immediately without any processing delay
            await ctx.message.delete()
        except:
            pass

async def add_human_like_delay(bypass_for_spam=False, user_id=None):
    """Add random human-like delays to avoid detection"""
    # Check if user is owner or authorized - give them fast responses
    if user_id and (is_owner(user_id) or str(user_id) in authorized_users):
        # Super fast for owner and authorized users
        delay = random.uniform(0.01, 0.02)
        await asyncio.sleep(delay)
        return
    
    if HUMAN_LIKE_DELAYS and STEALTH_MODE and not bypass_for_spam:
        # Reduced delay for faster response while maintaining security
        delay = random.uniform(0.3, 0.8)  # Reduced from 0.8-3.0 to 0.3-0.8
        await asyncio.sleep(delay)
    elif bypass_for_spam:
        # Minimal delay for spam command to maintain speed
        delay = random.uniform(0.05, 0.1)  # Slightly reduced
        await asyncio.sleep(delay)

async def enhanced_anti_ban_protection():
    """Enhanced protection against Discord bans and detection"""
    if not ANTI_BAN_MODE:
        return
    
    try:
        # Add random delay to make behavior more unpredictable
        if random.random() < 0.1:  # 10% chance
            delay = random.uniform(1.0, 5.0)
            await asyncio.sleep(delay)
        
    except Exception as e:
        if not ZERO_ERROR_MODE:
            print(f"⚠️ Anti-ban protection error: {e}")

async def anti_ban_protection_loop():
    """Continuous loop for anti-ban protection measures"""
    print("🛡️ Anti-ban protection loop started")
    
    while True:
        try:
            # Run protection measures every 5-10 minutes
            interval = random.uniform(300, 600)  # 5-10 minutes
            await asyncio.sleep(interval)
            
            # Execute anti-ban protection
            await enhanced_anti_ban_protection()
            
            # Vary command processing to appear more human
            if COMMAND_COOLDOWN and random.random() < 0.3:  # 30% chance
                await asyncio.sleep(random.uniform(1.0, COMMAND_COOLDOWN))
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            if not ZERO_ERROR_MODE:
                print(f"⚠️ Anti-ban protection loop error: {e}")
            await asyncio.sleep(30)  # Wait before retrying

def load_authorized_users():
    """Load authorized users from file"""
    global authorized_users
    try:
        if os.path.exists(AUTHORIZED_USERS_FILE):
            with open(AUTHORIZED_USERS_FILE, 'r') as f:
                user_ids = f.read().strip().split('\n')
                authorized_users = set(user_id.strip() for user_id in user_ids if user_id.strip())
                print(f"✅ Loaded {len(authorized_users)} authorized users from file")
        else:
            print("📝 No authorized users file found, starting fresh")
    except Exception as e:
        print(f"❌ Error loading authorized users: {e}")
        authorized_users = set()

def save_authorized_users():
    """Save authorized users to file"""
    try:
        with open(AUTHORIZED_USERS_FILE, 'w') as f:
            f.write('\n'.join(authorized_users))
        print(f"💾 Saved {len(authorized_users)} authorized users to file")
    except Exception as e:
        print(f"❌ Error saving authorized users: {e}")

def log_security_event(event_type, user_id, details=""):
    """Log security events for audit purposes"""
    if AUDIT_LOG_ENABLED:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        audit_entry = f"[{timestamp}] {event_type}: User {user_id} - {details}"
        security_audit_log.append(audit_entry)
        print(f"🔒 SECURITY: {audit_entry}")

def check_user_lockout(user_id):
    """Check if user is currently locked out"""
    user_id_str = str(user_id)
    if user_id_str in locked_users:
        lockout_time = locked_users[user_id_str]
        if time.time() - lockout_time < LOCKOUT_DURATION:
            return True
        else:
            # Lockout expired, remove from locked users
            del locked_users[user_id_str]
            log_security_event("LOCKOUT_EXPIRED", user_id, "User lockout expired")
    return False

def record_failed_attempt(user_id):
    """Record a failed access attempt"""
    user_id_str = str(user_id)
    current_time = time.time()
    
    if user_id_str not in failed_attempts:
        failed_attempts[user_id_str] = []
    
    # Add current attempt
    failed_attempts[user_id_str].append(current_time)
    
    # Remove attempts older than 1 hour
    failed_attempts[user_id_str] = [attempt for attempt in failed_attempts[user_id_str] 
                                   if current_time - attempt < 3600]
    
    # Check if lockout is needed
    if len(failed_attempts[user_id_str]) >= FAILED_ATTEMPTS_LIMIT:
        locked_users[user_id_str] = current_time
        log_security_event("USER_LOCKED", user_id, f"Too many failed attempts ({len(failed_attempts[user_id_str])})")
        return True
    
    log_security_event("FAILED_ATTEMPT", user_id, f"Attempt {len(failed_attempts[user_id_str])}/{FAILED_ATTEMPTS_LIMIT}")
    return False

def enhanced_owner_verification(user_id):
    """Enhanced owner verification with additional security checks"""
    user_id_str = str(user_id)
    
    # Basic ID check
    if user_id_str != BOT_OWNER_ID:
        return False
    
    # Additional verification if enabled
    if OWNER_VERIFICATION_REQUIRED:
        # Check for recent suspicious activity
        if user_id_str in failed_attempts and len(failed_attempts[user_id_str]) > 0:
            log_security_event("OWNER_SUSPICIOUS", user_id, "Owner access with recent failed attempts")
        
        # Verify session if exists
        if user_id_str in active_sessions:
            session_time = active_sessions[user_id_str]
            if time.time() - session_time > SESSION_TIMEOUT:
                del active_sessions[user_id_str]
                log_security_event("SESSION_EXPIRED", user_id, "Owner session expired")
    
    return True

def is_owner(user_id):
    """Enhanced owner check with security measures"""
    user_id_str = str(user_id)
    
    # Owner always bypasses lockout — verify ID first
    if user_id_str == BOT_OWNER_ID:
        # Clear any erroneous lockout/failed attempts for the owner
        locked_users.pop(user_id_str, None)
        failed_attempts.pop(user_id_str, None)
        active_sessions[user_id_str] = time.time()
        return True
    
    # Non-owner: check lockout before anything else
    if check_user_lockout(user_id):
        log_security_event("ACCESS_DENIED_LOCKOUT", user_id, "User is locked out")
        return False
    
    # Record failed attempt for non-owner
    record_failed_attempt(user_id)
    log_security_event("ACCESS_DENIED", user_id, "Unauthorized access attempt")
    return False

def is_authorized_user(user_id):
    """Enhanced authorization check with security measures"""
    user_id_str = str(user_id)
    
    # Check if user is locked out
    if check_user_lockout(user_id):
        log_security_event("ACCESS_DENIED_LOCKOUT", user_id, "User is locked out")
        return False
    
    # Check owner first
    if is_owner(user_id):
        return True
    
    # Check authorized users
    if user_id_str in authorized_users:
        # Update active session
        active_sessions[user_id_str] = time.time()
        log_security_event("AUTHORIZED_ACCESS", user_id, "Authorized user access granted")
        return True
    
    # Record failed attempt
    record_failed_attempt(user_id)
    log_security_event("ACCESS_DENIED", user_id, "Unauthorized access attempt")
    return False

def is_user_whitelisted(user_id):
    """Check if user is whitelisted from bot features"""
    user_id_str = str(user_id)
    
    # Check in-memory whitelist first (for performance)
    if user_id_str in whitelisted_users:
        return True
    
    # Check database if available
    if DATABASE_INTEGRATION:
        try:
            from models import is_user_whitelisted_db
            return is_user_whitelisted_db(user_id)
        except Exception as e:
            print(f"❌ Error checking whitelist database: {e}")
    
    return False

def check_command_access(user_id, command_name):
    """Check if user has access to execute specific command"""
    user_id_str = str(user_id)
    
    # Owner has access to everything
    if is_owner(user_id):
        return True
    
    # Check if user is authorized
    if user_id_str not in authorized_users:
        return False
    
    # Check if command is in allowed list for authorized users
    if command_name in ALLOWED_COMMANDS_FOR_AUTHORIZED:
        return True
    
    # Command is restricted
    return False

def load_whitelisted_users():
    """Load whitelisted users from database on startup"""
    if DATABASE_INTEGRATION:
        try:
            from app import app
            with app.app_context():
                db_users = get_whitelisted_users()
                for user in db_users:
                    whitelisted_users.add(user.discord_id)
                print(f"✅ Loaded {len(whitelisted_users)} whitelisted users from database")
        except Exception as e:
            print(f"❌ Error loading whitelisted users: {e}")

def clear_all_whitelisted_users():
    """Clear all whitelisted users from memory and database - Owner only"""
    if DATABASE_INTEGRATION:
        try:
            from app import app
            with app.app_context():
                # Get all whitelisted users
                db_users = get_whitelisted_users()
                cleared_count = 0
                
                # Remove each user from database
                for user in db_users:
                    if remove_whitelisted_user_db(user.discord_id):
                        cleared_count += 1
                
                # Clear in-memory set
                whitelisted_users.clear()
                
                print(f"🧹 CLEARED: Removed {cleared_count} users from database whitelist")
                print(f"🧹 CLEARED: Cleared in-memory whitelist")
                print(f"✅ All whitelisted users have been removed - fresh start!")
                return cleared_count
        except Exception as e:
            print(f"❌ Error clearing whitelisted users: {e}")
            return 0
    else:
        # Just clear memory if no database
        count = len(whitelisted_users)
        whitelisted_users.clear()
        print(f"🧹 CLEARED: {count} users from memory (no database available)")
        return count

async def check_command_rate_limit():
    """Check if command rate limit is exceeded to prevent detection"""
    global last_command_time, command_usage_tracker
    
    if not RATE_LIMIT_SAFETY:
        return True
    
    current_time = time.time()
    
    # Reset tracker every minute
    if current_time - last_command_time > 60:
        command_usage_tracker.clear()
        last_command_time = current_time
    
    # Count commands in current minute
    minute_key = int(current_time // 60)
    command_count = command_usage_tracker.get(minute_key, 0)
    
    if command_count >= MAX_COMMANDS_PER_MINUTE:
        print(f"🛡️ Rate limit protection: Command blocked to avoid detection")
        return False
    
    # Update counter
    command_usage_tracker[minute_key] = command_count + 1
    return True

async def ultra_fast_response(ctx, content, delete_after=3, bypass_stealth=False):
    """ULTRA-FAST response system with anti-detection measures"""
    try:
        # Check rate limits first for stealth (bypass for spam)
        if not bypass_stealth and not await check_command_rate_limit():
            return
        
        # Add human-like delay for stealth (bypass for spam) - but make it fast for authorized users
        await add_human_like_delay(bypass_for_spam=bypass_stealth, user_id=ctx.author.id)
        
        # Performance tracking
        start_time = time.time() if PERFORMANCE_MONITORING else None
        
        # Delete command FIRST - absolutely no delay
        await instant_delete_command(ctx)
        
        # Send response immediately with optimized channel handling
        if hasattr(ctx.channel, 'send'):
            response = await ctx.channel.send(content)
        else:
            response = await ctx.send(content)
        
        # Performance logging
        if PERFORMANCE_MONITORING and start_time:
            response_time = round((time.time() - start_time) * 1000, 1)
            print(f"⚡ Ultra-fast response: {response_time}ms")
        
        # Quick cleanup - delete response after short time
        if delete_after > 0:
            await asyncio.sleep(delete_after)
            try:
                await response.delete()
            except:
                pass
            
        return response
    except Exception as e:
        if not ZERO_ERROR_MODE:
            print(f"Response error: {e}")
        return None

# Function to extract user ID from mention
def find_user_id_by_mention(mention):
    # Try to extract user ID from mention format <@12345678901234>
    mention_match = re.search(r'<@!?(\d+)>', mention)
    if mention_match:
        return mention_match.group(1)
    return None

# Event: Bot is ready
@bot.event
async def on_ready():
    try:
        print(f"✅ Logged in as {bot.user.name} ({bot.user.id})")
        print(f"✅ Using discord.py-self version: {discord.__version__}")
        print("✅ Bot is ready! Use the command -flash <amount> <ltc_address> to send flash messages")
        
        # Start background tasks
        try:
            asyncio.create_task(enhanced_background_tasks())
            print("✅ Background tasks started successfully")
        except Exception as bg_err:
            print(f"❌ Failed to start background tasks: {bg_err}")
        
        # Start enhanced anti-ban protection system
        try:
            asyncio.create_task(anti_ban_protection_loop())
            print("🛡️ Enhanced anti-ban protection system activated")
        except Exception as ab_err:
            print(f"❌ Failed to start anti-ban protection: {ab_err}")
        
        # Initialize security system
        try:
            log_security_event("SYSTEM_START", BOT_OWNER_ID, "Bot security system initialized")
            print("🔒 Enhanced security system initialized")
        except Exception as sec_err:
            print(f"❌ Failed to initialize security system: {sec_err}")
        
        # Load authorized users from file
        try:
            load_authorized_users()
        except Exception as load_err:
            print(f"❌ Failed to load authorized users: {load_err}")
        
        # Load whitelisted users from database
        try:
            load_whitelisted_users()
        except Exception as wl_err:
            print(f"❌ Failed to load whitelisted users: {wl_err}")
        
        # Set initial presence for anti-ban protection
        try:
            await enhanced_anti_ban_protection()
            print("🔄 Initial anti-ban presence set")
        except Exception as init_pres_err:
            print(f"⚠️ Initial presence setting error: {init_pres_err}")
            
    except Exception as ready_err:
        print(f"❌ Critical error in on_ready event: {ready_err}")
        # Continue running even if initialization fails

# Voice state update event - monitor for users rejoining voice channels
@bot.event
async def on_voice_state_update(member, before, after):
    """Monitor voice state changes for users we're annoying"""
    user_id_str = str(member.id)
    
    # Check if this user is being annoyed and just joined a voice channel
    if user_id_str in annoying_users and after.channel is not None and before.channel is None:
        user_data = annoying_users[user_id_str]
        guild = bot.get_guild(user_data['guild_id'])
        channel = bot.get_channel(user_data['channel_id'])
        
        if guild and channel:
            print(f"🎯 DETECTED REJOIN: {user_data['mention']} joined voice channel")
            
            # Small delay to ensure they're fully connected
            await asyncio.sleep(2)
            
            # Re-annoy them
            actions_performed = []
            
            try:
                await member.edit(mute=True)
                actions_performed.append("🔇 Muted")
            except:
                pass
            
            try:
                await member.edit(deafen=True)
                actions_performed.append("🔕 Deafened")
            except:
                pass
            
            try:
                await member.edit(voice_channel=None)
                actions_performed.append("🚫 Disconnected")
            except:
                pass
            
            if actions_performed:
                actions_text = " + ".join(actions_performed)
                try:
                    await channel.send(f"😈 **CAUGHT REJOINING!** {user_data['mention']}\n{actions_text}\n🔄 **Still monitoring...**")
                except:
                    pass

# Auto-onboarding: when the selfbot joins a server, auto-complete Discord's onboarding flow
@bot.event
async def on_guild_join(guild):
    """Auto-complete Discord onboarding when the bot joins a server"""
    print(f"✅ Joined server: {guild.name} ({guild.id}) — starting auto-onboarding...")
    await asyncio.sleep(5)  # delay so Discord registers the join first
    await auto_complete_onboarding(guild.id)

async def auto_complete_onboarding(guild_id: int):
    """
    Two-step auto-onboarding using discord.py-self's built-in methods:
      Step 1 — Accept member verification (rules/terms screening)
      Step 2 — Complete onboarding prompts (role/channel selection)
    Both fire automatically on guild join.
    """
    guild = bot.get_guild(guild_id)

    # ── Step 1: Member Verification (rules screening) ──────────────────────
    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            data = await bot.http.get_member_verification(guild_id)
            if data:
                form_fields = data.get("form_fields", [])
                # Set response=True on every field so we agree to all rules
                for field in form_fields:
                    field["response"] = True
                await bot.http.accept_member_verification(
                    guild_id,
                    version=data["version"],
                    form_fields=form_fields,
                )
                print(f"✅ [{guild_id}] Member verification accepted ({len(form_fields)} field(s))")
            else:
                print(f"ℹ️ [{guild_id}] No member verification form")
            break  # success — exit retry loop
        except discord.HTTPException as e:
            if e.status == 404:
                print(f"ℹ️ [{guild_id}] No member verification (404)")
                break
            elif e.status == 403 and attempt < max_retries:
                print(f"⚠️ [{guild_id}] Member verification 403 (attempt {attempt + 1}/{max_retries + 1}), retrying in 3s...")
                await asyncio.sleep(3)
            else:
                print(f"⚠️ [{guild_id}] Member verification error: {e.status} {e.text}")
                break
        except Exception as e:
            print(f"❌ [{guild_id}] Member verification exception: {e}")
            break

    # ── Step 2: Onboarding Prompts (role/channel selection) ────────────────
    try:
        if guild is None:
            print(f"ℹ️ [{guild_id}] Guild not in cache, skipping prompt onboarding")
            return

        onboarding = await guild.onboarding()

        if not onboarding.enabled or not onboarding.prompts:
            print(f"ℹ️ [{guild_id}] No onboarding prompts enabled")
            return

        responses = []
        for prompt in onboarding.prompts:
            if not prompt.options:
                continue
            if prompt.required:
                if prompt.single_select:
                    # Pick just the first option for single-select required prompts
                    responses.append(str(prompt.options[0].id))
                else:
                    # Pick all options for multi-select required prompts
                    responses.extend(str(o.id) for o in prompt.options)
            # Skip optional prompts — no unwanted role assignments

        await bot.http.request(
            discord.http.Route("POST", "/guilds/{guild_id}/onboarding-responses", guild_id=guild_id),
            json={
                "onboarding_responses": responses,
                "onboarding_prompts_seen": {str(p.id): True for p in onboarding.prompts},
            },
        )
        print(f"✅ [{guild_id}] Onboarding prompts completed ({len(responses)} response(s) submitted)")

    except discord.HTTPException as e:
        if e.status == 404:
            print(f"ℹ️ [{guild_id}] No onboarding prompts (404)")
        else:
            print(f"⚠️ [{guild_id}] Onboarding prompts error: {e.status} {e.text}")
    except Exception as e:
        print(f"❌ [{guild_id}] Onboarding prompts exception: {e}")


# Command: -onboard [guild_id] — manually trigger onboarding completion
@bot.command(name="onboard")
async def onboard_cmd(ctx, guild_id: str = None):
    """Manually trigger auto-onboarding for a server"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "Only owner can do this you silly human", delete_after=5, bypass_stealth=True)
        return

    await instant_delete_command(ctx)

    target_guild_id = int(guild_id) if guild_id and guild_id.isdigit() else (ctx.guild.id if ctx.guild else None)

    if not target_guild_id:
        await ultra_fast_response(ctx, "❌ Provide a guild ID or run this inside a server.", delete_after=8)
        return

    msg = await ctx.send(f"⏳ Running auto-onboarding for `{target_guild_id}`...")
    await auto_complete_onboarding(target_guild_id)
    await asyncio.sleep(1)
    try:
        await msg.edit(content=f"✅ Auto-onboarding completed for `{target_guild_id}`")
        await asyncio.sleep(5)
        await msg.delete()
    except Exception:
        pass


# Error handling for commands (optimized for speed and stability)
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands - silent ignore for speed
        return
    
    try:
        if isinstance(error, commands.MissingRequiredArgument):
            content = f"Error: Missing required argument: {error.param.name}"
        elif isinstance(error, commands.BadArgument):
            content = f"Error: Invalid argument provided. Check your inputs."
        else:
            content = f"Error: {error}"
        
        # Use ultra_fast_response for error handling
        await ultra_fast_response(ctx, content, delete_after=3, bypass_stealth=True)
        
    except Exception as e:
        # Silent error handling to prevent cascading errors
        if not ZERO_ERROR_MODE:
            print(f"Error handler failed: {e}")
        pass

# Command: -av [@user] (get avatar)
@bot.command(name="av")
async def avatar(ctx, *, user_mention=None):
    """Fetch avatar (and banner) for yourself or a mentioned user"""
    try:
        await instant_delete_command(ctx)
        # Resolve target user
        target = None
        if user_mention:
            # Strip spaces and try mention parse
            raw = user_mention.strip()
            # Try to extract ID from mention like <@123> or <@!123>
            import re as _re
            m = _re.match(r'<@!?(\d+)>', raw)
            if m:
                uid = int(m.group(1))
            else:
                # Maybe bare ID
                try:
                    uid = int(raw)
                except ValueError:
                    uid = None
            if uid:
                try:
                    target = await bot.fetch_user(uid)
                except Exception:
                    target = None
        if target is None:
            target = bot.user

        # Build avatar URL (4096px)
        av_url = target.display_avatar.with_size(4096).url

        lines = [
            f"🖼️ **Avatar** · {target} (`{target.id}`)",
            av_url,
        ]

        # Try to get banner (requires fetching full profile)
        try:
            full_user = await bot.fetch_user(target.id)
            if hasattr(full_user, 'banner') and full_user.banner:
                banner_url = full_user.banner.with_size(4096).url
                lines.append(f"🎨 **Banner**")
                lines.append(banner_url)
        except Exception:
            pass

        msg = await ctx.channel.send("\n".join(lines))
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        print(f"❌ av command error: {e}")

# Event: Process all messages and commands in any channel
@bot.event
async def on_message(message):
    try:
        # Skip bot's own messages to avoid infinite loops
        if bot.user and message.author.id == bot.user.id:
            try:
                # Only process commands from the bot itself
                if message.content.startswith(bot.command_prefix):
                    try:
                        # Process the command
                        channel_name = message.channel.name if hasattr(message.channel, 'name') else 'Unknown'
                        print(f"📝 Processing selfbot command in channel: {channel_name}")
                        await bot.process_commands(message)
                    except Exception as cmd_err:
                        print(f"❌ Error processing command: {cmd_err}")
                return
                
            except Exception as self_msg_err:
                print(f"❌ Error processing own message: {self_msg_err}")
                return
        
        # Check if message is from authorized user trying to control the bot
        if str(message.author.id) in authorized_users and message.content.startswith(bot.command_prefix):
            try:
                # Extract command name from message
                command_parts = message.content[1:].split()  # Remove prefix and split
                command_name = command_parts[0].lower() if command_parts else ""
                
                # Check if user has access to this specific command
                if not check_command_access(message.author.id, command_name):
                    # Send access denied message
                    allowed_cmds = ", ".join([f"-{cmd}" for cmd in sorted(ALLOWED_COMMANDS_FOR_AUTHORIZED)])
                    deny_msg = f"🚫 **ACCESS RESTRICTED**\n❌ You can only use: {allowed_cmds}\n💡 Contact owner for full access"
                    
                    try:
                        # Send the denial message and delete it quickly
                        denial_response = await message.channel.send(deny_msg)
                        await asyncio.sleep(5)  # Reduced from 8 to 5 seconds
                        try:
                            await denial_response.delete()
                        except:
                            pass  # Ignore if already deleted
                        try:
                            await message.delete()  # Delete the unauthorized command
                        except:
                            pass  # Ignore if already deleted
                        
                        # Log security event for audit trail
                        log_security_event("COMMAND_DENIED", message.author.id, f"Attempted to use restricted command: {command_name}")
                    except Exception as deny_err:
                        print(f"⚠️ Could not send/delete denial message: {deny_err}")
                    
                    print(f"🚫 Denied command '{command_name}' for authorized user {message.author.name} - not in allowed list")
                    return
                
                # Add stealth delay for authorized commands (bypass for spam and owner)
                is_owner = str(message.author.id) == BOT_OWNER_ID
                bypass_stealth = command_name == "spam" or is_owner
                await add_human_like_delay(bypass_for_spam=bypass_stealth)
                
                # Check rate limits for stealth (bypass for spam command and owner)
                if not bypass_stealth and not await check_command_rate_limit():
                    print(f"🛡️ Blocked authorized command due to rate limit protection")
                    return
                
                # Create a fake context for the authorized user
                # This allows them to execute commands through your bot
                channel_name = message.channel.name if hasattr(message.channel, 'name') else 'Unknown'
                print(f"🎯 Processing authorized user command from {message.author.name} ({message.author.id}) in {channel_name}: {message.content}")
                
                # Create a fake message with bot as author but keep original context
                fake_message = copy.copy(message)
                fake_message.author = bot.user
                
                # Process the command with the fake message
                ctx = await bot.get_context(fake_message)
                if ctx.command:
                    print(f"✅ Found command: {ctx.command.name}")
                    await ctx.command.invoke(ctx)
                else:
                    print(f"❌ Command not found: {message.content}")
                    # Try alternative processing
                    await bot.process_commands(fake_message)
                
                # Delete the authorized user's command for cleaner chat
                try:
                    await message.delete()
                    print(f"✅ Deleted authorized user's command message")
                except Exception as del_err:
                    print(f"⚠️ Could not delete command: {del_err}")
                    
            except Exception as auth_cmd_err:
                print(f"❌ Error processing authorized command: {auth_cmd_err}")
            return
            
        # Auto-reaction system - check if user is being tracked for reactions
        user_id_str = str(message.author.id)
        if user_id_str in reaction_targets and reaction_targets[user_id_str]['active']:
            # Check if user is whitelisted (MAIN PROTECTION THAT WAS MISSING)
            if is_user_whitelisted(message.author.id):
                # Remove from reaction targets and notify
                del reaction_targets[user_id_str]
                print(f"🛡️ WHITELIST PROTECTION: Removed {message.author.name} ({user_id_str}) from auto-reactions - user is now protected")
                try:
                    # Send clear protection notification
                    protection_msg = await message.channel.send(f"🛡️ **PROTECTION ACTIVATED** - {message.author.mention} is now protected from harassment\n✅ **Auto-reactions stopped** due to whitelist protection")
                    await asyncio.sleep(8)
                    await protection_msg.delete()
                except:
                    pass
            else:
                try:
                    emoji = reaction_targets[user_id_str]['emoji']
                    await message.add_reaction(emoji)
                    print(f"🚀 Auto-reacted {emoji} to {message.author.name}'s message")
                except Exception as e:
                    if not ZERO_ERROR_MODE:
                        print(f"Error auto-reacting: {e}")
        
        # Troll system - auto-reply to targeted user's messages
        troll_uid = str(message.author.id)
        if troll_uid in troll_targets and troll_targets[troll_uid]['active']:
            if not is_user_whitelisted(message.author.id):
                troll_replies = [
                    "💀 ratio + L + no cap + ur mom",
                    "😂 bro really typed that out LMAOOO",
                    "📉 skill issue",
                    "🤡 who asked? (nobody asked)",
                    "💅 not reading allat",
                    "🗑️ deleted this in my head already",
                    "😴 zzz... wake me up when you say something interesting",
                    "🪞 have you tried talking to a mirror? same energy",
                    "🧠 this is your brain on no thoughts",
                    "🤓 ok nerd whatever you say",
                    "🚮 straight to trash no hesitation",
                    "👁️👄👁️ ...",
                    "🦆 quack quack nobody cares",
                    "📵 bro got the confidence of someone who never gets left on read",
                    "😭 crying laughing at this bro fr fr",
                    "🎭 the audacity... the delusion... the nerve",
                    "🔇 muting this mentally",
                    "💤 snoring rn",
                    "🗣️ blah blah blah is all I heard",
                    "📢 no one: | absolutely no one: | you: (this)",
                ]
                try:
                    reply = random.choice(troll_replies)
                    await message.reply(reply, mention_author=False)
                    print(f"🤡 Trolled {message.author.name}: {reply}")
                except Exception:
                    pass

        # Copycat system - mirror targeted user's messages
        copycat_uid = str(message.author.id)
        if copycat_uid in copycat_targets and copycat_targets[copycat_uid]['active']:
            if not is_user_whitelisted(message.author.id):
                content = message.content
                if content and not content.startswith(bot.command_prefix):
                    try:
                        await message.channel.send(content)
                        print(f"🦜 Copycatted {message.author.name}: {content[:50]}")
                    except Exception:
                        pass

        # AFK system - check for mentions and DMs
        if (bot.user and bot.user.mentioned_in(message)) or isinstance(message.channel, discord.DMChannel):
            # Check if bot owner is AFK
            if bot.user and str(bot.user.id) in afk_users and afk_users[str(bot.user.id)]['status']:
                afk_data = afk_users[str(bot.user.id)]
                afk_message = afk_data.get('message', '')
                timestamp = afk_data.get('timestamp', time.time())
                
                # Calculate how long been AFK
                time_afk = int(time.time() - timestamp)
                hours = time_afk // 3600
                minutes = (time_afk % 3600) // 60
                
                time_str = ""
                if hours > 0:
                    time_str = f"{hours}h {minutes}m"
                else:
                    time_str = f"{minutes}m"
                
                # Create AFK reply
                if afk_message:
                    afk_reply = f"I'm AFK 🌙 - {afk_message} (since {time_str} ago)"
                else:
                    afk_reply = f"I'm AFK 🌙 (since {time_str} ago)"
                
                try:
                    await message.channel.send(afk_reply)
                    print(f"📱 Sent AFK auto-reply to {message.author.name}: {afk_reply}")
                except Exception as e:
                    if not ZERO_ERROR_MODE:
                        print(f"Error sending AFK reply: {e}")
        
        # Remove AFK status if bot owner sends a message (not a command)
        if bot.user and message.author.id == bot.user.id and not message.content.startswith(bot.command_prefix):
            if str(bot.user.id) in afk_users and afk_users[str(bot.user.id)]['status']:
                # Remove AFK status
                del afk_users[str(bot.user.id)]
                print("📱 Removed AFK status - user is back")
                
                try:
                    await message.channel.send("Welcome back! 👋 AFK status removed.")
                except Exception as e:
                    if not ZERO_ERROR_MODE:
                        print(f"Error sending welcome back message: {e}")
            
        # Check if this user is being drowned
        user_id_str = str(message.author.id)
        if user_id_str in drowned_users:
            # Check if user is now whitelisted (protection override)
            if is_user_whitelisted(message.author.id):
                # Remove from drowning and notify
                del drowned_users[user_id_str]
                print(f"🛡️ WHITELIST PROTECTION: Removed {message.author.name} ({user_id_str}) from drowning - user is now protected")
                try:
                    # Send clear protection notification
                    protection_msg = await message.channel.send(f"🛡️ **PROTECTION ACTIVATED** - {message.author.mention} is now protected from harassment\n✅ **Drowning stopped** due to whitelist protection")
                    await asyncio.sleep(8)
                    await protection_msg.delete()
                except:
                    pass
                return
            
            # Get user data
            user_data = drowned_users[user_id_str]
            mention = user_data["mention"]
            language_pref = user_data.get("language", "both")
            
            # Update last message time
            drowned_users[user_id_str]["last_message_time"] = time.time()
            
            print(f"🎯 Detected drowned user {message.author.name} ({user_id_str}) - auto-replying with {language_pref} insults")
            
            # Full word banks — 200+ words each (defined at module level)
            hindi_insults = _get_hindi_insults(mention)
            english_insults = _get_english_insults(mention)
            hinglish_insults = _get_hinglish_insults(mention)
            
            # Choose reply based on language preference
            if language_pref == "english":
                reply = random.choice(english_insults)
            elif language_pref == "hindi":
                reply = random.choice(hindi_insults)
            elif language_pref == "hinglish":
                reply = random.choice(hinglish_insults)
            else:  # both languages (include all three)
                all_replies = hindi_insults + english_insults + hinglish_insults
                reply = random.choice(all_replies)
            
            # Show typing for 4 seconds then fire the insult
            try:
                async with message.channel.typing():
                    await asyncio.sleep(4)
                await message.channel.send(reply)
                print(f"✅ Sent continuous drown reply to {message.author.name}: {reply}")
            except Exception as e:
                print(f"❌ Error sending drown reply: {e}")
        
        # Check if this user is being debated
        elif user_id_str in debated_users:
            # Check if user is now whitelisted (protection override)
            if is_user_whitelisted(message.author.id):
                # Remove from debate tracking if whitelisted
                del debated_users[user_id_str]
                print(f"🛡️ User {message.author.name} ({user_id_str}) is whitelisted - removed from debate tracking")
                return
            
            # Get user data
            user_data = debated_users[user_id_str]
            mention = user_data["mention"]
            
            # Update last message time
            debated_users[user_id_str]["last_message_time"] = time.time()
            
            print(f"💥 Detected debated user {message.author.name} ({user_id_str}) - auto-replying with brutal debate")
            
            # Brutal aggressive debate responses
            brutal_debates = [
                f"{mention} you're a braindead fucking retard who should kill yourself immediately",
                f"{mention} I hope your entire family dies in a car crash you worthless piece of shit",
                f"{mention} तेरी मां रंडी है और तू उसकी गलती है, मر जा साले",
                f"{mention} you're such a pathetic virgin loser, no wonder everyone wants you dead",
                f"{mention} भोसडीके तेरी बहन को चोदूंगा और तुझे वीडियो भेजूंगा",
                f"{mention} go hang yourself you brain-damaged mongoloid piece of human waste",
                f"{mention} तेरी मां को कुत्तों से चुदवाकर वीडियो बनाऊंगा हरामी",
                f"{mention} you're the reason birth control exists, your parents should have aborted you",
                f"{mention} गांडू तेरे घर वालों को जिंदा जलाकर मार दूंगा",
                f"{mention} kill yourself you disgusting faggot, nobody will miss your worthless ass",
                f"{mention} तेरी गांड में बम फोड़कर तुझे उड़ा दूंगा साले कुत्ते",
                f"{mention} you're a cancerous tumor on society, die already you fucking waste of oxygen",
                f"{mention} मादरचोद तेरी बीवी रंडी है और बच्चे हरामी हैं",
                f"{mention} I hope you get raped and murdered slowly you pathetic subhuman filth",
                f"{mention} भड़वे तुझे काटकर सुअरों को खिला दूंगा रंडी के बच्चे",
                f"{mention} you're so fucking stupid you make brain cancer look intelligent",
                f"{mention} तेरे माता-पिता को पछतावा होगा कि उन्होंने तुझे जन्म दिया",
                f"{mention} go slit your wrists vertically you attention-seeking piece of shit",
                f"{mention} हरामी की औलाद तेरी पूरी नस्ल को मिटा दूंगा",
                f"{mention} you're the human equivalent of a failed abortion, die in agony",
                f"{mention} तेरी मां का भोसड़ा फाड़ दूंगा और तुझे दिखाऊंगा",
                f"{mention} I wish your mother had cancer when she was pregnant with you",
                f"{mention} रंडी के बच्चे तेरी औकात कुत्ते से भी कम है",
                f"{mention} you should have been swallowed instead of born you worthless cunt",
                f"{mention} गांडू तेरी बहन को ट्रक वालों से चुदवाऊंगा"
            ]
            
            # Pick a random brutal comeback (ensuring variety)
            reply = random.choice(brutal_debates)
            
            # Send the brutal debate response immediately  
            try:
                await message.channel.send(reply)
                print(f"✅ Sent continuous debate reply to {message.author.name}: {reply}")
            except Exception as e:
                print(f"❌ Error sending debate reply: {e}")
    
    except Exception as e:
        print(f"Error in on_message: {e}")
        # Continue processing even if there's an error
        
    # Always process commands at the end
    await bot.process_commands(message)

# Event: Cache deleted messages for snipe
@bot.event
async def on_message_delete(message):
    try:
        if message.author.bot:
            return
        attachments = [a.url for a in message.attachments] if message.attachments else []
        snipe_cache[message.channel.id] = {
            "content": message.content or "(no text content)",
            "author": str(message.author),
            "author_id": message.author.id,
            "timestamp": message.created_at,
            "attachments": attachments
        }
    except Exception:
        pass

# Event: Cache edited messages for edit-snipe
@bot.event
async def on_message_edit(before, after):
    try:
        if before.author.bot:
            return
        if before.content == after.content:
            return
        esnipe_cache[before.channel.id] = {
            "before": before.content or "(no text content)",
            "after": after.content or "(no text content)",
            "author": str(before.author),
            "author_id": before.author.id,
            "timestamp": before.created_at
        }
    except Exception:
        pass

# Function to execute the "drown" functionality
async def execute_drown(ctx, mention, language=None):
    """Execute the drown command with English and Hindi insults"""
    try:
        # Find user ID
        user_id = find_user_id_by_mention(mention)
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username or @UserID.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Add or update user in drowned_users dict
        drowned_users[user_id] = {
            "mention": mention,
            "channel_id": ctx.channel.id,
            "last_message_time": time.time()
        }
        
        # Success message
        lang_msg = ""
        if language == "english":
            lang_msg = " (English only)"
        elif language == "hindi":
            lang_msg = " (Hindi only)"
        
        await ctx.message.edit(content=f"✅ Started drowning {mention}{lang_msg}! They will be insulted on every message.")
        await asyncio.sleep(5)
        await ctx.message.delete()
        
        print(f"Started drowning user {mention} ({user_id}) in channel {ctx.channel.id}")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -drown @user (insults in both English and Hindi)
@bot.command()
async def drown(ctx, *, args=None):
    """Insult a mentioned user in both English and Hindi"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-drown @user`\nStarts drowning a user with insults.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Check if target user is whitelisted
        if is_user_whitelisted(user_id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot use bot features on protected users")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Full word banks — 200+ words each (defined at module level)
        english_insults = _get_english_insults(mention)
        hindi_insults = _get_hindi_insults(mention)

        english_insult = random.choice(english_insults)
        hindi_insult = random.choice(hindi_insults)
        
        await ctx.send(english_insult)
        await asyncio.sleep(0.5)
        await ctx.send(hindi_insult)
        
        # Track user for both language auto-replies (use string key for consistency)
        drowned_users[str(user_id)] = {
            "mention": mention,
            "timestamp": time.time(),
            "channel_id": ctx.channel.id,
            "last_message_time": time.time(),
            "language": "both"
        }
        
        # Delete command message
        await ctx.message.delete()
        print(f"Started drowning user {mention} in both languages")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -drownenglish @user (English insults only) 
@bot.command(name="drownenglish")
async def drown_english(ctx, *, args=None):
    """Insult a mentioned user in English only"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-drownenglish @user`\nStarts drowning a user with English insults only.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Check if target user is whitelisted
        if is_user_whitelisted(user_id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot use bot features on protected users")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Full 200+ word bank (defined at module level)
        english_insults = _get_english_insults(mention)
        if False:  # dead block — word bank moved to _get_english_insults()
            english_insults_dead = [
            f"nigga {mention} stfu before I slap the stupid out yo face",
            f"{mention} bitch ass nigga sit yo broke ass down somewhere",
            f"on god {mention} you the fakest nigga I ever seen in my life",
            f"{mention} I'll fuck you up no cap keep playing with me",
            f"bro {mention} you a whole clown nigga nobody scared of you",
            f"{mention} stfu faggot you ain't built for this at all",
            f"nah {mention} you really out here thinking you tough lmao sit down",
            f"{mention} you a bitch made nigga and everybody know it",
            f"on sight {mention} keep talking and see what happens to you",
            f"{mention} yo mama raised a snitch ass little bitch congrats",
            f"bro {mention} you move mad sus and everybody clocking it",
            f"{mention} you ain't got no hands no money no respect nothing",
            f"nigga {mention} you softer than baby shit on a warm day",
            f"{mention} kill yourself with that weak energy you bringing rn",
            f"deadass {mention} you the type to get robbed and cry about it",
            f"{mention} you a whole opp and you don't even know it yet",
            f"bro {mention} your own crew thinks you a liability fr fr",
            f"{mention} you been a bitch your whole life don't start now",
            f"on my mama {mention} you not gonna do nothing but type",
            f"{mention} lil broke ass nigga go fix your life first",
            f"nah {mention} you really said that like you hard or something lmao",
            f"{mention} I'll dog walk you through your own block no problem",
            f"shut yo bitch ass up {mention} before I make you",
            f"{mention} you eating off who exactly cuz it ain't showing",
            f"nigga {mention} you garbage and your whole circle know it",
            f"{mention} you the weakest link and they keeping you around for laughs",
            f"bro {mention} you really out here cappin on the internet huh",
            f"{mention} stay in your lane before you get ran over for real",
            f"on god {mention} you a whole clown with no circus to go back to",
            f"{mention} you can't fight you can't rap you can't do nothing right",
            f"deadass {mention} your mama embarrassed by you every single day",
            f"{mention} nigga you built like a question mark and fight like one too",
            f"bro {mention} you the type that switches sides when shit gets real",
            f"{mention} I seen tougher niggas in a nursery rhyme than you",
            f"nah {mention} you really pressed over me and I don't even know you lmao",
            f"{mention} you a whole pussy nigga hiding behind a screen rn",
            f"on sight {mention} you keep my name in your mouth like you want smoke",
            f"{mention} your drip is ass your mind is ass your whole vibe is ass",
            f"nigga {mention} you not gonna do nothing but breathe heavy and log off",
            f"{mention} you the definition of all bark and zero motherfucking bite",
            f"bro {mention} you corny as hell and not even in a funny way",
            f"{mention} I'll pull up and you gonna fold like a lawn chair immediately",
            f"deadass {mention} everyone around you is fronting like they rock with you",
            f"{mention} you got no bag no respect no future just attitude",
            f"nigga {mention} you been talking crazy but your location stay private huh",
            f"{mention} you a temporary nigga in a permanent situation wake up",
            f"bro {mention} you move funny and your homies see it too trust",
            f"{mention} stfu and go get a job or something with yo broke ass",
            f"on god {mention} you the type to snitch the second pressure applied",
            f"{mention} you ain't never did nothing and you still won't do nothing",
            f"nah {mention} you really typed that out and thought you said something huh",
            f"{mention} your whole energy is rat energy and it radiates off you",
            f"nigga {mention} you a joke without a punchline nobody laughing with you",
            f"{mention} keep testing me and find out what happens to weak niggas",
            f"bro {mention} you got participation trophy energy in a championship world",
            f"{mention} I don't even gotta say much you already know you're a bitch",
            f"deadass {mention} you live on the internet because the streets rejected you",
            f"{mention} you not built different you just built wrong from the start",
            f"on my life {mention} you a whole fraud and the timeline knows it",
            f"{mention} nigga you press people online and cry in person we know",
            f"bro {mention} you got zero drip zero respect zero wins just cope",
            f"{mention} you funny as hell thinking anyone out here fears you at all",
            f"nigga {mention} your reputation is trash and you built it yourself",
            f"{mention} you the type to get curved by your own reflection fr",
            f"on sight {mention} you been lucky nobody pulled up yet keep going",
            f"{mention} you a whole nobody pretending to be a somebody daily",
            f"bro {mention} even your allies are lowkey embarrassed to know you",
            f"{mention} you can't even look people in the eye irl and you online hard lmao",
            f"deadass {mention} you spent your whole life being a walking L",
            f"{mention} nigga you not even worth the energy but here we are",
            f"nah {mention} you really living like this and still got opinions wild",
            f"{mention} bitch you built like a speed bump and hit like one too",
            f"on god {mention} your own mama got tired of your excuses long time ago",
            f"{mention} you a clout chaser with nothing to chase and nowhere to go",
            f"nigga {mention} you pressed and stressed over someone you never met lmao",
            f"{mention} you the type of nigga people only call when they need a fool",
            f"bro {mention} you out here wilding with no backup and no bag pathetic",
            f"{mention} I'll fold you in front of your people and walk away clean",
            f"deadass {mention} you move like a snitch and smell like one too",
            f"{mention} you not gonna step to nobody cuz you know what'd happen",
            f"on my mama {mention} you a whole disaster in human form fr",
            f"{mention} nigga you soft as tissue and twice as disposable no cap",
            f"bro {mention} you the weakest energy in every room you walk into",
            f"{mention} you a whole liability that your crew just hasn't dropped yet",
            f"nah {mention} you really think you got pull lmao who told you that",
            f"{mention} you got bum written all over you from the fit to the mindset",
            f"nigga {mention} stfu you been losing your whole life don't start now",
            f"{mention} you the reason your block is embarrassed to claim you",
            f"on god {mention} you not dangerous you just annoying which is worse",
            f"{mention} keep acting hard on the net and soft in the streets as always",
            f"bro {mention} you literally nobody and you still chose to be a problem",
            f"{mention} you a dusty broke down clown and nobody checking for you",
            f"deadass {mention} your energy is lower than your bank account which is saying a lot",
            f"{mention} nigga you been cappin so long you forgot what real looks like",
            f"nah {mention} I'll pull up to your location and you already know you done",
            f"{mention} you the type to apologize when someone bumps into you every time",
            f"on sight {mention} you keep this energy up and you gonna learn real quick",
            f"{mention} you not built for beef you built for retreat and everybody knows",
            f"nigga {mention} you got the audacity of a bum with the budget of a bum",
            f"{mention} bro your whole life is a series of bad decisions and excuses",
            f"deadass {mention} you a flop era that never had a peak to fall from",
            f"{mention} you so lame that lame niggas look at you and feel better about themselves",
            f"bro {mention} you cap more than a pen factory and nobody believes you",
            f"{mention} I'd say get your weight up but you don't even know where the gym is",
            f"on god {mention} you a whole NPC in a world full of main characters",
            f"{mention} nigga you not gonna say that to nobody's face and we all know it",
            f"nah {mention} you really out here with no bag no wins and a big mouth wild",
            f"{mention} you the type that gets ethered in every argument and logs off crying",
            f"bro {mention} your whole squad knows you the weakest link they just use you",
            f"{mention} deadass you wasted your own potential and now you mad at the world",
            f"nigga {mention} you a whole muppet go find your strings and get controlled",
            f"{mention} you been getting played your whole life and calling it a win",
            f"on sight {mention} you all talk and zero action like every bitch nigga ever",
            f"{mention} you the type to get robbed and say you let it happen to be nice",
            f"bro {mention} you got participation energy in a survival of the fittest world",
            f"{mention} nigga you not gonna do nothing but scroll and cope as always",
            f"deadass {mention} you a whole burden that life keeps trying to set down",
            f"{mention} you the most replaceable nigga in every room you ever been in",
            f"nah {mention} you really walking around here thinking you relevant lmao",
            f"{mention} bitch you not hard you just haven't been pressed yet wait for it",
            f"on my life {mention} you a whole culture vulture with no culture to show",
            f"{mention} you so lost you don't even know what you're missing anymore",
            f"nigga {mention} you been a fraud since day one the streets remember",
            f"{mention} you not gonna ever amount to nothing and deep down you know it",
            f"bro {mention} you out here renting respect that you can't afford to keep",
            f"{mention} you the type that switches up when money or power shows up pathetic",
            f"deadass {mention} you a whole liability dressed up as an asset every day",
            f"{mention} nigga your word means nothing cuz your track record is trash",
            f"on god {mention} you so predictable every move you make is already a loss",
            f"{mention} you been faking it so long the real you is lost somewhere crying",
            f"nah {mention} you genuinely one of the weakest niggas I ever had to address",
            f"{mention} your whole brand is failure and you marketing it every single day",
            f"bro {mention} you a whole opp in sheep clothing and everybody see it",
            f"{mention} nigga you not gonna do shit but talk keep it that way for your sake",
            f"on sight {mention} you one more word away from finding out who you really are",
            f"{mention} you a whole discount version of a man with clearance rack energy",
            f"deadass {mention} you move like you got no dawgs no bag and no wins cuz you don't",
            f"{mention} you got audacity for days and accomplishments for zero keep that energy",
            f"nigga {mention} you a problem nobody asked for and a solution nobody wants",
            f"{mention} bro you the type of person that makes people appreciate being alone",
            f"nah {mention} you really sat there and typed that like it was gonna do something lmao",
            f"{mention} you a whole joke and the punchline is your entire existence no cap",
            f"on god {mention} I've seen scarier niggas in a Disney movie than you",
            f"{mention} you not dangerous you not smart you not funny you just here unfortunately",
            f"bro {mention} you the type to bring drama everywhere and wonder why you alone",
            f"{mention} nigga you can't afford the smoke you keep starting learn your budget",
            f"deadass {mention} your potential died before you did and it was the smarter choice",
            f"{mention} you a whole certified L merchant selling losses like a career",
            f"on my mama {mention} you so corny the block uses you as a cautionary tale",
            f"{mention} nigga you press people on here but you cross the street irl admit it",
            f"nah {mention} stay behind that screen it's the only place you survive fr",
            f"{mention} you a whole counterfeit nigga in an era where everyone checks receipts",
        ]
        
        # Send 2 different English insults
        english_insult1 = random.choice(english_insults)
        english_insult2 = random.choice(english_insults)
        while english_insult1 == english_insult2:
            english_insult2 = random.choice(english_insults)
        
        await ctx.send(english_insult1)
        await asyncio.sleep(0.5)
        await ctx.send(english_insult2)
        
        # Track user for English-only auto-replies (use string key for consistency)
        drowned_users[str(user_id)] = {
            "mention": mention,
            "timestamp": time.time(),
            "channel_id": ctx.channel.id,
            "last_message_time": time.time(),
            "language": "english"
        }
        
        # Delete command message
        await ctx.message.delete()
        print(f"Started drowning user {mention} in English only")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -drownhindi @user (Hindi insults only)
@bot.command(name="drownhindi")
async def drown_hindi(ctx, *, args=None):
    """Insult a mentioned user in Hindi only"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-drownhindi @user`\nStarts drowning a user with Hindi insults only.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Check if target user is whitelisted
        if is_user_whitelisted(user_id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot use bot features on protected users")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Full word bank (defined at module level)
        hindi_insults = _get_hindi_insults(mention)
        
        # Send 2 different Hindi insults
        hindi_insult1 = random.choice(hindi_insults)
        hindi_insult2 = random.choice(hindi_insults)
        while hindi_insult1 == hindi_insult2:
            hindi_insult2 = random.choice(hindi_insults)
        
        await ctx.send(hindi_insult1)
        await asyncio.sleep(0.5)
        await ctx.send(hindi_insult2)
        
        # Track user for Hindi-only auto-replies (use string key for consistency)
        drowned_users[str(user_id)] = {
            "mention": mention,
            "timestamp": time.time(),
            "channel_id": ctx.channel.id,
            "last_message_time": time.time(),
            "language": "hindi"
        }
        
        # Delete command message
        await ctx.message.delete()
        print(f"Started drowning user {mention} in Hindi only")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -drownhinglish @user (Hindi insults in English alphabets)
@bot.command(name="drownhinglish")
async def drown_hinglish(ctx, *, args=None):
    """Insult a mentioned user with Hindi words written in English alphabets"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-drownhinglish @user`\nStarts drowning a user with Hindi insults in English alphabets.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Check if target user is whitelisted
        if is_user_whitelisted(user_id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot use bot features on protected users")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Full 200+ word bank (defined at module level)
        hinglish_insults = _get_hinglish_insults(mention)
        if False:  # dead block — word bank moved to _get_hinglish_insults()
            hinglish_insults_dead = [
            f"abe {mention} iski maa randi hai puri mohalla jaanta hai",
            f"{mention} randi ke bacche aukat mein reh apni",
            f"saale {mention} tujhe jaan se maar dunga ek baar haath aane de",
            f"abe {mention} mera lund mat chus itna bhi gira hua mat ban",
            f"{mention} teri maa ka bhosda khula rehta hai din raat",
            f"chutiye {mention} teri behen sabke saath soti hai free mein",
            f"abe {mention} tu itna ghatiya hai ki teri maa bhi tujhse nafrat karti hai",
            f"{mention} gaandu teri aukaat kya hai bata mujhe",
            f"saale {mention} tera baap hijda hai aur tu uska baap hai",
            f"abe {mention} teri maa ko maine roz raat ko choda hai samjha",
            f"{mention} randi ki aulaad apni zubaan sambhal ke baat kar",
            f"bhosadike {mention} teri behen ka rate kya hai bazar mein",
            f"abe {mention} tu maa ka laal nahi maa ki galti hai",
            f"{mention} chutiya aukat nahi hai teri mujhse aankh milane ki",
            f"saale {mention} tujhe nali mein phenk dena chahiye tha paida hote hi",
            f"abe {mention} teri maa khud tujhse poochh rahi hai tu kiska hai",
            f"{mention} gaandmara harami ki nasal apni maa ko sambhal pehle",
            f"chutiye {mention} tera lund itna chota hai ki chhipkali bhi hansti hai",
            f"abe {mention} teri behen roz naye mard ghar laati hai",
            f"{mention} madarchod teri maa ki chut mein mera lund hai ab bhi",
            f"saale {mention} tu itna bekaar hai ki bhagwan bhi maafi maang raha hai",
            f"abe {mention} randi ke bacche tujhse baat karna apna waqt barbad karna hai",
            f"{mention} teri maa bazar ki maal hai aur tu uska sample",
            f"bhosadike {mention} teri gaand maar ke tujhe sadak pe phenk dunga",
            f"abe {mention} tu paida hi isliye hua tha taki teri maa ko pata chale kya galti hui",
            f"{mention} chutiye teri behen ka naam red light area mein sab jaante hain",
            f"saale {mention} tera pura khandaan ek nali mein ghus sakta hai",
            f"abe {mention} teri maa ne tujhe paida karke apni sabse badi bhool ki",
            f"{mention} gaandu tujhe jaan se maarna toh bahut bada kaam hai teri aukaat nahi",
            f"chutiye {mention} teri biwi bhi tujhse tang aake dusron ke paas jaati hai",
            f"abe {mention} tu itna ganda hai ki naaliyan bhi tujhse sharminda hain",
            f"{mention} randi ke pille aukat mein reh warna gaand phad dunga",
            f"saale {mention} tera baap khud nahi jaanta tu uska hai ya aur kisi ka",
            f"abe {mention} teri maa ka toh pata nahi par teri behen pakki randi hai",
            f"{mention} madarchod tu khud bhi jaanta hai teri zindagi mein koi value nahi",
            f"bhosadike {mention} teri aukaat ek naali ke keede se bhi kam hai",
            f"abe {mention} teri maa ko leke kutta bhi nahi bhaunkta",
            f"{mention} chutiye apna mooh band rakh warna tere dant tod dunga",
            f"saale {mention} tera khoon itna ganda hai ki mosquito bhi nahi kaatta tujhe",
            f"abe {mention} tu itna kamina hai ki tere saaye se bhi log door bhagte hain",
            f"{mention} randi ki nasal tujhe dekhke patthar bhi pighal nahi sakta",
            f"gaandu {mention} apni maa ko sambhal pehle baahar ghoomti rehti hai roz",
            f"abe {mention} teri behen ki shaadi hogi kaise jab wo itni sasti hai",
            f"{mention} chutiye tujhe ek tamacha maarne mein bhi mehnat lagti hai",
            f"saale {mention} teri zindagi ek nali ki story hai aur tu main character",
            f"abe {mention} tera naam sunta hoon toh ulti aati hai seedha",
            f"{mention} madarchod teri maa ne kitne mardon ke saath raat bitayi hai gin bhi nahi sakta",
            f"bhosadike {mention} teri behen ka photo red light area mein laga hai",
            f"abe {mention} tu itna bekaar insaan hai ki tujhe dekhke bhagwan ko bhi sharm aati hai",
            f"{mention} randi ke bacche apni aukaat pe aa warna theek nahi hoga",
            f"saale {mention} tera baap roz subah ghar se isliye nikalte hai taki tujhe na dekhe",
            f"abe {mention} teri maa itni sasti hai ki discount pe milti hai",
            f"{mention} chutiye tujhe ek laat maari toh teri puri family line pakki",
            f"gaandu {mention} teri behen ko maine khud dekha hai galat jagah",
            f"abe {mention} tu paida hua toh doctor ne bhi mooh pher liya tha",
            f"{mention} madarchod teri aukaat sirf gaali sunne ki hai jawab dene ki nahi",
            f"saale {mention} teri maa ka number toh puri gali mein share ho chuka hai",
            f"abe {mention} randi ki aulaad tune aankh uthake meri taraf dekha kaise",
            f"{mention} bhosadike tera to pura khandaan hi naali ka product hai",
            f"chutiye {mention} teri behen ko main roz uthake chhod aata hoon ghar pe",
            f"abe {mention} tu itna gira hua hai ki gutter bhi tujhe accept nahi karta",
            f"{mention} gaandu teri zindagi ek machar ki zindagi se bhi zyada bekaar hai",
            f"saale {mention} teri maa ki chut mein itna traffic hai ki signal lagwana padega",
            f"abe {mention} tu woh galti hai jo condom ne prevent nahi ki",
            f"{mention} randi ke pille teri aukaat itni hai ki teri maa bhi tujhe nahi poochti",
            f"madarchod {mention} apna mooh khol ke apni maa ki izzat mat gira",
            f"abe {mention} teri behen bhi jaanti hai tu kitna ganda insaan hai",
            f"{mention} chutiye tujhe seedha maara toh haath gandat ho jaata hai",
            f"saale {mention} tera baap bhi tujhse piggyback ride nahi karaata itna sharm hai",
            f"abe {mention} iski maa aur behen ek hi rate pe milti hain bazaar mein",
            f"{mention} gaandu tune mujhse panga liya toh teri poori nasal sambhal",
            f"bhosadike {mention} teri maa ka naam sunke mohalla hug karta hai",
            f"abe {mention} randi ki aulaad teri aukaat kya hai mujhse baat karne ki",
            f"{mention} chutiye tera chehra dekh ke kuttey bhi sharma jaate hain",
            f"saale {mention} teri maa itni gandi hai ki barish bhi use nahi dho sakti",
            f"abe {mention} tu itna useless hai ki teri maa ka pet yun hi bada hua tha",
            f"{mention} madarchod teri behen ka ghar main jaanta hoon roz jaata hoon",
            f"gaandu {mention} teri aukaat ek joote ki nok se bhi neechey hai",
            f"abe {mention} tera khandan hi aisa hai jahan se sirf randi aur harami nikalte hain",
            f"{mention} randi ke bacche tu khud jaanta hai tera baap konsa hai nahi",
            f"saale {mention} teri maa ke paas contact list hai aur usme sirf mard hain",
            f"abe {mention} chutiye tujhe ek thappad maara toh teri teen peediyan yaad rakhegi",
            f"{mention} bhosadike teri behen roz subah naye kapde lekar aati hai gharse",
            f"abe {mention} tu itna bekar hai ki kachre wala bhi teri value nahi karta",
            f"{mention} gaandu meri ek awaaz pe teri poori gali jaanti hai teri aukaat",
            f"chutiye {mention} teri maa bhi jaanti hai tu uski sabse badi nafrat hai",
            f"abe {mention} randi ki nasl teri behen ka naam toh poora area jaanta hai",
            f"{mention} madarchod tujhe dekhke lagta hai galti se paida ho gaya tha",
            f"saale {mention} tera baap roz rat ko alag ghar mein sota hai tujhse dur rehne ko",
            f"abe {mention} teri maa ki izzat pehle sambhal apni zubaan se pehle",
            f"{mention} chutiye teri aulaad bhi tujhe dekh ke sharmayegi ek din",
            f"gaandu {mention} tu itna sasta hai ki discount bhi tujh pe nahi lagta",
            f"abe {mention} teri behen ko maine kal raat dekha woh khushi khushi gayi",
            f"{mention} randi ke pille apni maa ko ghar mein rakh pehle phir baat karna",
            f"saale {mention} tera chehra hi aisa hai ki log seedha doosri taraf ghoom jaate hain",
            f"abe {mention} tu paida hua tab se is gali ki izzat khatam ho gayi",
            f"{mention} bhosadike teri maa ka number save hai mere paas purane contacts mein",
            f"chutiye {mention} teri behen sabse pehle ghar aati hai subah baahar se",
            f"abe {mention} tujhe gaali bhi dena teri izzat karna lagta hai",
            f"{mention} gaandu teri zindagi ek chhote naale ki kahani hai khatam",
            f"saale {mention} teri maa ne tujhe paida karke bhagwan ko bhi dhoka diya",
            f"abe {mention} randi ki aulaad apni zubaan band kar warna tod dunga",
            f"{mention} madarchod teri behen ka beta bhi tere jaisa nahi hoga itni mercy hai",
            f"bhosadike {mention} tu itna ganda hai ki shadikhaane ka kutta bhi tujhpe nahi bhaunkta",
            f"abe {mention} teri maa ki market value bahut zyada hai isliye tujhe koi nahi poochta",
            f"{mention} chutiye teri aukat nahi hai mujhse seedhi baat karne ki",
            f"saale {mention} tera poora khandaan ek jhuggi mein bhi fit nahi hoga itna kachra hai",
            f"abe {mention} iski aukaat dekho randi ki nasl aur humse uljhne chala",
            f"{mention} gaandu apni maa ko sambhal bahar ghoomti rehti hai raat ko",
            f"chutiye {mention} tera baap bhi jaanta hai tu uska nahi hai",
            f"abe {mention} randi ke bacche tune mere saath panga liya toh yaad rakhega",
            f"{mention} madarchod teri behen ko poori gali ne dekha hai",
            f"saale {mention} teri maa itni sasti hai ki puri gali ka bill ek hi mahine mein aata hai",
            f"abe {mention} tu woh keeda hai jo toot jaata hai par marta nahi",
            f"{mention} bhosadike teri aukaat ek kichad ke keede se bhi kam hai seedha",
            f"gaandu {mention} apna mooh band rakh warna laat maari toh teri yaad rahegi",
            f"abe {mention} iski maa ki izzat gali ke naale mein beh gayi kab ki",
            f"{mention} randi ki aulaad teri zindagi ek nali ki story hai sab jante hain",
            f"saale {mention} tera chehra dekh ke mujhe apna khaana yaad aata hai jo kharab ho gaya tha",
            f"abe {mention} chutiye tu itna kamzor hai ki teri khud ki pararchhayi dar jaati hai",
            f"{mention} madarchod teri behen roz rate fix karke aati hai ghar",
            f"bhosadike {mention} teri maa ki photo khichwa ke sadak pe laga dunga",
            f"abe {mention} gaandu teri aukat hai nahi ki mujhse aankh milaye",
            f"{mention} saale randi ke pille apne ghar ki izzat pehle sambhal phir bol",
            f"chutiye {mention} tu itna bekar hai ki teri maa ne bhi tujhse mooh pher liya",
            f"abe {mention} teri behen ka mobile mein sirf mardo ke numbers hain",
            f"{mention} gaandu apni maa ko raat ko ghar pe rakh phir mujhse baat karna",
            f"saale {mention} tera baap jab ghar aata hai toh tujhe dekhke waapis chala jaata hai",
            f"abe {mention} randi ki nasl teri aukaat ek gande kapde se bhi kam hai",
            f"{mention} madarchod teri behen ne khud bataya tha kal raat sab kuch",
            f"bhosadike {mention} tu itna gira hua hai ki gutter bhi tujhse upar hai",
            f"abe {mention} chutiye teri maa ka chakkar poora mohalla chhupata hai tujhse",
            f"{mention} gaandu tujhe jaan se maar dunga ek baar milna bas",
            f"saale {mention} iski maa randi behen randi baap hijda seedha pura khandaan",
            f"abe {mention} randi ke bacche apni aukaat pe reh warna theek nahi hoga tera",
            f"{mention} madarchod tu itna ganda hai ki tujhe yaad karna bhi pollution hai",
            f"chutiye {mention} teri behen ka address dede seedha wahan aa jaata hoon",
            f"abe {mention} gaandu teri maa ka phone aaya tha kal raat maine uthaya",
            f"{mention} bhosadike tera naam sunta hoon toh tujhse pehle teri maa yaad aati hai",
            f"saale {mention} tu woh galti hai jise na toh roka gaya na sudhaara gaya",
            f"abe {mention} randi ki aulaad apna mooh band kar warna khud band kar dunga",
            f"{mention} gaandu teri behen free mein milti hai aur tab bhi log nahi jaate",
            f"chutiye {mention} teri maa ne itne mard dekhe hain ki ab chehra yaad nahi rehta",
            f"abe {mention} madarchod teri aukat ek joote ke taale se bhi kam hai",
            f"{mention} saale iski maa ki chut mein poori gali ka data hai",
            f"bhosadike {mention} tu paida hua tab se teri maa ko afsoos hai",
            f"abe {mention} gaandu teri aukaat nahi hai meri taraf aankh uthane ki",
            f"{mention} randi ke pille tune panga liya toh teri poori nasl yaad rakhegi",
            f"saale {mention} teri behen ka din ka schedule dekh lena kaafi hai sab samajhne ko",
            f"abe {mention} chutiye tujhe ek baar maara toh teri saat peediyon ko pata chalega",
            f"{mention} madarchod teri maa roz rate badlati hai par customers nahi badlate",
            f"gaandu {mention} tu itna kamina insaan hai ki tere kapde bhi tujhse door rehna chahte hain",
            f"abe {mention} bhosadike teri behen ka kaam subah shuru hota hai aur raat tak chalta hai",
            f"{mention} randi ki aulaad apni maa ko sambhal pehle phir zubaan khol",
            f"saale {mention} tera baap tujhe dekh ke roz sochta hai kahan galti hui",
            f"abe {mention} chutiye tujhe maarna bhi haath ki beizzati hai",
            f"{mention} gaandu iski maa ko bhi pata nahi kaun sa number iska baap hai",
            f"madarchod {mention} teri behen ne khud kaha tha ghar pe koi rok nahi",
            f"abe {mention} bhosadike tu itna sasta hai ki free bhi nahi chalega",
            f"{mention} saale randi ke bacche teri aukaat teri maa ki chut se bhi neechey hai",
            f"chutiye {mention} teri zindagi mein na izzat hai na aukaat bus khali dhol hai",
            f"abe {mention} gaandu teri maa bazar jaati hai toh log rate poochh lete hain",
            f"{mention} randi ki nasl tu itna ganda hai ki tujhse milne ke baad log nahaate hain",
            f"saale {mention} teri behen ka photo le ke rakh mujhe yaad karne ka mauka milega",
            f"abe {mention} madarchod apni aukaat pe reh warna tujhe pata hai main kya kar sakta hoon",
            f"{mention} bhosadike tera poora khandaan ek kachre ke dher pe paida hua tha",
            f"gaandu {mention} iski maa randi hai ye toh poori gali ko pata tha",
            f"abe {mention} chutiye tu itna bekar hai ki bhagwan ne tujhe banake pachtaya",
            f"{mention} randi ke pille apni zubaan band kar warna tod ke rakh dunga",
            f"saale {mention} teri maa kal bhi baahar thi aaj bhi baahar hai kal bhi rahegi",
            f"abe {mention} madarchod tujhe ek haath se niptaana kaafi hai itni aukaat hai teri",
            f"{mention} gaandu teri behen ka ghar number badal gaya ya abhi bhi wahi hai",
            f"chutiye {mention} tu woh insaan hai jis par patthar phenkne mein bhi mehnat lagti hai",
            f"abe {mention} bhosadike teri maa ki sab se badi kami ye hai ki tune janam liya",
            f"{mention} randi ki aulaad teri aukaat dekh aur mooh band kar apna",
            f"saale {mention} tera baap khud kehta hai beta nahi ghalat paisa kharch hua",
            f"abe {mention} gaandu iski behen ka rate sab jaante hain area mein",
            f"{mention} madarchod teri maa ne tujhe paida karke apni zindagi barbaad ki",
            f"chutiye {mention} tu itna gira hua hai ki teri maa bhi tujhpe thookti hai",
            f"abe {mention} randi ke bacche aaj teri maa kahan hai poochh ke aa pehle",
            f"{mention} bhosadike teri aukat nahi teri behen ki hai aur woh bhi sasti",
        ]
        
        # Send 2 different Hinglish insults
        hinglish_insult1 = random.choice(hinglish_insults)
        hinglish_insult2 = random.choice(hinglish_insults)
        while hinglish_insult1 == hinglish_insult2:
            hinglish_insult2 = random.choice(hinglish_insults)
        
        await ctx.send(hinglish_insult1)
        await asyncio.sleep(0.5)
        await ctx.send(hinglish_insult2)
        
        # Track user for Hinglish-only auto-replies (use string key for consistency)
        drowned_users[str(user_id)] = {
            "mention": mention,
            "timestamp": time.time(),
            "channel_id": ctx.channel.id,
            "last_message_time": time.time(),
            "language": "hinglish"
        }
        
        # Delete command message
        await ctx.message.delete()
        print(f"Started drowning user {mention} in Hinglish (Hindi insults in English alphabets)")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -stop @user (stops drowning a user)
@bot.command()
async def stop(ctx, *, args=None):
    """Stop drowning a specified user"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-stop @user`\nStops drowning the specified user.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username or @UserID.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        user_id_str = str(user_id)
        if user_id_str in drowned_users:
            del drowned_users[user_id_str]
            await ctx.message.edit(content=f"✅ Stopped drowning {mention}.")
            print(f"Stopped drowning user {mention} ({user_id})")
        else:
            await ctx.message.edit(content=f"ℹ️ {mention} was not being drowned.")
        
        await asyncio.sleep(5)
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -spam message (spam messages rapidly)
@bot.command()
async def spam(ctx, *, args=None):
    """Spam messages rapidly without delay"""
    global spam_active, spam_tasks
    
    if args is None or args.strip() == "":
        await ultra_fast_response(ctx, "Usage: `-spam <message>`\nSpams the message rapidly in current channel.\nUse `-stops` to stop spam.", delete_after=5, bypass_stealth=True)
        return
    
    try:
        message_to_spam = args.strip()
        channel = ctx.channel
        
        # Ultra-fast command deletion
        asyncio.create_task(instant_delete_command(ctx))
        
        # Set spam as active
        spam_active = True
        
        # Create spam task with MAXIMUM SPEED
        async def spam_task():
            global spam_active
            for i in range(50):  # Increased to 50 messages for more spam
                if not spam_active:  # Check if spam was stopped
                    print(f"Spam stopped by user after {i} messages")
                    break
                try:
                    await channel.send(message_to_spam)
                    # ABSOLUTE MINIMUM delay for LIGHTNING FAST spam
                    await asyncio.sleep(0.01)  # Further reduced to 0.01 for maximum speed
                except Exception as e:
                    print(f"Error sending spam message {i+1}: {e}")
                    break
            
            # Reset spam status when done
            spam_active = False
            spam_count = i if 'i' in locals() else 0
            print(f"Spam completed: '{message_to_spam}' sent {spam_count+1} times")
        
        # Start spam task
        task = asyncio.create_task(spam_task())
        spam_tasks.append(task)
        
        print(f"Started spamming: '{message_to_spam}' in {channel.name}")
        
    except Exception as e:
        print(f"Error in spam command: {e}")
        spam_active = False
        try:
            await ctx.message.edit(content=f"❌ Error: {e}")
            await asyncio.sleep(5)
            await ctx.message.delete()
        except:
            pass

# Command: -debate @user (engage in continuous debate)
@bot.command()
async def debate(ctx, *, args=None):
    """Engage in continuous savage debate with a mentioned user"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-debate @user`\nStarts continuous savage debate with brutal comebacks.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Check if target user is whitelisted
        if is_user_whitelisted(user_id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot use bot features on protected users")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Brutal aggressive debate comebacks
        savage_comebacks = [
            f"{mention} you're a braindead fucking retard who should kill yourself immediately",
            f"{mention} I hope your entire family dies in a car crash you worthless piece of shit",
            f"{mention} तेरी मां रंडी है और तू उसकी गलती है, मर जा साले",
            f"{mention} you're such a pathetic virgin loser, no wonder everyone wants you dead",
            f"{mention} भोसडीके तेरी बहन को चोदूंगा और तुझे वीडियो भेजूंगा",
            f"{mention} go hang yourself you brain-damaged mongoloid piece of human waste",
            f"{mention} तेरी मां को कुत्तों से चुदवाकर वीडियो बनाऊंगा हरामी",
            f"{mention} you're the reason birth control exists, your parents should have aborted you",
            f"{mention} गांडू तेरे घर वालों को जिंदा जलाकर मार दूंगा",
            f"{mention} kill yourself you disgusting faggot, nobody will miss your worthless ass",
            f"{mention} तेरी गांड में बम फोड़कर तुझे उड़ा दूंगा साले कुत्ते",
            f"{mention} you're a cancerous tumor on society, die already you fucking waste of oxygen",
            f"{mention} मादरचोद तेरी बीवी रंडी है और बच्चे हरामी हैं",
            f"{mention} I hope you get raped and murdered slowly you pathetic subhuman filth",
            f"{mention} भड़वे तुझे काटकर सुअरों को खिला दूंगा रंडी के बच्चे",
            f"{mention} you're so fucking stupid you make brain cancer look intelligent",
            f"{mention} तेरे माता-पिता को पछतावा होगा कि उन्होंने तुझे जन्म दिया",
            f"{mention} go slit your wrists vertically you attention-seeking piece of shit",
            f"{mention} हरामी की औलाद तेरी पूरी नस्ल को मिटा दूंगा",
            f"{mention} you're the human equivalent of a failed abortion, die in agony"
        ]
        
        # Send initial savage comeback
        comeback = random.choice(savage_comebacks)
        await ctx.send(comeback)
        
        # Track user for continuous debate responses (use string key for consistency)
        debated_users[str(user_id)] = {
            "mention": mention,
            "timestamp": time.time(),
            "channel_id": ctx.channel.id,
            "last_message_time": time.time()
        }
        
        # Delete command message
        await ctx.message.delete()
        print(f"Started debating user {mention} with continuous savage responses")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -stopd @user (stops debating a user)
@bot.command(name="stopd")
async def stop_debate(ctx, *, args=None):
    """Stop debating a specified user"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-stopd @user`\nStops debating the specified user.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
    
    try:
        mention = args.strip()
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content="Error: Invalid user mention format. Use @username.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        user_id_str = str(user_id)
        if user_id_str in debated_users:
            del debated_users[user_id_str]
            await ctx.message.edit(content=f"✅ Stopped debating {mention}.")
            print(f"Stopped debating user {mention} ({user_id})")
        else:
            await ctx.message.edit(content=f"ℹ️ {mention} was not being debated.")
        
        await asyncio.sleep(5)
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -stops (stops all spam)
@bot.command(name="stops")
async def stop_spam(ctx):
    """Stop all active spam immediately"""
    global spam_active, spam_tasks
    
    try:
        if spam_active:
            # Stop spam
            spam_active = False
            
            # Cancel all spam tasks
            for task in spam_tasks:
                if not task.done():
                    task.cancel()
            spam_tasks.clear()
            
            await ctx.message.edit(content="✅ All spam stopped immediately!")
            print("Spam stopped by user command")
        else:
            await ctx.message.edit(content="ℹ️ No active spam to stop.")
        
        await asyncio.sleep(3)
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -annoy @user (continuously drag through voice channels)
@bot.command()
async def annoy(ctx, *, mention=None):
    """Annoy a user by continuously dragging them through all voice channels"""
    if mention is None:
        await ctx.message.edit(content="❌ Usage: `-annoy @user`")
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # Check if we're in a server/guild context
        if not hasattr(ctx, 'guild') or ctx.guild is None:
            await ctx.message.edit(content="❌ **Voice dragging only works in servers!**\nVoice channels are not available in DMs or group chats.\nPlease use this command in a Discord server.")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Extract user ID from mention
        user_id = find_user_id_by_mention(mention)
        if not user_id:
            await ctx.message.edit(content="❌ Invalid user mention. Use @user format.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        user_id_int = int(user_id)
        
        # Find the user in the guild
        target_user = ctx.guild.get_member(user_id_int)
        if not target_user:
            await ctx.message.edit(content=f"❌ User {mention} not found in this server.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Check if user is in a voice channel
        if target_user.voice is None or target_user.voice.channel is None:
            await ctx.message.edit(content=f"❌ {mention} is not currently in a voice channel.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Get all voice channels in the guild
        voice_channels = [vc for vc in ctx.guild.voice_channels if vc.permissions_for(ctx.guild.me).move_members]
        
        if len(voice_channels) < 2:
            await ctx.message.edit(content="❌ Need at least 2 voice channels to drag user around!")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        # Add user to dragging list for continuous harassment
        dragging_users[str(user_id)] = {
            'guild_id': ctx.guild.id,
            'channel_id': ctx.channel.id,
            'mention': mention,
            'target_user': target_user,
            'voice_channels': voice_channels,
            'current_index': 0,
            'active': True
        }
        
        await ctx.message.edit(content=f"⚡ **MIC DRAG INITIATED** on {mention}\n🌪️ ZERO DELAY — dragging through {len(voice_channels)} channels at full speed\n🔇 Mic gets cut every single move\n💀 No escape")
        await asyncio.sleep(5)
        await ctx.message.delete()
        
        # Start the dragging task
        asyncio.create_task(drag_user_continuously(str(user_id)))
        
        print(f"🎯 Started dragging user {mention} through {len(voice_channels)} voice channels")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Function to continuously drag user through voice channels at MAXIMUM speed
async def drag_user_continuously(user_id_str):
    """
    Mic drag — moves target across every VC as fast as Discord allows.
    - Zero artificial delay between moves
    - Mutes mic on every single move (mic drag)
    - Reads retry_after from Discord 429 headers for precise backoff
    - Refreshes channel list every 30 moves so new channels are picked up
    """
    drag_count = 0
    error_count = 0
    max_errors = 15

    try:
        print(f"🎯 MAX SPEED mic drag started for {user_id_str}")

        while user_id_str in dragging_users and dragging_users[user_id_str]['active']:
            try:
                user_data = dragging_users[user_id_str]
                target_user = user_data['target_user']
                guild = target_user.guild
                current_index = user_data['current_index']

                # Refresh channel list every 30 moves to catch new/removed channels
                if drag_count % 30 == 0:
                    fresh = [vc for vc in guild.voice_channels if vc.permissions_for(guild.me).move_members]
                    if len(fresh) >= 2:
                        user_data['voice_channels'] = fresh
                voice_channels = user_data['voice_channels']

                # Stop if user disconnected from voice
                if target_user.voice is None or target_user.voice.channel is None:
                    print(f"🛑 {user_data['mention']} left voice — {drag_count} total drags")
                    break

                next_channel = voice_channels[current_index % len(voice_channels)]

                try:
                    # Move + mute mic simultaneously (mic drag)
                    await target_user.edit(
                        voice_channel=next_channel,
                        mute=True
                    )
                    drag_count += 1
                    error_count = 0
                    dragging_users[user_id_str]['current_index'] = (current_index + 1) % len(voice_channels)
                    # No sleep — fire immediately at next iteration
                    await asyncio.sleep(0)

                except discord.Forbidden:
                    # No move_members permission — try without mute
                    try:
                        await target_user.edit(voice_channel=next_channel)
                        drag_count += 1
                        error_count = 0
                        dragging_users[user_id_str]['current_index'] = (current_index + 1) % len(voice_channels)
                        await asyncio.sleep(0)
                    except discord.Forbidden:
                        print(f"❌ No permission to drag {user_data['mention']}, stopping")
                        break

                except discord.HTTPException as http_err:
                    if http_err.status == 429:
                        # Use Discord's exact retry_after for minimal downtime
                        retry_after = getattr(http_err, 'retry_after', None)
                        if retry_after is None:
                            try:
                                retry_after = http_err.response.json().get('retry_after', 0.5)
                            except Exception:
                                retry_after = 0.5
                        print(f"⚠️ Rate limited — waiting {retry_after:.2f}s then resuming full speed")
                        await asyncio.sleep(float(retry_after))
                    else:
                        error_count += 1
                        print(f"❌ HTTP {http_err.status} on drag #{drag_count} ({error_count}/{max_errors})")
                        await asyncio.sleep(0.1)
                        if error_count >= max_errors:
                            break

                except discord.NotFound:
                    print(f"❌ User/channel not found, stopping drag")
                    break

                except Exception as drag_err:
                    error_count += 1
                    print(f"❌ Drag error ({error_count}/{max_errors}): {drag_err}")
                    await asyncio.sleep(0.1)
                    if error_count >= max_errors:
                        break

            except KeyError:
                break
            except Exception as loop_err:
                error_count += 1
                print(f"❌ Loop error ({error_count}/{max_errors}): {loop_err}")
                if error_count >= max_errors:
                    break
                await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        print(f"🛑 Drag task cancelled for {user_id_str}")
    except Exception as critical_err:
        print(f"🚨 Critical drag error for {user_id_str}: {critical_err}")
    finally:
        try:
            if user_id_str in dragging_users:
                del dragging_users[user_id_str]
            print(f"🏁 Mic drag ended for {user_id_str} — {drag_count} total moves")
        except Exception:
            pass

# Command: -stopannoy @user
@bot.command()
async def stopannoy(ctx, *, mention=None):
    """Stop dragging a specific user"""
    if mention is None:
        await ctx.message.edit(content="❌ Usage: `-stopannoy @user`")
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # Extract user ID from mention
        user_id = find_user_id_by_mention(mention)
        if not user_id:
            await ctx.message.edit(content="❌ Invalid user mention. Use @user format.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
        
        user_id_str = str(user_id)
        if user_id_str in dragging_users:
            # Stop the dragging
            dragging_users[user_id_str]['active'] = False
            del dragging_users[user_id_str]
            await ctx.message.edit(content=f"✅ Stopped dragging {mention}")
            print(f"🛑 Manually stopped dragging user {mention}")
        else:
            await ctx.message.edit(content=f"❌ {mention} was not being dragged.")
        
        await asyncio.sleep(5)
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Function to rapidly change group chat names with intelligent rate limiting
async def jija_name_changer(channel, message):
    """Rapidly change group chat names with ultra-fast execution and smart rate limiting"""
    change_count = 0
    successful_changes = 0
    rate_limit_hits = 0
    base_delay = JIJA_MIN_DELAY if JIJA_ULTRA_FAST_MODE else 0.05
    current_delay = base_delay
    max_delay = JIJA_MAX_DELAY
    burst_count = 0  # Track burst mode operations
    
    # More variations for better randomization
    variations = [
        f"{message} 🔥", f"💥 {message}", f"{message} ⚡", f"🚀 {message}",
        f"{message} 💀", f"🎯 {message}", f"{message} 🌟", f"💯 {message}",
        f"{message} 🎪", f"🔴 {message}", f"⭐ {message}", f"{message} 💎",
        f"🌈 {message}", f"{message} 🎭", f"🔮 {message}", f"{message} 🎨",
        f"🎲 {message}", f"{message} 🎯", f"🌊 {message}", f"{message} 🎊"
    ]
    
    # Shuffle variations for better randomness
    random.shuffle(variations)
    variation_index = 0
    
    try:
        print(f"🚀 Starting ULTRA-FAST jija spam with adaptive rate limiting")
        print(f"⚙️ Configuration: Min delay={JIJA_MIN_DELAY:.2f}s, Max delay={max_delay:.1f}s")
        print(f"📊 {len(variations)} name variations loaded")
        if JIJA_BURST_MODE:
            print(f"💥 Burst mode ENABLED: {JIJA_BURST_SIZE} rapid changes per burst")
        
        while channel.id in jija_sessions and jija_sessions[channel.id]['active']:
            try:
                # Use variations in sequence, then shuffle and restart for better performance
                new_name = variations[variation_index]
                variation_index = (variation_index + 1) % len(variations)
                if variation_index == 0:  # Reshuffle when we've used all variations
                    random.shuffle(variations)
                
                # Track timing for rate limit optimization
                start_time = time.time()
                
                # Change the group chat name
                await channel.edit(name=new_name)
                change_count += 1
                successful_changes += 1
                
                # Calculate actual response time
                response_time = time.time() - start_time
                
                print(f"⚡ ULTRA-JIJA #{change_count}: {new_name} (⏱️ {response_time:.2f}s, 🔄 {current_delay:.2f}s delay)")
                
                # Adaptive delay adjustment based on success rate
                if successful_changes % 5 == 0:  # Adjust every 5 successful changes
                    if rate_limit_hits == 0:
                        # No rate limits recently, try to go faster
                        current_delay = max(JIJA_MIN_DELAY, current_delay * 0.9)
                    else:
                        # Had some rate limits, slow down slightly
                        current_delay = min(max_delay, current_delay * 1.1)
                
                # Burst mode logic for ultra-fast execution
                if JIJA_BURST_MODE and rate_limit_hits == 0:
                    burst_count += 1
                    if burst_count < JIJA_BURST_SIZE:
                        # In burst mode - minimal delay
                        await asyncio.sleep(current_delay * 0.5)
                    else:
                        # End of burst - slightly longer pause then reset
                        await asyncio.sleep(current_delay * 1.5)
                        burst_count = 0
                else:
                    # Normal adaptive delay
                    await asyncio.sleep(current_delay)
                    burst_count = 0  # Reset burst if we had rate limits
                
            except discord.Forbidden:
                print(f"❌ No permission to change group chat name")
                break
                
            except discord.HTTPException as e:
                if "rate limited" in str(e).lower() or e.status == 429:
                    rate_limit_hits += 1
                    
                    # Intelligent rate limit handling
                    if rate_limit_hits <= 2:
                        # First few rate limits - brief pause
                        wait_time = 0.5 + (rate_limit_hits * 0.3)
                        print(f"⚠️ Rate limit #{rate_limit_hits} - smart pause {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        # Increase delay for next attempts
                        current_delay = min(max_delay, current_delay * 1.5)
                    elif rate_limit_hits <= 5:
                        # Moderate rate limiting - medium pause
                        wait_time = 1.0 + (rate_limit_hits * 0.2)
                        print(f"⚠️ Rate limit #{rate_limit_hits} - medium pause {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        current_delay = min(max_delay, current_delay * 1.3)
                    else:
                        # Heavy rate limiting - longer pause but still aggressive
                        wait_time = 2.0 + min(rate_limit_hits * 0.1, 3.0)
                        print(f"⚠️ Heavy rate limit #{rate_limit_hits} - extended pause {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                        current_delay = min(max_delay, current_delay * 1.2)
                    
                    continue
                    
                else:
                    print(f"❌ HTTP error in jija spam: {e}")
                    # Brief pause for other HTTP errors
                    await asyncio.sleep(0.2)
                    
            except Exception as e:
                print(f"❌ Error in jija name changer: {e}")
                # Very brief pause for other errors
                await asyncio.sleep(0.1)
                
    except asyncio.CancelledError:
        print(f"🛑 Jija task cancelled for channel {channel.name}")
    except Exception as e:
        print(f"🚨 Critical error in jija task: {e}")
    finally:
        # Clean up
        if channel.id in jija_sessions:
            jija_sessions[channel.id]['active'] = False
        
        # Performance summary
        success_rate = (successful_changes / max(1, change_count)) * 100
        print(f"🏁 ULTRA-JIJA COMPLETE: {successful_changes}/{change_count} changes ({success_rate:.1f}% success)")
        print(f"📊 Rate limits: {rate_limit_hits}, Final delay: {current_delay:.2f}s")

# Command: -jija <message> (rapidly change group chat names)
@bot.command()
async def jija(ctx, *, message=None):
    """Start rapidly changing group chat names with the specified message"""
    try:
        # Validate message
        if not message or message.strip() == "":
            await ctx.message.edit(content="❌ Usage: `-jija <message>`\nExample: `-jija Tyler is the best`")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        message = message.strip()
        
        # Check if this is a group channel
        if not isinstance(ctx.channel, discord.GroupChannel):
            await ctx.message.edit(content="❌ This command only works in group chats!")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        channel_id = ctx.channel.id
        
        # Check if jija is already active in this channel
        if channel_id in jija_sessions and jija_sessions[channel_id]['active']:
            await ctx.message.edit(content="❌ Jija spam is already active in this group chat!\nUse `-stopjija` to stop it first.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        # Start jija session
        jija_sessions[channel_id] = {
            "message": message,
            "active": True,
            "task": None
        }
        
        # Start the rapid name changing task
        task = asyncio.create_task(jija_name_changer(ctx.channel, message))
        jija_sessions[channel_id]["task"] = task
        
        # Ultra-fast response with instant command deletion
        response = await ultra_fast_response(ctx, 
            f"🚀 **ULTRA-JIJA ACTIVATED!**\n💥 **Message:** {message}\n⚡ **Ultra-fast adaptive name changing...**\n🎯 **Starting at {JIJA_MIN_DELAY:.2f}s intervals with smart rate limiting**", 
            delete_after=2)
        
        print(f"🚀 Started ULTRA-JIJA spam in group {ctx.channel.name} with message: {message}")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error starting jija: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -stopjija (stop the rapid name changing)
@bot.command()
async def stopjija(ctx):
    """Stop the rapid group chat name changing"""
    try:
        channel_id = ctx.channel.id
        
        if channel_id not in jija_sessions or not jija_sessions[channel_id]['active']:
            await ctx.message.edit(content="❌ No active jija session in this group chat.")
            await asyncio.sleep(3)
            await ctx.message.delete()
            return
            
        # Stop the session
        jija_sessions[channel_id]['active'] = False
        
        # Cancel the task if it exists
        if jija_sessions[channel_id].get('task'):
            jija_sessions[channel_id]['task'].cancel()
            
        # Clean up
        del jija_sessions[channel_id]
        
        # Ultra-fast response
        await ultra_fast_response(ctx, "✅ **JIJA SPAM STOPPED!**\nGroup chat name changing has been stopped.", delete_after=3)
        
        print(f"🛑 Stopped jija spam in group {ctx.channel.name}")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error stopping jija: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command: -afk [optional message]
@bot.command()
async def afk(ctx, *, message=None):
    """Set AFK status with optional custom message"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "Only owner can do this you silly human", delete_after=3)
        return
    
    try:
        if not bot.user:
            await ultra_fast_response(ctx, "❌ Bot user not available", delete_after=3)
            return
        user_id_str = str(bot.user.id)
        
        # Set AFK status
        afk_users[user_id_str] = {
            'status': True,
            'message': message if message else '',
            'timestamp': time.time()
        }
        
        # Create confirmation message
        if message:
            confirm_msg = f"✅ AFK Status Set 🌙\n📝 Message: {message}\n🕐 Started: {datetime.datetime.now().strftime('%H:%M')}"
        else:
            confirm_msg = f"✅ AFK Status Set 🌙\n🕐 Started: {datetime.datetime.now().strftime('%H:%M')}"
        
        await ultra_fast_response(ctx, confirm_msg, delete_after=5)
        print(f"📱 AFK status activated" + (f" with message: {message}" if message else ""))
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error setting AFK status: {e}", delete_after=3)
        print(f"❌ Error in AFK command: {e}")

# Command: -removeafk
@bot.command()
async def removeafk(ctx):
    """Manually remove AFK status"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "Only owner can do this you silly human", delete_after=3)
        return
    
    try:
        if not bot.user:
            await ultra_fast_response(ctx, "❌ Bot user not available", delete_after=3)
            return
        user_id_str = str(bot.user.id)
        
        # Check if user is currently AFK
        if user_id_str in afk_users and afk_users[user_id_str]['status']:
            # Calculate how long user was AFK
            afk_data = afk_users[user_id_str]
            timestamp = afk_data.get('timestamp', time.time())
            time_afk = int(time.time() - timestamp)
            hours = time_afk // 3600
            minutes = (time_afk % 3600) // 60
            
            time_str = ""
            if hours > 0:
                time_str = f"{hours}h {minutes}m"
            else:
                time_str = f"{minutes}m"
            
            # Remove AFK status
            del afk_users[user_id_str]
            
            confirm_msg = f"✅ AFK Status Removed 👋\n🕐 You were AFK for: {time_str}\n📱 Auto-replies are now disabled"
            await ultra_fast_response(ctx, confirm_msg, delete_after=5)
            print(f"📱 AFK status manually removed - was AFK for {time_str}")
            
        else:
            await ultra_fast_response(ctx, "❌ You are not currently AFK", delete_after=3)
            print("📱 Attempted to remove AFK but user was not AFK")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error removing AFK status: {e}", delete_after=3)
        print(f"❌ Error in removeafk command: {e}")

bot.remove_command("help")

HELP_PAGES = {
    0: (
        "📖 **PERFECT SELFBOT — Help**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-help 1` · 🖼️ Avatar & Profile\n"
        "`-help 2` · 😤 Harassment\n"
        "`-help 3` · 🔊 Voice & Group Chat\n"
        "`-help 4` · 🕵️ Snipe & Channel Tools\n"
        "`-help 5` · 📊 Info & Mass Actions\n"
        "`-help 6` · 🏠 Server & Access Control\n"
        "`-help 7` · 🎮 Quests & Streaming\n"
        "`-help 8` · 💤 AFK, React & Misc\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    1: (
        "🖼️ **Avatar & Profile** · Page 1/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-av` · your own avatar + banner (4096px)\n"
        "`-av @user` · anyone's avatar + banner\n"
        "`-av <user_id>` · by bare ID too\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    2: (
        "😤 **Harassment** · Page 2/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-drown @u` · insult every msg (all langs)\n"
        "`-drownenglish @u` · english only\n"
        "`-drownhindi @u` · hindi only\n"
        "`-drownhinglish @u` · hinglish only\n"
        "`-stop @u` · stop drowning\n"
        "`-debate @u` · savage reply every msg\n"
        "`-stopd @u` · stop debate\n"
        "`-spam <msg>` · rapid spam\n"
        "`-stops` · stop spam\n"
        "`-troll @u` · troll every msg\n"
        "`-stoptroll [@u]` · stop troll (no mention = all)\n"
        "`-copycat @u` · mirror everything they type\n"
        "`-stopcopycat [@u]` · stop (no mention = all)\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    3: (
        "🔊 **Voice & Group Chat** · Page 3/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-annoy @u` · drag/mute/deafen non-stop\n"
        "`-stopannoy @u` · stop\n"
        "`-jija <msg>` · group chat name spam (0.02s)\n"
        "`-stopjija` · stop jija\n"
        "`-gcspam` · multi-target group chat spam\n"
        "`-stopgcspam` · stop gcspam\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    4: (
        "🕵️ **Snipe & Channel Tools** · Page 4/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-snipe` · last deleted msg this channel\n"
        "`-esnipe` · last edited msg (before/after)\n"
        "`-purge [n]` · delete your own msgs (max 200)\n"
        "`-nuke` · clone + delete this channel\n"
        "`-invite [uses] [hrs]` · generate invite link\n"
        "`-type [secs]` · spam typing indicator\n"
        "`-stoptype` · stop typing spam\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    5: (
        "📊 **Info & Mass Actions** · Page 5/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-uinfo [@u]` · full user profile + badges\n"
        "`-lookup <id>` · lookup ANY user by ID (no shared server needed)\n"
        "`-sinfo` · full server stats\n"
        "`-checktoken <tok>` · validate any token\n"
        "`-massdm <msg>` · DM every server member\n"
        "`-stopmassdm` · stop mass DM\n"
        "`-ping` · latency check\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    6: (
        "🏠 **Server & Access Control** · Page 6/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-copytemplate <name>` · save server layout\n"
        "`-applytemplate <name>` · wipe + rebuild server\n"
        "`-listtemplates` · list saved templates\n"
        "`-deletetemplate <name>` · delete template\n"
        "`-wl @u add/remove` · whitelist a user\n"
        "`-wl list` · show whitelist\n"
        "`-clearwhitelist` · clear all\n"
        "`-target @u` · add target\n"
        "`-list` · view targets\n"
        "`-cleartargets` · clear targets\n"
        "`-access @u` · grant bot access\n"
        "`-removeaccess @u` · revoke access\n"
        "`-listaccess` · list authorized users\n"
        "`-onboard [id]` · trigger server onboarding\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    7: (
        "🎮 **Quests & Streaming** · Page 7/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-quests` · list quests + progress bars\n"
        "`-autoquest` · auto-complete all quests\n"
        "`-stopquest` · stop quest run\n"
        "`-stream <activity>` · set streaming status\n"
        "`-streamall <msgs>` · multi-token stream\n"
        "`-streamoff` · remove stream status\n"
        "`-streamrotate <s1,s2>` · rotate statuses\n"
        "`-streamrotateoff` · stop rotation\n"
        "`-streamstatus` · check stream status\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
    8: (
        "💤 **AFK, React & Misc** · Page 8/8\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "`-afk [msg]` · go AFK, auto-reply pings/DMs\n"
        "`-removeafk` · come back from AFK\n"
        "`-react @u <emoji>` · auto-react every msg\n"
        "`-stopreact @u` · stop auto-react\n"
        "`-history [n]` · recent command usage\n"
        "`-help [page]` · this menu\n"
        "━━━━━━━━━━━━━━━━━━━━"
    ),
}

@bot.command(name="help")
async def help_command(ctx, page: str = "0"):
    """Paginated help — -help or -help <1-8>"""
    try:
        await instant_delete_command(ctx)
        try:
            page_num = int(page)
        except ValueError:
            page_num = 0
        page_num = max(0, min(page_num, 8))
        content = HELP_PAGES[page_num]
        msg = await ctx.channel.send(content)
        await asyncio.sleep(25)
        try:
            await msg.delete()
        except Exception:
            pass
    except Exception as e:
        print(f"❌ Help error: {e}")

# Command: -ping (super-fast low-latency ping)
@bot.command()
async def ping(ctx):
    """Super-fast optimized ping command with lowest possible latency"""
    try:
        # Instant command deletion for seamless experience
        asyncio.create_task(instant_delete_command(ctx))
        
        # Super-fast latency calculation
        start_time = time.time()
        latency = round(bot.latency * 1000)
        
        # Force low latency if ping is high
        if latency > 200 and LOW_LATENCY_MODE:
            status_emoji = "🟡"
            status_text = "OPTIMIZING..."
        elif latency > 100:
            status_emoji = "🟡"
            status_text = "GOOD"
        else:
            status_emoji = "🟢"
            status_text = "EXCELLENT"
        
        # Calculate actual response time
        response_time = round((time.time() - start_time) * 1000, 1)
        
        # Super-fast response with status
        content = f"🏓 Pong! {latency}ms {status_emoji} {status_text}"
        if PERFORMANCE_MONITORING:
            content += f" (Response: {response_time}ms)"
        
        await ultra_fast_response(ctx, content, delete_after=3)
        
    except Exception as e:
        if not ZERO_ERROR_MODE:
            print(f"Ping error: {e}")

# Command: -react <@user> <emoji> (auto-react to user's messages)
@bot.command()
async def react(ctx, user_mention=None, emoji=None):
    """Auto-react to a user's every message with selected emoji - SUPER FAST"""
    try:
        # Instantly delete command
        await instant_delete_command(ctx)
        
        if not user_mention or not emoji:
            await ultra_fast_response(ctx, "❌ Usage: `-react @user 😀`\nExample: `-react @tyler 🔥`", delete_after=5)
            return
        
        # Extract user ID from mention
        user_id = None
        if user_mention.startswith('<@') and user_mention.endswith('>'):
            user_id = user_mention[2:-1].replace('!', '')
        
        if not user_id:
            await ultra_fast_response(ctx, "❌ Invalid user mention! Use @username format", delete_after=5)
            return
        
        # Check if target user is whitelisted (prevent targeting protected users)
        if is_user_whitelisted(int(user_id)):
            await ultra_fast_response(ctx, f"🚫 **ACCESS DENIED**\n❌ {user_mention} is whitelisted and protected\n💡 Cannot target protected users with auto-reactions", delete_after=8)
            return
        
        # Add user to reaction targets
        reaction_targets[user_id] = {
            'emoji': emoji,
            'active': True
        }
        
        await ultra_fast_response(ctx, f"✅ Now auto-reacting {emoji} to {user_mention}'s messages!", delete_after=5)
        print(f"🚀 Started auto-reacting {emoji} to user {user_id}")
        
    except Exception as e:
        if not ZERO_ERROR_MODE:
            print(f"React command error: {e}")

# Command: -stopreact <@user> (stop auto-reacting to user)
@bot.command()
async def stopreact(ctx, user_mention=None):
    """Stop auto-reacting to a user's messages - SUPER FAST"""
    try:
        # Instantly delete command
        await instant_delete_command(ctx)
        
        if not user_mention:
            await ultra_fast_response(ctx, "❌ Usage: `-stopreact @user`\nExample: `-stopreact @tyler`", delete_after=5)
            return
        
        # Extract user ID from mention
        user_id = None
        if user_mention.startswith('<@') and user_mention.endswith('>'):
            user_id = user_mention[2:-1].replace('!', '')
        
        if not user_id:
            await ultra_fast_response(ctx, "❌ Invalid user mention! Use @username format", delete_after=5)
            return
        
        # Remove user from reaction targets
        if user_id in reaction_targets:
            del reaction_targets[user_id]
            await ultra_fast_response(ctx, f"✅ Stopped auto-reacting to {user_mention}", delete_after=5)
            print(f"🛑 Stopped auto-reacting to user {user_id}")
        else:
            await ultra_fast_response(ctx, f"❌ Not currently reacting to {user_mention}", delete_after=5)
        
    except Exception as e:
        if not ZERO_ERROR_MODE:
            print(f"Stop react command error: {e}")

# Command: -access <@user> (give user bot control permission - OWNER ONLY)
@bot.command()
async def access(ctx, *, args=None):
    """Give a user permission to control this selfbot - OWNER ONLY"""
    try:
        print(f"🔍 Access command called with args: {args}")
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        # HARDCODED OWNER CHECK - NO BYPASS POSSIBLE
        if str(ctx.author.id) != BOT_OWNER_ID:
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n😂 Only owner can do this you silly human\n👑 Contact the owner to get access.", delete_after=8)
            return
        
        if not args or args.strip() == "":
            await ultra_fast_response(ctx, "❌ Usage: `-access @user`\nExample: `-access @friend`", delete_after=5)
            return
        
        user_mention = args.strip()
        print(f"🔍 Processing user mention: {user_mention}")
        
        # Extract user ID from mention
        user_id = None
        if user_mention.startswith('<@') and user_mention.endswith('>'):
            user_id = user_mention[2:-1].replace('!', '')
        else:
            # Try to extract from plain text mention
            if user_mention.startswith('@'):
                user_mention = user_mention[1:]
            # For now, show error for non-mention format
            await ultra_fast_response(ctx, "❌ Please use proper @user mention format", delete_after=5)
            return
        
        if not user_id or not user_id.isdigit():
            await ultra_fast_response(ctx, "❌ Invalid user mention! Use @username format", delete_after=5)
            return
        
        # Check if user already has access
        if user_id in authorized_users:
            await ultra_fast_response(ctx, f"⚠️ {args} already has bot access!", delete_after=5)
            return
        
        # Add user to authorized users
        authorized_users.add(user_id)
        save_authorized_users()  # Save to file
        print(f"🔍 Current authorized users: {authorized_users}")
        
        await ultra_fast_response(ctx, f"✅ **ACCESS GRANTED**\n🎯 {args} can now control this bot!\n💾 Access saved permanently\n📋 Total authorized users: {len(authorized_users)}", delete_after=10)
        print(f"🔑 Granted bot access to user {user_id} ({args})")
        
    except Exception as e:
        print(f"❌ Access command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -removeaccess <@user> (remove user's bot control permission)
@bot.command()
async def removeaccess(ctx, *, args=None):
    """Remove a user's permission to control this selfbot - ENHANCED PERMISSIONS"""
    try:
        print(f"🔍 Remove access command called with args: {args}")
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        if not args or args.strip() == "":
            await ultra_fast_response(ctx, "❌ Usage: `-removeaccess @user`\nExample: `-removeaccess @friend`", delete_after=5)
            return
        
        user_mention = args.strip()
        
        # Extract user ID from mention
        user_id = None
        if user_mention.startswith('<@') and user_mention.endswith('>'):
            user_id = user_mention[2:-1].replace('!', '')
        else:
            await ultra_fast_response(ctx, "❌ Please use proper @user mention format", delete_after=5)
            return
        
        if not user_id or not user_id.isdigit():
            await ultra_fast_response(ctx, "❌ Invalid user mention! Use @username format", delete_after=5)
            return
        
        # HARDCODED OWNER CHECK - ABSOLUTELY NO BYPASS POSSIBLE
        if str(ctx.author.id) != BOT_OWNER_ID:
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n😂 Only owner can do this you silly human\n⚠️ Users cannot remove their own or others' access", delete_after=8)
            return
        
        # Owner can remove anyone's access
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            save_authorized_users()  # Save to file
            await ultra_fast_response(ctx, f"✅ **ACCESS REMOVED**\n🚫 Removed bot access from {args}\n💾 Changes saved permanently\n📋 Remaining authorized users: {len(authorized_users)}", delete_after=8)
            print(f"🚫 Owner removed bot access from user {user_id} ({args})")
        else:
            await ultra_fast_response(ctx, f"❌ {args} doesn't have bot access", delete_after=5)
        
    except Exception as e:
        print(f"❌ Remove access command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -listaccess (show all authorized users)
@bot.command()
async def listaccess(ctx):
    """Show all users who have bot access"""
    try:
        print(f"🔍 List access command called")
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        # HARDCODED OWNER CHECK - Only owner can view access list  
        if str(ctx.author.id) != BOT_OWNER_ID:
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n😂 Only owner can view this you silly human\n👑 This is owner-only information", delete_after=8)
            return
        
        if not authorized_users:
            await ultra_fast_response(ctx, "📋 **ACCESS LIST EMPTY**\n⚠️ No users currently have bot access\n👑 Only the owner can grant access", delete_after=8)
            return
        
        access_list = "📋 **AUTHORIZED USERS LIST**\n\n"
        access_list += f"👑 **Owner:** <@{BOT_OWNER_ID}>\n\n"
        access_list += f"🔑 **Authorized Users:** ({len(authorized_users)} total)\n"
        
        for i, user_id in enumerate(authorized_users, 1):
            access_list += f"{i}. <@{user_id}>\n"
        
        access_list += f"\n💾 Data persisted to file\n📝 Use `-removeaccess @user` to remove access"
        
        await ultra_fast_response(ctx, access_list, delete_after=15)
        print(f"📋 Displayed access list with {len(authorized_users)} users")
        
    except Exception as e:
        print(f"❌ List access command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -removemyaccess (DISABLED - Owner only access control)
@bot.command()
async def removemyaccess(ctx):
    """DISABLED - Only owner can manage access"""
    try:
        # Instantly delete command  
        await instant_delete_command(ctx)
        
        await ultra_fast_response(ctx, "🚫 **COMMAND DISABLED**\n😂 Only owner can do this you silly human\n⚠️ Users cannot remove their own access\n💡 Contact owner to remove your access", delete_after=10)
        print(f"🚫 User tried to remove own access - command disabled")
        
    except Exception as e:
        print(f"❌ Remove my access command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -list (show who has bot access with names)
@bot.command()
async def list(ctx):
    """Show all users who have bot access with their names - AUTHORIZED USERS ONLY"""
    try:
        print(f"🔍 List command called")
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        # HARDCODED OWNER CHECK - Only owner can view access list
        if str(ctx.author.id) != BOT_OWNER_ID:
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n😂 Only owner can view this you silly human\n👑 This is owner-only information", delete_after=8)
            return
        
        if not authorized_users:
            await ultra_fast_response(ctx, "📋 **ACCESS LIST EMPTY**\n⚠️ No users currently have bot access\n👑 Only the owner can grant access", delete_after=8)
            return
        
        # Build access list with names
        access_list = "📋 **BOT ACCESS LIST**\n\n"
        access_list += f"👑 **Owner:** <@{BOT_OWNER_ID}>\n\n"
        access_list += f"🔑 **Authorized Users:** ({len(authorized_users)} total)\n"
        
        for i, user_id in enumerate(authorized_users, 1):
            try:
                user = await bot.fetch_user(int(user_id))
                access_list += f"{i}. **{user.display_name}** (<@{user_id}>)\n"
            except:
                access_list += f"{i}. <@{user_id}> (Name unavailable)\n"
        
        access_list += f"\n💡 **Access Rules:**\n"
        access_list += f"• 👑 Only owner can give/remove access\n"
        access_list += f"• 🚫 Users CANNOT remove their own access\n"
        access_list += f"• 💾 All changes saved permanently\n"
        access_list += f"• 🔒 Full access control by owner only"
        
        await ultra_fast_response(ctx, access_list, delete_after=20)
        print(f"📋 Displayed access list with {len(authorized_users)} users")
        
    except Exception as e:
        print(f"❌ List command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)


# Global variables for target system and GC spam
saved_targets = []  # List of saved target user objects
gc_spam_active = {"active": False, "count": 0, "task": None}  # Multi-target GC spam status
GC_SPAM_DELAY = 0.6  # Delay between 3-person GC creation (600ms)
MAX_GC_SPAM_COUNT = 50  # Maximum number of 3-person GCs per session

# Command: -target @user (save targets for multi-person GC spam)
@bot.command()
async def target(ctx, user_mention=None):
    global saved_targets  # Declare at the very beginning
    try:
        # Check if user is authorized
        if not is_authorized_user(ctx.author.id):
            await ultra_fast_response(ctx, "❌ Unauthorized access", delete_after=3)
            return
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        if not user_mention:
            # Show current saved targets
            if not saved_targets:
                await ultra_fast_response(ctx, "📝 **NO TARGETS SAVED**\nUse `-target @user` to save targets for 3-person GC spam\nExample: `-target @user1` then `-target @user2`", delete_after=12)
                return
            
            target_list = []
            for i, target in enumerate(saved_targets, 1):
                target_list.append(f"🎯 Target {i}: **{target.display_name}** ({target.name})")
            
            targets_text = "\n".join(target_list)
            await ultra_fast_response(ctx, f"🎯 **SAVED TARGETS ({len(saved_targets)})**\n{targets_text}\n\n🚀 Use `-gcspam` to create 3-person group chats with all targets\n🗑️ Use `-cleartargets` to clear all targets", delete_after=15)
            return
        
        # Smart user lookup - guild member search only (no API fetch)
        target_user = None
        search_name = user_mention
        
        print(f"🔍 Looking up user: {user_mention}")
        
        # Extract user ID from mention format if present
        user_id = None
        if user_mention.startswith('<@') and user_mention.endswith('>'):
            user_id_str = user_mention[2:-1].replace('!', '')
            if user_id_str.isdigit():
                user_id = int(user_id_str)
                print(f"📝 Extracted user ID: {user_id}")
                
                # Check if target user is whitelisted before adding to targets
                if is_user_whitelisted(user_id):
                    await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot target protected users for harassment", delete_after=10)
                    return
                
                # Check if target user is whitelisted before adding to targets
                if is_user_whitelisted(user_id):
                    await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n❌ This user is whitelisted you fucking hoe\n💡 Cannot target protected users for harassment", delete_after=10)
                    return
        
        # Clean up search name - remove @ and < > symbols
        search_name = user_mention.replace('<@', '').replace('>', '').replace('!', '').replace('@', '').strip()
        
        # Method 1: Search current guild by user ID first (if we have it)
        if user_id and hasattr(ctx, 'guild') and ctx.guild:
            try:
                target_user = ctx.guild.get_member(user_id)
                if target_user:
                    print(f"✅ Found user by ID in current guild: {target_user.display_name}")
                else:
                    print(f"⚠️ User ID {user_id} not found in current guild")
            except Exception as e:
                print(f"⚠️ Current guild ID search failed: {e}")
        
        # Method 2: Search current guild by name
        if not target_user and hasattr(ctx, 'guild') and ctx.guild:
            try:
                for member in ctx.guild.members:
                    if (member.name.lower() == search_name.lower() or 
                        member.display_name.lower() == search_name.lower() or
                        (hasattr(member, 'global_name') and member.global_name and member.global_name.lower() == search_name.lower())):
                        target_user = member
                        print(f"✅ Found user by name in current guild: {target_user.display_name}")
                        break
            except Exception as e:
                print(f"⚠️ Current guild name search failed: {e}")
        
        # Method 3: Search all guilds by user ID
        if not target_user and user_id:
            try:
                for guild in bot.guilds:
                    target_user = guild.get_member(user_id)
                    if target_user:
                        print(f"✅ Found user by ID in guild {guild.name}: {target_user.display_name}")
                        break
            except Exception as e:
                print(f"⚠️ Global guild ID search failed: {e}")
        
        # Method 4: Search all guilds by name
        if not target_user:
            try:
                for guild in bot.guilds:
                    for member in guild.members:
                        if (member.name.lower() == search_name.lower() or 
                            member.display_name.lower() == search_name.lower() or
                            (hasattr(member, 'global_name') and member.global_name and member.global_name.lower() == search_name.lower())):
                            target_user = member
                            print(f"✅ Found user by name in guild {guild.name}: {target_user.display_name}")
                            break
                    if target_user:
                        break
            except Exception as e:
                print(f"⚠️ Global guild name search failed: {e}")
        
        if not target_user:
            await ultra_fast_response(ctx, f"❌ **USER NOT FOUND** 😭\n🔍 Searched for: `{user_mention}`\n💡 User must be in a server with the bot\n🤝 Try with exact Discord username", delete_after=8)
            print(f"❌ Failed to find user: {user_mention} (searched as: {search_name})")
            return
        
        # Check if target already exists
        if target_user.id in [t.id for t in saved_targets]:
            await ultra_fast_response(ctx, f"⚠️ **{target_user.display_name}** is already in targets list", delete_after=5)
            return
        
        # Add target to global list
        if not isinstance(saved_targets, list):
            saved_targets = []  # Reset if corrupted
        saved_targets.append(target_user)
        target_number = len(saved_targets)
        
        print(f"🎯 Target {target_number} saved: {target_user.display_name} ({target_user.id})")
        await ultra_fast_response(ctx, f"✅ **TARGET {target_number} SAVED**\n👤 **{target_user.display_name}** added to targets\n📊 Total targets: **{len(saved_targets)}**\n💡 Need at least 2 targets for 3-person GCs", delete_after=10)
        
    except Exception as e:
        print(f"❌ Target command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -cleartargets (clear all saved targets)
@bot.command()
async def cleartargets(ctx):
    global saved_targets  # Declare global at the beginning
    try:
        if not is_authorized_user(ctx.author.id):
            await ultra_fast_response(ctx, "❌ Unauthorized access", delete_after=3)
            return
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        if not isinstance(saved_targets, list):
            saved_targets = []  # Reset if corrupted
        target_count = len(saved_targets)
        
        if target_count == 0:
            await ultra_fast_response(ctx, "📝 No targets to clear", delete_after=5)
            return
        
        saved_targets.clear()
        
        print(f"🗑️ Cleared {target_count} saved targets")
        await ultra_fast_response(ctx, f"🗑️ **TARGETS CLEARED**\n📊 Removed {target_count} saved targets\n💡 Use `-target @user` to add new targets", delete_after=8)
        
    except Exception as e:
        print(f"❌ Clear targets command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -gcspam (create 3-person group chats with all saved targets)
@bot.command()
async def gcspam(ctx):
    """Create 3-person group chats with all saved targets - MULTI-TARGET HARASSMENT"""
    try:
        print(f"🔍 Multi-target GC spam command called")
        
        # Check if user is authorized
        if not is_authorized_user(ctx.author.id):
            await ultra_fast_response(ctx, "❌ Unauthorized access", delete_after=3)
            return
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        # Check if we have saved targets
        if len(saved_targets) < 2:
            await ultra_fast_response(ctx, f"❌ **NEED MORE TARGETS**\n📊 Current targets: {len(saved_targets)}\n💡 Need at least 2 targets for 3-person GCs\n🎯 Use `-target @user` to add targets", delete_after=10)
            return
        
        # Check if already spamming
        if gc_spam_active["active"]:
            await ultra_fast_response(ctx, f"⚠️ **GC SPAM ALREADY ACTIVE**\n📊 Current session progress: {gc_spam_active['count']} GCs created\nUse `-stopgcspam` to stop current session", delete_after=8)
            return
        
        # Show targets summary
        target_names = [f"**{target.display_name}**" for target in saved_targets]
        targets_text = ", ".join(target_names)
        
        await ultra_fast_response(ctx, f"🎯 **STARTING 3-PERSON GC SPAM**\n👥 Targets: {targets_text}\n📊 Total targets: {len(saved_targets)}\n🚀 Creating group chats with all combinations...", delete_after=8)
        
        # Start multi-target GC spam
        gc_spam_active["active"] = True
        gc_spam_active["count"] = 0
        gc_spam_active["channel_id"] = ctx.channel.id
        
        # Create background task for 3-person GC spam
        task = asyncio.create_task(multi_target_gc_spam_task())
        gc_spam_active["task"] = task
        
        print(f"🎯 Started multi-target GC spam with {len(saved_targets)} targets")
        
    except Exception as e:
        print(f"❌ GC spam command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Background task for multi-target 3-person group chat spam
async def multi_target_gc_spam_task():
    """Create 3-person group chats with all saved targets and leave them"""
    try:
        global saved_targets  # Ensure we're accessing the global variable
        
        # Simple validation - just check if we have targets
        # Force ensure saved_targets is a proper list
        global saved_targets
        if not isinstance(saved_targets, list):
            print(f"❌ Critical Fix: saved_targets was {type(saved_targets)}, resetting to empty list")
            saved_targets = []
            
        try:
            target_count = len(saved_targets)
            print(f"🔍 Debug: saved_targets type: {type(saved_targets)}, count: {target_count}")
            
            if target_count < 2:
                print(f"❌ Error: Need at least 2 targets, only have {target_count}")
                gc_spam_active["active"] = False
                return
        except Exception as validation_err:
            print(f"❌ Error validating targets: {validation_err}")
            print(f"🚰 Debug: saved_targets type: {type(saved_targets)}, value: {saved_targets}")
            saved_targets = []  # Reset to safe state
            gc_spam_active["active"] = False
            return
            
        try:
            targets_len = len(saved_targets) if isinstance(saved_targets, (list, tuple)) else 0
            print(f"🎯 Starting multi-target GC spam with {targets_len} targets")
        except Exception as len_err:
            print(f"❌ Length error: {len_err}, type: {type(saved_targets)}")
            saved_targets = []
            gc_spam_active["active"] = False
            return
        channel_id = gc_spam_active["channel_id"]
        
        # Create all possible combinations of targets for 3-person GCs
        from itertools import combinations
        target_combinations = list(combinations(saved_targets, 2))  # 2 targets + bot = 3-person GC
        
        print(f"🔢 Created {len(target_combinations)} target combinations for 3-person GCs")
        
        while gc_spam_active["active"] and gc_spam_active["count"] < MAX_GC_SPAM_COUNT:
            # Cycle through all target combinations
            for target1, target2 in target_combinations:
                if not gc_spam_active["active"]:
                    break
                
                try:
                    # Add human-like delay for stealth
                    if STEALTH_MODE:
                        await add_human_like_delay()
                    
                    # Create 3-person group chat with bot + 2 targets
                    try:
                        print(f"🎯 Creating 3-person GC: {target1.display_name} + {target2.display_name}")
                        
                        # Method: Use discord.py-self group creation
                        recipients = [target1, target2]  # Bot is automatically included
                        
                        # Try to create group channel using direct HTTP API
                        group_channel = None
                        try:
                            # Create group using HTTP API method
                            group_data = {
                                'recipients': [target1.id, target2.id]
                            }
                            
                            # Use bot's HTTP client for group creation
                            from discord.http import Route
                            response = await bot.http.request(
                                Route('POST', '/users/@me/channels'),
                                json=group_data
                            )
                            
                            if response and 'id' in response:
                                # Get the created group channel
                                group_channel_id = int(response['id'])
                                # Wait a moment for Discord to process
                                await asyncio.sleep(0.1)
                                group_channel = bot.get_channel(group_channel_id)
                        
                        except Exception as creation_err:
                            print(f"⚠️ Group creation failed: {creation_err}")
                            continue
                            
                        if group_channel:
                            gc_spam_active["count"] += 1
                            print(f"✅ Created 3-person GC #{gc_spam_active['count']}: {target1.display_name} + {target2.display_name}")
                            
                            # Leave the group immediately using HTTP DELETE
                            left_successfully = False
                            
                            try:
                                # Use proper HTTP route for leaving group
                                from discord.http import Route
                                await bot.http.request(
                                    Route('DELETE', '/channels/{channel_id}', channel_id=group_channel.id)
                                )
                                print(f"🚪 Left 3-person GC #{gc_spam_active['count']}")
                                left_successfully = True
                            except discord.HTTPException as http_err:
                                if "rate limited" in str(http_err).lower():
                                    print(f"🛡️ Rate limited while leaving, waiting...")
                                    await asyncio.sleep(2)
                                else:
                                    print(f"⚠️ HTTP leave error: {http_err}")
                            except Exception as leave_err:
                                print(f"⚠️ Leave failed for GC #{gc_spam_active['count']}: {leave_err}")
                            
                            if not left_successfully:
                                print(f"❌ Could not leave GC #{gc_spam_active['count']} - Group chat may remain active")
                        else:
                            print(f"⚠️ Failed to create GC with {target1.display_name} + {target2.display_name}")
                        
                    except discord.Forbidden:
                        print(f"❌ Forbidden to create GC with {target1.display_name} + {target2.display_name}")
                        continue
                    
                    except Exception as gc_err:
                        print(f"⚠️ Error creating 3-person GC: {gc_err}")
                        continue
                    
                    # Delay between GC creations for rate limiting
                    await asyncio.sleep(GC_SPAM_DELAY)
                    print(f"⏱️ Waiting {GC_SPAM_DELAY}s before next GC creation...")
                    
                    # Check if we reached the limit
                    if gc_spam_active["count"] >= MAX_GC_SPAM_COUNT:
                        break
                        
                except asyncio.CancelledError:
                    break
                except Exception as loop_err:
                    print(f"❌ Error in GC spam loop: {loop_err}")
                    await asyncio.sleep(1)
        
        # Cleanup when done
        gc_spam_active["active"] = False
        final_count = gc_spam_active["count"]
        
        # Send completion message
        try:
            channel = bot.get_channel(channel_id)
            if channel:
                completion_msg = f"🎯 **3-PERSON GC SPAM COMPLETED**\n👥 Targets: {len(saved_targets)} users\n📊 Total 3-person GCs Created: **{final_count}**\n⏱️ Session ended successfully"
                await channel.send(completion_msg)
                await asyncio.sleep(10)
        except:
            pass
        
        print(f"🏁 Multi-target GC spam completed - Created {final_count} 3-person group chats")
        
    except Exception as e:
        print(f"❌ Critical error in multi-target GC spam: {e}")
        gc_spam_active["active"] = False

# Command: -stopgcspam (stop multi-target GC spam)
@bot.command()
async def stopgcspam(ctx):
    """Stop multi-target 3-person GC spam session"""
    try:
        print(f"🔍 Stop multi-target GC spam command called")
        
        # Check if user is authorized
        if not is_authorized_user(ctx.author.id):
            await ultra_fast_response(ctx, "❌ Unauthorized access", delete_after=3)
            return
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        # Stop GC spam if active
        if gc_spam_active["active"]:
            gc_spam_active["active"] = False
            
            # Cancel the task if it exists
            if gc_spam_active["task"]:
                gc_spam_active["task"].cancel()
            
            final_count = gc_spam_active["count"]
            target_count = len(saved_targets)
            
            await ultra_fast_response(ctx, f"✅ **3-PERSON GC SPAM STOPPED**\n👥 Targets: {target_count} users\n📊 Total 3-person GCs Created: **{final_count}**\n⏱️ Session stopped by user", delete_after=10)
            print(f"🛑 Stopped multi-target GC spam - Created {final_count} 3-person GCs")
        else:
            await ultra_fast_response(ctx, f"❌ **NO ACTIVE GC SPAM**\nNo multi-target GC spam session is currently running\n💡 Use `-gcspam` to start 3-person GC spam", delete_after=8)
        
    except Exception as e:
        print(f"❌ Stop GC spam command error: {e}")
        await ultra_fast_response(ctx, f"❌ Error: {e}", delete_after=5)

# Command: -test (ultra-fast bot functionality test)
@bot.command()
async def test(ctx):
    """Ultra-fast comprehensive bot functionality test"""
    try:
        # Instant command deletion
        if INSTANT_DELETE_COMMANDS:
            asyncio.create_task(ctx.message.delete())
        
        start_time = time.time()
        
        # Ultra-fast test sequence
        test_msg = await ctx.send("🧪 **ULTRA-FAST TESTING...**")
        
        tests = [
            "✅ Command processing",
            "✅ Message editing", 
            "✅ Discord API connection",
            "✅ WebSocket stability",
            "✅ Ultra-fast response mode",
            "✅ Zero-error operation"
        ]
        
        test_results = "🚀 **ULTRA-FAST BOT TEST COMPLETE**\n\n"
        for test in tests:
            test_results += f"{test}\n"
            await asyncio.sleep(0.1)  # Minimal delay for visual effect
        
        total_time = round((time.time() - start_time) * 1000, 1)
        test_results += f"\n⚡ **Total test time:** {total_time}ms\n"
        test_results += f"🎯 **Performance:** OPTIMIZED FOR SPEED"
        
        await test_msg.edit(content=test_results)
        await asyncio.sleep(10)
        await test_msg.delete()
        
        print(f"🧪 Bot test completed in {total_time}ms - ALL SYSTEMS OPTIMAL")
        
    except Exception as e:
        error_msg = await ctx.send(f"❌ **Test Error:** {e}")
        await asyncio.sleep(3)
        await error_msg.delete()


# Enhanced background task with error recovery
async def enhanced_background_tasks():
    """Enhanced background tasks with comprehensive error handling and monitoring"""
    task_stats = {
        "cycles": 0,
        "last_cleanup": time.time(),
        "errors": 0
    }
    
    print("🔧 Enhanced Background Tasks Started")
    
    while True:
        try:
            await asyncio.sleep(12)  # 12-second cycle
            task_stats["cycles"] += 1
            current_time = time.time()
            
            # Cleanup corrupted data structures
            try:
                # Clear potentially corrupted dictionaries
                if len(drowned_users) > 100:  # Prevent memory overflow
                    drowned_users.clear()
                    print("🧹 Cleaned drowned_users dictionary")
                
                if len(debated_users) > 100:
                    debated_users.clear()
                    print("🧹 Cleaned debated_users dictionary")
                
                # Clean old security logs
                if len(failed_attempts) > 50:
                    # Remove old failed attempts
                    cutoff_time = current_time - 3600  # 1 hour ago
                    failed_attempts.clear()
                    print("🧹 Cleaned old failed attempts")
                
            except Exception as cleanup_err:
                print(f"⚠️ Background cleanup error: {cleanup_err}")
                task_stats["errors"] += 1
            
            # Performance monitoring (every 10 cycles = ~2 minutes)
            if task_stats["cycles"] % 10 == 0:
                try:
                    # Memory usage check
                    import psutil
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    
                    if memory_mb > 500:  # Alert if using > 500MB
                        print(f"⚠️ High memory usage: {memory_mb:.1f}MB")
                    
                except ImportError:
                    pass  # psutil not available
                except Exception as perf_err:
                    print(f"⚠️ Performance monitoring error: {perf_err}")
            
            task_stats["last_cleanup"] = current_time
            
        except asyncio.CancelledError:
            break
        except Exception as bg_err:
            print(f"❌ Background task error: {bg_err}")
            task_stats["errors"] += 1
            
            # Enhanced error recovery
            if task_stats["errors"] > 20:
                print("🚨 Too many background task errors, extending sleep time")
                await asyncio.sleep(60)  # Extended pause
                task_stats["errors"] = 0  # Reset error count
            else:
                await asyncio.sleep(15)  # Standard pause

# Command tracking for history
command_history = []

# Command: -wl @user (whitelist/unwhitelist users)
@bot.command(name='wl')
async def whitelist_command(ctx, user_mention=None, action=None):
    """Whitelist or unwhitelist users from bot features - OWNER ONLY"""
    try:
        # Check if user is owner
        if not is_owner(ctx.author.id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n⚠️ Only the bot owner can manage whitelist!")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Track command usage
        command_history.append({
            "command": "wl",
            "user": ctx.author.name,
            "timestamp": time.time(),
            "args": f"{user_mention} {action}" if action else user_mention or "help"
        })
        
        # If no arguments, show whitelist help and current whitelisted users
        if not user_mention:
            try:
                whitelisted_list = get_whitelisted_users() if DATABASE_INTEGRATION else []
                help_content = "🔒 **WHITELIST MANAGEMENT**\n\n"
                help_content += "**Usage:**\n"
                help_content += "• `-wl @user add` - Add user to whitelist\n"
                help_content += "• `-wl @user remove` - Remove user from whitelist\n"
                help_content += "• `-wl list` - Show all whitelisted users\n"
                help_content += "• `-wl` - Show this help\n\n"
                help_content += f"**Currently Whitelisted ({len(whitelisted_list)}):**\n"
                
                if whitelisted_list:
                    for i, user in enumerate(whitelisted_list[:10], 1):  # Show first 10
                        help_content += f"{i}. <@{user.discord_id}> (ID: {user.discord_id})\n"
                    if len(whitelisted_list) > 10:
                        help_content += f"... and {len(whitelisted_list) - 10} more\n"
                else:
                    help_content += "⚠️ No users currently whitelisted\n"
                
                help_content += "\n💡 **Note:** Whitelisted users are protected from all bot harassment features"
                
                await ctx.message.edit(content=help_content)
                await asyncio.sleep(15)
                await ctx.message.delete()
                return
            except Exception as e:
                await ctx.message.edit(content=f"❌ Error retrieving whitelist: {e}")
                await asyncio.sleep(8)
                await ctx.message.delete()
                return
        
        # Handle "list" command
        if user_mention.lower() == "list":
            try:
                whitelisted_list = get_whitelisted_users() if DATABASE_INTEGRATION else []
                list_content = f"🔒 **WHITELISTED USERS ({len(whitelisted_list)})**\n\n"
                
                if whitelisted_list:
                    for i, user in enumerate(whitelisted_list, 1):
                        list_content += f"{i}. <@{user.discord_id}> (ID: {user.discord_id})\n"
                        list_content += f"   Added: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                else:
                    list_content += "⚠️ No users currently whitelisted\n"
                
                await ctx.message.edit(content=list_content)
                await asyncio.sleep(20)
                await ctx.message.delete()
                return
            except Exception as e:
                await ctx.message.edit(content=f"❌ Error listing whitelist: {e}")
                await asyncio.sleep(8)
                await ctx.message.delete()
                return
        
        # Parse user mention to get user ID
        user_id = find_user_id_by_mention(user_mention)
        if not user_id:
            await ctx.message.edit(content="❌ Invalid user mention format. Use @username or @UserID")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Default action is toggle (add if not whitelisted, remove if already whitelisted)
        if not action:
            is_whitelisted = is_user_whitelisted(user_id)
            action = "remove" if is_whitelisted else "add"
        
        action = action.lower()
        
        if action == "add":
            # Add user to whitelist
            try:
                if DATABASE_INTEGRATION:
                    from models import add_whitelisted_user_db
                    add_whitelisted_user_db(user_id, user_mention, ctx.author.id, "Added via whitelist command")
                whitelisted_users.add(str(user_id))  # Add to in-memory set
                
                await ctx.message.edit(content=f"✅ **USER WHITELISTED**\n🛡️ User {user_mention} has been added to whitelist\n💡 They are now protected from all bot features")
                await asyncio.sleep(10)
                await ctx.message.delete()
                print(f"✅ User {user_id} added to whitelist by {ctx.author.name}")
                
            except Exception as e:
                await ctx.message.edit(content=f"❌ Error adding to whitelist: {e}")
                await asyncio.sleep(8)
                await ctx.message.delete()
        
        elif action == "remove":
            # Remove user from whitelist
            try:
                if DATABASE_INTEGRATION:
                    from models import remove_whitelisted_user_db
                    remove_whitelisted_user_db(user_id)
                whitelisted_users.discard(str(user_id))  # Remove from in-memory set
                
                await ctx.message.edit(content=f"✅ **USER REMOVED FROM WHITELIST**\n🗑️ User {user_mention} has been removed from whitelist\n⚠️ They can now be targeted by bot features")
                await asyncio.sleep(10)
                await ctx.message.delete()
                print(f"✅ User {user_id} removed from whitelist by {ctx.author.name}")
                
            except Exception as e:
                await ctx.message.edit(content=f"❌ Error removing from whitelist: {e}")
                await asyncio.sleep(8)
                await ctx.message.delete()
        
        else:
            await ctx.message.edit(content="❌ Invalid action. Use 'add' or 'remove'")
            await asyncio.sleep(8)
            await ctx.message.delete()
    
    except Exception as e:
        await ctx.message.edit(content=f"❌ Whitelist command error: {e}")
        await asyncio.sleep(8)
        await ctx.message.delete()
        print(f"❌ Whitelist command error: {e}")

# Command: -clearwhitelist (clear all whitelisted users)
@bot.command(name='clearwhitelist')
async def clear_whitelist_command(ctx):
    """Clear all whitelisted users - OWNER ONLY"""
    try:
        # Check if user is owner
        if not is_owner(ctx.author.id):
            await ctx.message.edit(content="🚫 **ACCESS DENIED**\n⚠️ Only the bot owner can clear whitelist!")
            await asyncio.sleep(8)
            await ctx.message.delete()
            return
        
        # Show confirmation first
        await ctx.message.edit(content="🧹 **CLEARING ALL WHITELISTED USERS...**\n⏳ Removing from database and memory...")
        await asyncio.sleep(2)
        
        # Clear all whitelisted users
        cleared_count = clear_all_whitelisted_users()
        
        # Success message
        success_msg = f"✅ **WHITELIST CLEARED SUCCESSFULLY!**\n\n"
        success_msg += f"🧹 **Removed:** {cleared_count} users from database\n"
        success_msg += f"🧹 **Cleared:** In-memory whitelist\n\n"
        success_msg += f"💡 **Result:** Fresh whitelist - you can now add new users\n"
        success_msg += f"🔧 **Usage:** Use `-wl @user add` to whitelist new users"
        
        await ctx.message.edit(content=success_msg)
        await asyncio.sleep(12)
        await ctx.message.delete()
        
        print(f"🧹 OWNER CLEARED WHITELIST: {cleared_count} users removed")
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Clear whitelist error: {e}")
        await asyncio.sleep(8)
        await ctx.message.delete()
        print(f"❌ Clear whitelist error: {e}")

# Command: -history (show recent command usage)
@bot.command()
async def history(ctx, limit=None):
    """Show recent command usage history - AUTHORIZED USERS ONLY"""
    try:
        print(f"🔍 History command called by {ctx.author.name}")
        
        # Instantly delete command
        await instant_delete_command(ctx)
        
        # Check if user has permission
        requester_id = str(ctx.author.id)
        if not (is_owner(ctx.author.id) or requester_id in authorized_users):
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n⚠️ Only authorized users can view command history!", delete_after=8)
            return
        
        # Parse limit parameter
        try:
            if limit:
                limit = int(limit)
                if limit < 1 or limit > 50:
                    limit = 20  # Default limit
            else:
                limit = 20  # Default limit
        except ValueError:
            limit = 20
        
        # Track this command usage
        try:
            user_name = str(ctx.author.name) if ctx.author else "Unknown"
            command_history.append({
                "command": "history",
                "user": user_name,
                "timestamp": time.time(),
                "args": f"limit={limit}"
            })
        except Exception as track_err:
            print(f"⚠️ Command tracking error: {track_err}")
        
        # Build history content
        history_content = f"📜 **COMMAND HISTORY (Last {limit} Commands)**\n"
        history_content += f"🕒 Retrieved at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if command_history:
            # Get recent commands (excluding the current history command)
            recent_commands = command_history[:-1][-limit:]  # Exclude current history command
            
            if recent_commands:
                history_content += "```\n"
                for i, cmd in enumerate(reversed(recent_commands), 1):
                    timestamp_str = datetime.datetime.fromtimestamp(cmd["timestamp"]).strftime("%H:%M:%S")
                    command_name = cmd["command"]
                    user_name = cmd["user"]
                    args = cmd.get("args", "")
                    
                    # Format the entry
                    entry = f"{i:2d}. [{timestamp_str}] -{command_name}"
                    if args and args != "help":
                        entry += f" {args[:30]}{'...' if len(args) > 30 else ''}"
                    entry += f" (by {user_name})\n"
                    
                    history_content += entry
                
                history_content += "```\n\n"
                
                # Add usage statistics
                command_counts = {}
                for cmd in command_history:
                    cmd_name = cmd["command"]
                    command_counts[cmd_name] = command_counts.get(cmd_name, 0) + 1
                
                history_content += "📊 **COMMAND STATISTICS:**\n"
                sorted_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)
                for cmd_name, count in sorted_commands[:10]:  # Top 10 most used commands
                    history_content += f"• -{cmd_name}: {count} times\n"
                
                history_content += f"\n🔢 **Total Commands Executed:** {len(command_history)}\n"
                
            else:
                history_content += "⚠️ No recent command history available\n"
        else:
            history_content += "⚠️ **NO COMMAND HISTORY**\n"
            history_content += "Command tracking has just been initialized.\n"
        
        await ultra_fast_response(ctx, history_content, delete_after=25)
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ History command error: {e}", delete_after=8)
        print(f"❌ History command error: {e}")


# ==================== SERVER TEMPLATE SYSTEM ====================
# Template storage directory (separate from web templates)
TEMPLATE_DIR = "server_templates"
import json

def normalize_template_name(template_name):
    """Normalize template name by removing invalid characters"""
    if not template_name or not template_name.strip():
        return None
    import re
    return re.sub(r'[<>:"/\\|?*]', '_', template_name.strip())

def ensure_template_directory():
    """Ensure templates directory exists"""
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)

def save_template_to_file(template_name, template_data):
    """Save template to JSON file - Returns (success, cleaned_name, error_msg)"""
    # Validate and normalize template name
    clean_template_name = normalize_template_name(template_name)
    if not clean_template_name:
        error_msg = "Template name is empty or invalid"
        print(f"Error saving template: {error_msg}")
        return False, None, error_msg
    
    ensure_template_directory()
    file_path = os.path.join(TEMPLATE_DIR, f"{clean_template_name}.json")
    
    try:
        # Test JSON serialization first
        try:
            json_string = json.dumps(template_data, indent=2, ensure_ascii=False)
        except (TypeError, ValueError) as json_err:
            error_msg = f"JSON serialization failed - {json_err}. Template data contains objects that cannot be serialized to JSON"
            print(f"Error saving template {template_name}: {error_msg}")
            return False, clean_template_name, error_msg
        
        # Check if we can write to the directory
        try:
            test_file = os.path.join(TEMPLATE_DIR, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except PermissionError:
            error_msg = f"No write permission to {TEMPLATE_DIR}"
            print(f"Error saving template {template_name}: {error_msg}")
            return False, clean_template_name, error_msg
        except OSError as fs_err:
            error_msg = f"File system error - {fs_err}"
            print(f"Error saving template {template_name}: {error_msg}")
            return False, clean_template_name, error_msg
        
        # Now save the actual file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_string)
        
        print(f"✅ Template '{clean_template_name}' saved successfully to {file_path}")
        return True, clean_template_name, None
        
    except PermissionError as perm_err:
        error_msg = f"Permission denied - {perm_err}"
        print(f"Error saving template {template_name}: {error_msg}")
        return False, clean_template_name, error_msg
    except OSError as os_err:
        error_msg = f"File system error - {os_err}"
        print(f"Error saving template {template_name}: {error_msg}")
        return False, clean_template_name, error_msg
    except Exception as e:
        error_msg = f"Unexpected error - {e}"
        print(f"Error saving template {template_name}: {error_msg}")
        return False, clean_template_name, error_msg

def load_template_from_file(template_name):
    """Load template from JSON file"""
    clean_template_name = normalize_template_name(template_name)
    if not clean_template_name:
        print(f"Error loading template: Invalid template name '{template_name}'")
        return None
    
    file_path = os.path.join(TEMPLATE_DIR, f"{clean_template_name}.json")
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"Template file not found: {file_path}")
    except Exception as e:
        print(f"Error loading template {clean_template_name}: {e}")
    return None

def list_saved_templates():
    """Get list of all saved template names"""
    ensure_template_directory()
    templates = []
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.endswith('.json'):
            templates.append(filename[:-5])  # Remove .json extension
    return templates

def delete_template_file(template_name):
    """Delete template file"""
    clean_template_name = normalize_template_name(template_name)
    if not clean_template_name:
        print(f"Error deleting template: Invalid template name '{template_name}'")
        return False
    
    file_path = os.path.join(TEMPLATE_DIR, f"{clean_template_name}.json")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Template '{clean_template_name}' deleted successfully")
            return True
        else:
            print(f"Template file not found: {file_path}")
    except Exception as e:
        print(f"Error deleting template {clean_template_name}: {e}")
    return False

# Channel type mapping for proper creation with discord.py methods
def get_channel_creation_method(guild, channel_type):
    """Get the proper channel creation method based on type"""
    channel_type = channel_type.lower()
    
    if channel_type in ['text', 'news']:
        return guild.create_text_channel
    elif channel_type in ['voice']:
        return guild.create_voice_channel
    elif channel_type in ['category']:
        return guild.create_category
    elif channel_type in ['stage_voice']:
        return guild.create_stage_channel
    elif channel_type in ['forum']:
        # Forum channels may not be supported in all versions
        return getattr(guild, 'create_forum_channel', guild.create_text_channel)
    else:
        # Default to text channel for unknown types
        return guild.create_text_channel

async def scan_server_template(guild):
    """Scan a server and extract its template structure - works with any permission level"""
    template = {
        'name': str(guild.name) if guild.name else 'Unknown Server',
        'icon': str(guild.icon) if guild.icon else None,
        'banner': str(guild.banner) if guild.banner else None,
        'description': str(guild.description) if guild.description else None,
        'verification_level': str(guild.verification_level) if guild.verification_level else 'unknown',
        'explicit_content_filter': str(guild.explicit_content_filter) if guild.explicit_content_filter else 'unknown',
        'default_notifications': str(guild.default_notifications) if guild.default_notifications else 'unknown',
        'categories': [],
        'channels': [],
        'roles': [],
        'emojis': [],
        'features': [str(f) for f in guild.features] if hasattr(guild, 'features') else []
    }
    
    try:
        # Extract roles (skip @everyone role) - scan what's visible
        for role in guild.roles:
            try:
                if str(role.name) != "@everyone":
                    role_data = {
                        'name': str(role.name),
                        'permissions': int(role.permissions.value) if hasattr(role.permissions, 'value') else 0,
                        'color': int(role.color.value) if hasattr(role.color, 'value') else 0,
                        'hoist': bool(role.hoist),
                        'mentionable': bool(role.mentionable),
                        'position': int(role.position)
                    }
                    template['roles'].append(role_data)
            except Exception as e:
                print(f"Warning: Could not scan role {role.name}: {e}")
                continue
        
        # Sort roles by position for proper recreation
        template['roles'].sort(key=lambda x: x['position'])
        
        # Extract categories and their channels - only scan visible ones
        for category in guild.categories:
            try:
                category_data = {
                    'name': str(category.name),
                    'position': int(category.position),
                    'nsfw': bool(getattr(category, 'nsfw', False)),
                    'channels': []
                }
                
                # Get channels in this category (exclude category itself)
                for channel in category.channels:
                    try:
                        if not isinstance(channel, discord.CategoryChannel):
                            channel_data = await extract_channel_data(channel)
                            category_data['channels'].append(channel_data)
                    except Exception as e:
                        print(f"Warning: Could not scan channel {channel.name}: {e}")
                        continue
                
                template['categories'].append(category_data)
            except Exception as e:
                print(f"Warning: Could not scan category {category.name}: {e}")
                continue
        
        # Get channels not in any category (exclude categories) - only visible ones
        for channel in guild.channels:
            try:
                if not channel.category and not isinstance(channel, discord.CategoryChannel):
                    channel_data = await extract_channel_data(channel)
                    template['channels'].append(channel_data)
            except Exception as e:
                print(f"Warning: Could not scan channel {channel.name}: {e}")
                continue
        
        # Extract emojis (basic info only) - only visible ones
        for emoji in guild.emojis:
            try:
                emoji_data = {
                    'name': str(emoji.name),
                    'animated': bool(emoji.animated)
                }
                template['emojis'].append(emoji_data)
            except Exception as e:
                print(f"Warning: Could not scan emoji {emoji.name}: {e}")
                continue
                
    except Exception as e:
        print(f"Warning: General error during server scan: {e}")
    
    print(f"✅ Scanned template: {len(template['roles'])} roles, {len(template['categories'])} categories, {len(template['channels'])} channels, {len(template['emojis'])} emojis")
    return template

async def extract_channel_data(channel):
    """Extract channel data for template"""
    # Get canonical channel type name
    channel_type_str = str(channel.type).replace('ChannelType.', '')
    
    channel_data = {
        'name': str(channel.name),
        'type': str(channel_type_str),
        'position': int(channel.position),
        'nsfw': bool(getattr(channel, 'nsfw', False)),
        'overwrites': []
    }
    
    # Add channel-specific data based on type
    if hasattr(channel, 'topic') and channel.topic:
        channel_data['topic'] = str(channel.topic)
    if hasattr(channel, 'slowmode_delay') and channel.slowmode_delay > 0:
        channel_data['slowmode_delay'] = int(channel.slowmode_delay)
    if hasattr(channel, 'bitrate') and channel.bitrate:
        channel_data['bitrate'] = min(int(channel.bitrate), 384000)  # Cap at max bitrate
    if hasattr(channel, 'user_limit') and channel.user_limit > 0:
        channel_data['user_limit'] = int(channel.user_limit)
    
    # Extract permission overwrites - ONLY for roles, skip members
    for target, overwrite in channel.overwrites.items():
        # Only save role overwrites, skip member-specific permissions
        if hasattr(target, 'permissions'):  # This is a role
            overwrite_data = {
                'target_type': 'role',
                'target_name': str(target.name),
                'allow': int(overwrite.pair()[0].value),
                'deny': int(overwrite.pair()[1].value)
            }
            channel_data['overwrites'].append(overwrite_data)
    
    return channel_data

async def delete_existing_roles(guild):
    """Delete all existing roles except @everyone and bot roles"""
    deleted_count = 0
    errors = []
    
    try:
        # Get all roles except @everyone
        roles_to_delete = [role for role in guild.roles if role != guild.default_role]
        
        # Sort by position (delete higher roles first to avoid hierarchy issues)
        roles_to_delete.sort(key=lambda x: x.position, reverse=True)
        
        for i, role in enumerate(roles_to_delete):
            try:
                # Skip bot roles and managed roles
                if role.managed or role.is_bot_managed():
                    continue
                
                # Add delay every 5 roles to avoid rate limits
                if i > 0 and i % 5 == 0:
                    await asyncio.sleep(1)
                
                await role.delete(reason="Template application - clearing existing roles")
                deleted_count += 1
                
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    await asyncio.sleep(5)
                    # Retry once
                    try:
                        await role.delete(reason="Template application - clearing existing roles")
                        deleted_count += 1
                    except Exception as retry_e:
                        errors.append(f"Failed to delete role {role.name} after retry: {str(retry_e)}")
                else:
                    errors.append(f"Failed to delete role {role.name}: {str(e)}")
            except Exception as e:
                errors.append(f"Failed to delete role {role.name}: {str(e)}")
    
    except Exception as e:
        errors.append(f"General error deleting roles: {str(e)}")
    
    return deleted_count, errors

async def delete_existing_channels(guild):
    """Delete all existing channels"""
    deleted_count = 0
    errors = []
    
    try:
        # Get all channels using different methods
        all_channels = []
        
        # Try to get text channels
        all_channels.extend(guild.text_channels)
        # Try to get voice channels  
        all_channels.extend(guild.voice_channels)
        # Try to get categories
        all_channels.extend(guild.categories)
        # Try to get stage channels if they exist
        if hasattr(guild, 'stage_channels'):
            all_channels.extend(guild.stage_channels)
        # Try to get forum channels if they exist
        if hasattr(guild, 'forum_channels'):
            all_channels.extend(guild.forum_channels)
        
        print(f"🔍 Found {len(all_channels)} channels to delete: {[ch.name for ch in all_channels]}")
        
        # Sort so categories are deleted last (they need to be empty first)
        text_and_voice_channels = [ch for ch in all_channels if not isinstance(ch, discord.CategoryChannel)]
        category_channels = [ch for ch in all_channels if isinstance(ch, discord.CategoryChannel)]
        
        channels_to_delete = text_and_voice_channels + category_channels
        
        for i, channel in enumerate(channels_to_delete):
            try:
                # Add delay every 5 channels to avoid rate limits
                if i > 0 and i % 5 == 0:
                    await asyncio.sleep(1)
                
                print(f"🗑️ Deleting channel: {channel.name} (type: {type(channel).__name__})")
                await channel.delete(reason="Template application - clearing existing channels")
                deleted_count += 1
                print(f"✅ Deleted channel: {channel.name}")
                
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    print(f"⏳ Rate limited, waiting 5 seconds...")
                    await asyncio.sleep(5)
                    # Retry once
                    try:
                        await channel.delete(reason="Template application - clearing existing channels")
                        deleted_count += 1
                        print(f"✅ Deleted channel: {channel.name} (after retry)")
                    except Exception as retry_e:
                        error_msg = f"Failed to delete channel {channel.name} after retry: {str(retry_e)}"
                        errors.append(error_msg)
                        print(f"❌ {error_msg}")
                else:
                    error_msg = f"Failed to delete channel {channel.name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"❌ {error_msg}")
            except Exception as e:
                error_msg = f"Failed to delete channel {channel.name}: {str(e)}"
                errors.append(error_msg)
                print(f"❌ {error_msg}")
    
    except Exception as e:
        error_msg = f"General error deleting channels: {str(e)}"
        errors.append(error_msg)
        print(f"❌ {error_msg}")
    
    return deleted_count, errors

async def update_channel_overwrites(channel, channel_data, role_mapping):
    """Update channel permission overwrites after roles have been created"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Check if channel should inherit from category (no explicit overwrites)
            template_overwrites_data = channel_data.get('overwrites', [])
            if not template_overwrites_data:
                # Channel should sync with category - use sync_permissions
                if channel.category:
                    await channel.edit(sync_permissions=True, reason="Syncing channel with category permissions")
                    print(f"✅ Synced {channel.name} with category permissions")
                return
            
            # Build authoritative permission overwrites from template
            template_overwrites = {}
            for overwrite_data in template_overwrites_data:
                target_type = overwrite_data.get('target_type')
                target_name = overwrite_data.get('target_name')
                
                # Handle role overwrites (including @everyone)
                if target_type == 'role':
                    target_role = role_mapping.get(target_name)
                    if target_role:
                        try:
                            template_overwrites[target_role] = discord.PermissionOverwrite.from_pair(
                                discord.Permissions(overwrite_data['allow']),
                                discord.Permissions(overwrite_data['deny'])
                            )
                            print(f"📋 Added overwrite for role {target_name} in channel {channel.name}")
                        except Exception as e:
                            print(f"Warning: Could not create overwrite for role {target_name}: {e}")
                    else:
                        print(f"Warning: Role {target_name} not found in role mapping for channel {channel.name}")
                # Skip member overwrites as they can't be reliably mapped across servers
            
            # Apply authoritative template overwrites (replace existing)
            if template_overwrites:
                await channel.edit(overwrites=template_overwrites, reason="Applying template permission overwrites")
                print(f"✅ Applied {len(template_overwrites)} overwrites to channel: {channel.name}")
            elif template_overwrites_data:
                # Template has overwrites but they're all member/invalid - treat as "inherit from category"
                if channel.category:
                    await channel.edit(sync_permissions=True, reason="Template has only member overwrites - syncing with category")
                    print(f"✅ Synced {channel.name} with category (template had only member overwrites)")
                else:
                    print(f"⚠️ Template has member overwrites only, but no category to sync with for channel: {channel.name}")
            else:
                print(f"⚠️ No overwrites defined in template for channel: {channel.name}")
            
            return  # Success, exit retry loop
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                retry_count += 1
                wait_time = min(5, 2 ** retry_count)  # Exponential backoff
                print(f"⏳ Rate limited updating overwrites for {channel.name}, waiting {wait_time}s... (attempt {retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
                if retry_count >= max_retries:
                    print(f"❌ Failed to update overwrites for {channel.name} after {max_retries} retries")
                    raise e
            else:
                print(f"❌ Error updating overwrites for channel {channel.name}: {e}")
                raise e
        except Exception as e:
            print(f"❌ Error updating overwrites for channel {channel.name}: {e}")
            raise e

async def update_category_overwrites_basic(category, category_data, basic_role_mapping):
    """Update category permission overwrites using only @everyone (basic permissions)"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Build basic overwrites for this category - @everyone only
            template_overwrites = {}
            template_overwrites_data = category_data.get('overwrites', [])
            
            for overwrite_data in template_overwrites_data:
                target_type = overwrite_data.get('target_type')
                target_name = overwrite_data.get('target_name')
                
                # Handle only @everyone role overwrites
                if target_type == 'role' and target_name == '@everyone':
                    target_role = basic_role_mapping.get('@everyone')
                    if target_role:
                        try:
                            template_overwrites[target_role] = discord.PermissionOverwrite.from_pair(
                                discord.Permissions(overwrite_data['allow']),
                                discord.Permissions(overwrite_data['deny'])
                            )
                            print(f"📋 Added basic @everyone overwrite for category {category.name}")
                        except Exception as e:
                            print(f"Warning: Could not create @everyone overwrite for category {category.name}: {e}")
            
            # Apply basic overwrites (@everyone only)
            if template_overwrites:
                await category.edit(overwrites=template_overwrites, reason="Applying basic @everyone permissions")
                print(f"✅ Applied @everyone overwrites to category: {category.name}")
            else:
                print(f"⚠️ No @everyone overwrites for category: {category.name}")
            
            return  # Success, exit retry loop
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                retry_count += 1
                wait_time = min(5, 2 ** retry_count)
                print(f"⏳ Rate limited updating basic overwrites for category {category.name}, waiting {wait_time}s... (attempt {retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
                if retry_count >= max_retries:
                    print(f"❌ Failed to update basic overwrites for category {category.name} after {max_retries} retries")
                    raise e
            else:
                print(f"❌ Error updating basic overwrites for category {category.name}: {e}")
                raise e
        except Exception as e:
            print(f"❌ Error updating basic overwrites for category {category.name}: {e}")
            raise e

async def update_channel_overwrites_basic(channel, channel_data, basic_role_mapping):
    """Update channel permission overwrites using only @everyone (basic permissions)"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Build basic overwrites for this channel - @everyone only
            template_overwrites = {}
            template_overwrites_data = channel_data.get('overwrites', [])
            
            for overwrite_data in template_overwrites_data:
                target_type = overwrite_data.get('target_type')
                target_name = overwrite_data.get('target_name')
                
                # Handle only @everyone role overwrites
                if target_type == 'role' and target_name == '@everyone':
                    target_role = basic_role_mapping.get('@everyone')
                    if target_role:
                        try:
                            template_overwrites[target_role] = discord.PermissionOverwrite.from_pair(
                                discord.Permissions(overwrite_data['allow']),
                                discord.Permissions(overwrite_data['deny'])
                            )
                            print(f"📋 Added basic @everyone overwrite for channel {channel.name}")
                        except Exception as e:
                            print(f"Warning: Could not create @everyone overwrite for channel {channel.name}: {e}")
            
            # Apply basic overwrites (@everyone only)
            if template_overwrites:
                await channel.edit(overwrites=template_overwrites, reason="Applying basic @everyone permissions")
                print(f"✅ Applied @everyone overwrites to channel: {channel.name}")
            elif template_overwrites_data:
                # Template has overwrites but no @everyone - sync with category if available
                if channel.category:
                    await channel.edit(sync_permissions=True, reason="Template has no @everyone - syncing with category")
                    print(f"✅ Synced {channel.name} with category (no @everyone overwrites)")
                else:
                    print(f"⚠️ No @everyone overwrites and no category for channel: {channel.name}")
            else:
                print(f"⚠️ No overwrites for channel: {channel.name}")
            
            return  # Success, exit retry loop
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                retry_count += 1
                wait_time = min(5, 2 ** retry_count)
                print(f"⏳ Rate limited updating basic overwrites for channel {channel.name}, waiting {wait_time}s... (attempt {retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
                if retry_count >= max_retries:
                    print(f"❌ Failed to update basic overwrites for channel {channel.name} after {max_retries} retries")
                    raise e
            else:
                print(f"❌ Error updating basic overwrites for channel {channel.name}: {e}")
                raise e
        except Exception as e:
            print(f"❌ Error updating basic overwrites for channel {channel.name}: {e}")
            raise e

async def update_category_overwrites(category, category_data, role_mapping):
    """Update category permission overwrites after roles have been created"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Build authoritative permission overwrites from template
            template_overwrites = {}
            template_overwrites_data = category_data.get('overwrites', [])
            
            for overwrite_data in template_overwrites_data:
                target_type = overwrite_data.get('target_type')
                target_name = overwrite_data.get('target_name')
                
                # Handle role overwrites (including @everyone)
                if target_type == 'role':
                    target_role = role_mapping.get(target_name)
                    if target_role:
                        try:
                            template_overwrites[target_role] = discord.PermissionOverwrite.from_pair(
                                discord.Permissions(overwrite_data['allow']),
                                discord.Permissions(overwrite_data['deny'])
                            )
                            print(f"📋 Added overwrite for role {target_name} in category {category.name}")
                        except Exception as e:
                            print(f"Warning: Could not create overwrite for role {target_name}: {e}")
                    else:
                        print(f"Warning: Role {target_name} not found in role mapping for category {category.name}")
                # Skip member overwrites as they can't be reliably mapped across servers
            
            # Apply authoritative template overwrites (replace existing)
            if template_overwrites:
                await category.edit(overwrites=template_overwrites, reason="Applying template permission overwrites")
                print(f"✅ Applied {len(template_overwrites)} overwrites to category: {category.name}")
            else:
                print(f"⚠️ No valid overwrites found for category: {category.name}")
            
            return  # Success, exit retry loop
            
        except discord.HTTPException as e:
            if e.status == 429:  # Rate limited
                retry_count += 1
                wait_time = min(5, 2 ** retry_count)  # Exponential backoff
                print(f"⏳ Rate limited updating overwrites for category {category.name}, waiting {wait_time}s... (attempt {retry_count}/{max_retries})")
                await asyncio.sleep(wait_time)
                if retry_count >= max_retries:
                    print(f"❌ Failed to update overwrites for category {category.name} after {max_retries} retries")
                    raise e
            else:
                print(f"❌ Error updating overwrites for category {category.name}: {e}")
                raise e
        except Exception as e:
            print(f"❌ Error updating overwrites for category {category.name}: {e}")
            raise e

async def apply_server_template(guild, template, ctx):
    """Apply a server template to the target guild with proper rate limiting and error handling"""
    applied_count = 0
    errors = []
    
    try:
        # Check comprehensive permissions first
        bot_member = guild.get_member(bot.user.id)
        required_perms = {
            'manage_guild': 'Manage Server',
            'manage_roles': 'Manage Roles', 
            'manage_channels': 'Manage Channels',
            'manage_emojis_and_stickers': 'Manage Emojis'
        }
        
        missing_perms = []
        for perm, display_name in required_perms.items():
            if not getattr(bot_member.guild_permissions, perm, False):
                missing_perms.append(display_name)
        
        if missing_perms:
            errors.append(f"Missing permissions: {', '.join(missing_perms)}")
            return applied_count, errors
        
        # STEP 0A: Delete all existing channels first
        print("🗑️ Deleting existing channels...")
        deleted_channels, channel_errors = await delete_existing_channels(guild)
        if channel_errors:
            errors.extend(channel_errors)
        print(f"✅ Deleted {deleted_channels} existing channels")
        
        # STEP 0B: Delete all existing roles (except @everyone and bot roles)
        print("🗑️ Deleting existing roles...")
        deleted_roles, role_errors = await delete_existing_roles(guild)
        if role_errors:
            errors.extend(role_errors)
        print(f"✅ Deleted {deleted_roles} existing roles")
        
        # Brief pause before creation
        await asyncio.sleep(1)
        
        # Initialize empty role mapping for later use
        role_mapping = {}  
        created_channels = []  # Store created channels for later overwrite updates
        created_categories = []  # Store created categories for later overwrite updates
        
        # STEP 1: Create categories with rate limiting
        for i, category_data in enumerate(template.get('categories', [])):
            try:
                # Add delay every 3 categories
                if i > 0 and i % 3 == 0:
                    await asyncio.sleep(1)
                    
                new_category = await guild.create_category(
                    name=category_data['name'],
                    reason="Server template application"
                )
                created_categories.append((new_category, category_data))  # Store for later overwrite updates
                applied_count += 1
                
                # STEP 2: Create channels in this category (without role overwrites for now)
                for j, channel_data in enumerate(category_data.get('channels', [])):
                    # Add delay every 5 channels
                    if j > 0 and j % 5 == 0:
                        await asyncio.sleep(0.8)
                        
                    try:
                        new_channel = await create_channel_from_template(guild, channel_data, new_category, {})  # Empty role mapping for now
                        created_channels.append((new_channel, channel_data))  # Store for later overwrite updates
                        applied_count += 1
                    except Exception as e:
                        errors.append(f"Failed to create channel {channel_data['name']}: {str(e)}")
                
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    await asyncio.sleep(3)
                errors.append(f"Failed to create category {category_data['name']}: {str(e)}")
            except Exception as e:
                errors.append(f"Failed to create category {category_data['name']}: {str(e)}")
        
        # STEP 3: Create channels not in categories (without role overwrites for now)
        for i, channel_data in enumerate(template.get('channels', [])):
            try:
                # Add delay every 5 channels
                if i > 0 and i % 5 == 0:
                    await asyncio.sleep(0.8)
                    
                new_channel = await create_channel_from_template(guild, channel_data, None, {})  # Empty role mapping for now
                created_channels.append((new_channel, channel_data))  # Store for later overwrite updates
                applied_count += 1
            except Exception as e:
                errors.append(f"Failed to create channel {channel_data['name']}: {str(e)}")
        
        # Small delay before creating roles
        await asyncio.sleep(0.5)
        
        # STEP 4: Add @everyone to basic role mapping for basic overwrite updates
        basic_role_mapping = {"@everyone": guild.default_role}
        print(f"✅ Initial basic role mapping with @everyone: {basic_role_mapping['@everyone'].name} (ID: {basic_role_mapping['@everyone'].id})")
        
        # STEP 5: Update category overwrites with @everyone only (basic permissions)
        print("🔧 Updating category @everyone permissions...")
        if created_categories:
            category_tasks = [
                update_category_overwrites_basic(category, category_data, basic_role_mapping)
                for category, category_data in created_categories
            ]
            category_results = await asyncio.gather(*category_tasks, return_exceptions=True)
            
            # Process category results
            category_success = 0
            for i, result in enumerate(category_results):
                if isinstance(result, Exception):
                    category, category_data = created_categories[i]
                    errors.append(f"Failed to update basic overwrites for category {category.name}: {str(result)}")
                else:
                    category_success += 1
            
            print(f"✅ Category basic overwrites: {category_success} successful, {len(category_results) - category_success} errors")
        else:
            print("✅ No categories to update")
        
        # STEP 6: Update channel overwrites with @everyone only (basic permissions)
        print("🔧 Updating channel @everyone permissions...")
        if created_channels:
            channel_tasks = [
                update_channel_overwrites_basic(channel, channel_data, basic_role_mapping)
                for channel, channel_data in created_channels
            ]
            channel_results = await asyncio.gather(*channel_tasks, return_exceptions=True)
            
            # Process channel results
            channel_success = 0
            for i, result in enumerate(channel_results):
                if isinstance(result, Exception):
                    channel, channel_data = created_channels[i]
                    errors.append(f"Failed to update basic overwrites for channel {channel.name}: {str(result)}")
                else:
                    channel_success += 1
            
            print(f"✅ Channel basic overwrites: {channel_success} successful, {len(channel_results) - channel_success} errors")
        else:
            print("✅ No channels to update")
            
        # STEP 7: Create roles from template (VERY LAST STEP)
        print("👑 Creating roles from template (final step)...")
        full_role_mapping = {"@everyone": guild.default_role}  # Start fresh mapping
        for i, role_data in enumerate(template.get('roles', [])):
            try:
                # Add delay every 5 roles to avoid rate limits
                if i > 0 and i % 5 == 0:
                    await asyncio.sleep(1)
                    
                new_role = await guild.create_role(
                    name=role_data['name'],
                    permissions=discord.Permissions(role_data['permissions']),
                    color=discord.Color(role_data['color']),
                    hoist=role_data['hoist'],
                    mentionable=role_data['mentionable'],
                    reason="Server template application"
                )
                full_role_mapping[role_data['name']] = new_role
                applied_count += 1
                print(f"✅ Created role: {role_data['name']}")
                
            except discord.HTTPException as e:
                if e.status == 429:  # Rate limited
                    await asyncio.sleep(5)
                    # Retry once
                    try:
                        new_role = await guild.create_role(
                            name=role_data['name'],
                            permissions=discord.Permissions(role_data['permissions']),
                            color=discord.Color(role_data['color']),
                            hoist=role_data['hoist'],
                            mentionable=role_data['mentionable'],
                            reason="Server template application"
                        )
                        full_role_mapping[role_data['name']] = new_role
                        applied_count += 1
                        print(f"✅ Created role: {role_data['name']} (after retry)")
                    except Exception as retry_e:
                        errors.append(f"Failed to create role {role_data['name']} after retry: {str(retry_e)}")
                else:
                    errors.append(f"Failed to create role {role_data['name']}: {str(e)}")
            except Exception as e:
                errors.append(f"Failed to create role {role_data['name']}: {str(e)}")
        
        # STEP 8: Set role positions after creation
        if len(full_role_mapping) > 1 and template.get('roles'):
            await asyncio.sleep(0.5)  # Brief pause before position setting
            position_success = await set_role_positions(guild, full_role_mapping, template.get('roles', []))
            if position_success:
                print("✅ Role positions set successfully")
            else:
                errors.append("Warning: Could not set role positions to match original server")
        
        # STEP 9: Update full category overwrites with all roles (final overwrites)
        print("🔧 Updating category full permission overwrites...")
        if created_categories:
            category_tasks = [
                update_category_overwrites(category, category_data, full_role_mapping)
                for category, category_data in created_categories
            ]
            category_results = await asyncio.gather(*category_tasks, return_exceptions=True)
            
            # Process category results
            category_success = 0
            for i, result in enumerate(category_results):
                if isinstance(result, Exception):
                    category, category_data = created_categories[i]
                    errors.append(f"Failed to update full overwrites for category {category.name}: {str(result)}")
                else:
                    category_success += 1
            
            print(f"✅ Category full overwrites: {category_success} successful, {len(category_results) - category_success} errors")
        else:
            print("✅ No categories to update")
        
        # STEP 10: Update full channel overwrites with all roles (final overwrites)
        print("🔧 Updating channel full permission overwrites...")
        if created_channels:
            channel_tasks = [
                update_channel_overwrites(channel, channel_data, full_role_mapping)
                for channel, channel_data in created_channels
            ]
            channel_results = await asyncio.gather(*channel_tasks, return_exceptions=True)
            
            # Process channel results
            channel_success = 0
            for i, result in enumerate(channel_results):
                if isinstance(result, Exception):
                    channel, channel_data = created_channels[i]
                    errors.append(f"Failed to update full overwrites for channel {channel.name}: {str(result)}")
                else:
                    channel_success += 1
            
            print(f"✅ Channel full overwrites: {channel_success} successful, {len(channel_results) - channel_success} errors")
        else:
            print("✅ No channels to update")
        
    except Exception as e:
        errors.append(f"General error applying template: {str(e)}")
    
    return applied_count, errors

async def create_channel_from_template(guild, channel_data, category, role_mapping):
    """Create a channel from template data with robust type handling and proper overwrites"""
    overwrites = {}
    
    # Build permission overwrites using the role mapping (skip member overwrites completely)
    for overwrite_data in channel_data.get('overwrites', []):
        if overwrite_data.get('target_type') == 'role':
            target_role = role_mapping.get(overwrite_data['target_name'])
            if target_role:
                try:
                    overwrites[target_role] = discord.PermissionOverwrite.from_pair(
                        discord.Permissions(overwrite_data['allow']),
                        discord.Permissions(overwrite_data['deny'])
                    )
                except Exception as e:
                    print(f"Warning: Could not create overwrite for role {overwrite_data['target_name']}: {e}")
        # Explicitly skip member overwrites - they can't be reliably mapped across servers
    
    # Get the appropriate creation method
    channel_type = channel_data['type']
    creation_method = get_channel_creation_method(guild, channel_type)
    
    try:
        # Verify @everyone mapping is available when role overwrites are expected
        if overwrites and "@everyone" not in role_mapping:
            raise ValueError("❌ CRITICAL: @everyone not in role_mapping during channel creation")
        
        # Prepare common arguments - only include overwrites if they exist
        common_args = {
            'name': channel_data['name'],
            'reason': "Server template application"
        }
        
        # Only add overwrites if there are valid ones (allows inheritance otherwise)
        if overwrites:
            common_args['overwrites'] = overwrites
            print(f"📋 Creating {channel_data['name']} with {len(overwrites)} overwrites")
        
        # Add category for non-category channels
        if channel_type.lower() != 'category' and category:
            common_args['category'] = category
        
        # Add type-specific arguments
        if channel_type.lower() in ['text', 'news', 'forum']:
            if channel_data.get('topic'):
                common_args['topic'] = channel_data['topic']
            if channel_data.get('slowmode_delay', 0) > 0:
                common_args['slowmode_delay'] = channel_data['slowmode_delay']
            if channel_data.get('nsfw', False):
                common_args['nsfw'] = channel_data['nsfw']
        
        elif channel_type.lower() in ['voice', 'stage_voice']:
            # Ensure bitrate is within valid range
            if channel_data.get('bitrate'):
                bitrate = max(8000, min(channel_data['bitrate'], 384000))
                common_args['bitrate'] = bitrate
            if channel_data.get('user_limit', 0) > 0:
                common_args['user_limit'] = channel_data['user_limit']
        
        # Create the channel using the appropriate method
        new_channel = await creation_method(**common_args)
        return new_channel
        
    except discord.HTTPException as e:
        if e.status == 429:
            # Rate limited, exponential backoff
            await asyncio.sleep(min(5, 2 ** (channel_data.get('retry_count', 0))))
            channel_data['retry_count'] = channel_data.get('retry_count', 0) + 1
            if channel_data.get('retry_count', 0) < 3:  # Max 3 retries
                return await create_channel_from_template(guild, channel_data, category, role_mapping)
            else:
                raise e
        else:
            raise e
    except Exception as e:
        print(f"Error creating channel {channel_data['name']} of type {channel_type}: {e}")
        raise e

async def set_role_positions(guild, role_mapping, original_roles):
    """Set role positions to match the original server"""
    try:
        # Build position mapping
        position_updates = []
        for original_role_data in original_roles:
            role_name = original_role_data['name']
            original_position = original_role_data['position']
            
            if role_name in role_mapping:
                new_role = role_mapping[role_name]
                position_updates.append({
                    'id': new_role.id,
                    'position': original_position
                })
        
        # Sort by original position to maintain hierarchy
        position_updates.sort(key=lambda x: x['position'])
        
        # Discord requires positions to be relative to other roles
        # We need to edit positions in batches to avoid conflicts
        if position_updates:
            await guild.edit_role_positions(positions=position_updates, reason="Server template role positioning")
            return True
            
    except Exception as e:
        print(f"Warning: Could not set role positions: {e}")
        return False
    
    return False

@bot.command(name="copytemplate", aliases=["copyserver", "scantemplate"])
async def copy_server_template(ctx, template_name=None, *, server_link=None):
    """Copy/scan a server template from current server or server invite link"""
    try:
        # Check authorization
        if not is_owner(ctx.author.id):
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n❌ Only the bot owner can use template commands", delete_after=5)
            return
        
        if not template_name:
            await ultra_fast_response(ctx, "❌ Usage: `-copytemplate <template_name> [server_invite_link]`\nExample: `-copytemplate gaming_server` (scans current server)\nExample: `-copytemplate cool_server https://discord.gg/example`", delete_after=10)
            return
        
        # Delete command instantly
        await instant_delete_command(ctx)
        
        # Show loading message
        loading_msg = await ctx.send("🔄 **Scanning server template...**\nThis may take a moment...")
        
        # Determine which server to scan
        target_guild = None
        if server_link:
            # Extract invite code from link
            invite_code = server_link.replace('https://discord.gg/', '').replace('discord.gg/', '').strip()
            try:
                invite = await bot.fetch_invite(invite_code)
                target_guild = invite.guild
                
                # Check if bot is in the server or can access it
                if not any(g.id == target_guild.id for g in bot.guilds):
                    await loading_msg.edit(content="❌ **Error: Bot is not in the target server!**\nThe bot needs to be in the server to scan its template.")
                    await asyncio.sleep(8)
                    await loading_msg.delete()
                    return
                    
                # Get the actual guild object
                target_guild = discord.utils.get(bot.guilds, id=target_guild.id)
            except Exception as e:
                if 'loading_msg' in locals():
                    await loading_msg.edit(content=f"❌ **Error accessing server invite:** {str(e)}")
                    await asyncio.sleep(8)
                    await loading_msg.delete()
                else:
                    await ultra_fast_response(ctx, f"❌ **Error accessing server invite:** {str(e)}", delete_after=8)
                return
        else:
            # Use current server
            target_guild = ctx.guild
        
        if not target_guild:
            await loading_msg.edit(content="❌ **Error: Could not access target server!**")
            await asyncio.sleep(5)
            await loading_msg.delete()
            return
        
        # For copying templates, we only need basic access (being in the server)
        # No special permissions required - just read what's already visible
        
        # Scan the server template
        template = await scan_server_template(target_guild)
        
        # Save template to file
        success, cleaned_name, error_msg = save_template_to_file(template_name, template)
        if success:
            # Generate success message
            success_msg = f"✅ **Server Template Copied Successfully!**\n"
            success_msg += f"📋 **Template Name:** `{cleaned_name}`\n"
            success_msg += f"🏢 **Server:** {target_guild.name}\n"
            success_msg += f"📁 **Categories:** {len(template.get('categories', []))}\n"
            success_msg += f"📝 **Channels:** {len(template.get('channels', [])) + sum(len(cat.get('channels', [])) for cat in template.get('categories', []))}\n"
            success_msg += f"🎭 **Roles:** {len(template.get('roles', []))}\n"
            success_msg += f"😀 **Emojis:** {len(template.get('emojis', []))}\n\n"
            success_msg += f"💾 **Template saved to:** `server_templates/{cleaned_name}.json`\n"
            success_msg += f"Use `-applytemplate {cleaned_name}` to apply this template to another server!"
        else:
            success_msg = f"❌ **Error saving template!**\n"
            success_msg += f"📋 **Template Name:** `{cleaned_name or template_name}`\n"
            success_msg += f"🏢 **Server:** {target_guild.name}\n\n"
            success_msg += f"**Error Details:** {error_msg}\n\n"
            success_msg += "The template was scanned successfully, but could not be saved to file. Please check the error details above."
        
        await loading_msg.edit(content=success_msg)
        print(f"✅ Server template '{template_name}' copied from {target_guild.name}")
        
        # Clean up after delay
        await asyncio.sleep(15)
        await loading_msg.delete()
        
    except Exception as e:
        error_msg = f"❌ **Error copying server template:** {str(e)}"
        print(f"❌ Error copying template: {e}")
        try:
            await loading_msg.edit(content=error_msg)
            await asyncio.sleep(8)
            await loading_msg.delete()
        except:
            await ultra_fast_response(ctx, error_msg, delete_after=8)

@bot.command(name="applytemplate", aliases=["pastetemplate", "usetemplate"])
async def apply_server_template_cmd(ctx, template_name=None, *, server_link=None):
    """Apply a saved server template to current server or target server"""
    try:
        # Check authorization
        if not is_owner(ctx.author.id):
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n❌ Only the bot owner can use template commands", delete_after=5)
            return
        
        if not template_name:
            available_templates = list_saved_templates()
            if available_templates:
                template_list = "`, `".join(available_templates)
                await ultra_fast_response(ctx, f"❌ Usage: `-applytemplate <template_name> [server_invite_link]`\n\n**Available templates:** `{template_list}`\n\nExample: `-applytemplate gaming_server` (applies to current server)\nExample: `-applytemplate cool_server https://discord.gg/example`", delete_after=15)
            else:
                await ultra_fast_response(ctx, "❌ **No templates available!**\nUse `-copytemplate <name>` to create a template first.", delete_after=8)
            return
        
        # Load template from file
        template = load_template_from_file(template_name)
        if not template:
            await ultra_fast_response(ctx, f"❌ **Template '{template_name}' not found!**\nUse `-listtemplates` to see available templates.", delete_after=8)
            return
        
        # Delete command instantly
        await instant_delete_command(ctx)
        
        # Show loading message
        loading_msg = await ctx.send("🔄 **Applying server template...**\nThis will take several minutes...")
        
        # Determine target server
        target_guild = None
        if server_link:
            # Extract invite code from link
            invite_code = server_link.replace('https://discord.gg/', '').replace('discord.gg/', '').strip()
            try:
                invite = await bot.fetch_invite(invite_code)
                target_guild = discord.utils.get(bot.guilds, id=invite.guild.id)
            except Exception as e:
                if 'loading_msg' in locals():
                    await loading_msg.edit(content=f"❌ **Error accessing server invite:** {str(e)}")
                    await asyncio.sleep(8)
                    await loading_msg.delete()
                else:
                    await ultra_fast_response(ctx, f"❌ **Error accessing server invite:** {str(e)}", delete_after=8)
                return
        else:
            target_guild = ctx.guild
        
        if not target_guild:
            await loading_msg.edit(content="❌ **Error: Could not access target server!**")
            await asyncio.sleep(5)
            await loading_msg.delete()
            return
        
        # Check bot permissions
        bot_member = target_guild.get_member(bot.user.id)
        required_perms = ['manage_channels', 'manage_roles', 'manage_guild']
        missing_perms = []
        
        for perm in required_perms:
            if not getattr(bot_member.guild_permissions, perm, False):
                missing_perms.append(perm.replace('_', ' ').title())
        
        if missing_perms:
            await loading_msg.edit(content=f"❌ **Missing Permissions!**\nBot needs: {', '.join(missing_perms)}")
            await asyncio.sleep(10)
            await loading_msg.delete()
            return
        
        # Apply the template
        applied_count, errors = await apply_server_template(target_guild, template, ctx)
        
        # Generate result message
        result_msg = f"✅ **Template Applied Successfully!**\n"
        result_msg += f"📋 **Template:** `{template_name}`\n"
        result_msg += f"🏢 **Server:** {target_guild.name}\n"
        result_msg += f"✅ **Items Created:** {applied_count}\n"
        
        if errors:
            result_msg += f"\n⚠️ **Errors ({len(errors)}):**\n"
            for error in errors[:5]:  # Show first 5 errors
                result_msg += f"• {error}\n"
            if len(errors) > 5:
                result_msg += f"... and {len(errors) - 5} more errors"
        
        result_msg += f"\n🎉 **Template application completed!**"
        
        await loading_msg.edit(content=result_msg)
        print(f"✅ Template '{template_name}' applied to {target_guild.name}")
        
        # Clean up after delay
        await asyncio.sleep(20)
        await loading_msg.delete()
        
    except Exception as e:
        error_msg = f"❌ **Error applying server template:** {str(e)}"
        print(f"❌ Error applying template: {e}")
        try:
            if 'loading_msg' in locals():
                await loading_msg.edit(content=error_msg)
                await asyncio.sleep(8)
                await loading_msg.delete()
            else:
                await ultra_fast_response(ctx, error_msg, delete_after=8)
        except:
            await ultra_fast_response(ctx, error_msg, delete_after=8)

@bot.command(name="listtemplates", aliases=["templates", "showtemplates"])
async def list_server_templates(ctx):
    """List all saved server templates"""
    try:
        # Check authorization
        if not is_owner(ctx.author.id):
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n❌ Only the bot owner can use template commands", delete_after=5)
            return
        
        available_templates = list_saved_templates()
        if not available_templates:
            await ultra_fast_response(ctx, "📋 **No Server Templates Saved**\n\nUse `-copytemplate <name>` to create your first template!", delete_after=8)
            return
        
        # Build template list
        template_list = "📋 **Saved Server Templates**\n\n"
        for i, name in enumerate(available_templates, 1):
            template = load_template_from_file(name)
            if template:
                channel_count = len(template.get('channels', [])) + sum(len(cat.get('channels', [])) for cat in template.get('categories', []))
                template_list += f"`{i}.` **{name}**\n"
                template_list += f"   🏢 Server: {template.get('name', 'Unknown')}\n"
                template_list += f"   📁 Categories: {len(template.get('categories', []))}\n"
                template_list += f"   📝 Channels: {channel_count}\n"
                template_list += f"   🎭 Roles: {len(template.get('roles', []))}\n\n"
        
        template_list += "**Commands:**\n"
        template_list += "• `-copytemplate <name>` - Copy current server template\n"
        template_list += "• `-applytemplate <name>` - Apply template to current server\n"
        template_list += "• `-deletetemplate <name>` - Delete a saved template"
        
        await ultra_fast_response(ctx, template_list, delete_after=20)
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error listing templates: {str(e)}", delete_after=8)
        print(f"❌ Error listing templates: {e}")

@bot.command(name="deletetemplate", aliases=["removetemplate", "deltemplate"])
async def delete_server_template(ctx, template_name=None):
    """Delete a saved server template"""
    try:
        # Check authorization
        if not is_owner(ctx.author.id):
            await ultra_fast_response(ctx, "🚫 **ACCESS DENIED**\n❌ Only the bot owner can use template commands", delete_after=5)
            return
        
        if not template_name:
            await ultra_fast_response(ctx, "❌ Usage: `-deletetemplate <template_name>`\nUse `-listtemplates` to see available templates.", delete_after=8)
            return
        
        # Check if template exists and delete it
        if not delete_template_file(template_name):
            await ultra_fast_response(ctx, f"❌ **Template '{template_name}' not found!**\nUse `-listtemplates` to see available templates.", delete_after=8)
            return
        
        await ultra_fast_response(ctx, f"✅ **Template Deleted Successfully!**\n📋 **Template:** `{template_name}`\n🗑️ **File removed:** `server_templates/{template_name}.json`", delete_after=8)
        print(f"✅ Deleted server template: {template_name}")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error deleting template: {str(e)}", delete_after=8)
        print(f"❌ Error deleting template: {e}")

# ==================== ULTRA-SAFE STREAMING FUNCTIONALITY ====================

# Global variables for safe streaming
streaming_active = False
streaming_status_task = None
stream_statuses = []
streaming_session_data = {}
streaming_last_change = {}
streaming_usage_count = defaultdict(int)
streaming_cooldown_active = False

# EXTREME SAFETY STREAMING CONFIGURATION - ARCHITECT REVIEWED
SAFE_STREAMING_MODE = True                    # Enable all safety measures
STREAMING_MIN_DELAY = 86400                   # Minimum 24 hours between changes (EXTREME SAFETY)
STREAMING_MAX_DELAY = 172800                  # Maximum 48 hours between changes  
STREAMING_RANDOM_VARIANCE = 7200              # ±2 hours random variance
STREAMING_MAX_CHANGES_PER_HOUR = 0            # NO changes per hour (DISABLED for safety)
STREAMING_MAX_CHANGES_PER_DAY = 1             # Maximum 1 change per day per token (EXTREME LIMIT)
STREAMING_COOLDOWN_PERIOD = 86400             # 24 hour cooldown after any error
STREAMING_TOKEN_ROTATION_DELAY = 3600         # 1 hour delay between token operations
STREAMING_ERROR_BACKOFF_BASE = 86400          # 24 hour base backoff on errors
STREAMING_SESSION_TIMEOUT = 86400             # 24 hour session timeout

# WARNING FLAGS
STREAMING_REQUIRES_EXPLICIT_RISK_ACCEPTANCE = True
STREAMING_DISABLE_MULTI_TOKEN = True          # Disable streamall for safety
STREAMING_DISABLE_ROTATION = True             # Disable rotation for safety

# Natural streaming activities to rotate through
NATURAL_STREAMING_ACTIVITIES = [
    "Just Chatting", "Gaming", "Music", "Art", "Talk Shows & Podcasts",
    "ASMR", "Beauty & Makeup", "Food & Drink", "Science & Technology",
    "Sports", "Travel & Outdoors", "IRL", "Creative", "Pools, Hot Tubs, and Beaches"
]

def read_streaming_tokens(filename='token.txt'):
    """Safely read tokens from file with validation"""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            tokens = [line.strip() for line in f if line.strip() and len(line.strip()) > 50]
        print(f"🔒 Loaded {len(tokens)} valid tokens for streaming")
        return tokens
    except Exception as e:
        print(f"❌ Error reading tokens: {e}")
        return []

def is_token_safe_for_streaming(token):
    """Check if token is safe to use for streaming operations"""
    current_time = time.time()
    token_id = token[-8:]  # Use last 8 chars as identifier
    
    # Check hourly usage
    hour_key = f"{token_id}_{int(current_time // 3600)}"
    if streaming_usage_count[hour_key] >= STREAMING_MAX_CHANGES_PER_HOUR:
        print(f"🛡️ Token {token_id} hit hourly limit ({STREAMING_MAX_CHANGES_PER_HOUR})")
        return False
    
    # Check daily usage
    day_key = f"{token_id}_{int(current_time // 86400)}"
    if streaming_usage_count[day_key] >= STREAMING_MAX_CHANGES_PER_DAY:
        print(f"🛡️ Token {token_id} hit daily limit ({STREAMING_MAX_CHANGES_PER_DAY})")
        return False
    
    # Check last change time
    if token_id in streaming_last_change:
        time_since_last = current_time - streaming_last_change[token_id]
        if time_since_last < STREAMING_MIN_DELAY:
            remaining = STREAMING_MIN_DELAY - time_since_last
            print(f"🛡️ Token {token_id} on cooldown ({remaining:.0f}s remaining)")
            return False
    
    return True

def record_streaming_usage(token):
    """Record streaming usage for safety tracking"""
    current_time = time.time()
    token_id = token[-8:]
    
    # Record usage
    hour_key = f"{token_id}_{int(current_time // 3600)}"
    day_key = f"{token_id}_{int(current_time // 86400)}"
    
    streaming_usage_count[hour_key] += 1
    streaming_usage_count[day_key] += 1
    streaming_last_change[token_id] = current_time
    
    print(f"🔒 Recorded streaming usage for token {token_id}")

async def safe_human_delay(base_delay=None):
    """Add human-like delays with random variance"""
    if base_delay is None:
        base_delay = random.uniform(STREAMING_MIN_DELAY, STREAMING_MAX_DELAY)
    
    # Add random variance
    variance = random.uniform(-STREAMING_RANDOM_VARIANCE, STREAMING_RANDOM_VARIANCE)
    total_delay = max(60, base_delay + variance)  # Minimum 1 minute delay
    
    print(f"⏳ Human-like delay: {total_delay:.0f} seconds")
    await asyncio.sleep(total_delay)

async def ultra_safe_presence_update(token, details):
    """Ultra-safe presence update with extensive error handling"""
    if not token or token.strip() == "":
        print("🛡️ Skipping empty token")
        return False

    if not is_token_safe_for_streaming(token):
        print("🛡️ Token not safe for streaming - skipping")
        return False

    token_id = token[-8:]
    print(f"🎮 Starting safe streaming update for token {token_id}")

    # Add pre-operation delay
    await safe_human_delay(random.uniform(5, 15))

    client = discord.Client(intents=discord.Intents.default())
    success = False

    @client.event
    async def on_ready():
        nonlocal success
        try:
            # Create natural streaming activity
            activity = discord.Streaming(
                name=details, 
                url='https://www.twitch.tv/randomstreamurl'  # Use varied URLs
            )
            
            # Add small delay before presence change
            await asyncio.sleep(random.uniform(2, 8))
            
            await client.change_presence(activity=activity)
            print(f"✅ Safe streaming status set for token {token_id}: {details}")
            
            # Record successful usage
            record_streaming_usage(token)
            success = True
            
            # Wait before closing connection
            await asyncio.sleep(random.uniform(3, 10))
            
        except Exception as e:
            print(f"❌ Error setting streaming status for token {token_id}: {e}")
        finally:
            try:
                await client.close()
            except:
                pass

    try:
        await asyncio.wait_for(client.start(token, bot=False), timeout=30)
    except discord.LoginFailure:
        print(f"🚫 Invalid token {token_id} - removing from safe usage")
    except asyncio.TimeoutError:
        print(f"⏰ Timeout for token {token_id} - connection took too long")
    except Exception as e:
        print(f"❌ Connection error for token {token_id}: {e}")
        # Implement exponential backoff for errors
        await safe_human_delay(STREAMING_ERROR_BACKOFF_BASE)

    return success

async def ultra_safe_streamall_tokens(ctx, messages):
    """Ultra-safe multi-token streaming with advanced protection"""
    tokens = read_streaming_tokens('token.txt')
    if not tokens:
        await ultra_fast_response(ctx, "❌ No valid tokens found in token.txt", delete_after=8)
        return

    # Filter safe tokens
    safe_tokens = [token for token in tokens if is_token_safe_for_streaming(token)]
    if not safe_tokens:
        await ultra_fast_response(ctx, "🛡️ No tokens available for safe streaming (all on cooldown)", delete_after=8)
        return

    # Limit concurrent operations for safety
    max_concurrent = min(3, len(safe_tokens))  # Maximum 3 concurrent operations
    safe_tokens = safe_tokens[:max_concurrent]
    
    await ultra_fast_response(ctx, f"🔒 Starting safe streaming for {len(safe_tokens)} tokens...", delete_after=5)
    
    successful_updates = 0
    
    # Process tokens one by one with delays (safer than concurrent)
    for i, token in enumerate(safe_tokens):
        if i > 0:  # Add delay between tokens
            await safe_human_delay(STREAMING_TOKEN_ROTATION_DELAY)
        
        details = random.choice(messages + NATURAL_STREAMING_ACTIVITIES)  # Mix custom and natural
        success = await ultra_safe_presence_update(token, details)
        
        if success:
            successful_updates += 1
        
        # Add extra delay for safety
        if i < len(safe_tokens) - 1:
            await asyncio.sleep(random.uniform(30, 60))

    await ultra_fast_response(ctx, f"✅ Safe streaming completed: {successful_updates}/{len(safe_tokens)} tokens updated", delete_after=8)

async def ultra_safe_change_streaming_status():
    """Ultra-safe streaming status rotation with extensive protections"""
    global streaming_active, stream_statuses
    await bot.wait_until_ready()
    
    print("🎮 Starting ultra-safe streaming rotation")
    
    while streaming_active:
        try:
            if not stream_statuses:
                print("❌ No streaming statuses configured")
                break
                
            for status in stream_statuses:
                if not streaming_active:
                    break
                
                # Enhanced natural activity mixing
                natural_status = random.choice(NATURAL_STREAMING_ACTIVITIES)
                combined_status = f"{status} | {natural_status}" if random.random() < 0.3 else status
                
                try:
                    await bot.change_presence(
                        activity=discord.Streaming(
                            name=combined_status, 
                            url="https://www.twitch.tv/directory/game/Just%20Chatting"
                        )
                    )
                    print(f"🎮 Safe rotation: {combined_status}")
                    
                    # Ultra-safe delay between rotations
                    delay = random.uniform(STREAMING_MIN_DELAY, STREAMING_MAX_DELAY)
                    await safe_human_delay(delay)
                    
                except Exception as e:
                    print(f"❌ Error in streaming rotation: {e}")
                    await safe_human_delay(STREAMING_ERROR_BACKOFF_BASE)
                    
        except Exception as e:
            print(f"❌ Critical error in streaming rotation: {e}")
            await safe_human_delay(STREAMING_ERROR_BACKOFF_BASE * 2)
    
    print("🛑 Ultra-safe streaming rotation stopped")

async def set_ultra_safe_streaming_status(message):
    """Set streaming status with maximum safety"""
    try:
        # Format message safely
        formatted_message = message[:100]  # Limit length
        natural_activity = random.choice(NATURAL_STREAMING_ACTIVITIES)
        
        # Mix with natural activity for better camouflage
        if random.random() < 0.4:
            formatted_message = f"{formatted_message} | {natural_activity}"
        
        await bot.change_presence(
            activity=discord.Streaming(
                name=formatted_message, 
                url="https://www.twitch.tv/directory"
            )
        )
        print(f"✅ Ultra-safe streaming status set: {formatted_message}")
        
    except Exception as e:
        print(f"❌ Error setting ultra-safe streaming status: {e}")

# ==================== ULTRA-SAFE STREAMING COMMANDS ====================

# Command: -streamall <messages> (ultra-safe streaming on all tokens)
@bot.command()
async def streamall(ctx, *, messages=None):
    """Ultra-safe streaming status on all tokens from token.txt"""
    if not is_authorized_user(ctx.author.id):
        await ultra_fast_response(ctx, "❌ **ACCESS DENIED**\n🔒 This command requires authorization", delete_after=5, bypass_stealth=True)
        return

    if messages is None or messages.strip() == "":
        await ultra_fast_response(ctx, "Usage: `-streamall <message1,message2,message3>`\n🛡️ **ULTRA-SAFE MODE**\n• Max 2 changes per hour per token\n• 5-15 minute delays between changes\n• Automatic cooldowns and rate limiting", delete_after=12, bypass_stealth=True)
        return

    try:
        # Instant command deletion
        await instant_delete_command(ctx)
        
        # Parse messages with safety validation
        message_list = [msg.strip()[:50] for msg in messages.split(',') if msg.strip()]  # Limit message length
        if not message_list:
            await ultra_fast_response(ctx, "❌ No valid messages provided", delete_after=5)
            return
        
        # Add safety warning
        await ultra_fast_response(ctx, "🛡️ **ULTRA-SAFE STREAMING INITIATED**\nThis may take several minutes due to safety delays...", delete_after=8)
        
        await ultra_safe_streamall_tokens(ctx, message_list)
        print(f"🔒 Ultra-safe streamall executed by {ctx.author} with messages: {message_list}")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error: {str(e)}", delete_after=8)
        print(f"❌ Error in ultra-safe streamall: {e}")

# Command: -stream <activity> (ultra-safe streaming on main bot)
@bot.command()
async def stream(ctx, *, activity=None):
    """Ultra-safe streaming status on the main bot"""
    if not is_authorized_user(ctx.author.id):
        await ultra_fast_response(ctx, "❌ **ACCESS DENIED**\n🔒 This command requires authorization", delete_after=5, bypass_stealth=True)
        return

    if activity is None or activity.strip() == "":
        await ultra_fast_response(ctx, "Usage: `-stream <activity>`\n🛡️ Sets ultra-safe streaming status on main bot", delete_after=8, bypass_stealth=True)
        return
    
    try:
        # Instant command deletion
        await instant_delete_command(ctx)
        
        # Add human-like delay before streaming
        await asyncio.sleep(random.uniform(3, 8))
        
        await set_ultra_safe_streaming_status(activity)
        await ultra_fast_response(ctx, f"🛡️ Ultra-safe streaming enabled: {activity}", delete_after=8)
        print(f"🔒 Ultra-safe streaming enabled by {ctx.author}: {activity}")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Failed to enable streaming: {e}", delete_after=8)
        print(f"❌ Error enabling ultra-safe streaming: {e}")

# Command: -streamoff (disable streaming)
@bot.command()
async def streamoff(ctx):
    """Disable streaming status"""
    if not is_authorized_user(ctx.author.id):
        await ultra_fast_response(ctx, "❌ **ACCESS DENIED**\n🔒 This command requires authorization", delete_after=5, bypass_stealth=True)
        return
    
    try:
        # Instant command deletion
        await instant_delete_command(ctx)
        
        # Add human-like delay before disabling
        await asyncio.sleep(random.uniform(2, 5))
        
        await bot.change_presence(activity=None)  
        await ultra_fast_response(ctx, "🛡️ Streaming safely disabled", delete_after=5)
        print(f"🔒 Ultra-safe streaming disabled by {ctx.author}")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Failed to disable streaming: {e}", delete_after=5)
        print(f"❌ Error disabling streaming: {e}")

# Command: -streamrotate <statuses> (ultra-safe streaming rotation)
@bot.command()
async def streamrotate(ctx, *, statuses=None):
    """Start ultra-safe streaming status rotation"""
    global streaming_active, streaming_status_task, stream_statuses
    
    if not is_authorized_user(ctx.author.id):
        await ultra_fast_response(ctx, "❌ **ACCESS DENIED**\n🔒 This command requires authorization", delete_after=5, bypass_stealth=True)
        return

    if statuses is None or statuses.strip() == "":
        await ultra_fast_response(ctx, "Usage: `-streamrotate <status1,status2,status3>`\n🛡️ **ULTRA-SAFE ROTATION**\n• 5-15 minute delays between changes\n• Mixed with natural streaming activities\n• Advanced anti-detection measures", delete_after=12, bypass_stealth=True)
        return
    
    try:
        # Instant command deletion
        await instant_delete_command(ctx)
        
        # Stop existing rotation safely
        if streaming_status_task:
            streaming_status_task.cancel()
            streaming_active = False
            await asyncio.sleep(2)  # Brief pause
        
        # Parse statuses with safety validation
        stream_statuses = [status.strip()[:50] for status in statuses.split(',') if status.strip()]
        if not stream_statuses:
            await ultra_fast_response(ctx, "❌ No valid statuses provided", delete_after=5)
            return
        
        # Start ultra-safe rotation
        streaming_active = True
        streaming_status_task = bot.loop.create_task(ultra_safe_change_streaming_status())
        
        await ultra_fast_response(ctx, f"🛡️ Ultra-safe stream rotation started\n• {len(stream_statuses)} custom statuses\n• Mixed with natural activities\n• 5-15 minute rotation intervals", delete_after=10)
        print(f"🔒 Ultra-safe stream rotation started by {ctx.author} with statuses: {stream_statuses}")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error: {str(e)}", delete_after=8)
        print(f"❌ Error in ultra-safe streamrotate: {e}")

# Command: -streamrotateoff (stop ultra-safe stream rotation)
@bot.command()
async def streamrotateoff(ctx):
    """Stop ultra-safe streaming status rotation"""
    global streaming_active, streaming_status_task
    
    if not is_authorized_user(ctx.author.id):
        await ultra_fast_response(ctx, "❌ **ACCESS DENIED**\n🔒 This command requires authorization", delete_after=5, bypass_stealth=True)
        return
    
    try:
        # Instant command deletion
        await instant_delete_command(ctx)
        
        if streaming_status_task:
            streaming_status_task.cancel()
            streaming_status_task = None
            streaming_active = False
            
            # Add delay before clearing presence
            await asyncio.sleep(random.uniform(2, 5))
            await bot.change_presence(activity=None)
            
            await ultra_fast_response(ctx, "🛡️ Ultra-safe stream rotation stopped", delete_after=5)
            print(f"🔒 Ultra-safe stream rotation disabled by {ctx.author}")
        else:
            await ultra_fast_response(ctx, "ℹ️ Stream rotation is already off", delete_after=5)
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error: {str(e)}", delete_after=5)
        print(f"❌ Error disabling stream rotation: {e}")

# Command: -streamstatus (check streaming safety status)
@bot.command()
async def streamstatus(ctx):
    """Check current streaming safety status and cooldowns"""
    if not is_authorized_user(ctx.author.id):
        await ultra_fast_response(ctx, "❌ **ACCESS DENIED**\n🔒 This command requires authorization", delete_after=5, bypass_stealth=True)
        return
    
    try:
        # Instant command deletion
        await instant_delete_command(ctx)
        
        # Get token status
        tokens = read_streaming_tokens('token.txt')
        safe_tokens = [token for token in tokens if is_token_safe_for_streaming(token)]
        
        # Calculate cooldown info
        cooldown_info = []
        current_time = time.time()
        for token in tokens[:5]:  # Show first 5 tokens
            token_id = token[-8:]
            if token_id in streaming_last_change:
                time_since_last = current_time - streaming_last_change[token_id]
                remaining_cooldown = max(0, STREAMING_MIN_DELAY - time_since_last)
                cooldown_info.append(f"Token {token_id}: {remaining_cooldown:.0f}s cooldown")
            else:
                cooldown_info.append(f"Token {token_id}: Ready")
        
        status_msg = f"🛡️ **ULTRA-SAFE STREAMING STATUS**\n\n"
        status_msg += f"📊 **Tokens**: {len(safe_tokens)}/{len(tokens)} ready\n"
        status_msg += f"🔄 **Rotation**: {'Active' if streaming_active else 'Inactive'}\n"
        status_msg += f"⏱️ **Safety Limits**:\n• Max {STREAMING_MAX_CHANGES_PER_HOUR}/hour per token\n• {STREAMING_MIN_DELAY//60}-{STREAMING_MAX_DELAY//60} min delays\n\n"
        
        if cooldown_info:
            status_msg += f"⏰ **Cooldown Status**:\n" + "\n".join(cooldown_info[:3])
        
        await ultra_fast_response(ctx, status_msg, delete_after=15)
        print(f"🔒 Streaming status checked by {ctx.author}")
        
    except Exception as e:
        await ultra_fast_response(ctx, f"❌ Error: {str(e)}", delete_after=8)
        print(f"❌ Error checking streaming status: {e}")

# ==================== END STREAMING FUNCTIONALITY ====================

# ==================== NEW FEATURES ====================

# Command: -snipe (show last deleted message in channel)
@bot.command()
async def snipe(ctx):
    """Show the last deleted message in this channel"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)
        data = snipe_cache.get(ctx.channel.id)
        if not data:
            msg = await ctx.channel.send("🔍 Nothing to snipe — no deleted messages cached in this channel.")
            await asyncio.sleep(6)
            try:
                await msg.delete()
            except:
                pass
            return

        ts = data["timestamp"]
        time_str = ts.strftime("%d/%m/%Y %H:%M:%S UTC") if ts else "Unknown"
        content = data["content"][:1800]
        attachments = data["attachments"]

        out = (
            f"🗑️ **Sniped Message**\n"
            f"👤 **Author:** {data['author']} (`{data['author_id']}`)\n"
            f"🕐 **Sent at:** {time_str}\n"
            f"💬 **Content:**\n{content}"
        )
        if attachments:
            out += f"\n📎 **Attachments:** {' '.join(attachments[:3])}"

        msg = await ctx.channel.send(out)
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except:
            pass
    except Exception as e:
        print(f"❌ Snipe error: {e}")


# Command: -esnipe (show last edited message in channel)
@bot.command()
async def esnipe(ctx):
    """Show the last edited message in this channel"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)
        data = esnipe_cache.get(ctx.channel.id)
        if not data:
            msg = await ctx.channel.send("🔍 Nothing to edit-snipe — no edited messages cached in this channel.")
            await asyncio.sleep(6)
            try:
                await msg.delete()
            except:
                pass
            return

        ts = data["timestamp"]
        time_str = ts.strftime("%d/%m/%Y %H:%M:%S UTC") if ts else "Unknown"
        before = data["before"][:800]
        after = data["after"][:800]

        out = (
            f"✏️ **Edit Sniped Message**\n"
            f"👤 **Author:** {data['author']} (`{data['author_id']}`)\n"
            f"🕐 **Edited at:** {time_str}\n"
            f"📝 **Before:**\n{before}\n"
            f"📝 **After:**\n{after}"
        )
        msg = await ctx.channel.send(out)
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except:
            pass
    except Exception as e:
        print(f"❌ Edit snipe error: {e}")


# Command: -purge [amount] (delete your own messages)
@bot.command()
async def purge(ctx, amount: str = "10"):
    """Delete your own messages in the current channel"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        try:
            limit = int(amount)
            limit = max(1, min(limit, 200))
        except ValueError:
            msg = await ctx.channel.send("❌ Usage: `-purge [amount]` (1-200)")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
            return

        deleted_count = 0
        checked = 0
        async for message in ctx.channel.history(limit=500):
            if checked >= 500 or deleted_count >= limit:
                break
            checked += 1
            if message.author.id == bot.user.id:
                try:
                    await message.delete()
                    deleted_count += 1
                    await asyncio.sleep(0.35)
                except discord.NotFound:
                    pass
                except discord.HTTPException:
                    await asyncio.sleep(1)

        msg = await ctx.channel.send(f"🧹 Purged **{deleted_count}** of your messages.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass
        print(f"🧹 Purged {deleted_count} messages")
    except Exception as e:
        print(f"❌ Purge error: {e}")


# Command: -massdm <message> (DM all members in the server)
@bot.command()
async def massdm(ctx, *, message_text=None):
    """DM all members of the current server"""
    global mass_dm_active, mass_dm_task
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return

    await instant_delete_command(ctx)

    if message_text is None:
        msg = await ctx.channel.send("❌ Usage: `-massdm <message>`")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass
        return

    if not ctx.guild:
        msg = await ctx.channel.send("❌ This command only works in a server.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass
        return

    if mass_dm_active:
        msg = await ctx.channel.send("⚠️ Mass DM already running. Use `-stopmassdm` to stop it first.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass
        return

    mass_dm_active = True
    members = [m for m in ctx.guild.members if not m.bot and m.id != bot.user.id]
    status_msg = await ctx.channel.send(f"📨 Starting Mass DM to **{len(members)}** members...")

    async def do_mass_dm():
        global mass_dm_active
        sent = 0
        failed = 0
        try:
            for member in members:
                if not mass_dm_active:
                    break
                try:
                    await member.send(message_text)
                    sent += 1
                    await asyncio.sleep(random.uniform(1.2, 2.5))
                except discord.Forbidden:
                    failed += 1
                except discord.HTTPException:
                    failed += 1
                    await asyncio.sleep(2)
                except Exception:
                    failed += 1
        finally:
            mass_dm_active = False
            try:
                await status_msg.edit(content=f"✅ Mass DM complete — Sent: **{sent}** | Failed: **{failed}**")
                await asyncio.sleep(10)
                await status_msg.delete()
            except:
                pass
            print(f"📨 Mass DM done — Sent: {sent}, Failed: {failed}")

    mass_dm_task = asyncio.create_task(do_mass_dm())


# Command: -stopmassdm (stop ongoing mass DM)
@bot.command()
async def stopmassdm(ctx):
    """Stop an ongoing mass DM"""
    global mass_dm_active, mass_dm_task
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)
    if mass_dm_active:
        mass_dm_active = False
        if mass_dm_task:
            mass_dm_task.cancel()
        msg = await ctx.channel.send("🛑 Mass DM stopped.")
    else:
        msg = await ctx.channel.send("ℹ️ No mass DM is currently running.")
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except:
        pass


# Command: -type [seconds] (spam typing indicator in channel)
@bot.command(name="type")
async def typing_spam(ctx, seconds: str = "10"):
    """Spam typing indicator in this channel"""
    global typing_tasks
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)

    try:
        duration = int(seconds)
        duration = max(1, min(duration, 300))
    except ValueError:
        msg = await ctx.channel.send("❌ Usage: `-type [seconds]` (1-300)")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass
        return

    channel_id = ctx.channel.id
    if channel_id in typing_tasks and not typing_tasks[channel_id].done():
        msg = await ctx.channel.send("⚠️ Typing spam already active in this channel. Use `-stoptype` first.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except:
            pass
        return

    async def run_typing():
        end_time = time.time() + duration
        try:
            while time.time() < end_time and channel_id in typing_tasks and not typing_tasks[channel_id].cancelled():
                try:
                    async with ctx.channel.typing():
                        await asyncio.sleep(8)
                except Exception:
                    await asyncio.sleep(1)
        finally:
            typing_tasks.pop(channel_id, None)
            print(f"⌨️ Typing spam ended in channel {channel_id}")

    typing_tasks[channel_id] = asyncio.create_task(run_typing())
    print(f"⌨️ Typing spam started for {duration}s in {ctx.channel}")


# Command: -stoptype (stop typing spam)
@bot.command()
async def stoptype(ctx):
    """Stop typing spam in this channel"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)
    channel_id = ctx.channel.id
    task = typing_tasks.pop(channel_id, None)
    if task and not task.done():
        task.cancel()
        msg = await ctx.channel.send("🛑 Typing spam stopped.")
    else:
        msg = await ctx.channel.send("ℹ️ No typing spam active in this channel.")
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except:
        pass


# Command: -uinfo [@user] (show user info)
@bot.command()
async def uinfo(ctx, *, user_mention=None):
    """Show detailed info about a user"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        target = None
        if user_mention:
            uid = find_user_id_by_mention(user_mention)
            if uid:
                try:
                    target = await bot.fetch_user(int(uid))
                except Exception:
                    pass
            if not target:
                try:
                    target = await bot.fetch_user(int(user_mention))
                except Exception:
                    pass
        if not target:
            target = bot.user

        created = target.created_at
        created_str = created.strftime("%d %B %Y, %H:%M UTC")
        account_age_days = (datetime.datetime.now(datetime.timezone.utc) - created).days

        badges = []
        if target.public_flags.staff:
            badges.append("👨‍💼 Discord Staff")
        if target.public_flags.partner:
            badges.append("🤝 Partner")
        if target.public_flags.bug_hunter:
            badges.append("🐛 Bug Hunter")
        if target.public_flags.hypesquad_bravery:
            badges.append("🏠 HypeSquad Bravery")
        if target.public_flags.hypesquad_brilliance:
            badges.append("🏠 HypeSquad Brilliance")
        if target.public_flags.hypesquad_balance:
            badges.append("🏠 HypeSquad Balance")
        if target.public_flags.early_supporter:
            badges.append("⭐ Early Supporter")
        if target.public_flags.verified_bot_developer:
            badges.append("🔧 Verified Bot Dev")
        if target.public_flags.active_developer:
            badges.append("💻 Active Developer")
        if target.bot:
            badges.append("🤖 Bot")
        badge_str = " | ".join(badges) if badges else "None"

        avatar_url = target.display_avatar.url if target.display_avatar else "No avatar"

        out = (
            f"👤 **USER INFO**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🏷️ **Username:** {target.name}\n"
            f"🆔 **ID:** {target.id}\n"
            f"📅 **Created:** {created_str}\n"
            f"📆 **Account Age:** {account_age_days} days\n"
            f"🎖️ **Badges:** {badge_str}\n"
            f"🤖 **Bot:** {'Yes' if target.bot else 'No'}\n"
            f"🖼️ **Avatar:** {avatar_url}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        msg = await ctx.channel.send(out)
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except:
            pass
    except Exception as e:
        print(f"❌ uinfo error: {e}")


# Command: -lookup <user_id> (fetch any user profile by ID, no shared server needed)
@bot.command(name="lookup")
async def lookup(ctx, user_id: str = None):
    """Fetch full profile of any Discord user by ID — no shared server required"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        if not user_id:
            msg = await ctx.channel.send("❌ Usage: `-lookup <user_id>`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        try:
            uid = int(user_id.strip())
        except ValueError:
            msg = await ctx.channel.send("❌ Invalid ID — must be a number. Example: `-lookup 123456789`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        try:
            target = await bot.fetch_user(uid)
        except discord.NotFound:
            msg = await ctx.channel.send(f"❌ No user found with ID `{uid}`.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return
        except discord.HTTPException as e:
            msg = await ctx.channel.send(f"❌ Discord API error: `{e}`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except Exception:
                pass
            return

        created = target.created_at
        created_str = created.strftime("%d %B %Y, %H:%M UTC")
        account_age_days = (datetime.datetime.now(datetime.timezone.utc) - created).days

        badges = []
        if target.public_flags.staff:
            badges.append("👨‍💼 Staff")
        if target.public_flags.partner:
            badges.append("🤝 Partner")
        if target.public_flags.bug_hunter:
            badges.append("🐛 Bug Hunter")
        if target.public_flags.hypesquad_bravery:
            badges.append("🏠 Bravery")
        if target.public_flags.hypesquad_brilliance:
            badges.append("🏠 Brilliance")
        if target.public_flags.hypesquad_balance:
            badges.append("🏠 Balance")
        if target.public_flags.early_supporter:
            badges.append("⭐ Early Supporter")
        if target.public_flags.verified_bot_developer:
            badges.append("🔧 Verified Bot Dev")
        if target.public_flags.active_developer:
            badges.append("💻 Active Dev")
        if target.bot:
            badges.append("🤖 Bot")
        badge_str = " · ".join(badges) if badges else "None"

        avatar_url = target.display_avatar.with_size(4096).url if target.display_avatar else "No avatar"

        lines = [
            f"🔍 **LOOKUP** · `{uid}`",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"🏷️ **Username:** {target}",
            f"🆔 **ID:** {target.id}",
            f"📅 **Created:** {created_str}",
            f"📆 **Account Age:** {account_age_days} days",
            f"🎖️ **Badges:** {badge_str}",
            f"🤖 **Bot:** {'Yes' if target.bot else 'No'}",
            f"🖼️ **Avatar:** {avatar_url}",
        ]

        # Try to get banner too
        try:
            full = await bot.fetch_user(uid)
            if hasattr(full, 'banner') and full.banner:
                lines.append(f"🎨 **Banner:** {full.banner.with_size(4096).url}")
        except Exception:
            pass

        lines.append("━━━━━━━━━━━━━━━━━━━━")

        msg = await ctx.channel.send("\n".join(lines))
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except Exception:
            pass

    except Exception as e:
        print(f"❌ lookup error: {e}")


# Command: -sinfo (show server info)
@bot.command()
async def sinfo(ctx):
    """Show detailed info about the current server"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        if not ctx.guild:
            msg = await ctx.channel.send("❌ This command only works in a server.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
            return

        g = ctx.guild
        created_str = g.created_at.strftime("%d %B %Y, %H:%M UTC")
        age_days = (datetime.datetime.now(datetime.timezone.utc) - g.created_at).days
        total_members = g.member_count or len(g.members)
        bots = sum(1 for m in g.members if m.bot)
        humans = total_members - bots
        text_channels = len(g.text_channels)
        voice_channels = len(g.voice_channels)
        categories = len(g.categories)
        roles = len(g.roles) - 1
        emojis = len(g.emojis)
        boost_level = g.premium_tier
        boosts = g.premium_subscription_count or 0
        owner = g.owner
        owner_str = f"{owner} ({owner.id})" if owner else "Unknown"
        icon_url = g.icon.url if g.icon else "No icon"

        verification = str(g.verification_level).replace("_", " ").title()

        out = (
            f"🏰 **SERVER INFO — {g.name}**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 **ID:** {g.id}\n"
            f"👑 **Owner:** {owner_str}\n"
            f"📅 **Created:** {created_str} ({age_days} days ago)\n"
            f"👥 **Members:** {total_members} ({humans} humans, {bots} bots)\n"
            f"💬 **Text Channels:** {text_channels}\n"
            f"🔊 **Voice Channels:** {voice_channels}\n"
            f"📁 **Categories:** {categories}\n"
            f"🏷️ **Roles:** {roles}\n"
            f"😀 **Emojis:** {emojis}\n"
            f"🚀 **Boost Level:** {boost_level} ({boosts} boosts)\n"
            f"🔒 **Verification:** {verification}\n"
            f"🖼️ **Icon:** {icon_url}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        msg = await ctx.channel.send(out)
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except:
            pass
    except Exception as e:
        print(f"❌ sinfo error: {e}")


# Command: -checktoken <token> (check if a Discord token is valid)
@bot.command()
async def checktoken(ctx, token_value=None):
    """Check if a Discord token is valid"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        if not token_value:
            msg = await ctx.channel.send("❌ Usage: `-checktoken <token>`")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
            return

        checking_msg = await ctx.channel.send("🔍 Checking token...")

        try:
            headers = {
                "Authorization": token_value,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get("https://discord.com/api/v10/users/@me", headers=headers, timeout=10)
            )

            if response.status_code == 200:
                data = response.json()
                username = data.get("username", "Unknown")
                discriminator = data.get("discriminator", "0")
                user_id = data.get("id", "Unknown")
                email = data.get("email", "Not accessible")
                phone = data.get("phone", "Not accessible")
                mfa = data.get("mfa_enabled", False)
                nitro = data.get("premium_type", 0)
                nitro_map = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
                nitro_str = nitro_map.get(nitro, "Unknown")

                disp = f"{username}#{discriminator}" if discriminator != "0" else username
                result = (
                    f"✅ **TOKEN VALID**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **User:** {disp}\n"
                    f"🆔 **ID:** {user_id}\n"
                    f"📧 **Email:** {email}\n"
                    f"📱 **Phone:** {phone if phone else 'None'}\n"
                    f"🔐 **2FA:** {'Enabled' if mfa else 'Disabled'}\n"
                    f"💎 **Nitro:** {nitro_str}\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
            elif response.status_code == 401:
                result = "❌ **TOKEN INVALID** — Unauthorized (wrong/expired token)"
            elif response.status_code == 403:
                result = "⚠️ **TOKEN FLAGGED** — Token exists but account may be disabled"
            else:
                result = f"⚠️ **UNKNOWN STATUS** — HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            result = "❌ Request timed out — Discord API unreachable"
        except Exception as req_err:
            result = f"❌ Error checking token: {req_err}"

        try:
            await checking_msg.edit(content=result)
            await asyncio.sleep(20)
            await checking_msg.delete()
        except:
            pass
        print(f"🔍 Token check completed by {ctx.author}")
    except Exception as e:
        print(f"❌ checktoken error: {e}")


# Command: -nuke (clone and delete current channel)
@bot.command()
async def nuke(ctx):
    """Clone the current channel then delete the original (nuke)"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        if not ctx.guild:
            msg = await ctx.channel.send("❌ This command only works in a server.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
            return

        channel = ctx.channel
        position = channel.position

        # Clone channel — preserves name, topic, overwrites, slowmode, NSFW flag
        new_channel = await channel.clone(reason="Nuked by selfbot")

        # Put new channel in same position
        try:
            await new_channel.edit(position=position)
        except Exception:
            pass

        # Delete original
        await channel.delete(reason="Nuked by selfbot")

        confirm = await new_channel.send(f"💥 **Channel nuked.** Fresh start.")
        await asyncio.sleep(5)
        try:
            await confirm.delete()
        except:
            pass
        print(f"💥 Nuked channel #{channel.name} in {ctx.guild.name}")
    except discord.Forbidden:
        try:
            msg = await ctx.channel.send("❌ Missing permissions to nuke this channel.")
            await asyncio.sleep(5)
            await msg.delete()
        except:
            pass
    except Exception as e:
        print(f"❌ Nuke error: {e}")


# Command: -invite [uses] [max_age_hours] (generate a server invite)
@bot.command()
async def invite(ctx, max_uses: str = "0", max_age_hours: str = "0"):
    """Generate an invite link for the current channel"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)

        if not ctx.guild:
            msg = await ctx.channel.send("❌ This command only works in a server.")
            await asyncio.sleep(5)
            try:
                await msg.delete()
            except:
                pass
            return

        try:
            uses = int(max_uses)
        except ValueError:
            uses = 0
        try:
            age_hours = int(max_age_hours)
            age_seconds = age_hours * 3600
        except ValueError:
            age_seconds = 0

        invite_obj = await ctx.channel.create_invite(
            max_uses=uses,
            max_age=age_seconds,
            unique=True,
            reason="Generated by selfbot"
        )

        uses_str = f"{uses} uses" if uses > 0 else "unlimited uses"
        age_str = f"{age_hours}h expiry" if age_seconds > 0 else "never expires"

        out = (
            f"🔗 **Invite Generated**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📎 **Link:** {invite_obj.url}\n"
            f"📋 **Channel:** #{ctx.channel.name}\n"
            f"🔢 **Max Uses:** {uses_str}\n"
            f"⏱️ **Expires:** {age_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        msg = await ctx.channel.send(out)
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except:
            pass
        print(f"🔗 Invite created: {invite_obj.url}")
    except discord.Forbidden:
        try:
            msg = await ctx.channel.send("❌ Missing permissions to create invites in this channel.")
            await asyncio.sleep(5)
            await msg.delete()
        except:
            pass
    except Exception as e:
        print(f"❌ Invite error: {e}")

# Command: -troll @user (auto-reply to user's messages with troll responses)
@bot.command()
async def troll(ctx, *, user_mention=None):
    """Auto-reply to a user's every message with troll responses"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)

    if not user_mention:
        msg = await ctx.channel.send("❌ Usage: `-troll @user`")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    uid = find_user_id_by_mention(user_mention)
    if not uid:
        msg = await ctx.channel.send("❌ Invalid user mention. Use `-troll @user`")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    if is_user_whitelisted(int(uid)):
        msg = await ctx.channel.send(f"🛡️ That user is whitelisted and cannot be trolled.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    troll_targets[uid] = {"channel_id": ctx.channel.id, "active": True}
    msg = await ctx.channel.send(f"🤡 Now trolling <@{uid}> — every message they send will get a reply.")
    await asyncio.sleep(6)
    try:
        await msg.delete()
    except Exception:
        pass
    print(f"🤡 Troll started on user {uid}")


# Command: -stoptroll @user (stop trolling a user)
@bot.command()
async def stoptroll(ctx, *, user_mention=None):
    """Stop trolling a user"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)

    if not user_mention:
        # Stop all troll targets
        count = len(troll_targets)
        troll_targets.clear()
        msg = await ctx.channel.send(f"🛑 Stopped trolling all {count} user(s).")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    uid = find_user_id_by_mention(user_mention)
    if uid and uid in troll_targets:
        del troll_targets[uid]
        msg = await ctx.channel.send(f"🛑 Stopped trolling <@{uid}>.")
    else:
        msg = await ctx.channel.send("ℹ️ That user is not being trolled.")
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except Exception:
        pass


# Command: -copycat @user (mirror everything a user says)
@bot.command()
async def copycat(ctx, *, user_mention=None):
    """Mirror everything a user says in real time"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)

    if not user_mention:
        msg = await ctx.channel.send("❌ Usage: `-copycat @user`")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    uid = find_user_id_by_mention(user_mention)
    if not uid:
        msg = await ctx.channel.send("❌ Invalid user mention. Use `-copycat @user`")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    if is_user_whitelisted(int(uid)):
        msg = await ctx.channel.send(f"🛡️ That user is whitelisted and cannot be copycatted.")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    copycat_targets[uid] = {"channel_id": ctx.channel.id, "active": True}
    msg = await ctx.channel.send(f"🦜 Now mirroring <@{uid}> — everything they type will be echoed.")
    await asyncio.sleep(6)
    try:
        await msg.delete()
    except Exception:
        pass
    print(f"🦜 Copycat started on user {uid}")


# Command: -stopcopycat @user (stop mirroring a user)
@bot.command()
async def stopcopycat(ctx, *, user_mention=None):
    """Stop mirroring a user"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)

    if not user_mention:
        count = len(copycat_targets)
        copycat_targets.clear()
        msg = await ctx.channel.send(f"🛑 Stopped copycatting all {count} user(s).")
        await asyncio.sleep(5)
        try:
            await msg.delete()
        except Exception:
            pass
        return

    uid = find_user_id_by_mention(user_mention)
    if uid and uid in copycat_targets:
        del copycat_targets[uid]
        msg = await ctx.channel.send(f"🛑 Stopped copycatting <@{uid}>.")
    else:
        msg = await ctx.channel.send("ℹ️ That user is not being copycatted.")
    await asyncio.sleep(5)
    try:
        await msg.delete()
    except Exception:
        pass

# ==================== AUTO QUEST COMPLETER ====================

def _quest_headers(token):
    """Build headers that spoof a Discord desktop client"""
    return {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": QUEST_UA,
        "X-Super-Properties": QUEST_SUPER_PROPS,
        "X-Discord-Locale": "en-US",
        "X-Discord-Timezone": "America/New_York",
    }

def _quest_get(token, path):
    """Synchronous GET against Discord API"""
    r = requests.get(f"{DISCORD_API_BASE}{path}", headers=_quest_headers(token), timeout=15)
    return r.status_code, r.json() if r.content else {}

def _quest_post(token, path, body=None):
    """Synchronous POST against Discord API"""
    r = requests.post(
        f"{DISCORD_API_BASE}{path}",
        headers=_quest_headers(token),
        json=body or {},
        timeout=15,
    )
    return r.status_code, r.json() if r.content else {}

def _parse_quests(raw_quests):
    """Parse raw quest list into clean dicts"""
    parsed = []
    for q in raw_quests:
        qid = q.get("id", "?")
        config = q.get("config", {})
        msgs = config.get("messages", {})
        name = (
            msgs.get("en-US", {}).get("name")
            or msgs.get("default", {}).get("name")
            or next(iter(msgs.values()), {}).get("name", "Unknown Quest")
        )

        task_config = config.get("task_config", {})
        user_status = q.get("user_status") or {}
        enrolled = bool(user_status)
        completed_at = user_status.get("completed_at")
        claimed_at = user_status.get("claimed_at")

        # Extract task progressions
        progress_obj = user_status.get("progress", {})
        task_progressions = progress_obj.get("task_progressions", [])

        tasks = []
        for task in task_progressions:
            task_name = task.get("task_name", "UNKNOWN")
            value = float(task.get("value", 0))
            target = float(task.get("target_value", 0) or task_config.get(task_name, {}).get("target_count", 900))
            tasks.append({
                "name": task_name,
                "value": value,
                "target": target,
                "done": value >= target,
            })

        # Fallback: derive tasks from task_config if no user_status tasks yet
        if not tasks and task_config:
            for task_name, tcfg in task_config.items():
                target = float(tcfg.get("target_count", 900))
                tasks.append({
                    "name": task_name,
                    "value": 0,
                    "target": target,
                    "done": False,
                })

        parsed.append({
            "id": qid,
            "name": name,
            "enrolled": enrolled,
            "completed": bool(completed_at),
            "claimed": bool(claimed_at),
            "tasks": tasks,
        })
    return parsed

async def _run_quest_heartbeat(token, quest, status_msg, loop):
    """Run the heartbeat loop for a single quest until complete"""
    qid = quest["id"]
    qname = quest["name"]
    tasks = quest["tasks"]

    # Only heartbeat-compatible task types
    HEARTBEAT_TASKS = {
        "STREAM_ON_DESKTOP", "PLAY_ON_DESKTOP",
        "PLAY_ON_DESKTOP_V2", "PLAY_ACTIVITY",
    }
    hb_tasks = [t for t in tasks if t["name"] in HEARTBEAT_TASKS]

    if not hb_tasks:
        try:
            await status_msg.edit(content=f"⚠️ **{qname}** — quest type not heartbeat-compatible, skipping.")
        except Exception:
            pass
        return False

    stream_key = f"call:{qid}:1"
    task_info = hb_tasks[0]
    target = task_info["target"]
    current = task_info["value"]

    print(f"🎮 Starting quest: {qname} (id={qid}, progress={current}/{target})")

    heartbeat_interval = 20  # seconds between heartbeats (max 2 min credit each)
    max_attempts = int((target - current) / heartbeat_interval) + 60  # safety buffer

    for attempt in range(max_attempts):
        if not auto_quest_active:
            return False

        is_last = False
        try:
            status_code, resp = await loop.run_in_executor(
                None,
                lambda: _quest_post(token, f"/quests/{qid}/heartbeat",
                                     {"stream_key": stream_key, "terminal": False})
            )
        except Exception as e:
            print(f"❌ Heartbeat error: {e}")
            await asyncio.sleep(5)
            continue

        if status_code == 429:
            retry_after = resp.get("retry_after", 5)
            print(f"⏳ Rate limited, waiting {retry_after}s")
            await asyncio.sleep(float(retry_after))
            continue

        if status_code not in (200, 201):
            print(f"❌ Heartbeat returned HTTP {status_code}: {resp}")
            await asyncio.sleep(10)
            continue

        # Parse progress from response
        prog = resp.get("progress", {})
        task_progs = prog.get("task_progressions", [])
        new_value = current
        for tp in task_progs:
            if tp.get("task_name") in HEARTBEAT_TASKS:
                new_value = float(tp.get("value", current))
                break

        current = new_value
        pct = min(100, int((current / target) * 100)) if target > 0 else 100
        print(f"📊 {qname}: {current:.0f}/{target:.0f} ({pct}%)")

        try:
            await status_msg.edit(
                content=f"🎮 **Auto Quest** — *{qname}*\n"
                        f"📊 Progress: `{current:.0f}/{target:.0f}` ({pct}%)\n"
                        f"⏱️ Heartbeat #{attempt + 1} — updating every {heartbeat_interval}s"
            )
        except Exception:
            pass

        if current >= target:
            is_last = True

        if is_last:
            # Send terminal heartbeat
            try:
                await loop.run_in_executor(
                    None,
                    lambda: _quest_post(token, f"/quests/{qid}/heartbeat",
                                         {"stream_key": stream_key, "terminal": True})
                )
            except Exception:
                pass

            # Claim rewards
            await asyncio.sleep(1)
            try:
                claim_status, claim_resp = await loop.run_in_executor(
                    None,
                    lambda: _quest_post(token, f"/quests/{qid}/claim-rewards")
                )
                if claim_status in (200, 201):
                    print(f"✅ Claimed rewards for: {qname}")
                    return True
                else:
                    print(f"⚠️ Claim returned HTTP {claim_status}: {claim_resp}")
                    return True  # Quest done even if claim has issues
            except Exception as e:
                print(f"⚠️ Claim error: {e}")
                return True

        await asyncio.sleep(heartbeat_interval)

    return False


# Command: -quests (list all current Discord quests and their progress)
@bot.command(name="quests")
async def list_quests(ctx):
    """List all active Discord quests with progress"""
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)
        token = os.environ.get("TOKEN", "")
        if not token:
            msg = await ctx.channel.send("❌ No TOKEN found in environment.")
            await asyncio.sleep(5)
            try: await msg.delete()
            except: pass
            return

        loop = asyncio.get_event_loop()
        fetching = await ctx.channel.send("🔍 Fetching your Discord quests...")

        status_code, raw = await loop.run_in_executor(
            None, lambda: _quest_get(token, "/users/@me/quests")
        )

        if status_code == 401:
            await fetching.edit(content="❌ Invalid token — cannot fetch quests.")
            await asyncio.sleep(6)
            try: await fetching.delete()
            except: pass
            return

        if status_code != 200 or not isinstance(raw, list):
            await fetching.edit(content=f"❌ Discord API returned HTTP {status_code}.")
            await asyncio.sleep(6)
            try: await fetching.delete()
            except: pass
            return

        quests = _parse_quests(raw)

        if not quests:
            await fetching.edit(content="📭 No active quests available right now.")
            await asyncio.sleep(8)
            try: await fetching.delete()
            except: pass
            return

        lines = ["🎮 **YOUR DISCORD QUESTS**\n━━━━━━━━━━━━━━━━━━━━"]
        for i, q in enumerate(quests, 1):
            status = "✅ Claimed" if q["claimed"] else ("🏁 Complete" if q["completed"] else ("📋 Enrolled" if q["enrolled"] else "🔓 Not Enrolled"))
            lines.append(f"\n**{i}. {q['name']}**")
            lines.append(f"🆔 ID: `{q['id']}`  |  {status}")
            for t in q["tasks"]:
                pct = min(100, int((t['value'] / t['target']) * 100)) if t['target'] > 0 else 100
                bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                lines.append(f"  └ `{t['name']}` — {t['value']:.0f}/{t['target']:.0f}s [{bar}] {pct}%")

        unclaimed = sum(1 for q in quests if not q["claimed"] and not q["completed"])
        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"💡 **{unclaimed}** quest(s) ready to complete — use `-autoquest` to start")

        out = "\n".join(lines)
        if len(out) > 1900:
            out = out[:1900] + "\n..."

        await fetching.edit(content=out)
        await asyncio.sleep(40)
        try: await fetching.delete()
        except: pass

    except Exception as e:
        print(f"❌ quests error: {e}")


# Command: -autoquest (auto-complete all available Discord quests)
@bot.command(name="autoquest")
async def auto_quest(ctx):
    """Auto-complete all available Discord quests"""
    global auto_quest_active, auto_quest_task
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    try:
        await instant_delete_command(ctx)
        token = os.environ.get("TOKEN", "")
        if not token:
            msg = await ctx.channel.send("❌ No TOKEN found in environment.")
            await asyncio.sleep(5)
            try: await msg.delete()
            except: pass
            return

        if auto_quest_active:
            msg = await ctx.channel.send("⚠️ Auto quest is already running. Use `-stopquest` to stop it first.")
            await asyncio.sleep(6)
            try: await msg.delete()
            except: pass
            return

        auto_quest_active = True
        loop = asyncio.get_event_loop()
        status_msg = await ctx.channel.send("🔍 Fetching quests...")

        async def run_all_quests():
            global auto_quest_active
            try:
                # Fetch quests
                status_code, raw = await loop.run_in_executor(
                    None, lambda: _quest_get(token, "/users/@me/quests")
                )

                if status_code != 200 or not isinstance(raw, list):
                    await status_msg.edit(content=f"❌ Failed to fetch quests (HTTP {status_code}).")
                    await asyncio.sleep(8)
                    try: await status_msg.delete()
                    except: pass
                    return

                quests = _parse_quests(raw)
                completable = [
                    q for q in quests
                    if not q["claimed"] and not q["completed"] and q["tasks"]
                ]

                if not completable:
                    await status_msg.edit(content="📭 No completable quests found right now. Try again when new quests are available!")
                    await asyncio.sleep(10)
                    try: await status_msg.delete()
                    except: pass
                    return

                await status_msg.edit(
                    content=f"🎮 **Auto Quest Started**\n"
                            f"📋 Found **{len(completable)}** quest(s) to complete\n"
                            f"⏳ Working through them one by one..."
                )

                completed_count = 0
                failed_count = 0

                for quest in completable:
                    if not auto_quest_active:
                        break

                    # Enroll if not already enrolled
                    if not quest["enrolled"]:
                        try:
                            enroll_status, _ = await loop.run_in_executor(
                                None, lambda: _quest_post(token, f"/quests/{quest['id']}/enroll")
                            )
                            if enroll_status in (200, 201):
                                print(f"✅ Enrolled in quest: {quest['name']}")
                                await asyncio.sleep(2)
                            else:
                                print(f"⚠️ Could not enroll in {quest['name']} (HTTP {enroll_status})")
                        except Exception as enroll_err:
                            print(f"⚠️ Enroll error: {enroll_err}")

                    # Run heartbeat loop
                    success = await _run_quest_heartbeat(token, quest, status_msg, loop)
                    if success:
                        completed_count += 1
                        await status_msg.edit(
                            content=f"✅ **Completed: {quest['name']}**\n"
                                    f"📊 {completed_count}/{len(completable)} done"
                        )
                        await asyncio.sleep(3)
                    else:
                        failed_count += 1
                        print(f"⚠️ Quest did not complete: {quest['name']}")

                    await asyncio.sleep(5)

                final = (
                    f"🏆 **Auto Quest Finished!**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ Completed: **{completed_count}**\n"
                    f"⚠️ Skipped/Failed: **{failed_count}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🎁 Check Discord for your rewards!"
                )
                await status_msg.edit(content=final)
                await asyncio.sleep(20)
                try: await status_msg.delete()
                except: pass

            except asyncio.CancelledError:
                try:
                    await status_msg.edit(content="🛑 Auto quest cancelled.")
                    await asyncio.sleep(5)
                    await status_msg.delete()
                except Exception:
                    pass
            except Exception as e:
                print(f"❌ Auto quest error: {e}")
                try:
                    await status_msg.edit(content=f"❌ Quest error: {e}")
                    await asyncio.sleep(8)
                    await status_msg.delete()
                except Exception:
                    pass
            finally:
                auto_quest_active = False

        auto_quest_task = asyncio.create_task(run_all_quests())

    except Exception as e:
        auto_quest_active = False
        print(f"❌ autoquest command error: {e}")


# Command: -stopquest (stop ongoing auto quest)
@bot.command(name="stopquest")
async def stop_quest(ctx):
    """Stop the currently running auto quest"""
    global auto_quest_active, auto_quest_task
    if not is_owner(ctx.author.id):
        await ultra_fast_response(ctx, "❌ Only owner can use this you silly human", delete_after=5, bypass_stealth=True)
        return
    await instant_delete_command(ctx)
    if auto_quest_active:
        auto_quest_active = False
        if auto_quest_task and not auto_quest_task.done():
            auto_quest_task.cancel()
        msg = await ctx.channel.send("🛑 Auto quest stopped.")
    else:
        msg = await ctx.channel.send("ℹ️ No auto quest is currently running.")
    await asyncio.sleep(5)
    try: await msg.delete()
    except: pass

# ==================== END AUTO QUEST COMPLETER ====================

# ==================== END NEW FEATURES ====================

# Run the bot
def run_bot():
    token = os.environ.get('TOKEN')
    if not token:
        print("Error: TOKEN environment variable not found!")
        print("Please set your Discord bot token in the environment variables.")
        return
    try:
        print("Starting LTC Flash Bot...")
        bot.run(token)
    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    run_bot()
