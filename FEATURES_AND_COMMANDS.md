# LTC Flash Discord Selfbot - Complete Features & Commands Guide

## System Overview
A sophisticated Discord selfbot with advanced messaging, interaction, and automation capabilities, designed for dynamic user engagement across multiple communication channels with LTC flash functionality and aggressive interaction features.

## Core Architecture Components

### 1. **Main Bot (main.py)** - Primary Implementation
- Built with `discord.py-self` library
- Prefix: `-` (dash)
- Self-bot capability for using personal Discord account
- Auto-recovery system integration
- Voice channel monitoring
- Background task management

### 2. **Web Interface (app.py)**
- Flask-based control panel
- Bot start/stop controls
- 24/7 operation setup
- Status monitoring
- Token management

### 3. **Auto-Recovery System (auto_recovery.py)**
- Automatic bot restart on crashes
- Process monitoring
- Error logging and tracking
- Cooldown management (max 10 restarts per hour)

### 4. **Alternative Implementations**
- `working_bot.py` - Direct API/WebSocket implementation
- `working_selfbot.py` - Alternative selfbot architecture
- `ltc_flash_bot.py` - Simplified version

---

## Complete Command Reference

### 💰 **LTC Flash Commands**

#### `-flash <amount> <ltc_address>`
- **Purpose**: Send LTC flash message to ALL accessible channels
- **Example**: `-flash 0.5 LTC_ADDRESS_HERE`
- **Features**:
  - Validates LTC address format
  - Supports amounts with/without $ symbol
  - Progress tracking during mass sending
  - Success/failure count reporting
  - Adaptive delay to avoid rate limits
  - Auto-deletes command after completion

#### `-flashchannel <amount> <ltc_address>`
- **Purpose**: Send LTC flash to current channel only
- **Example**: `-flashchannel 1.0 LTC_ADDRESS_HERE`
- **Features**:
  - Same validation as flash command
  - Limited to current channel
  - Faster execution than mass flash

#### `-bal <ltc_address>`
- **Purpose**: Check real LTC balance of an address
- **Example**: `-bal LTC_ADDRESS_HERE`
- **Features**:
  - Uses Blockcypher API for real balance data
  - Displays balance with 8 decimal precision
  - Error handling for invalid addresses
  - Timeout protection (10 seconds)

---

### 😈 **Harassment & Drowning Commands**

#### `-drown @user`
- **Purpose**: Start continuous harassment of mentioned user
- **Features**:
  - Responds to EVERY message from target user
  - Uses both English and Hindi insults
  - Tracks user across channels
  - Auto-deletes command message
  - Extremely aggressive content

#### `-drownenglish @user`
- **Purpose**: English-only harassment mode
- **Features**:
  - Same as drown but English insults only
  - 15+ different insult variations
  - Immediate dual-insult delivery

#### `-drownhindi @user`
- **Purpose**: Hindi-only harassment mode
- **Features**:
  - Same as drown but Hindi insults only
  - 15+ different insult variations in Hindi script
  - Cultural-specific aggressive content

#### `-stop @user`
- **Purpose**: Stop drowning specified user
- **Features**:
  - Removes user from tracking system
  - Confirmation message
  - Immediate effect

---

### 🔥 **Debate & Response Commands**

#### `-debate @user`
- **Purpose**: Engage in continuous aggressive debate
- **Features**:
  - Auto-responds to every message from target
  - 20+ savage comeback variations
  - Mixed English/Hindi responses
  - Tracks user for continuous engagement
  - More extreme than drowning

#### `-stopd @user`
- **Purpose**: Stop debating specified user
- **Features**:
  - Removes from debate tracking
  - Immediate cessation of responses

---

### 📢 **Spam Commands**

#### `-spam <message>`
- **Purpose**: Rapid message spam (50 messages)
- **Example**: `-spam Hello everyone!`
- **Features**:
  - Sends 50 rapid messages
  - 0.05 second delay between messages
  - Can be stopped mid-execution
  - Background task execution

#### `-stops`
- **Purpose**: Stop all active spam immediately
- **Features**:
  - Cancels all running spam tasks
  - Immediate termination
  - Clears task queue

---

### 🎙️ **Voice Channel Dragging**

#### `-annoy @user`
- **Purpose**: ULTRA-FAST voice channel dragging for maximum disorientation
- **Features**:
  - **LIGHTNING SPEED**: Drags every 0.2 seconds (was 1.5 seconds)
  - Drags target through ALL voice channels in server
  - **RAPID FIRE** movement - target can't understand what's happening
  - Completely disorients the victim with ultra-fast switching
  - No muting/deafening (pure chaotic dragging harassment)
  - Requires move_members permission
  - Auto-detection of voice channel availability
  - Stops if user leaves voice entirely

#### `-stopannoy @user`
- **Purpose**: Stop dragging a specific user
- **Features**:
  - Immediately stops the dragging task
  - Removes from tracking system
  - Provides confirmation message

---

### 🎯 **Utility Commands**

