#!/usr/bin/env python3
"""
Script to fix indentation issues in the link_reaction.py file with regular expressions.
"""
import re
import sys

def fix_indentation(filepath):
    print(f"Reading file: {filepath}")
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace duplicate "Create directory if it doesn't exist" comment
    content = re.sub(
        r'(\s+)# Create directory if it doesn\'t exist\s+# Check if file exists and if PID is already in the file',
        r'\1# Check if file exists and if PID is already in the file',
        content
    )
    
    # Fix broken original_message_handler line
    content = re.sub(
        r'original_message_handler = bot\.event_handlers\.get\(\'on_message\', None\) if hasattr\(bot, \'event_handlers\'\) \nelse None',
        r'original_message_handler = bot.event_handlers.get(\'on_message\', None) if hasattr(bot, \'event_handlers\') else None',
        content
    )
    
    # Fix indentation for the os.makedirs line and below
    content = re.sub(
        r'(\s+)# Create directory if it doesn\'t exist\s+os\.makedirs\(.*\)\s+(\s+)if os\.path\.exists',
        r'\1# Create directory if it doesn\'t exist\n\1os.makedirs(os.path.dirname(os.path.abspath(store_file_path)), exist_ok=True)\n\1\n\1if os.path.exists',
        content
    )
    
    # Fix indentation for all the file checking section
    pattern = r'(\s+)if os\.path\.exists\(store_file_path\) and os\.path\.getsize\(store_file_path\) > 0:'
    matches = re.findall(pattern, content)
    if matches:
        base_indent = matches[0]
        
        # Fix the indentation in this section
        content = re.sub(
            r'(\s+)if os\.path\.exists\(store_file_path\) and os\.path\.getsize\(store_file_path\) > 0:[\s\n]+with open\(store_file_path, "r"\) as f:[\s\n]+# Read all existing PIDs[\s\n]+existing_content = f\.read\(\)[\s\n]+existing_pids = \{.*?\}[\s\n]+[\s\n]+# Check if file ends with newline[\s\n]+needs_newline = not existing_content\.endswith\(\'\\n\'\)[\s\n]+file_empty = not existing_content\.strip\(\)[\s\n]+[\s\n]+logger\.debug\(f"Found \{len\(existing_pids\)\} existing PIDs in file"\)',
            f'{base_indent}if os.path.exists(store_file_path) and os.path.getsize(store_file_path) > 0:\n{base_indent}    with open(store_file_path, "r") as f:\n{base_indent}        # Read all existing PIDs\n{base_indent}        existing_content = f.read()\n{base_indent}        existing_pids = {{line.strip() for line in existing_content.splitlines() if line.strip()}}\n{base_indent}        \n{base_indent}        # Check if file ends with newline\n{base_indent}        needs_newline = not existing_content.endswith(\'\\n\')\n{base_indent}        file_empty = not existing_content.strip()\n{base_indent}        \n{base_indent}        logger.debug(f"Found {{len(existing_pids)}} existing PIDs in file")',
            content
        )
    
    # Fix indentation for the "Check if PID already exists" section
    content = re.sub(
        r'(\s+)# Check if PID already exists in the file\s+if pid_value in existing_pids:[\s\n]+logger\.info\(f"PID \{pid_value\} already exists in file, skipping"\)[\s\n]+await message\.channel\.send\(.*?\)[\s\n]+return',
        r'\1# Check if PID already exists in the file\n\1if pid_value in existing_pids:\n\1    logger.info(f"PID {pid_value} already exists in file, skipping")\n\1    await message.channel.send(f"ℹ️ Product ID `{pid_value}` already exists in {store_config.get(\'name\', \'LUISAVIAROMA\')} tracking list.")\n\1    return',
        content
    )
    
    # Fix indentation for the "Append the PID to the file" section
    content = re.sub(
        r'(\s+)# Append the PID to the file\s+with open\(store_file_path, "a"\) as f:[\s\n]+if needs_newline:[\s\n]+f\.write\(f"\\n\{pid_value\}\\n"\)[\s\n]+logger\.info\(f"Added newline before writing PID"\)[\s\n]+elif file_empty:[\s\n]+f\.write\(f"\{pid_value\}\\n"\)[\s\n]+else:[\s\n]+f\.write\(f"\{pid_value\}\\n"\)',
        r'\1# Append the PID to the file\n\1with open(store_file_path, "a") as f:\n\1    if needs_newline:\n\1        f.write(f"\\n{pid_value}\\n")\n\1        logger.info(f"Added newline before writing PID")\n\1    elif file_empty:\n\1        f.write(f"{pid_value}\\n")\n\1    else:\n\1        f.write(f"{pid_value}\\n")',
        content
    )
    
    # Fix indentation for logger.info and send confirmation
    content = re.sub(
        r'(\s+)logger\.info\(f"Successfully added PID \{pid_value\} to \{store_file_path\}"\)[\s\n]+[\s\n]+# Send confirmation response[\s\n]+await message\.channel\.send\(.*?\)',
        r'\1logger.info(f"Successfully added PID {pid_value} to {store_file_path}")\n\1\n\1# Send confirmation response\n\1await message.channel.send(f"✅ Added product ID `{pid_value}` to {store_config.get(\'name\', \'LUISAVIAROMA\')} tracking list.")',
        content
    )
    
    # Fix indentation for exception handling
    content = re.sub(
        r'(\s+)except Exception as e:[\s\n]+logger\.error\(f"Failed to write PID to file: \{str\(e\)}"\)[\s\n]+await message\.channel\.send\(.*?\)',
        r'\1except Exception as e:\n\1    logger.error(f"Failed to write PID to file: {str(e)}")\n\1    await message.channel.send(f"❌ Error saving product ID: {str(e)}")',
        content
    )
    
    # Fix indentation for else blocks
    content = re.sub(
        r'(\s+)else:[\s\n]+logger\.error\(f"No file path configured for \{store_config\.get\(\'name\', \'LUISAVIAROMA\'\)}"\)[\s\n]+await message\.channel\.send\(.*?\)',
        r'\1else:\n\1    logger.error(f"No file path configured for {store_config.get(\'name\', \'LUISAVIAROMA\')}")\n\1    await message.channel.send(f"❌ Error: {store_config.get(\'name\', \'LUISAVIAROMA\')} file path not configured.")',
        content
    )
    
    content = re.sub(
        r'(\s+)else:[\s\n]+logger\.warning\(f"No product ID found in this \{store_config\.get\(\'name\', \'LUISAVIAROMA\'\)} embed"\)[\s\n]+await message\.channel\.send\(.*?\)',
        r'\1else:\n\1    logger.warning(f"No product ID found in this {store_config.get(\'name\', \'LUISAVIAROMA\')} embed")\n\1    await message.channel.send(f"❌ No product ID found in this {store_config.get(\'name\', \'LUISAVIAROMA\')} embed.")',
        content
    )
    
    output_path = filepath + ".fixed"
    print(f"Writing fixed content to {output_path}")
    with open(output_path, 'w') as f:
        f.write(content)
    
    print("Done! Review the changes and then replace the original file if the fixes look good.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "modules/mod/link_reaction/link_reaction.py"
    
    fix_indentation(filepath) 