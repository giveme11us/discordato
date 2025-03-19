#!/usr/bin/env python3
"""
Script to fix specific syntax errors in link_reaction.py:
1. Fix unterminated string literal in endswith() call
2. Fix try block without except/finally clauses
"""
import re

def fix_specific_errors(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the broken newline in the endswith function
    pattern = r"needs_newline = not existing_content\.endswith\('[\s\n]+'\)"
    replacement = r"needs_newline = not existing_content.endswith('\\n')"
    content = re.sub(pattern, replacement, content)
    
    # Fix the broken try block by ensuring it has except/finally
    pattern = r"(\s+)try:(?:\s+.*?){1,50}?(?!\s+except|\s+finally)"
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        # Find the try block without except/finally
        try_pattern = r"(\s+)try:(\s+.*?)(?=(\s+)(?!except|finally|[a-zA-Z]))"
        
        # Add except block
        content = re.sub(
            try_pattern,
            r"\1try:\2\1except Exception as e:\1    logger.error(f\"Unexpected error: {str(e)}\")\1    await message.channel.send(f\"❌ Error: {str(e)}\")",
            content, 
            flags=re.DOTALL
        )
    
    # Fix extra parentheses and closing tracking list string
    content = re.sub(
        r"tracking list\.\"\)\)",
        r"tracking list.\")",
        content
    )
    
    output_path = file_path + ".fixed"
    print(f"Writing fixed content to {output_path}")
    with open(output_path, 'w') as f:
        f.write(content)
    
    print("Done! Review the changes before replacing the original file.")

if __name__ == "__main__":
    fix_specific_errors("modules/mod/link_reaction/link_reaction.py") 