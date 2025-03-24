"""
Redeye Profile Command

Command for viewing and managing profiles from the profiles.csv file.
"""

import os
import csv
import discord
from discord import app_commands
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from utils.permissions import redeye_only
from config.features.redeye_config import redeye as redeye_config
from config.features.embed_config import embed as embed_config
from typing import Optional, List, Set
from discord.ext import commands
from .account_gen import generate_accounts, create_accounts_file  # Import account generation functions

# Set up debug logging
logger = logging.getLogger('discord_bot.modules.redeye.profile_cmd')
logger.setLevel(logging.DEBUG)

class RedeyePermissionError(app_commands.CheckFailure):
    """Custom error for Redeye permission failures."""
    pass

def apply_embed_settings(embed: discord.Embed) -> discord.Embed:
    """Apply global embed settings to an embed."""
    # Handle color value that could be either string or int
    color_value = embed_config.EMBED_COLOR
    if isinstance(color_value, str):
        color_value = int(color_value, 16)
    embed.color = discord.Color(color_value)
    
    embed.set_footer(text=embed_config.FOOTER_TEXT, icon_url=embed_config.FOOTER_ICON_URL)
    embed.set_thumbnail(url=embed_config.THUMBNAIL_URL)
    if embed_config.INCLUDE_TIMESTAMP:
        embed.timestamp = discord.utils.utcnow()
    return embed

