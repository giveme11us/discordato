#!/usr/bin/env python3
"""
Command Registration Script

This script manually registers and syncs slash commands with Discord.
It provides a more user-friendly interface than sync_commands.py.
"""

import os
import sys
import requests
import json
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

# Commands to register
COMMANDS = [
    {
        "name": "ping",
        "description": "Check if the bot is responsive and view latency"
    },
    {
        "name": "hi",
        "description": "Get a friendly greeting from the bot"
    },
    {
        "name": "number",
        "description": "Generate a random number within a specified range",
        "options": [
            {
                "name": "min_value",
                "description": "The minimum value (default: 1)",
                "type": 4,  # INTEGER
                "required": False
            },
            {
                "name": "max_value",
                "description": "The maximum value (default: 100)",
                "type": 4,  # INTEGER
                "required": False
            }
        ]
    },
    {
        "name": "pinger-config",
        "description": "Configure the pinger feature",
        "options": [
            {
                "name": "setting",
                "description": "The setting to view or modify (channel, whitelist, everyone, here)",
                "type": 3,  # STRING
                "required": False
            },
            {
                "name": "value",
                "description": "The new value for the setting",
                "type": 3,  # STRING
                "required": False
            }
        ]
    }
]

def register_commands_to_guild(guild_id):
    """Register commands to a specific guild using PUT to overwrite all commands at once"""
    url = f"https://discord.com/api/v10/applications/{APP_ID}/guilds/{guild_id}/commands"
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"Registering commands to guild {guild_id}...")
    
    # First, delete all existing commands
    print(f"Clearing existing commands from guild {guild_id}...")
    try:
        # This is the key change - use PUT to overwrite all commands at once
        response = requests.put(url, headers=headers, json=[])
        if response.status_code == 200:
            print("  ✅ Successfully cleared existing commands")
        else:
            print(f"  ⚠️ Could not clear commands: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ⚠️ Error clearing commands: {str(e)}")
    
    # Then, register all commands at once with PUT
    try:
        response = requests.put(url, headers=headers, json=COMMANDS)
        
        if response.status_code == 200:
            print(f"  ✅ Successfully registered all commands")
            for command in response.json():
                print(f"    - {command['name']}")
        else:
            print(f"  ❌ Failed to register commands: {response.status_code} {response.text}")
            
            # Fall back to registering one by one if bulk registration fails
            print("  ⚠️ Falling back to individual command registration...")
            for command in COMMANDS:
                response = requests.post(url, headers=headers, json=command)
                
                if response.status_code in (200, 201):
                    print(f"    ✅ Registered command: {command['name']}")
                else:
                    print(f"    ❌ Failed to register command {command['name']}: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ❌ Error registering commands: {str(e)}")

def register_commands_globally():
    """Register commands globally using PUT to overwrite all commands at once"""
    url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
    
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("Registering commands globally...")
    
    # First, attempt to clear existing commands
    print("Clearing existing global commands...")
    try:
        response = requests.put(url, headers=headers, json=[])
        if response.status_code == 200:
            print("  ✅ Successfully cleared existing commands")
        else:
            print(f"  ⚠️ Could not clear commands: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ⚠️ Error clearing commands: {str(e)}")
    
    # Then, register all commands at once with PUT
    try:
        response = requests.put(url, headers=headers, json=COMMANDS)
        
        if response.status_code == 200:
            print(f"  ✅ Successfully registered all commands")
            for command in response.json():
                print(f"    - {command['name']}")
        else:
            print(f"  ❌ Failed to register commands: {response.status_code} {response.text}")
            
            # Fall back to registering one by one
            print("  ⚠️ Falling back to individual command registration...")
            for command in COMMANDS:
                response = requests.post(url, headers=headers, json=command)
                
                if response.status_code in (200, 201):
                    print(f"    ✅ Registered command: {command['name']}")
                else:
                    print(f"    ❌ Failed to register command {command['name']}: {response.status_code} {response.text}")
    except Exception as e:
        print(f"  ❌ Error registering commands: {str(e)}")

def main():
    print(f"Using Application ID: {APP_ID}")
    
    if GUILD_IDS:
        for guild_id in GUILD_IDS:
            register_commands_to_guild(guild_id)
    else:
        register_commands_globally()
    
    print("Command registration complete.")
    print("Note: It may take a few minutes for commands to appear in Discord.")

if __name__ == "__main__":
    main() 