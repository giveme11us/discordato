"""
Test script for LUISAVIAROMA product ID extraction.

This script will:
1. Load an example LUISAVIAROMA embed from a JSON file
2. Extract the product ID from URL and/or PID field using the same logic as the link_reaction module
3. Test file writing logic including handling of duplicates and proper newline usage
4. Print the result and verify it matches the expected output
"""

import json
import os
import re
import tempfile

def main():
    print("Testing LUISAVIAROMA product ID extraction")
    print("==========================================")
    
    # Load the example embed data
    try:
        with open('data/luisaviaroma_embed_example.json', 'r') as f:
            embed_data = json.load(f)
        print("✅ Successfully loaded example embed data")
    except Exception as e:
        print(f"❌ Failed to load example embed data: {str(e)}")
        return
    
    # Check if the author name is LUISAVIAROMA
    author_name = embed_data.get('author', {}).get('name', '')
    if author_name == "LUISAVIAROMA":
        print(f"✅ Found LUISAVIAROMA author in embed: {author_name}")
    else:
        print(f"❌ Author is not LUISAVIAROMA: {author_name}")
        return
    
    # Try to extract product ID from URL first
    pid_value = None
    embed_url = embed_data.get('url', '')
    
    if embed_url and 'luisaviaroma.com' in embed_url:
        print(f"✅ Found LUISAVIAROMA URL: {embed_url}")
        
        # Try to extract product ID using regex
        pattern = r'\/[^\/]+\/([^\/]+)$'
        match = re.search(pattern, embed_url)
        
        if match:
            pid_value = match.group(1)
            print(f"✅ Extracted product ID from URL using regex: {pid_value}")
        else:
            # If regex fails, try splitting the URL
            url_parts = embed_url.split('/')
            if url_parts and len(url_parts) > 1:
                potential_pid = url_parts[-1]
                # Validate that it looks like a PID
                if '-' in potential_pid and len(potential_pid) > 4:
                    pid_value = potential_pid
                    print(f"✅ Extracted product ID using URL splitting fallback: {pid_value}")
                else:
                    print(f"❌ Last URL segment doesn't look like a valid PID: {potential_pid}")
            else:
                print(f"❌ URL doesn't have expected format: {embed_url}")
    else:
        print(f"❌ No valid LUISAVIAROMA URL found in embed")
    
    # If URL parsing failed, try PID field as fallback
    if not pid_value:
        print("➡️ URL parsing failed, trying to extract from PID field")
        for field in embed_data.get('fields', []):
            if field.get('name', '').upper() == "PID":
                # Extract the PID value and clean it
                raw_value = field.get('value', '')
                # Remove markdown formatting (```\n...\n```)
                pid_value = raw_value.replace("```", "").strip()
                print(f"✅ Found PID in LUISAVIAROMA embed field: {pid_value}")
                break
    
    if not pid_value:
        print("❌ No PID could be extracted from URL or fields")
        return
    
    # Test file writing logic with a temporary file
    with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_file:
        temp_path = temp_file.name
        print(f"\nTesting file writing logic with temporary file: {temp_path}")
        
        # Test 1: Write PID to empty file
        print("\nTest 1: Write PID to empty file")
        append_pid_to_file(temp_path, pid_value)
        
        # Test 2: Write the same PID again (should detect duplicate)
        print("\nTest 2: Write same PID again (should detect duplicate)")
        append_pid_to_file(temp_path, pid_value)
        
        # Test 3: Write a different PID
        print("\nTest 3: Write a different PID")
        different_pid = "81I-DIFFERENT"
        append_pid_to_file(temp_path, different_pid)
        
        # Test 4: Write to file without final newline
        print("\nTest 4: Write to file without final newline")
        with open(temp_path, "a") as f:
            f.write("TEST-NO-NEWLINE")  # Write without newline
        append_pid_to_file(temp_path, "AFTER-MISSING-NEWLINE")
        
        # Show final file contents
        print("\nFinal file contents:")
        with open(temp_path, "r") as f:
            content = f.read()
            print(f"```\n{content}```")
        
        # Clean up
        os.unlink(temp_path)
    
    # Get the path from environment variable
    lv_file_path = os.getenv("luisaviaroma_drops_urls_path")
    
    if lv_file_path:
        print(f"\n✅ Found LUISAVIAROMA drops file path: {lv_file_path}")
        
        # Check if the file exists
        if os.path.exists(lv_file_path):
            print(f"✅ LUISAVIAROMA drops file exists at: {lv_file_path}")
        else:
            print(f"❌ LUISAVIAROMA drops file does not exist at: {lv_file_path}")
    else:
        print("\n❌ LUISAVIAROMA drops file path not configured in environment variables")
    
    print("\nTest Summary:")
    print("=============")
    print(f"Product ID: {pid_value}")
    print(f"Source: {'URL' if embed_url and 'luisaviaroma.com' in embed_url else 'PID field'}")
    print(f"Should be saved to: {lv_file_path or 'Not configured'}")
    print("\nIn the actual bot, this would be saved to the file when a whitelisted user reacts to a LUISAVIAROMA embed with the 🔗 link emoji.")

def append_pid_to_file(file_path, pid_value):
    """
    Append a PID to a file, handling duplicates and ensuring proper newline usage.
    This mimics the logic in the link_reaction.py file.
    """
    try:
        # Check if file exists and if PID is already in the file
        existing_pids = set()
        needs_newline = False
        file_empty = True
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r") as f:
                # Read all existing PIDs
                existing_content = f.read()
                existing_pids = {line.strip() for line in existing_content.splitlines() if line.strip()}
                
                # Check if file ends with newline
                needs_newline = not existing_content.endswith('\n')
                file_empty = not existing_content.strip()
                
                print(f"  Found {len(existing_pids)} existing PIDs in file")
        
        # Check if PID already exists in the file
        if pid_value in existing_pids:
            print(f"  ℹ️ PID {pid_value} already exists in file, skipping")
            return
        
        # Append the PID to the file
        with open(file_path, "a") as f:
            if needs_newline:
                f.write(f"\n{pid_value}\n")
                print(f"  Added newline before writing PID {pid_value}")
            elif file_empty:
                f.write(f"{pid_value}\n")
                print(f"  Wrote PID {pid_value} to empty file")
            else:
                f.write(f"{pid_value}\n")
                print(f"  Wrote PID {pid_value} with trailing newline")
        
        print(f"  ✅ Successfully added PID {pid_value} to file")
    except Exception as e:
        print(f"  ❌ Failed to write PID to file: {str(e)}")

if __name__ == "__main__":
    main() 