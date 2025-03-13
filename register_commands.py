#!/usr/bin/env python3
"""
Register Commands

This script uses the Discord HTTP API to register slash commands.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Discord token and application ID
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
APPLICATION_ID = os.getenv('APPLICATION_ID')

# Get guild IDs
GUILD_IDS_STR = os.getenv('GUILD_IDS', '')
GUILD_IDS = [id for id in GUILD_IDS_STR.split(',') if id]

# Define headers for API requests
headers = {
    'Authorization': f'Bot {TOKEN}',
    'Content-Type': 'application/json'
}

# Define commands to register
commands = [
    {
        'name': 'ping',
        'description': 'Check if the bot is responsive and view latency',
        'type': 1  # CHAT_INPUT
    },
    {
        'name': 'hi',
        'description': 'Get a friendly greeting from the bot',
        'type': 1  # CHAT_INPUT
    },
    {
        'name': 'number',
        'description': 'Generate a random number within a specified range',
        'type': 1,  # CHAT_INPUT
        'options': [
            {
                'name': 'min_value',
                'description': 'The minimum value (default: 1)',
                'type': 4,  # INTEGER
                'required': False
            },
            {
                'name': 'max_value',
                'description': 'The maximum value (default: 100)',
                'type': 4,  # INTEGER
                'required': False
            }
        ]
    }
]

def register_commands_to_guild(guild_id):
    """
    Register commands to a specific guild.
    
    Args:
        guild_id (str): The guild ID to register commands to
    """
    url = f'https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{guild_id}/commands'
    
    print(f"Registering commands to guild {guild_id}...")
    
    # Register each command
    for command in commands:
        response = requests.post(url, headers=headers, json=command)
        
        if response.status_code in (200, 201):
            print(f"  ✅ Registered command: {command['name']}")
        else:
            print(f"  ❌ Failed to register command {command['name']}: {response.status_code}")
            print(f"     Response: {response.text}")

def register_commands_globally():
    """
    Register commands globally.
    """
    url = f'https://discord.com/api/v10/applications/{APPLICATION_ID}/commands'
    
    print("Registering commands globally...")
    
    # Register each command
    for command in commands:
        response = requests.post(url, headers=headers, json=command)
        
        if response.status_code in (200, 201):
            print(f"  ✅ Registered command: {command['name']}")
        else:
            print(f"  ❌ Failed to register command {command['name']}: {response.status_code}")
            print(f"     Response: {response.text}")

def main():
    """
    Main function.
    """
    if not TOKEN:
        print("Error: No Discord token found. Set DISCORD_BOT_TOKEN in .env file.")
        return
    
    if not APPLICATION_ID:
        print("Error: No Application ID found. Set APPLICATION_ID in .env file.")
        return
    
    print(f"Using Application ID: {APPLICATION_ID}")
    
    # Register commands to guilds
    if GUILD_IDS:
        for guild_id in GUILD_IDS:
            register_commands_to_guild(guild_id)
    else:
        # Register commands globally
        register_commands_globally()
    
    print("Command registration complete.")

if __name__ == "__main__":
    main() 