"""
Helper Utilities

This module provides common helper functions for the Discord bot.
"""

import re
import discord
from discord.ext import commands

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
    
    return embed 