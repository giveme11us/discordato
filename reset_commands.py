#!/usr/bin/env python3
"""
Command Reset Script

This script completely removes all slash commands from Discord.
Use it when you need to reset your bot's commands.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Application ID
APP_ID = os.getenv('APPLICATION_ID')
if not APP_ID:
    print("ERROR: No application ID found. Set APPLICATION_ID in your .env file.")
    sys.exit(1)

# Get Bot Token
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not BOT_TOKEN:
    print("ERROR: No bot token found. Set DISCORD_BOT_TOKEN in your .env file.")
    sys.exit(1)

# Get Guild IDs
guild_ids_str = os.getenv('GUILD_IDS', '')
GUILD_IDS = [id.strip() for id in guild_ids_str.split(',') if id.strip()]

def reset_guild_commands(guild_id):
    """Reset all commands for a specific guild"""
    url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{guild_id}/commands"
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"Resetting commands for guild {guild_id}...")
    
    try:
        response = requests.put(url, headers=headers, json=[])
        
        if response.status_code == 200:
            print(f"  ✅ Successfully reset all commands for guild {guild_id}")
        else:
            print(f"  ❌ Failed to reset commands: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ❌ Error resetting commands: {str(e)}")

def reset_global_commands():
    """Reset all global commands"""
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("Resetting global commands...")
    
    try:
        response = requests.put(url, headers=headers, json=[])
        
        if response.status_code == 200:
            print("  ✅ Successfully reset all global commands")
        else:
            print(f"  ❌ Failed to reset commands: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ❌ Error resetting commands: {str(e)}")

def main():
    print(f"Using Application ID: {APP_ID}")
    
    # Ask for confirmation
    confirm = input("⚠️  WARNING: This will delete ALL commands. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    # Reset guild commands
    if GUILD_IDS:
        for guild_id in GUILD_IDS:
            reset_guild_commands(guild_id)
    
    # Also reset global commands
    reset_global_commands()
    
    print("\nCommand reset complete.")
    print("Note: It may take a few minutes for changes to appear in Discord.")

if __name__ == "__main__":
    main() 