#### `-ping`
- **Purpose**: Test bot responsiveness
- **Features**:
  - Shows latency in milliseconds
  - Confirms bot is online
  - Auto-deletes after 5 seconds

#### `-afk [reason]`
- **Purpose**: Set AFK status with optional reason (works like official Discord bots)
- **Example**: `-afk Going to sleep` or `-afk` (no reason)
- **Features**:
  - Auto-replies when bot is mentioned while AFK
  - Shows AFK duration and reason in mentions
  - Tracks time since AFK was set
  - **AUTO-REMOVES** when you send ANY message (not just commands)
  - Shows "Welcome back! You were AFK for X time" message

#### `-unafk`
- **Purpose**: Manually remove AFK status
- **Features**:
  - Shows total AFK duration
  - Displays original AFK reason
  - Returns to normal operation
  - Welcome back message
  - **Note**: Not needed usually as AFK auto-removes on any message

#### `-help` / `-helpme`
- **Purpose**: Display command help
- **Features**:
  - Complete command reference
  - Usage examples
  - Feature explanations
  - Longer display time (20 seconds)

---

## Automatic Features

### 🥀 **"Sybau" Auto-Reaction**
- **Trigger**: Any message containing "sybau" (case-insensitive)
- **Action**: Automatically adds 🥀💔 reactions
- **Scope**: Works in all channel types (DM, group, server)

### 🔄 **Auto-Recovery System**
- **Features**:
  - Monitors bot process health
  - Automatic restart on crashes
  - Error logging and tracking
  - Cooldown management
  - Signal handling for clean shutdown

### 📊 **Status Tracking**
- **Bot Status**: Running/stopped state
- **Activity Status**: "tyler is sleeping 😴"
- **Last Started**: Timestamp tracking
- **Keep-Alive**: 24/7 operation support

---

## Web Interface Features

### 🌐 **Control Panel (Flask App)**
- **Start Bot**: Launch bot with auto-recovery
- **Stop Bot**: Graceful shutdown
- **Status Check**: Real-time bot status
- **Token Verification**: Validate Discord token
- **24/7 Setup**: Instructions for Always-On operation

### 📈 **Monitoring**
- **Process Status**: Check if bot is running
- **Recovery Status**: Auto-recovery system health
- **Error Tracking**: Last error information
- **Restart Count**: Number of restarts in cooldown period

---

## Advanced Features

### 🎯 **User Tracking Systems**
1. **Drowned Users**: Continuous harassment tracking
2. **Debated Users**: Aggressive response tracking  
3. **Annoying Users**: Voice channel harassment tracking

### 🔧 **Smart Features**
- **Command Validation**: Proper argument checking
- **Error Handling**: Graceful error recovery
- **Auto-Cleanup**: Message deletion timers
- **Permission Handling**: Graceful permission failure handling
- **Rate Limit Protection**: Adaptive delays

### 🛡️ **Safety Features**
- **Self-Message Skip**: Avoids infinite loops
- **Process Monitoring**: Health checks
- **Clean Shutdown**: Proper termination handling
- **Resource Management**: Task cleanup

---

## Configuration & Setup

### 🔑 **Required Environment Variables**
- `TOKEN`: Discord account token (required)
- `SESSION_SECRET`: Flask session secret
- `DATABASE_URL`: PostgreSQL connection string
- `PORT`: Web server port (default: 5000)

### 🚀 **Startup Options**
1. **Web Only**: `./start.sh web`
2. **Bot Only**: `./start.sh bot` 
3. **Full System**: `./start.sh` (default)
4. **With Recovery**: `python start_bot_with_recovery.py`

### 📦 **Dependencies**
- `discord.py-self`: Core selfbot functionality
- `flask`: Web interface
- `requests`: API calls
- `psycopg2-binary`: Database connectivity
- `gunicorn`: Production web server

---

## File Structure

```
├── main.py                    # Primary bot implementation
├── app.py                     # Flask web interface
├── auto_recovery.py           # Auto-restart system
├── working_bot.py            # Alternative implementation
├── working_selfbot.py        # Another implementation
├── ltc_flash_bot.py          # Simplified version
├── start.sh                  # Master startup script
├── start_web_and_bot.sh     # Combined startup
├── templates/               # HTML templates
│   ├── index.html          # Main control panel
│   └── setup_24_7.html     # 24/7 setup guide
└── viggle_ai.py            # Image animation features
```

---

## Important Notes

⚠️ **Content Warning**: This bot contains extremely offensive and inappropriate content including:
- Severe profanity and hate speech
- Harassment and cyberbullying features
- Content in multiple languages designed to offend

⚠️ **Legal Warning**: Usage of this bot may violate:
- Discord Terms of Service
- Anti-harassment policies
- Local laws regarding cyberbullying
- Platform automation rules

⚠️ **Technical Warning**: 
- Self-bots are against Discord ToS
- Account may be banned for usage
- Use at your own risk

This documentation is for educational and reference purposes only.