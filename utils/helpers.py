"""
Helper Utilities

This module provides common helper functions for the Discord bot.
"""

import re
import discord
from discord.ext import commands
from config.features.embed_config import embed as embed_config

def is_admin(ctx):
    """
    Check if a user has administrator permissions.
    
    Args:
        ctx: The command context
    
    Returns:
        bool: True if the user is an administrator, False otherwise
    """
    return ctx.author.guild_permissions.administrator

def is_moderator(ctx):
    """
    Check if a user has moderator permissions.
    
    Args:
        ctx: The command context
    
    Returns:
        bool: True if the user is a moderator, False otherwise
    """
    # Check for specific permissions that moderators typically have
    return (ctx.author.guild_permissions.manage_messages or
            ctx.author.guild_permissions.kick_members or
            ctx.author.guild_permissions.ban_members)

def format_time(seconds):
    """
    Format a time in seconds to a human-readable string.
    
    Args:
        seconds (int): The time in seconds
    
    Returns:
        str: A formatted time string
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    time_parts = []
    if days > 0:
        time_parts.append(f"{days}d")
    if hours > 0:
        time_parts.append(f"{hours}h")
    if minutes > 0:
        time_parts.append(f"{minutes}m")
    if seconds > 0 or not time_parts:
        time_parts.append(f"{seconds}s")
    
    return " ".join(time_parts)

def clean_text(text):
    """
    Clean text by removing mentions, links, and excessive whitespace.
    
    Args:
        text (str): The text to clean
    
    Returns:
        str: The cleaned text
    """
    # Remove mentions
    text = re.sub(r'<@!?\d+>', '[MENTION]', text)
    
    # Remove links
    text = re.sub(r'https?://\S+', '[LINK]', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

async def send_error_embed(interaction, error_message, title="Error", ephemeral=True):
    """
    Send a consistently styled error embed as an interaction response.
    
    Args:
        interaction (discord.Interaction): The interaction to respond to
        error_message (str): The error message to display
        title (str, optional): The title of the error embed. Defaults to "Error".
        ephemeral (bool, optional): Whether the response should be ephemeral. Defaults to True.
        
    Returns:
        bool: True if the error message was sent successfully, False otherwise
    """
    # Create an error embed with consistent styling
    embed = discord.Embed(
        title=title,
        description=error_message,
        color=discord.Color.red()
    )
    
    # Apply default styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    # Try to respond with the error message
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger('discord_bot.utils.helpers')
        logger.error(f"Failed to send error response: {e}")
        return False

def create_embed(title, description=None, color=discord.Color.blue(), fields=None, footer=None, thumbnail=None):
    """
    Create a Discord embed.
    
    Args:
        title (str): The title of the embed
        description (str, optional): The description of the embed. Defaults to None.
        color (discord.Color, optional): The color of the embed. Defaults to discord.Color.blue().
        fields (list, optional): A list of field tuples (name, value, inline). Defaults to None.
        footer (str, optional): The footer text. Defaults to None.
        thumbnail (str, optional): The thumbnail URL. Defaults to None.
    
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(title=title, description=description, color=color)
    
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    
    if footer:
        embed.set_footer(text=footer)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    # Apply default styling from embed_config
    embed = embed_config.apply_default_styling(embed)
    
    return embed 