def get_user_profiles(user_id: str) -> List[dict]:
    """Get all profiles for a user."""
    profiles = []
    try:
        if os.path.exists(redeye_config.PROFILES_PATH):
            with open(redeye_config.PROFILES_PATH, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Check if the profile belongs to the user
                    if row['Name'].startswith(user_id):
                        profiles.append(row)
    except Exception as e:
        logger.error(f"Error reading profiles: {e}", exc_info=True)
    
    return sorted(profiles, key=lambda x: int(x['Name'].split('_')[1]) if '_' in x['Name'] else 0)

def has_redeye_permission():
    """Check if user has permission to use Redeye commands."""
    async def predicate(interaction: discord.Interaction) -> bool:
        try:
            logger.debug(f"=== Permission Check Start ===")
            logger.debug(f"User ID: {interaction.user.id}")
            
            # Get whitelisted role IDs from environment
            whitelisted_roles = os.getenv('REDEYE_WHITELIST_ROLE_IDS', '').split(',')
            whitelisted_roles = [int(role_id) for role_id in whitelisted_roles if role_id]
            logger.debug(f"Whitelisted Role IDs: {whitelisted_roles}")
            
            # Check if we're in a guild
            if not interaction.guild:
                logger.debug("Not in a guild context")
                raise RedeyePermissionError("This command can only be used in a server.")

            # Check if the user is a member
            if not isinstance(interaction.user, discord.Member):
                logger.debug("User is not a Member instance")
                raise RedeyePermissionError("Could not verify user permissions.")
            
            try:
                # Get fresh member data
                logger.debug("Fetching fresh member data...")
                member = await interaction.guild.fetch_member(interaction.user.id)
                logger.debug(f"Member fetched: {member.id}")
                
                # Get member's roles
                member_roles = member.roles
                role_ids = [r.id for r in member_roles]
                logger.debug(f"Member roles: {role_ids}")
                
                # Check if user has any of the whitelisted roles
                has_role = any(role_id in whitelisted_roles for role_id in role_ids)
                logger.debug(f"Has whitelisted role: {has_role}")
                
                if not has_role:
                    role_names = []
                    for role_id in whitelisted_roles:
                        role = discord.utils.get(interaction.guild.roles, id=role_id)
                        if role:
                            role_names.append(role.name)
                    role_list = " or ".join(role_names)
                    raise RedeyePermissionError(f"You need the {role_list} role to use Redeye module commands.")
                
                logger.debug("=== Permission Check Success ===")
                return True
                
            except discord.NotFound:
                logger.debug("Member not found")
                raise RedeyePermissionError("Could not verify user permissions. Please try again.")
            except Exception as e:
                if isinstance(e, RedeyePermissionError):
                    raise
                logger.error(f"Error fetching fresh data: {e}", exc_info=True)
                raise RedeyePermissionError("An error occurred while checking permissions.")
            
        except Exception as e:
            if isinstance(e, RedeyePermissionError):
                raise
            logger.error(f"Error checking Redeye permissions: {e}", exc_info=True)
            logger.debug("=== Permission Check Error ===")
            raise RedeyePermissionError("An error occurred while checking permissions.")
    
    return app_commands.check(predicate)

# Add error handler for the commands
async def handle_permission_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle permission check errors."""
    if isinstance(error, RedeyePermissionError):
        if not interaction.response.is_done():
            embed = discord.Embed(
                title="❌ Permission Required",
                description=str(error),
                color=discord.Color.red()
            )
            embed = apply_embed_settings(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return True
    return False

class ProfileModal(discord.ui.Modal, title='Add Profile'):
    """Modal for adding a new profile."""
    
    webhook = discord.ui.TextInput(
        label='Webhook URL',
        placeholder='Enter your webhook URL',
        required=True,
    )
    
    size_lower = discord.ui.TextInput(
        label='Size Lower Bound',
        placeholder='Enter lower bound (e.g. 8)',
        required=True,
    )
    
    size_upper = discord.ui.TextInput(
        label='Size Upper Bound',
        placeholder='Enter upper bound (e.g. 12)',
        required=True,
    )
    
    email = discord.ui.TextInput(
        label='Email',
        placeholder='Enter your email',
        required=True,
    )
    
    password = discord.ui.TextInput(
        label='Password',
        placeholder='Enter your password',
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Handle form submission."""
        try:
            # Validate size bounds
            try:
                lower = float(self.size_lower.value)
                upper = float(self.size_upper.value)
                if lower >= upper:
                    raise ValueError("Lower bound must be less than upper bound")
            except ValueError as e:
                await interaction.response.send_message(
                    f"❌ Invalid size range: {str(e)}",
                    ephemeral=True
                )
                return

            # Get existing profiles to determine the next profile number
            user_id = str(interaction.user.id)
            existing_profiles = get_user_profiles(user_id)
            profile_number = len(existing_profiles) + 1
            profile_name = f"{user_id}_{profile_number}"

            # Create profile data in the correct order:
            # Name,Webhook,SizeLowerBound,SizeUpperBound,Multiplier,Email,Password,IsPaypal
            profile_data = {
                'Name': profile_name,
                'Webhook': self.webhook.value,
                'SizeLowerBound': str(lower),
                'SizeUpperBound': str(upper),
                'Multiplier': '1',
                'Email': self.email.value,
                'Password': self.password.value,
                'IsPaypal': 'true'
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(redeye_config.PROFILES_PATH), exist_ok=True)

            # Write to CSV
            file_exists = os.path.exists(redeye_config.PROFILES_PATH)
            fieldnames = ['Name', 'Webhook', 'SizeLowerBound', 'SizeUpperBound', 'Multiplier', 'Email', 'Password', 'IsPaypal']
            
            if not file_exists:
                # Create new file with headers
                with open(redeye_config.PROFILES_PATH, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(profile_data)
            else:
                # Read existing content to check if we need a newline
                with open(redeye_config.PROFILES_PATH, 'r') as f:
                    content = f.read()
                
                # Append to file, adding newline only if the file doesn't end with one
                with open(redeye_config.PROFILES_PATH, 'a', newline='') as f:
                    if content and not content.endswith('\n'):
                        f.write('\n')
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(profile_data)

            embed = discord.Embed(title="✅ Profile Added Successfully")
            embed = apply_embed_settings(embed)
            embed.description = f"Profile #{profile_number} created for {interaction.user.mention}"
            embed.add_field(
                name="Size Range",
                value=f"{lower} - {upper}",
                inline=True
            )
            embed.add_field(
                name="Email",
                value=self.email.value,
                inline=True
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error adding profile: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ An error occurred while adding your profile.",
                ephemeral=True
            )

def remove_profile(user_id: str, profile_number: int) -> bool:
    """
    Remove a profile from the CSV file.
    
    Args:
        user_id: The user's ID
        profile_number: The profile number to remove
    
    Returns:
        bool: True if profile was removed successfully
    """
    try:
        if not os.path.exists(redeye_config.PROFILES_PATH):
            return False
            
        # Read all profiles
        profiles = []
        with open(redeye_config.PROFILES_PATH, 'r', newline='') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                profiles.append(row)
        
        # Get user's profiles
        user_profiles = [p for p in profiles if p['Name'].startswith(user_id)]
        if not user_profiles or profile_number > len(user_profiles):
            return False
            
        # Find the profile to remove
        profile_to_remove = user_profiles[profile_number - 1]
        profiles.remove(profile_to_remove)
        
        # Write back all profiles except the removed one
        with open(redeye_config.PROFILES_PATH, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(profiles)
            
        return True
    except Exception as e:
        logger.error(f"Error removing profile: {e}", exc_info=True)
        return False

async def setup_profile_cmd(bot, registered_commands=None):
    """
    Set up the redeye profile commands.
    
    Args:
        bot: The Discord bot to add the command to
        registered_commands: Optional set of registered commands
    """
    logger.info("Setting up redeye profile commands")
    
    # Create the command group
    redeye = app_commands.Group(name='redeye', description='Redeye module commands')
    
    @redeye.command(name="profile-view")
    @app_commands.describe(
        profile_number="Optional: Profile number to view (1, 2, 3, etc.)"
    )
    @has_redeye_permission()
    async def view_profiles(
        interaction: discord.Interaction,
        profile_number: Optional[int] = None
    ):
        """View profiles from the Redeye profiles.csv file."""
        try:
            user_id = str(interaction.user.id)
            user_profiles = get_user_profiles(user_id)
            
            if not user_profiles:
                embed = discord.Embed(title="No Profile Found")
                embed = apply_embed_settings(embed)
                embed.description = "You don't have any profiles set up yet."
                embed.add_field(
                    name="Add a Profile",
                    value="Use `/redeye profile-add` to create your profile.",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # If only one profile or specific profile requested, show detailed view
            if len(user_profiles) == 1 or profile_number:
                if profile_number:
                    if profile_number < 1 or profile_number > len(user_profiles):
                        await interaction.response.send_message(
                            f"❌ Profile #{profile_number} not found. You have {len(user_profiles)} profile(s).",
                            ephemeral=True
                        )
                        return
                    profile = user_profiles[profile_number - 1]
                else:
                    profile = user_profiles[0]

                embed = discord.Embed(title=f"Profile #{profile['Name'].split('_')[1] if '_' in profile['Name'] else '1'}")
                embed = apply_embed_settings(embed)
                embed.add_field(
                    name="Size Range",
                    value=f"{profile['SizeLowerBound']} - {profile['SizeUpperBound']}",
                    inline=True
                )
                embed.add_field(
                    name="Email",
                    value=profile['Email'],
                    inline=True
                )
                embed.add_field(
                    name="Password",
                    value=f"||{profile['Password']}||",
                    inline=True
                )
                embed.add_field(
                    name="Webhook",
                    value=profile['Webhook'],
                    inline=False
                )
            else:
                # Show profile list
                embed = discord.Embed(title="Your Profiles")
                embed = apply_embed_settings(embed)
                embed.description = f"Found {len(user_profiles)} profiles. Use `/redeye profile-view profile_number:X` to view details."
                for i, profile in enumerate(user_profiles, 1):
                    embed.add_field(
                        name=f"Profile #{i}",
                        value=f"Size: {profile['SizeLowerBound']} - {profile['SizeUpperBound']}\nEmail: {profile['Email']}",
                        inline=False
                    )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error viewing profile: {e}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while viewing profiles.",
                    ephemeral=True
                )
    
    @redeye.command(name="profile-add")
    @has_redeye_permission()
    async def add_profile(interaction: discord.Interaction):
        """Add a new profile to the Redeye profiles.csv file."""
        try:
            modal = ProfileModal()
            await interaction.response.send_modal(modal)
        except Exception as e:
            logger.error(f"Error showing profile modal: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ An error occurred while opening the profile form.",
                ephemeral=True
            )
    
    @redeye.command(name="profile-remove")
    @app_commands.describe(
        profile_number="The profile number to remove (1, 2, 3, etc.)"
    )
    @has_redeye_permission()
    async def remove_profile_cmd(
        interaction: discord.Interaction,
        profile_number: Optional[int] = None
    ):
        """Remove a profile from your profiles list."""
        try:
            user_id = str(interaction.user.id)
            user_profiles = get_user_profiles(user_id)
            
            if not user_profiles:
                embed = discord.Embed(title="No Profiles Found")
                embed = apply_embed_settings(embed)
                embed.description = "You don't have any profiles to remove."
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # If user has only one profile, remove it without asking for a number
            if len(user_profiles) == 1:
                profile_number = 1
            
            # If user has multiple profiles but didn't specify which one
            if profile_number is None:
                embed = discord.Embed(title="Multiple Profiles Found")
                embed = apply_embed_settings(embed)
                embed.description = "Please specify which profile to remove using the profile number."
                for i, profile in enumerate(user_profiles, 1):
                    embed.add_field(
                        name=f"Profile #{i}",
                        value=f"Size: {profile['SizeLowerBound']} - {profile['SizeUpperBound']}\nEmail: {profile['Email']}",
                        inline=False
                    )
                embed.add_field(
                    name="Usage",
                    value="Use `/redeye profile-remove profile_number:X` to remove a specific profile.",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Validate profile number
            if profile_number < 1 or profile_number > len(user_profiles):
                await interaction.response.send_message(
                    f"❌ Profile #{profile_number} not found. You have {len(user_profiles)} profile(s).",
                    ephemeral=True
                )
                return
            
            # Remove the profile
            profile = user_profiles[profile_number - 1]
            if remove_profile(user_id, profile_number):
                embed = discord.Embed(title="✅ Profile Removed")
                embed = apply_embed_settings(embed)
                embed.description = f"Successfully removed Profile #{profile_number}"
                embed.add_field(
                    name="Profile Details",
                    value=f"Size: {profile['SizeLowerBound']} - {profile['SizeUpperBound']}\nEmail: {profile['Email']}",
                    inline=False
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(
                    "❌ An error occurred while removing the profile.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Error removing profile: {e}", exc_info=True)
            await interaction.response.send_message(
                "❌ An error occurred while removing the profile.",
                ephemeral=True
            )
    
    @redeye.command(name="account-gen")
    @app_commands.describe(
        storename="The name of the store to generate accounts for (e.g. luisaviaroma)",
        catchall="The catchall domain for email generation (e.g. @example.com)",
        quantity="The number of accounts to generate (1-50)"
    )
    @has_redeye_permission()
    async def account_gen(
        interaction: discord.Interaction,
        storename: str,
        catchall: str,
        quantity: app_commands.Range[int, 1, 50]
    ):
        """Generate accounts for a specific store."""
        try:
            # Validate catchall format
            if not catchall.startswith("@"):
                await interaction.response.send_message(
                    "❌ Catchall must start with @ (e.g. @example.com)",
                    ephemeral=True
                )
                return

            # Send initial response
            await interaction.response.defer(ephemeral=True)
            
            # Generate accounts
            accounts = await generate_accounts(storename, catchall, quantity)
            
            if not accounts:
                await interaction.followup.send(
                    f"❌ Failed to generate accounts for {storename}. Please check the store name and try again.",
                    ephemeral=True
                )
                return
            
            # Create accounts file
            accounts_file = create_accounts_file(accounts)
            
            # Send response with file
            embed = discord.Embed(
                title="✅ Account Generation Complete",
                description=f"Successfully generated {len(accounts)} accounts for {storename}",
                color=discord.Color.green()
            )
            embed = apply_embed_settings(embed)
            
            await interaction.followup.send(
                embed=embed,
                file=accounts_file,
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in account generation: {e}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred while generating accounts.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ An error occurred while generating accounts.",
                    ephemeral=True
                )
    
    # Add error handlers for the commands
    @view_profiles.error
    async def view_profiles_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if not await handle_permission_error(interaction, error):
            # Only propagate the error if we didn't handle it
            raise error
    
    @add_profile.error
    async def add_profile_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if not await handle_permission_error(interaction, error):
            raise error
    
    @remove_profile_cmd.error
    async def remove_profile_cmd_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if not await handle_permission_error(interaction, error):
            raise error
    
    @account_gen.error
    async def account_gen_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if not await handle_permission_error(interaction, error):
            raise error
    
    # Add the command group to the bot
    await bot.tree.sync()
    bot.tree.add_command(redeye)
    
    logger.info("Successfully set up redeye profile commands")
    
    # Return registered_commands if provided
    return registered_commands if registered_commands is not None else set()

@app_commands.command(name="profile-view")
@has_redeye_permission()
async def handle_profile_view(
    interaction: discord.Interaction,
    profile_number: Optional[int] = None
):
    """
    View profiles command.
    
    Args:
        interaction: The Discord interaction
        profile_number: Optional profile number to view specific profile
    """
    try:
        user_profiles = get_user_profiles(str(interaction.user.id))
        
        if not user_profiles:
            embed = discord.Embed(title="No Profile Found")
            embed = apply_embed_settings(embed)
            embed.description = "You don't have any profiles set up yet."
            embed.add_field(
                name="Add a Profile",
                value="Use `/redeye profile-add` to create your profile.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if profile_number:
            # Show specific profile
            if profile_number < 1 or profile_number > len(user_profiles):
                await interaction.response.send_message(
                    f"❌ Profile #{profile_number} not found. You have {len(user_profiles)} profile(s).",
                    ephemeral=True
                )
                return
            profile = user_profiles[profile_number - 1]

            embed = discord.Embed(title=f"Profile #{profile['Name'].split('_')[1] if '_' in profile['Name'] else '1'}")
            embed = apply_embed_settings(embed)
            embed.add_field(
                name="Size Range",
                value=f"{profile['SizeLowerBound']} - {profile['SizeUpperBound']}",
                inline=True
            )
            embed.add_field(
                name="Email",
                value=profile['Email'],
                inline=True
            )
            embed.add_field(
                name="Password",
                value=f"||{profile['Password']}||",
                inline=True
            )
            embed.add_field(
                name="Webhook",
                value=profile['Webhook'],
                inline=False
            )
        else:
            # Show all profiles
            embed = discord.Embed(title="Your Profiles")
            embed = apply_embed_settings(embed)
            embed.description = f"Found {len(user_profiles)} profiles. Use `/redeye profile-view profile_number:X` to view details."
            for i, profile in enumerate(user_profiles, 1):
                embed.add_field(
                    name=f"Profile #{i}",
                    value=f"Size: {profile['SizeLowerBound']} - {profile['SizeUpperBound']}\nEmail: {profile['Email']}",
                    inline=False
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Error viewing profile: {e}", exc_info=True)
        await interaction.response.send_message(
            "❌ An error occurred while viewing profiles.",
            ephemeral=True
        )

@app_commands.command(name="profile-add")
@has_redeye_permission()
async def handle_profile_add(interaction: discord.Interaction):
    """Add profile command."""
    try:
        modal = ProfileModal()
        await interaction.response.send_modal(modal)
    except Exception as e:
        logger.error(f"Error showing profile modal: {e}", exc_info=True)
        await interaction.response.send_message(
            "❌ An error occurred while opening the profile form.",
            ephemeral=True
        ) 