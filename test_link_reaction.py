"""
Test script for LUISAVIAROMA product ID extraction.

This script will:
1. Load an example LUISAVIAROMA embed from a JSON file
2. Extract the product ID from URL and/or PID field using the same logic as the link_reaction module
3. Print the result and verify it matches the expected output
"""

import json
import os
import re

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
    
    # Get the path from environment variable
    lv_file_path = os.getenv("luisaviaroma_drops_urls_path")
    
    if lv_file_path:
        print(f"✅ Found LUISAVIAROMA drops file path: {lv_file_path}")
        
        # Check if the file exists
        if os.path.exists(lv_file_path):
            print(f"✅ LUISAVIAROMA drops file exists at: {lv_file_path}")
        else:
            print(f"❌ LUISAVIAROMA drops file does not exist at: {lv_file_path}")
    else:
        print("❌ LUISAVIAROMA drops file path not configured in environment variables")
    
    print("\nTest Summary:")
    print("=============")
    print(f"Product ID: {pid_value}")
    print(f"Source: {'URL' if embed_url and 'luisaviaroma.com' in embed_url else 'PID field'}")
    print(f"Should be saved to: {lv_file_path or 'Not configured'}")
    print("\nIn the actual bot, this would be saved to the file when a whitelisted user reacts to a LUISAVIAROMA embed with the 🔗 link emoji.")

if __name__ == "__main__":
    main() 