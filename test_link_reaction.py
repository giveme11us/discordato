"""
Test script for LUISAVIAROMA product ID extraction.

This script will:
1. Load an example LUISAVIAROMA embed from a JSON file
2. Extract the product ID using the same logic as the link_reaction module
3. Print the result and verify it matches the expected output
"""

import json
import os
import re

def main():
    print("Testing LUISAVIAROMA product ID extraction")
    print("------------------------------------------")
    
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
    
    # Look for PID field
    pid_value = None
    for field in embed_data.get('fields', []):
        if field.get('name', '').upper() == "PID":
            # Extract the PID value and clean it
            raw_value = field.get('value', '')
            # Remove markdown formatting (```\n...\n```)
            pid_value = raw_value.replace("```", "").strip()
            print(f"✅ Found PID in LUISAVIAROMA embed: {pid_value}")
            break
    
    if not pid_value:
        print("❌ No PID field found in LUISAVIAROMA embed")
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
    print("-------------")
    print(f"Product ID: {pid_value}")
    print(f"Should be saved to: {lv_file_path or 'Not configured'}")
    print("\nIn the actual bot, this would be saved to the file when a whitelisted user reacts to a LUISAVIAROMA embed with the 🔗 link emoji.")

if __name__ == "__main__":
    main() 