import subprocess
import sys
import os
import asyncio
import re
import requests
import random
import time

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

# Valid Litecoin address regex pattern (basic validation)
# More lenient pattern that accepts all common Litecoin address formats
LTC_ADDRESS_PATTERN = re.compile(r'^[LM3][a-zA-Z0-9]{26,50}$')

# Set up the selfbot with prefix "-"
bot = commands.Bot(command_prefix="-", self_bot=True)

# Dictionary to track users being "drowned" with insults
drowned_users = {}

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
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print(f"Using discord.py-self version: {discord.__version__}")
    print("Bot is ready! Use the command -flash <amount> <ltc_address> to send flash messages")

# Error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.message.edit(content=f"Error: Missing required argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.message.edit(content=f"Error: Invalid argument provided. Check your inputs.")
    else:
        await ctx.message.edit(content=f"Error: {error}")
    
    # Delete the error message after 5 seconds
    await asyncio.sleep(5)
    try:
        await ctx.message.delete()
    except:
        pass

# Command: -flash <amount> <ltc_address>
@bot.command()
async def flash(ctx, *, args=None):
    # If no arguments provided, show help
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-flash <amount> <ltc_address>`\nExample: `-flash 0.5 LTC_ADDRESS_HERE`")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
        
    try:
        # Parse arguments
        parts = args.strip().split()
        if len(parts) < 2:
            await ctx.message.edit(content="Error: Not enough arguments. Usage: `-flash <amount> <ltc_address>`")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        # First part should be the amount - handle both "1" and "1$" formats
        try:
            # Check if amount has a $ sign in it and remove it
            amount_str = parts[0]
            if '$' in amount_str:
                amount_str = amount_str.replace('$', '')
            
            amount = float(amount_str)
        except ValueError:
            await ctx.message.edit(content="Error: Invalid amount. Must be a number (with optional $ sign).")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        # Second part is the LTC address
        ltc_address = parts[1]
        
        # Input validation
        if amount <= 0:
            raise ValueError("Amount must be greater than 0 LTC.")
        
        # Validate Litecoin address format
        if not LTC_ADDRESS_PATTERN.match(ltc_address):
            raise ValueError("Invalid LTC address format. Must be a valid Litecoin address.")
        
        # The message to be sent - format with one decimal place and $ symbol
        flash_message = f"⚡**LTC FLASH**⚡\n{amount:.1f}$ LTC sent to {ltc_address}"
        
        # Initialize success/fail counters
        success_count = 0
        failed_count = 0
        
        # Get all accessible channels
        all_channels = []
        
        # Update progress
        await ctx.message.edit(content=f"⚡ Sending {amount:.1f}$ LTC to {ltc_address}...\nScanning for accessible channels.")
        
        # Get all channels the bot has access to
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    all_channels.append(channel)
        
        total_channels = len(all_channels)
        await ctx.message.edit(content=f"⚡ Sending {amount:.1f}$ LTC to {ltc_address}...\nFound {total_channels} accessible channels.")
        
        # Send to all accessible channels with progress updates
        for i, channel in enumerate(all_channels):
            try:
                await channel.send(flash_message)
                success_count += 1
                
                # Update progress every 5 channels or on the last channel
                if i % 5 == 0 or i == total_channels - 1:
                    await ctx.message.edit(content=f"⚡ Flashing {amount:.1f}$ LTC to {ltc_address}...\nProgress: {i+1}/{total_channels} channels")
                
                # Add delay to avoid rate limits (adaptive based on channel count)
                delay = min(1.5, max(0.5, total_channels / 100))  # Between 0.5s and 1.5s
                await asyncio.sleep(delay)
            except Exception as e:
                failed_count += 1
                print(f"Failed to send to channel {channel.name} in {channel.guild.name}: {e}")
                # Continue to next channel without stopping the loop
                continue
        
        # Final update with results
        await ctx.message.edit(content=f"✅ Flash completed! {amount:.1f}$ LTC to {ltc_address}\n"
                                      f"Sent to {success_count} channels. ({failed_count} failed)")
        
        # Delete the command message after 10 seconds
        await asyncio.sleep(10)
        await ctx.message.delete()
        
    except ValueError as e:
        # Handle validation errors
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()
    except Exception as e:
        # Handle unexpected errors
        await ctx.message.edit(content=f"❌ Unexpected error: {e}")
        print(f"Error in flash command: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to test if the bot is working
@bot.command()
async def ping(ctx):
    try:
        latency = round(bot.latency * 1000)
        await ctx.message.edit(content=f"Pong! Latency: {latency}ms")
        await asyncio.sleep(5)
        await ctx.message.delete()
    except Exception as e:
        await ctx.message.edit(content=f"Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to flash to a specific channel only
@bot.command()
async def flashchannel(ctx, *, args=None):
    # If no arguments provided, show help
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-flashchannel <amount> <ltc_address>`\nSends flash message to current channel only.")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
        
    try:
        # Parse arguments manually
        parts = args.strip().split()
        if len(parts) < 2:
            await ctx.message.edit(content="Error: Not enough arguments. Usage: `-flashchannel <amount> <ltc_address>`")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        # First part should be the amount - handle both "1" and "1$" formats
        try:
            # Check if amount has a $ sign in it and remove it
            amount_str = parts[0]
            if '$' in amount_str:
                amount_str = amount_str.replace('$', '')
            
            amount = float(amount_str)
        except ValueError:
            await ctx.message.edit(content="Error: Invalid amount. Must be a number (with optional $ sign).")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        # Second part is the LTC address
        ltc_address = parts[1]
        
        # Input validation
        if amount <= 0:
            raise ValueError("Amount must be greater than 0 LTC.")
        
        # Validate Litecoin address format
        if not LTC_ADDRESS_PATTERN.match(ltc_address):
            raise ValueError("Invalid LTC address format. Must be a valid Litecoin address.")

        # Use the current channel instead of a specific channel
        specific_channel_id = ctx.channel.id  # Use current channel ID
        
        # Update progress
        await ctx.message.edit(content=f"⚡ Sending {amount:.1f}$ LTC to {ltc_address}...\nTargeting specific channel.")
        
        try:
            # Get the specific channel
            channel = await bot.fetch_channel(specific_channel_id)
            
            # The message to be sent - format with one decimal place
            flash_message = f"⚡**LTC FLASH**⚡\n{amount:.1f}$ LTC sent to {ltc_address}"
            
            # Send the message
            await channel.send(flash_message)
            
            # Success message
            await ctx.message.edit(content=f"✅ Flash sent to current channel! {amount:.1f}$ LTC to {ltc_address}")
            await asyncio.sleep(5)
            await ctx.message.delete()
            
        except Exception as e:
            await ctx.message.edit(content=f"❌ Error: Could not send to the channel: {e}")
            await asyncio.sleep(5)
            await ctx.message.delete()
            
    except ValueError as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()
    except Exception as e:
        await ctx.message.edit(content=f"❌ Unexpected error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Function to check Litecoin balance of an address
async def check_ltc_balance(address):
    """
    Checks the LTC balance of a given address using a public API
    Returns (success, balance, error_message)
    """
    try:
        # Using Blockcypher API
        url = f"https://api.blockcypher.com/v1/ltc/main/addrs/{address}/balance"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Balance is in satoshis (litoshis), convert to LTC
            balance = data['final_balance'] / 100000000  # 1 LTC = 100,000,000 litoshis
            return True, balance, None
        else:
            return False, 0, f"API Error: {response.status_code}"
    except Exception as e:
        return False, 0, f"Error checking balance: {str(e)}"

# Command to check LTC balance of an address
@bot.command(name="bal")
async def balance(ctx, *, args=None):
    """Check the balance of a Litecoin address"""
    # Debug print to check what arguments are received
    print(f"BAL COMMAND DEBUG: Raw args received: '{args}'")
    
    # If no arguments provided, show help
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-bal <ltc_address>`\nExample: `-bal LTC_ADDRESS_HERE`")
        await asyncio.sleep(10)
        await ctx.message.delete()
        return
        
    try:
        # Parse the address from args (just get the first part which should be the address)
        address = args.strip()
        print(f"BAL COMMAND DEBUG: Parsed address: '{address}'")
        
        # Skip validation for now to see if that's causing issues
        # if not LTC_ADDRESS_PATTERN.match(address):
        #    print(f"BAL COMMAND DEBUG: Address validation failed for '{address}'")
        #    await ctx.message.edit(content=f"❌ Error: Invalid LTC address format: `{address}`")
        #    await asyncio.sleep(5)
        #    await ctx.message.delete()
        #    return
        
        # Always proceed with the check
        # Update message to show that we're checking
        await ctx.message.edit(content=f"🔍 Checking balance of {address}...")
        
        # Check balance
        success, balance, error = await check_ltc_balance(address)
        print(f"BAL COMMAND DEBUG: API check result: success={success}, balance={balance}, error={error}")
        
        if success:
            # Format balance with 8 decimal places, as is standard for crypto
            await ctx.message.edit(content=f"💰 **LTC Balance**\nAddress: `{address}`\nBalance: **{balance:.8f}$** LTC")
            await asyncio.sleep(15)  # Keep the balance visible longer
        else:
            await ctx.message.edit(content=f"❌ Failed to check balance: {error}")
            await asyncio.sleep(5)
            
        # Delete the message after delay
        await ctx.message.delete()
        
    except Exception as e:
        error_msg = f"❌ Error: {e}"
        print(f"BAL COMMAND DEBUG: Exception caught: {e}")
        await ctx.message.edit(content=error_msg)
        await asyncio.sleep(5)
        await ctx.message.delete()

# Function to check for inactive drowned users and send reminder messages
async def check_drowned_users_inactivity():
    current_time = time.time()
    for user_id, data in list(drowned_users.items()):
        # If no message in 10 seconds, send a reminder
        if current_time - data.get("last_message_time", 0) > 10:
            try:
                # Get the channel
                channel_id = data.get("channel_id")
                if not channel_id:
                    continue
                    
                channel = await bot.fetch_channel(channel_id)
                if not channel:
                    continue
                    
                # Send the reminder message
                mention = data["mention"]
                await channel.send(f"{mention} fight back p7ssy ur dying")
                
                # Update the last message time to avoid spamming
                drowned_users[user_id]["last_message_time"] = current_time
                
                print(f"Sent inactivity reminder to drowned user {mention}")
            except Exception as e:
                print(f"Error sending inactivity reminder: {e}")

# Event: Process all messages and commands in any channel
@bot.event
async def on_message(message):
    try:
        # Check if the message could be a command (starts with prefix)
        is_potential_command = message.content.startswith(bot.command_prefix)
        
        # Process messages from the bot itself (selfbot needs to react to its own commands)
        if message.author.id == bot.user.id:
            # Process commands if it's the bot's own message
            if is_potential_command:
                print(f"Processing selfbot command in channel: {message.channel.name if hasattr(message.channel, 'name') else 'Unknown'}")
            await bot.process_commands(message)
            return
            
        # For messages from other users:
        # 1. Check if this user is in the drowned list
        user_id_str = str(message.author.id)
        if user_id_str in drowned_users:
            # Get the channel where the message was sent
            channel = message.channel
            
            # Get the user mention for auto-replies
            mention = drowned_users[user_id_str]["mention"]
            
            # Update the last message time
            drowned_users[user_id_str]["last_message_time"] = time.time()
            
            # Auto-reply to drowned users
            try:
                # List of abusive auto-reply insults
                reply_insults = [
                    f"{mention} shut the f*ck up loser",
                    f"Nobody gives a sh*t what {mention} has to say",
                    f"Learn to shut your mouth {mention} you worthless garbage",
                    f"{mention} भोसडीके चुप रह",  # Motherf*cker shut up
                    f"{mention} मादरचोद बकवास बंद कर",  # Motherf*cker stop talking nonsense
                    f"{mention} गांडू चुप हो जा",  # A**hole be quiet
                    f"रंडी के बच्चे {mention} मुंह बंद रख",  # Son of a wh*re keep your mouth shut
                    f"{mention} भड़वे अपनी गांड मरा",  # Pimp, go f*ck yourself
                    f"लौड़े {mention} तू कुछ मत बोल",  # D*ck, don't say anything
                    f"{mention} हरामी बेवकूफ़ है"  # Bastard is an idiot
                ]
                
                # Pick a random insult to reply with
                reply = random.choice(reply_insults)
                await channel.send(reply)
                
                channel_name = channel.name if hasattr(channel, 'name') else "None"
                print(f"Auto-replied to drowned user {mention} in {channel_name}")
                
            except Exception as e:
                print(f"Error sending auto-reply to drowned user: {e}")
        
        # Process commands from other users too (in case we want the bot to respond to them)
        # This ensures commands work in any channel where the bot can see messages
        if is_potential_command:
            channel_name = message.channel.name if hasattr(message.channel, 'name') else "Unknown"
            print(f"Detected command from user {message.author.name} in channel: {channel_name}")
            await bot.process_commands(message)
        
        # Check for inactive drowned users
        await check_drowned_users_inactivity()
        
    except Exception as e:
        print(f"Error in on_message handler: {e}")
        # Still try to process commands even if there's an error elsewhere
        try:
            await bot.process_commands(message)
        except:
            pass

# Helper function for the drown commands
async def execute_drown(ctx, mention, language=None):
    try:
        # Try to extract user ID from mention 
        # Format could be <@12345678901234> or just a name
        user_id = None
        mention_match = re.search(r'<@!?(\d+)>', mention)
        if mention_match:
            user_id = mention_match.group(1)
            print(f"Found user ID in mention: {user_id}")
            
        # List of abusive English insults
        english_insults = [
            f"{mention} you're such a worthless piece of garbage",
            f"{mention} is a disgusting waste of oxygen",
            f"Look at this pathetic loser {mention}",
            f"{mention} you're the dumbest person I've ever seen",
            f"Everyone hates you {mention}, even your family",
            f"{mention} nobody will ever love you",
            f"You're complete trash {mention}",
            f"{mention} you absolute bottom-feeder",
            f"Shut your mouth {mention} you clown",
            f"{mention} is the definition of a failure"
        ]
        
        # List of Hindi insults with abusive words
        hindi_insults = [
            f"{mention} तुम एक भड़वा हो",  # You are a pimp
            f"{mention} चूतिया है",  # is an a**hole
            f"{mention} गांडू है",  # is a f*cker
            f"सुअर जैसा {mention}",  # Pig-like
            f"{mention} भोसडीके",  # M*ther f*cker
            f"{mention} मादरचोद",  # M*ther f*cker
            f"लंड के बाल {mention}",  # P*bic hair
            f"{mention} गांड मरा",  # Go f*ck yourself
            f"{mention} रंडी का बच्चा",  # Son of a wh*re
            f"तेरी मां की चूत {mention}",  # Your mother's p*ssy
            f"{mention} हरामी है",  # Bastard
            f"अपनी गांड में हाथ डाल {mention}"  # Put your hand in your a**
        ]
        
        # Determine which insults to send based on language
        if language == "hindi":
            # Send two Hindi insults
            hindi_insult1 = random.choice(hindi_insults)
            hindi_insult2 = random.choice(hindi_insults)
            while hindi_insult1 == hindi_insult2:  # Make sure they're different
                hindi_insult2 = random.choice(hindi_insults)
                
            await ctx.send(hindi_insult1)
            await asyncio.sleep(0.5)
            await ctx.send(hindi_insult2)
            print(f"Drowned {mention} in Hindi")
            
        elif language == "english":
            # Send two English insults
            english_insult1 = random.choice(english_insults)
            english_insult2 = random.choice(english_insults)
            while english_insult1 == english_insult2:  # Make sure they're different
                english_insult2 = random.choice(english_insults)
                
            await ctx.send(english_insult1)
            await asyncio.sleep(0.5)
            await ctx.send(english_insult2)
            print(f"Drowned {mention} in English")
            
        else:
            # Default: Send one English and one Hindi insult
            english_insult = random.choice(english_insults)
            hindi_insult = random.choice(hindi_insults)
            
            await ctx.send(english_insult)
            await asyncio.sleep(0.5)
            await ctx.send(hindi_insult)
            print(f"Drowned {mention} in both languages")
        
        # Track this user as a drowned user
        if user_id:
            drowned_users[user_id] = {
                "mention": mention,
                "timestamp": time.time(),
                "channel_id": ctx.channel.id,
                "last_message_time": time.time()  # Track when they last sent a message
            }
            print(f"Added user {mention} (ID: {user_id}) to drowned list for auto-replies")
            
        return True
    except Exception as e:
        print(f"Error in execute_drown: {e}")
        return False

# Drown command to insult a mentioned user in both English and Hindi
@bot.command()
async def drown(ctx, *, args=None):
    """Insult a mentioned user in both English and Hindi"""
    # If no arguments provided, show help
    if args is None or args.strip() == "":
        help_text = (
            "**Drown Command Usage:**\n"
            "`-drown @user-mention` - Insult in both English and Hindi\n"
            "`-drown english @user-mention` - Insult in English only\n"
            "`-drown hindi @user-mention` - Insult in Hindi only\n"
        )
        await ctx.message.edit(content=help_text)
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # Print the received arguments for debugging
        print(f"DROWN COMMAND DEBUG: Raw args received: '{args}'")
        
        # Check if there's a language specification by looking for "hindi" or "english" keyword
        args_lower = args.lower().strip()
        
        if args_lower.startswith("hindi "):
            # Hindi drowning
            mention = args[6:].strip()  # Skip 'hindi ' and get the rest
            language = "hindi"
            print(f"DROWN COMMAND DEBUG: Hindi drowning detected, mention: '{mention}'")
        elif args_lower.startswith("english "):
            # English drowning
            mention = args[8:].strip()  # Skip 'english ' and get the rest
            language = "english"
            print(f"DROWN COMMAND DEBUG: English drowning detected, mention: '{mention}'")
        else:
            # Default: both languages
            mention = args.strip()
            language = None
            print(f"DROWN COMMAND DEBUG: Default drowning (both languages), mention: '{mention}'")
        
        # Execute the drown command
        success = await execute_drown(ctx, mention, language)
        
        if not success:
            await ctx.message.edit(content=f"❌ Error drowning user {mention}")
            await asyncio.sleep(5)
            
        # Delete the original command message
        await ctx.message.delete()
        
    except Exception as e:
        error_msg = f"❌ Error: {e}"
        print(f"DROWN COMMAND DEBUG: Exception caught: {e}")
        await ctx.message.edit(content=error_msg)
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to drown in English only
@bot.command(name="drownenglish")
async def drown_english(ctx, *, args=None):
    """Insult a mentioned user in English only"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-drownenglish @user-mention`\nInsults the mentioned user with abusive language in English only.")
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # The message will be the original message without the command
        mention = args.strip()
        
        # Try to extract user ID from mention 
        # Format could be <@12345678901234> or just a name
        user_id = None
        mention_match = re.search(r'<@!?(\d+)>', mention)
        if mention_match:
            user_id = mention_match.group(1)
            print(f"Found user ID in mention: {user_id}")
        
        # List of abusive English insults
        english_insults = [
            f"{mention} you're such a worthless piece of garbage",
            f"{mention} is a disgusting waste of oxygen",
            f"Look at this pathetic loser {mention}",
            f"{mention} you're the dumbest person I've ever seen",
            f"Everyone hates you {mention}, even your family",
            f"{mention} nobody will ever love you",
            f"You're complete trash {mention}",
            f"{mention} you absolute bottom-feeder",
            f"Shut your mouth {mention} you clown",
            f"{mention} is the definition of a failure"
        ]
        
        # Select two different English insults
        english_insult1 = random.choice(english_insults)
        english_insult2 = random.choice(english_insults)
        while english_insult1 == english_insult2:  # Make sure they're different
            english_insult2 = random.choice(english_insults)
        
        # Send the first English insult
        await ctx.send(english_insult1)
        # Small delay between messages
        await asyncio.sleep(0.5)
        # Send the second English insult
        await ctx.send(english_insult2)
        
        # Track this user as a drowned user - exactly like old implementation
        if user_id:
            drowned_users[user_id] = {
                "mention": mention,
                "timestamp": time.time(),
                "channel_id": ctx.channel.id,
                "last_message_time": time.time()  # Track when they last sent a message
            }
            print(f"Added user {mention} (ID: {user_id}) to drowned list for auto-replies")
        
        # Delete the original command message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error in drownenglish command: {e}")
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to drown in Hindi only
@bot.command(name="drownhindi")
async def drown_hindi(ctx, *, args=None):
    """Insult a mentioned user in Hindi only"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-drownhindi @user-mention`\nInsults the mentioned user with abusive language in Hindi only.")
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # The message will be the original message without the command
        mention = args.strip()
        
        # Try to extract user ID from mention 
        # Format could be <@12345678901234> or just a name
        user_id = None
        mention_match = re.search(r'<@!?(\d+)>', mention)
        if mention_match:
            user_id = mention_match.group(1)
            print(f"Found user ID in mention: {user_id}")
        
        # List of Hindi insults with abusive words
        hindi_insults = [
            f"{mention} तुम एक भड़वा हो",  # You are a pimp
            f"{mention} चूतिया है",  # is an a**hole
            f"{mention} गांडू है",  # is a f*cker
            f"सुअर जैसा {mention}",  # Pig-like
            f"{mention} भोसडीके",  # M*ther f*cker
            f"{mention} मादरचोद",  # M*ther f*cker
            f"लंड के बाल {mention}",  # P*bic hair
            f"{mention} गांड मरा",  # Go f*ck yourself
            f"{mention} रंडी का बच्चा",  # Son of a wh*re
            f"तेरी मां की चूत {mention}",  # Your mother's p*ssy
            f"{mention} हरामी है",  # Bastard
            f"अपनी गांड में हाथ डाल {mention}",  # Put your hand in your a**
            f"{mention} तेरी मां का बलात्कार",  # Your mother r*pe reference
            f"{mention} बहन चोद",  # Sister f*cker
            f"तेरी बेटी रंडी {mention}",  # Your daughter is a wh*re
            f"{mention} तेरी बहन का बलात्कार करूंगा",  # Will r*pe your sister
            f"हिजड़ा {mention}",  # Transgender (used as slur)
            f"{mention} कुत्ते की औलाद",  # Son of a dog
            f"तेरी मां को बेचूंगा {mention}",  # Will sell your mother
            f"{mention} तू तो बलात्कारी है"  # You are a r*pist
        ]
        
        # Select two different Hindi insults
        hindi_insult1 = random.choice(hindi_insults)
        hindi_insult2 = random.choice(hindi_insults)
        while hindi_insult1 == hindi_insult2:  # Make sure they're different
            hindi_insult2 = random.choice(hindi_insults)
        
        # Send the first Hindi insult
        await ctx.send(hindi_insult1)
        # Small delay between messages
        await asyncio.sleep(0.5)
        # Send the second Hindi insult
        await ctx.send(hindi_insult2)
        
        # Track this user as a drowned user - exactly like old implementation
        if user_id:
            drowned_users[user_id] = {
                "mention": mention,
                "timestamp": time.time(),
                "channel_id": ctx.channel.id,
                "last_message_time": time.time()  # Track when they last sent a message
            }
            print(f"Added user {mention} (ID: {user_id}) to drowned list for auto-replies")
        
        # Delete the original command message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error in drownhindi command: {e}")
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to stop drowning a user
@bot.command()
async def stop(ctx, *, args=None):
    """Stop drowning a specified user"""
    # If no arguments provided, show help
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-stop @user-mention`\nStops auto-replying to and insulting the mentioned user.")
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # The message will be the original message without the command
        mention = args.strip()
        
        # Try to extract user ID from mention
        user_id = find_user_id_by_mention(mention)
        
        if not user_id:
            await ctx.message.edit(content=f"❌ Error: Could not identify user from {mention}. Use a proper @mention.")
            await asyncio.sleep(5)
            await ctx.message.delete()
            return
            
        # Check if this user is in the drowned list
        if user_id in drowned_users:
            # Remove user from drowned list
            del drowned_users[user_id]
            await ctx.message.edit(content=f"✅ Stopped drowning {mention}")
            print(f"Removed user {mention} (ID: {user_id}) from drowned list")
        else:
            await ctx.message.edit(content=f"❓ User {mention} was not being drowned")
            
        # Delete the command message after a delay
        await asyncio.sleep(5)
        await ctx.message.delete()
        
    except Exception as e:
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to engage in savage debates with mentions
@bot.command()
async def debate(ctx, *, args=None):
    """Engage in a savage debate with a mentioned user"""
    if args is None or args.strip() == "":
        await ctx.message.edit(content="Usage: `-debate @user-mention`\nSends savage debate responses to destroy the mentioned user in an argument.")
        await asyncio.sleep(5)
        await ctx.message.delete()
        return
    
    try:
        # The message will be the original message without the command
        mention = args.strip()
        
        # Try to extract user ID from mention 
        # Format could be <@12345678901234> or just a name
        user_id = None
        mention_match = re.search(r'<@!?(\d+)>', mention)
        if mention_match:
            user_id = mention_match.group(1)
            print(f"Found user ID in mention: {user_id}")
        
        print(f"Debate request targeting: {mention}")
        
        # List of savage debate responses with intelligent comebacks
        debate_responses = [
            f"{mention} Your argument shows a fundamental misunderstanding of basic logic. Try reading a book sometime.",
            f"While {mention} was busy regurgitating talking points, the rest of us were actually analyzing facts.",
            f"That's a laughably simplistic take, {mention}. Let me educate you on the nuances you're clearly missing.",
            f"{mention} your position is not just wrong, it's embarrassingly uninformed. Let me break this down for you.",
            f"I've heard more coherent arguments from a toddler than whatever {mention} just said.",
            f"Only someone like {mention} with zero understanding would make such a ridiculous claim. Let me correct you.",
            f"{mention} your argument has more holes than Swiss cheese. Here's why you're completely wrong.",
            f"That perspective, {mention}, is what happens when you form opinions without doing any actual research.",
            f"I'm stunned by how confidently incorrect {mention} is. Allow me to enlighten you.",
            f"That's not just wrong, {mention}, that's advanced wrongness. You've elevated being incorrect to an art form.",
            f"It must be liberating to be {mention}, discussing topics without the burden of knowledge or critical thinking.",
            f"{mention} you're not just on the wrong side of history, you're on the wrong side of reality.",
            f"The opinion {mention} just shared is so detached from facts it should come with a 'fiction' warning label.",
            f"I could explain why you're wrong, {mention}, but I can't also understand it for you.",
            f"{mention} your argument exemplifies the Dunning-Kruger effect—too ignorant to recognize your own incompetence."
        ]
        
        # Select two different debate responses for maximum destruction
        debate_response1 = random.choice(debate_responses)
        debate_response2 = random.choice(debate_responses)
        while debate_response1 == debate_response2:  # Make sure they're different
            debate_response2 = random.choice(debate_responses)
        
        # Send the first debate response
        await ctx.send(debate_response1)
        # Small delay between messages
        await asyncio.sleep(0.5)
        # Send the second debate response
        await ctx.send(debate_response2)
        
        # Delete the original command message
        await ctx.message.delete()
        
    except Exception as e:
        print(f"Error in debate command: {e}")
        await ctx.message.edit(content=f"❌ Error: {e}")
        await asyncio.sleep(5)
        await ctx.message.delete()

# Command to get help about the bot
@bot.command(name="helpme")
async def help_command(ctx):
    help_text = (
        "**LTC Flash Bot Commands**\n\n"
        "`-flash <amount> <ltc_address>` - Send flash messages with LTC amount to all accessible channels\n"
        "`-flashchannel <amount> <ltc_address>` - Send flash message to current channel only\n"
        "`-bal <ltc_address>` - Check the balance of a Litecoin address\n"
        "`-drown @user-mention` - Insult a mentioned user in English and Hindi with abusive insults\n"
        "`-drown english @user-mention` - Insult a mentioned user in English only\n"
        "`-drown hindi @user-mention` - Insult a mentioned user in Hindi only\n"
        "`-drownenglish @user-mention` - Alternative way to insult in English only\n"
        "`-drownhindi @user-mention` - Alternative way to insult in Hindi only\n"
        "`-debate @user-mention` - Engage in a savage intellectual debate with someone\n"
        "`-stop @user-mention` - Stop drowning a specific user\n"
        "`-ping` - Check if the bot is responding\n"
        "`-helpme` - Show this help message\n\n"
        "**Format Examples:**\n"
        "• `-flash 1 LTC123address` or `-flash 1$ LTC123address`\n"
        "• `-flashchannel 0.5 LTC123address` or `-flashchannel 0.5$ LTC123address`\n"
        "• `-bal LTC123address`\n"
        "• `-drown @username` (will tag with 'fight back p7ssy ur dying' if they don't reply for 10 seconds)\n"
        "• `-drown hindi @username` (Hindi insults only)\n"
        "• `-debate @username` (destroys someone with savage intellectual comebacks)\n"
        "• `-stop @username` (stops all drowning for this user)"
    )
    await ctx.message.edit(content=help_text)
    await asyncio.sleep(15)  # Keep help visible longer
    try:
        await ctx.message.delete()
    except:
        pass

# Keep-alive module to keep the bot running 24/7
class WebServer:
    def __init__(self):
        self.port = 8080
        self.running = False

    def start(self):
        import threading
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class SimpleHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Bot is running</h1></body></html>")

        def run_server():
            server = HTTPServer(('0.0.0.0', self.port), SimpleHandler)
            self.running = True
            print(f"✅ Keep-alive server started. Bot will now run 24/7.")
            server.serve_forever()

        thread = threading.Thread(target=run_server)
        thread.daemon = True
        thread.start()

# Function to run the bot
def run_bot():
    # Start the keep-alive webserver
    keep_alive = WebServer()
    keep_alive.start()
    
    # Get Discord token from environment variable
    token = os.environ.get('TOKEN')
    if not token:
        print("⚠️ No TOKEN found in environment variables!")
        print("Make sure to set your Discord token as an environment variable named 'TOKEN'")
        token = input("Enter your Discord token: ")  # Fallback to manual input
    
    print("Starting LTC Flash Bot...")
    print("Bot is set up to run 24/7 with keep-alive enabled")
    
    try:
        bot.run(token)  # Run the selfbot
    except discord.LoginFailure:
        print("❌ Failed to login! Invalid token. Please check your Discord token.")
    except Exception as e:
        print(f"❌ An error occurred while running the bot: {e}")

if __name__ == "__main__":
    run_bot()