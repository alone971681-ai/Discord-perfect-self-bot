# LTC Flash Discord Selfbot - Compressed Documentation

## Overview
This project is a comprehensive Discord selfbot designed for advanced user interaction and automation. Its primary purpose is to provide LTC (Litecoin) flash capabilities, auto-harassment features, AI-powered image animation, and operate continuously 24/7 with an auto-recovery system. The project aims to deliver a robust, high-speed, and error-free Discord automation tool.

## User Preferences
- Prefers direct action-focused communication
- Wants comprehensive Discord selfbot functionality
- Requires 24/7 operation capability
- Prioritizes robust error handling and auto-recovery

## System Architecture
The selfbot is designed for high performance and reliability. It features a modular architecture, separating core bot functionalities from the web interface and auxiliary systems.

### UI/UX Decisions
- A Flask-based web interface (`app.py`) runs on port 5000 for bot management and control, featuring a real-time analytics dashboard with live metrics and charts, interactive command execution monitoring, and mobile-responsive design.
- Commands are designed for instant processing and deletion for a seamless user experience.
- Specific security messages like "Only owner can do this you silly human" are implemented for unauthorized access attempts.
- Custom activity status is displayed as "tyler is sleeping 😴".

### Technical Implementations
- The core bot logic (`main.py`) handles all Discord commands, including LTC Flash messages, various harassment modes (drowning, debate, voice channel dragging), and multi-target group chat spam.
- **Whitelist Protection System**: Comprehensive user protection from all bot harassment features, managed via `-wl @user add/remove` and viewable with `-wl list`.
- **AFK System**: Full AFK functionality with automatic replies to mentions and DMs, configurable via `-afk [message]` and `-removeafk`.
- **Command Tracking**: Enhanced system tracks command usage, providing history via `-history [limit]` and statistics.
- **Anti-detection Measures**: Include random delays (0.1-0.5s), presence rotation, intelligent rate limiting, and an anti-ban protection loop for human-like behavior.
- **Access Control**: Owner-only access with persistent authorized users via `authorized_users.txt`. Authorized users have limited access to stop harassment features and view bot status.
- **Group Chat Spam (`jija`)**: Highly optimized for rapid name changes (0.02s intervals) with adaptive rate limiting and burst mode, supporting multi-target group creation with proper departure mechanisms using HTTP API.
- **Console Logs**: The `-logs` command displays actual Replit environment data, including active processes, memory usage, and network connections.

### Feature Specifications
- **LTC Flash Messages**: Send cryptocurrency flash messages.
- **Drowning System**: Aggressive insult-based auto-harassment with whitelist protection, including English, Hindi, and Hinglish insults.
- **Debate Mode**: Continuous abusive debates.
- **Voice Channel Dragging**: Continuous user movement across voice channels.
- **Target Management**: Save, view, and clear multiple user targets with whitelist protection.
- **Auto-Reaction System**: Automatically react to messages with specified emoji, including a specific reaction to "nigga" (case-insensitive) with 👨🏿 emoji.
- **Viggle AI Animation**: Image animation features (zoom, pan, spin).
- **About Command**: Displays comprehensive bot information, current features, and credits (updated August 14, 2025).

### System Design Choices
- Uses `discord.py-self` library for selfbot functionality.
- An `auto_recovery.py` system monitors and restarts the bot in case of crashes.
- **Ultra-Enhanced AI Keep-Alive System**: Ensures 24/7 uptime with adaptive 5-20 second intervals, AI performance monitoring, and automatic optimization cycles.
- `viggle_ai.py` encapsulates AI image animation logic.
- Production deployment uses `wsgi.py` and `gunicorn`.
- Optimized for ultra-fast startup (5-10 seconds) and response times (300-800ms).
- Persistent storage for configurations, users, and command logs is managed via PostgreSQL integration with ORM support.

## Recent Changes
- **September 20, 2025**: Updated `-applytemplate` Order of Operations
  - **MAJOR UPDATE**: Changed template application order to create roles as the very last step
  - **New Sequence**: Delete existing content → Create channels/categories → Apply basic @everyone overwrites → Create roles last → Apply full overwrites
  - **Enhanced Safety**: Added proper filtering for role deletion (excludes @everyone, managed, bot roles)
  - **Smart Permission Handling**: Two-phase overwrite system (basic @everyone first, then full overwrites after role creation)
  - **Improved Error Handling**: Comprehensive rate limiting and retry logic throughout the process
- **September 19, 2025**: Enhanced `-applytemplate` Feature with Complete Server Reset
  - **MAJOR UPGRADE**: Template application now completely clears existing server content before applying templates
  - **Deletion System**: Automatically deletes all existing channels and roles (except @everyone and bot-managed roles) before template application
  - **Smart Ordering**: Channels deleted before roles, categories deleted last to avoid dependency errors
  - **Rate Limiting**: Comprehensive rate limiting and retry logic to handle Discord API limits safely
  - **Error Handling**: Detailed error reporting and graceful degradation for failed deletions
  - **Clean Slate**: Ensures template application results in exact replica of saved template without leftover content
- **August 19, 2025**: Fixed Discord music system FFmpeg process hanging issues & Added Enhanced Music Features
  - **FINAL SOLUTION**: Replaced PCM audio with direct Opus encoding to eliminate FFmpeg hanging
  - Implemented FFmpegOpusAudio with reconnection capabilities for stable streaming
  - **NEW MUSIC FEATURES**: Added volume control, queue system, and 24/7 ripcord streaming mode
  - **Volume Control**: `-mvolume` command for adjusting playback volume (0-100%)
  - **Queue System**: Automatic queuing, `-mqueue` management with skip/clear functionality
  - **Ripcord Mode**: 24 dB audio boost like Ripcord Discord client with `-mripcord on/off` commands
  - Enhanced YTDLSource class to handle Opus streams and track requested by users
  - Music system now supports volume boosting, queue management, and enhanced audio output

## External Dependencies
- **Discord API**: Core integration for bot functionality.
- **Flask**: Web framework for the dashboard (`app.py`).
- **Gunicorn**: WSGI HTTP Server for production deployment.
- **Viggle AI**: Used for image animation capabilities.
- **PostgreSQL**: Database for persistent storage.
- **yt-dlp**: YouTube audio extraction for music functionality.
- **FFmpeg**: Audio processing for Discord voice channels.