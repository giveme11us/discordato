"""
path: modules/redeye/__init__.py
purpose: Handles redeye profile and task management with secure storage
critical:
- Manages redeye profiles
- Handles task configuration
- Provides profile commands
- Validates all inputs
- Securely stores sensitive data
"""

import os
import csv
import json
import logging
from typing import Dict, List, Optional
import discord
from discord.ext import commands
from core.validation import InputValidator
from core.error_handler import ValidationError
from core.secure_storage import secure_storage

logger = logging.getLogger('discord_bot.redeye')

# Configuration
PROFILES_FILE = 'data/redeye/profiles.csv'
TASKS_FILE = 'data/redeye/tasks.csv'

# Sensitive fields that should be stored securely
SENSITIVE_FIELDS = {
    'Webhook',
    'UpstreamProxyURL',
    'UpstreamAkmaiCookieURL',
    'Phone',
    'Address',
    'ZipCode',
    'CodFisc'
}

def load_profiles() -> List[Dict[str, str]]:
    """
    Load profiles from CSV file and secure storage.
    
    Returns:
        List[Dict[str, str]]: List of profile dictionaries
    """
    profiles = []
    try:
        # Load base profiles from CSV
        with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            profiles = list(reader)
            
        # Load sensitive data from secure storage
        secure_data = secure_storage.get('profiles', {})
        
        # Validate each profile and merge with secure data
        validated_profiles = []
        for profile in profiles:
            try:
                # Merge with secure data
                profile_id = profile['Name']
                if profile_id in secure_data:
                    for field in SENSITIVE_FIELDS:
                        if field in secure_data[profile_id]:
                            profile[field] = secure_data[profile_id][field]
                
                # Validate complete profile
                validated = InputValidator.validate_profile(profile)
                validated_profiles.append(validated)
            except ValidationError as e:
                logger.warning(f"Invalid profile data: {e}")
                continue
                
        return validated_profiles
    except Exception as e:
        logger.error(f"Error loading profiles: {e}", exc_info=True)
        return []

def save_profile(profile: Dict[str, str]) -> bool:
    """
    Save a profile to CSV and secure storage.
    
    Args:
        profile: The profile data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate profile data
        validated_profile = InputValidator.validate_profile(profile)
        
        # Separate sensitive data
        secure_data = {field: validated_profile[field] for field in SENSITIVE_FIELDS}
        public_profile = {k: v for k, v in validated_profile.items() if k not in SENSITIVE_FIELDS}
        
        # Load existing profiles from CSV
        profiles = []
        fieldnames = []
        try:
            with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                profiles = list(reader)
        except FileNotFoundError:
            fieldnames = list(public_profile.keys())
            
        # Update existing profile or add new one in CSV
        profile_updated = False
        for i, existing in enumerate(profiles):
            if existing['Name'] == public_profile['Name']:
                profiles[i] = public_profile
                profile_updated = True
                break
                
        if not profile_updated:
            profiles.append(public_profile)
            
        # Write public data to CSV
        with open(PROFILES_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(profiles)
            
        # Save sensitive data to secure storage
        stored_data = secure_storage.get('profiles', {})
        stored_data[validated_profile['Name']] = secure_data
        secure_storage.set('profiles', stored_data)
            
        return True
    except Exception as e:
        logger.error(f"Error saving profile: {e}", exc_info=True)
        return False

async def setup(bot, registered_commands=None):
    """
    Set up the redeye module.
    
    Args:
        bot: The Discord bot instance
        registered_commands: Set of already registered commands
        
    Returns:
        Set[str]: Updated set of registered commands
    """
    # Initialize registered_commands if not provided
    if registered_commands is None:
        registered_commands = set()
        
    # Register redeye-profiles command if not already registered
    if 'redeye-profiles' not in registered_commands:
        @bot.tree.command(
            name="redeye-profiles",
            description="View your redeye profiles"
        )
        async def redeye_profiles(interaction: discord.Interaction):
            """View your redeye profiles."""
            try:
                profiles = load_profiles()
                if not profiles:
                    await interaction.response.send_message(
                        "No profiles found.",
                        ephemeral=True
                    )
                    return
                
                # Filter profiles to only show those matching the user's ID
                user_profiles = [p for p in profiles if p['Name'] == str(interaction.user.id)]
                
                if not user_profiles:
                    await interaction.response.send_message(
                        "You don't have any profiles.",
                        ephemeral=True
                    )
                    return
                    
                # Create embed for profiles
                embed = discord.Embed(
                    title="Your Redeye Profiles",
                    description=f"Found {len(user_profiles)} profile(s) for {interaction.user.mention}",
                    color=int(os.getenv('EMBED_COLOR', '00ff1f'), 16)
                )
                
                # Add profiles to embed
                for profile in user_profiles:
                    # Personal Information
                    personal_info = (
                        f"**Name:** {profile['FirstName']} {profile['LastName']}\n"
                        f"**Phone:** {profile['Phone']}\n"
                        f"**Address:** {profile['Address']}\n"
                        f"**City:** {profile['City']}, {profile['StateId']} {profile['ZipCode']}\n"
                        f"**Country:** {profile['CountryId']}\n"
                        f"**Fiscal Code:** {profile.get('CodFisc', 'N/A')}"
                    )
                    
                    # Timing Settings
                    timing_info = (
                        f"**Timeout:** {profile['TimeoutLowerBound']} - {profile['TimeoutUpperBound']}ms\n"
                        f"**Delay:** {profile['DelayLowerBound']} - {profile['DelayUpperBound']}ms\n"
                        f"**Keep Alive:** {profile['KeepConnectionsAlive']}"
                    )
                    
                    # Connection Settings
                    connection_info = (
                        f"**Webhook:** `{profile['Webhook']}`\n"
                        f"**Proxy URL:** `{profile.get('UpstreamProxyURL', 'N/A')}`\n"
                        f"**Akamai Cookie URL:** `{profile.get('UpstreamAkmaiCookieURL', 'N/A')}`"
                    )
                    
                    # Add fields to embed
                    embed.add_field(
                        name=f"Profile Details",
                        value="**Personal Information:**\n" + personal_info + "\n\n" +
                              "**Timing Settings:**\n" + timing_info + "\n\n" +
                              "**Connection Settings:**\n" + connection_info,
                        inline=False
                    )
                    
                await interaction.response.send_message(
                    embed=embed,
                    ephemeral=True
                )
                
            except Exception as e:
                logger.error(f"Error displaying profiles: {e}", exc_info=True)
                await interaction.response.send_message(
                    "An error occurred while loading profiles.",
                    ephemeral=True
                )
                
        registered_commands.add('redeye-profiles')
        logger.info("Registered command: redeye-profiles")
        
    return registered_commands

async def teardown(bot):
    """Clean up the redeye module."""
    pass

def load_tasks() -> List[Dict[str, str]]:
    """
    Load tasks from CSV file.
    
    Returns:
        List[Dict[str, str]]: List of task dictionaries
    """
    tasks = []
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tasks = list(reader)
    except Exception as e:
        logger.error(f"Error loading tasks: {e}", exc_info=True)
    return tasks
