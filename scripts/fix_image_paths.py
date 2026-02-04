#!/usr/bin/env python3
"""
Script to fix incorrect image paths in markdown files.
Calculates the correct relative path to assets based on file location.
"""

import os
import re

CONTENT_DIR = 'content'
ASSETS_DIR = 'content/assets'


def get_correct_relative_path(file_path, asset_path):
    """
    Calculate the correct relative path from a markdown file to an asset.
    
    Args:
        file_path: Path to the markdown file (e.g., content/02-People/NPCs/Amazonki/Aella.md)
        asset_path: The asset path after 'assets/' (e.g., placeholder.png or sessions/001/image.png)
    
    Returns:
        Correct relative path from the markdown file to the asset.
    """
    # Get the directory containing the markdown file
    file_dir = os.path.dirname(file_path)
    
    # Calculate relative path from file_dir to ASSETS_DIR
    rel_path = os.path.relpath(ASSETS_DIR, file_dir)
    
    # Combine with the asset path
    return os.path.join(rel_path, asset_path).replace('\\', '/')


def fix_image_paths_in_file(file_path):
    """
    Fix image paths in a single markdown file.
    Returns True if changes were made, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    original_content = content
    
    # Pattern to match markdown images with relative paths to assets
    # Matches: ![alt text](../some/path/assets/something.png)
    pattern = r'!\[([^\]]*)\]\(((?:\.\.\/)+assets\/[^)]+)\)'
    
    def fix_path(match):
        alt_text = match.group(1)
        old_path = match.group(2)
        
        # Extract the part after 'assets/'
        assets_idx = old_path.find('assets/')
        if assets_idx == -1:
            return match.group(0)  # No change
        
        asset_subpath = old_path[assets_idx + len('assets/'):]
        
        # Calculate the correct relative path
        correct_path = get_correct_relative_path(file_path, asset_subpath)
        
        # Check if the asset actually exists
        full_asset_path = os.path.join(ASSETS_DIR, asset_subpath)
        if not os.path.exists(full_asset_path):
            # Asset doesn't exist, but still fix the path structure
            pass
        
        if old_path != correct_path:
            return f'![{alt_text}]({correct_path})'
        return match.group(0)
    
    content = re.sub(pattern, fix_path, content)
    
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    return False


def main():
    if not os.path.exists(CONTENT_DIR):
        print(f"Error: Directory '{CONTENT_DIR}' not found.")
        return

    fixed_count = 0
    checked_count = 0
    
    for root, dirs, files in os.walk(CONTENT_DIR):
        # Skip assets directory
        if 'assets' in dirs:
            dirs.remove('assets')
        
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            file_path = os.path.join(root, filename)
            checked_count += 1
            
            if fix_image_paths_in_file(file_path):
                print(f"Fixed: {file_path}")
                fixed_count += 1

    print(f"\nDone! Fixed {fixed_count} files out of {checked_count} checked.")


if __name__ == "__main__":
    main()
