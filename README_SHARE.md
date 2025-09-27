# LTC Flash Discord Selfbot

A powerful Discord selfbot with LTC (Litecoin) flash capabilities, auto-harassment features, and AI-powered image animation.

## ⚠️ Important Warning

**Using selfbots (bots on user accounts) is against Discord's Terms of Service**. This can result in your account being banned. Use at your own risk and for educational purposes only.

## Features

- **LTC Flash Messages**: Send Litecoin-related flash messages to users
- **Drowning System**: Auto-harass users with multilingual insults
- **Debate Mode**: Engage in intellectual debates with targeted users in Hinglish
- **AI Image Animation**: Animate images using Viggle AI with the `-meme` command
- **24/7 Operation**: Runs continuously with auto-recovery even when Replit is closed
- **Web Dashboard**: Control and monitor your bot through a web interface

## Setup Instructions

1. Fork this Replit project
2. Add your Discord token as an environment secret named `TOKEN`
3. Start the application using the web interface
4. (Optional) For 24/7 operation:
   - Enable "Always On" in your Replit project settings
   - Set up UptimeRobot to ping your Replit URL (see detailed setup page)

## Available Commands

### LTC Commands
- `-flash @user $amount <message>` - Flash LTC to mentioned user with custom message
- `-flashchannel $amount <message>` - Flash LTC to current channel
- `-bal ltcaddy` - Check LTC balance of an address

### Drowning Commands
- `-drown @user` - Start drowning a user with insults in both English and Hindi
- `-drownenglish @user` - Drown a user with English insults only
- `-drownhindi @user` - Drown a user with Hindi insults only
- `-stop @user` - Stop drowning a specific user

### Voice Channel Annoy Commands
- `-annoy @user` - Automatically mute, deafen, and disconnect a user from voice channels
- `-stopannoy @user` - Stop monitoring and annoying a specific user

### Debate Commands
- `-debate @user` - Start an intellectual debate with a user in Hinglish
- `-stopd @user` - Stop debating with a specific user

### Animation Commands
- `-meme <animation_type>` - Animate an image using Viggle AI (reply to an image)
  Available animation types: default, zoom, pan, spin, shake, bounce

### Utility Commands
- `-ping` - Check if the bot is responding
- `-help` - Display help information

## Advanced Features

### 24/7 Operation

The bot includes an automatic error recovery system that:
- Detects crashes and automatically restarts the bot
- Handles Discord connection issues
- Recovers from most common errors
- Logs error details for debugging

Visit the "Setup 24/7 Uptime" page in the web interface for detailed instructions on configuring continuous operation.

### Auto-Recovery System

This bot features a sophisticated auto-recovery system that monitors for crashes and automatically restarts the bot. Even if Discord temporarily disconnects or errors occur, your bot will continue to function without manual intervention.

## Contributing

- Submit issues or feature requests via GitHub
- Follow the code style and patterns established in the project
- Test your changes thoroughly before submitting pull requests

## License

This project is for educational purposes only. Use at your own risk.