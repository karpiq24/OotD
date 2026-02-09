#!/usr/bin/env python3
import os
import argparse
import zipfile
import re
from datetime import datetime

def find_and_zip(search_strings, merge=False):
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    content_dir = os.path.join(project_root, 'content')
    
    # Create zip filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construct a meaningful filename base
    if len(search_strings) == 1:
        base_name = search_strings[0]
    else:
        # Join first few chars of each or just "multi_search"
        base_name = "multi_search"
        
    sanitized_search = "".join([c for c in base_name if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_')
    if not sanitized_search:
        sanitized_search = "search_result"
    
    zip_filename = f"found_files_{sanitized_search}_{timestamp}.zip"
    zip_path = os.path.join(project_root, zip_filename)

    found_files = set()

    print(f"Searching for any of {search_strings} in {content_dir} (Markdown files only)...")

    # Walk through the content directory
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            # Filter for markdown files only
            if not file.lower().endswith('.md'):
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check if ANY of the search strings are in the matching file
                    for s in search_strings:
                        if s in content:
                            found_files.add(file_path)
                            break # File found, no need to check other strings
            except Exception as e:
                # Silently skip unreadable files or print error if critical
                # print(f"Could not read {file_path}: {e}")
                pass

    if not found_files:
        print("No files found containing any of the search strings.")
        return

    print(f"Found {len(found_files)} unique files. Creating zip at {zip_path}...")

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if merge:
                # Group files by top-level category
                files_by_category = {}
                for file_path in found_files:
                    rel_path = os.path.relpath(file_path, content_dir)
                    parts = rel_path.split(os.sep)
                    
                    if len(parts) > 1:
                        # It is in a subdirectory, e.g. 01-Sessions
                        category_raw = parts[0]
                        # Remove leading numbers and dash (e.g. 01-Sessions -> Sessions)
                        category = re.sub(r'^\d+-', '', category_raw)
                    else:
                        # File in root
                        category = "General"
                    
                    if category not in files_by_category:
                        files_by_category[category] = []
                    files_by_category[category].append(file_path)
                
                # Write merged files
                for category, paths in files_by_category.items():
                    merged_content = []
                    # Sort by path to ensure deterministic order
                    for fp in sorted(paths):
                        try:
                            rel_name = os.path.relpath(fp, content_dir)
                            with open(fp, 'r', encoding='utf-8') as f:
                                f_content = f.read()
                                merged_content.append(f"# File: {rel_name}\n\n{f_content}")
                        except Exception as e:
                            print(f"Error reading {fp} for merge: {e}")
                    
                    # Join with separators
                    full_text = "\n\n---\n\n".join(merged_content)
                    zipf.writestr(f"{category}.md", full_text)
                    print(f"Merged {len(paths)} files into {category}.md")

            else:
                # Standard behavior: zip individual files preserving structure
                for file_path in found_files:
                    # Store files relative to project root to preserve folder structure within the zip
                    arcname = os.path.relpath(file_path, project_root)
                    zipf.write(file_path, arcname)
        
        print(f"Successfully created: {zip_path}")
        print(f"Total files processed: {len(found_files)}")
        
    except Exception as e:
        print(f"Error creating zip file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find markdown files in 'content/' containing specific strings and zip them.")
    parser.add_argument("search_strings", nargs='+', help="One or more strings to search for. Files containing ANY of these strings will be included.")
    parser.add_argument("--merge", action="store_true", help="Merge found files into single markdown files per top-level category (e.g. Sessions.md, People.md).")
    
    args = parser.parse_args()
    
    find_and_zip(args.search_strings, merge=args.merge)
