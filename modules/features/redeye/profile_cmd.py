"""
Redeye Profile Command

Command for viewing profiles from the profiles.csv file.
"""

import os
import csv
import discord
from discord import app_commands
import logging
from utils.permissions import redeye_only
from config.features.redeye_config import redeye as redeye_config
from config.features.embed_config import embed as embed_config

logger = logging.getLogger('discord_bot.modules.redeye.profile_cmd')

async def handle_profile_view(interaction, profile_name=None):
    """
    Handle the profile view command.
    
    Args:
        interaction: The Discord interaction
        profile_name: Optional name of a specific profile to view
    """
    profiles_path = redeye_config.PROFILES_PATH
    
    # Check if profiles file exists
    if not os.path.exists(profiles_path):
        await interaction.response.send_message(
            f"❌ Profiles file not found at: `{profiles_path}`", 
            ephemeral=True
        )
        return
    
    try:
        # Read profiles from CSV
        profiles = []
        with open(profiles_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                profiles.append(row)
        
        if not profiles:
            await interaction.response.send_message(
                "❌ No profiles found in the profiles file.",
                ephemeral=True
            )
            return
        
        # If profile_name is specified, filter to just that profile
        if profile_name:
            profiles = [p for p in profiles if p.get('Name', '').lower() == profile_name.lower()]
            if not profiles:
                await interaction.response.send_message(
                    f"❌ Profile '{profile_name}' not found.",
                    ephemeral=True
                )
                return
        
        # Create embed for the profile(s)
        if profile_name and profiles:
            # Single profile view
            profile = profiles[0]
            embed = create_profile_embed(profile)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # List all profiles
            embed = discord.Embed(
                title="Redeye Profiles",
                description=f"Found {len(profiles)} profiles in total."
            )
            
            # Apply styling from embed_config
            embed = embed_config.apply_default_styling(embed)
            
            # Add each profile as a field
            for i, profile in enumerate(profiles):
                name = profile.get('Name', 'Unnamed')
                field_value = f"**Profile Name:** {name}"
                
                embed.add_field(
                    name=f"{i+1}. {name}",
                    value=field_value,
                    inline=True
                )
            
            # Add usage instructions as a field instead of footer
            embed.add_field(
                name="Examples",
                value="Use `/redeye-profiles profile_name:Test` to view full details of a specific profile.",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        logger.error(f"Error reading profiles file: {str(e)}")
        await interaction.response.send_message(
            f"❌ Error reading profiles: {str(e)}",
            ephemeral=True
        )

def create_profile_embed(profile):
    """
    Create an embed for a single profile.
    
    Args:
        profile: Profile data dictionary
    
    Returns:
        discord.Embed: The created embed
    """
    name = profile.get('Name', 'Unnamed')
    
    embed = discord.Embed(
        title=f"Profile: {name}",
        description="Detailed profile information"
    )
    
    # Apply styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Webhook
    embed.add_field(
        name="Webhook",
        value=f"`{profile.get('Webhook', 'None')}`",
        inline=False
    )
    
    # Personal information
    personal_info = (
        f"**Name:** {profile.get('FirstName', 'N/A')} {profile.get('LastName', 'N/A')}\n"
        f"**Phone:** {profile.get('Phone', 'N/A')}\n"
        f"**Address:** {profile.get('Address', 'N/A')}\n"
        f"**City:** {profile.get('City', 'N/A')}\n"
        f"**Zip:** {profile.get('ZipCode', 'N/A')}\n"
        f"**State:** {profile.get('StateId', 'N/A')}\n"
        f"**Country:** {profile.get('CountryId', 'N/A')}\n"
        f"**Fiscal Code:** {profile.get('CodFisc', 'N/A')}"
    )
    embed.add_field(
        name="Personal Information",
        value=personal_info,
        inline=False
    )
    
    return embed

def setup_profile_cmd(bot):
    """
    Set up the redeye-profiles command.
    
    Args:
        bot: The Discord bot to add the command to
    """
    logger.info("Setting up redeye-profiles command")
    
    @bot.tree.command(
        name="redeye-profiles",
        description="View profiles from the Redeye profiles.csv file"
    )
    @app_commands.describe(
        profile_name="Optional: Name of a specific profile to view"
    )
    @redeye_only()
    async def redeye_profiles(
        interaction: discord.Interaction,
        profile_name: str = None
    ):
        """
        View profiles from the Redeye profiles.csv file.
        
        Args:
            interaction: The Discord interaction
            profile_name: Optional name of a specific profile to view
        """
        await handle_profile_view(interaction, profile_name)
    
    logger.info("Successfully set up redeye-profiles command") 