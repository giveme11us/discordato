#!/usr/bin/env python3
"""
Script to fix indentation issues in the link_reaction.py file.
"""
import sys
import re

def fix_indentation(input_file, output_file):
    print(f"Reading from {input_file}")
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Fix common indentation errors
    
    # Fix process_message function - only add link reaction section
    content = content.replace(
        """    # Only add link reaction if the message contains embeds or links from supported stores
        if not has_supported_store_embed:
        logger.debug(f"Skipping link reaction - no content from supported stores found")
            return
        
        # For webhook/app messages or whitelisted users with supported store embeds:
    logger.info(f"Adding link reaction to message with supported store content")
        
        # Check if this message is also in a category that gets the forward reaction
        # If so, wait 3 seconds to make sure the forward reaction is added first
    # Access CATEGORY_IDS as a property, not a function
    forward_category_ids = forward_config.settings_manager.get("CATEGORY_IDS", [])
    is_forward_category = hasattr(message.channel, 'category_id') and message.channel.category_id in forward_category_ids
        should_delay = False
        
    # Also get ENABLED as a property
    forward_enabled = forward_config.settings_manager.get("ENABLED", False)""",
        """    # Only add link reaction if the message contains embeds or links from supported stores
    if not has_supported_store_embed:
        logger.debug(f"Skipping link reaction - no content from supported stores found")
        return
    
    # For webhook/app messages or whitelisted users with supported store embeds:
    logger.info(f"Adding link reaction to message with supported store content")
    
    # Check if this message is also in a category that gets the forward reaction
    # If so, wait 3 seconds to make sure the forward reaction is added first
    # Access CATEGORY_IDS as a property, not a function
    forward_category_ids = forward_config.settings_manager.get("CATEGORY_IDS", [])
    is_forward_category = hasattr(message.channel, 'category_id') and message.channel.category_id in forward_category_ids
    should_delay = False
    
    # Also get ENABLED as a property
    forward_enabled = forward_config.settings_manager.get("ENABLED", False)""")
    
    # Fix indentation in if enabled
    content = content.replace(
        """    if is_forward_category and forward_enabled:
            # This message will also get a forward reaction
            # from the reaction_forward module, so add delay
            logger.debug(f"Message will also get forward reaction, adding delay before link reaction")
            should_delay = True
        
        try:
            # Add the delay if needed
            if should_delay:
                await asyncio.sleep(3)
                
            # Add the link emoji reaction
        link_emoji = config.settings_manager.get("LINK_EMOJI", "🔗")
        await message.add_reaction(link_emoji)
            if message.webhook_id:
                logger.info(f"Added link reaction to webhook message in {message.channel.name}")
            elif message.application_id:
                logger.info(f"Added link reaction to app message in {message.channel.name}")
            else:
                logger.info(f"Added link reaction to message from {message.author} in {message.channel.name}")
        except Exception as e:
            logger.error(f"Failed to add reaction: {str(e)}")""",
        """    if is_forward_category and forward_enabled:
        # This message will also get a forward reaction
        # from the reaction_forward module, so add delay
        logger.debug(f"Message will also get forward reaction, adding delay before link reaction")
        should_delay = True
    
    try:
        # Add the delay if needed
        if should_delay:
            await asyncio.sleep(3)
            
        # Add the link emoji reaction
        link_emoji = config.settings_manager.get("LINK_EMOJI", "🔗")
        await message.add_reaction(link_emoji)
        if message.webhook_id:
            logger.info(f"Added link reaction to webhook message in {message.channel.name}")
        elif message.application_id:
            logger.info(f"Added link reaction to app message in {message.channel.name}")
        else:
            logger.info(f"Added link reaction to message from {message.author} in {message.channel.name}")
    except Exception as e:
        logger.error(f"Failed to add reaction: {str(e)}")""")
    
    # Fix indentation in process_luisaviaroma_embed function
    content = content.replace(
        """        # Extract PID from URL or PID field
                pid_value = None
        
        # Try URL extraction first
        if embed.url:
            logger.info(f"Trying URL extraction for LuisaViaRoma")
            # Extract from URL pattern
                        url_parts = embed.url.split('/')
                        if url_parts and len(url_parts) > 1:
                            potential_pid = url_parts[-1]
                # Check if it matches LuisaViaRoma PID format (usually has hyphens)
                if '-' in potential_pid:
                                pid_value = potential_pid
                    logger.info(f"Extracted product ID from URL: {pid_value}")""",
        """        # Extract PID from URL or PID field
        pid_value = None
        
        # Try URL extraction first
        if embed.url:
            logger.info(f"Trying URL extraction for LuisaViaRoma")
            # Extract from URL pattern
            url_parts = embed.url.split('/')
            if url_parts and len(url_parts) > 1:
                potential_pid = url_parts[-1]
                # Check if it matches LuisaViaRoma PID format (usually has hyphens)
                if '-' in potential_pid:
                    pid_value = potential_pid
                    logger.info(f"Extracted product ID from URL: {pid_value}")""")
    
    # Fix more indentation in process_luisaviaroma_embed
    content = content.replace(
        """        # If URL extraction didn't work, try the PID field
        if not pid_value:
                    for field in embed.fields:
                        if field.name.upper() == "PID":
                            raw_value = field.value
                            pid_value = raw_value.replace("```", "").strip()
                            logger.info(f"Found PID in field: {pid_value}")
                            break
                
        # If we found a PID, save it to the configured file path
                if pid_value:
            # Get file path from store config - use the user-set path
            store_file_path = store_config.get('file_path')
                    
                    if store_file_path:
                logger.info(f"Using file path from store configuration: {store_file_path}")
                        try:
                            # Check if file exists and if PID is already in the file
                            existing_pids = set()
                            needs_newline = False
                            file_empty = True
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(os.path.abspath(store_file_path)), exist_ok=True)""",
        """        # If URL extraction didn't work, try the PID field
        if not pid_value:
            for field in embed.fields:
                if field.name.upper() == "PID":
                    raw_value = field.value
                    pid_value = raw_value.replace("```", "").strip()
                    logger.info(f"Found PID in field: {pid_value}")
                    break
        
        # If we found a PID, save it to the configured file path
        if pid_value:
            # Get file path from store config - use the user-set path
            store_file_path = store_config.get('file_path')
            
            if store_file_path:
                logger.info(f"Using file path from store configuration: {store_file_path}")
                try:
                    # Check if file exists and if PID is already in the file
                    existing_pids = set()
                    needs_newline = False
                    file_empty = True
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(os.path.abspath(store_file_path)), exist_ok=True)""")
    
    # Fix the rest of process_luisaviaroma_embed
    content = content.replace(
        """                            if os.path.exists(store_file_path) and os.path.getsize(store_file_path) > 0:
                                with open(store_file_path, "r") as f:
                                    # Read all existing PIDs
                                    existing_content = f.read()
                                    existing_pids = {line.strip() for line in existing_content.splitlines() if line.strip()}
                                    
                                    # Check if file ends with newline
                                    needs_newline = not existing_content.endswith('\n')
                                    file_empty = not existing_content.strip()
                                    
                                    logger.debug(f"Found {len(existing_pids)} existing PIDs in file")
                            
                            # Check if PID already exists in the file
                            if pid_value in existing_pids:
                                logger.info(f"PID {pid_value} already exists in file, skipping")
                        await message.channel.send(f"ℹ️ Product ID `{pid_value}` already exists in {store_config.get('name', 'LUISAVIAROMA')} tracking list.")
                                return
                            
                            # Append the PID to the file
                            with open(store_file_path, "a") as f:
                                if needs_newline:
                                    f.write(f"\\n{pid_value}\\n")
                                    logger.info(f"Added newline before writing PID")
                                elif file_empty:
                                    f.write(f"{pid_value}\\n")
                                else:
                                    f.write(f"{pid_value}\\n")
                            
                            logger.info(f"Successfully added PID {pid_value} to {store_file_path}")
                            
                            # Send confirmation response
                    await message.channel.send(f"✅ Added product ID `{pid_value}` to {store_config.get('name', 'LUISAVIAROMA')} tracking list.")
                        except Exception as e:
                            logger.error(f"Failed to write PID to file: {str(e)}")
                            await message.channel.send(f"❌ Error saving product ID: {str(e)}")
                    else:
                logger.error(f"No file path configured for {store_config.get('name', 'LUISAVIAROMA')}")
                await message.channel.send(f"❌ Error: {store_config.get('name', 'LUISAVIAROMA')} file path not configured.")
                else:
            logger.warning(f"No product ID found in this {store_config.get('name', 'LUISAVIAROMA')} embed")
            await message.channel.send(f"❌ No product ID found in this {store_config.get('name', 'LUISAVIAROMA')} embed.")""",
        """                    if os.path.exists(store_file_path) and os.path.getsize(store_file_path) > 0:
                        with open(store_file_path, "r") as f:
                            # Read all existing PIDs
                            existing_content = f.read()
                            existing_pids = {line.strip() for line in existing_content.splitlines() if line.strip()}
                            
                            # Check if file ends with newline
                            needs_newline = not existing_content.endswith('\\n')
                            file_empty = not existing_content.strip()
                            
                            logger.debug(f"Found {len(existing_pids)} existing PIDs in file")
                    
                    # Check if PID already exists in the file
                    if pid_value in existing_pids:
                        logger.info(f"PID {pid_value} already exists in file, skipping")
                        await message.channel.send(f"ℹ️ Product ID `{pid_value}` already exists in {store_config.get('name', 'LUISAVIAROMA')} tracking list.")
                        return
                    
                    # Append the PID to the file
                    with open(store_file_path, "a") as f:
                        if needs_newline:
                            f.write(f"\\n{pid_value}\\n")
                            logger.info(f"Added newline before writing PID")
                        elif file_empty:
                            f.write(f"{pid_value}\\n")
                        else:
                            f.write(f"{pid_value}\\n")
                    
                    logger.info(f"Successfully added PID {pid_value} to {store_file_path}")
                    
                    # Send confirmation response
                    await message.channel.send(f"✅ Added product ID `{pid_value}` to {store_config.get('name', 'LUISAVIAROMA')} tracking list.")
                except Exception as e:
                    logger.error(f"Failed to write PID to file: {str(e)}")
                    await message.channel.send(f"❌ Error saving product ID: {str(e)}")
            else:
                logger.error(f"No file path configured for {store_config.get('name', 'LUISAVIAROMA')}")
                await message.channel.send(f"❌ Error: {store_config.get('name', 'LUISAVIAROMA')} file path not configured.")
        else:
            logger.warning(f"No product ID found in this {store_config.get('name', 'LUISAVIAROMA')} embed")
            await message.channel.send(f"❌ No product ID found in this {store_config.get('name', 'LUISAVIAROMA')} embed.")""")
    
    print(f"Writing fixed content to {output_file}")
    with open(output_file, 'w') as f:
        f.write(content)
    
    print("Done!")

if __name__ == "__main__":
    input_file = "modules/mod/link_reaction/link_reaction.py"
    output_file = "modules/mod/link_reaction/link_reaction.py.fixed"
    
    fix_indentation(input_file, output_file) 