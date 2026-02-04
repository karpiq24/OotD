#!/usr/bin/env python3
"""
Remove duplicate H1 headers from markdown files when the frontmatter title
contains the same value. This is needed because Quartz renders the frontmatter
title as the page heading, so having an H1 with the same text creates duplicates.
"""
import os
import re
import argparse

def normalize_title(title):
    """
    Normalize a title for comparison by:
    - Lowercasing
    - Removing extra whitespace
    - Stripping quotes
    """
    if not title:
        return ""
    normalized = title.lower().strip()
    normalized = normalized.strip('"').strip("'")
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized

def process_file(file_path, dry_run=False):
    """
    Process a single markdown file.
    Returns True if the file was modified, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    # Check for frontmatter
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL | re.MULTILINE)
    if not fm_match:
        return False  # No frontmatter, nothing to do
    
    frontmatter = fm_match.group(1)
    frontmatter_end = fm_match.end()
    
    # Extract title from frontmatter
    title_match = re.search(r'^title:\s*(.*)$', frontmatter, re.MULTILINE | re.IGNORECASE)
    if not title_match:
        return False  # No title in frontmatter, nothing to do
    
    fm_title = title_match.group(1).strip().strip('"').strip("'")
    
    # Get content after frontmatter
    after_fm = content[frontmatter_end:]
    
    # Look for H1 at the start of content (possibly with leading whitespace/newlines)
    h1_match = re.match(r'^(\s*)(#\s+(.+?)\s*)\n', after_fm)
    if not h1_match:
        return False  # No H1 header right after frontmatter
    
    h1_full = h1_match.group(2)  # The full H1 line (# Title)
    h1_title = h1_match.group(3)  # Just the title text
    
    # Compare titles (normalized)
    if normalize_title(fm_title) != normalize_title(h1_title):
        return False  # Titles don't match, keep both
    
    # Remove the duplicate H1
    # We need to remove the H1 line and any trailing newlines that would create excess whitespace
    new_after_fm = after_fm[h1_match.end():]
    # Strip leading newlines but keep one for proper spacing
    new_after_fm = new_after_fm.lstrip('\n')
    if new_after_fm:
        new_after_fm = '\n' + new_after_fm
    
    new_content = content[:frontmatter_end].rstrip('\n') + '\n' + new_after_fm
    
    if dry_run:
        print(f"Would modify: {file_path}")
        print(f"  Removing duplicate H1: '{h1_title}'")
        return True
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Modified: {file_path}")
        print(f"  Removed duplicate H1: '{h1_title}'")
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def process_directory(root_dir, dry_run=False):
    """
    Recursively process all markdown files in a directory.
    """
    modified_count = 0
    processed_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Skip assets directory
        if 'assets' in dirs:
            dirs.remove('assets')
        
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                processed_count += 1
                if process_file(file_path, dry_run):
                    modified_count += 1
    
    return processed_count, modified_count

def main():
    parser = argparse.ArgumentParser(
        description='Remove duplicate H1 headers from markdown files when frontmatter title matches.'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='content',
        help='Directory or file to process (default: content)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be modified without making changes'
    )
    
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        if process_file(args.path, args.dry_run):
            print("\n1 file would be modified." if args.dry_run else "\n1 file modified.")
        else:
            print("\nNo changes needed.")
    elif os.path.isdir(args.path):
        processed, modified = process_directory(args.path, args.dry_run)
        action = "would be modified" if args.dry_run else "modified"
        print(f"\nProcessed {processed} files, {modified} {action}.")
    else:
        print(f"Error: '{args.path}' is not a valid file or directory.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
