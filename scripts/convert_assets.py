#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import shutil
import re
from pathlib import Path

# Configuration
CONTENT_DIR = 'content'
ASSETS_DIR = 'content/assets'
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
VIDEO_EXTENSIONS = {'.mp4'}

try:
    from PIL import Image
    from tqdm import tqdm
except ImportError:
    print("Error: Dependencies are not installed. Please run 'pip install -r requirements.txt'")
    sys.exit(1)

def get_file_stats(file_path):
    """Return size in bytes."""
    return os.path.getsize(file_path)

def format_size(size_bytes):
    """Format size in human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def convert_image(input_path, dry_run=False):
    """Convert image to webp using Pillow."""
    output_path = input_path.with_suffix('.webp')
    
    if input_path.suffix.lower() == '.webp':
        return None, 0, 0

    try:
        if not dry_run:
            with Image.open(input_path) as img:
                img.save(output_path, 'WEBP', quality=80)
        
        # Stats
        original_size = get_file_stats(input_path)
        new_size = 0 if dry_run else get_file_stats(output_path)
        
        return output_path, original_size, new_size
    except Exception as e:
        tqdm.write(f"Error converting {input_path}: {e}")
        return None, 0, 0

def convert_video(input_path, dry_run=False):
    """Convert video to webm using ffmpeg."""
    output_path = input_path.with_suffix('.webm')
    
    if input_path.suffix.lower() == '.webm':
        return None, 0, 0
    
    # ffmpeg command for webm (VP9)
    # Added -hide_banner -loglevel error -stats to show progress but hide spam
    cmd = [
        'ffmpeg', '-y', '-i', str(input_path),
        '-hide_banner', '-loglevel', 'error', '-stats',
        '-c:v', 'libvpx-vp9', '-crf', '30', '-b:v', '0',
        '-c:a', 'libopus',
        str(output_path)
    ]

    try:
        if not dry_run:
            # allow stdout/stderr to pass through to show progress
            # stdin=subprocess.DEVNULL helps avoid ffmpeg stealing input from tqdm/terminal
            result = subprocess.run(cmd, stdin=subprocess.DEVNULL)
            if result.returncode != 0:
                tqdm.write(f"Error converting {input_path} with ffmpeg (check output above)")
                return None, 0, 0
        else:
           # Simulate checks
           pass
        
        original_size = get_file_stats(input_path)
        new_size = 0 if dry_run else get_file_stats(output_path)
        
        return output_path, original_size, new_size

    except Exception as e:
        tqdm.write(f"Error executing ffmpeg for {input_path}: {e}")
        return None, 0, 0

def update_references(content_dir, mapping, dry_run=False):
    """
    Update markdown files to point to new assets.
    mapping: dict of {old_filename: new_filename}
    """
    updated_files_count = 0
    
    # Pre-calculate replacements: old_filename -> new_filename
    replacements = {k.name: v.name for k, v in mapping.items()}
    
    if not replacements:
        return 0

    print(f"Scanning {content_dir} for references to update...")

    # We can't easily count files beforehand without walking twice, so generic progress or just print
    # Let's just walk.
    
    for root, _, files in os.walk(content_dir):
        for file in files:
            if not file.endswith('.md'):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                file_changed = False
                
                for old_name, new_name in replacements.items():
                    if old_name in new_content:
                        new_content = new_content.replace(old_name, new_name)
                        file_changed = True
                
                if file_changed:
                    updated_files_count += 1
                    if not dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
            except Exception as e:
                print(f"Error updating references in {file_path}: {e}")

    return updated_files_count

def main():
    parser = argparse.ArgumentParser(description="Convert assets to web-friendly formats and update references.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate conversion and updates without changing files.")
    parser.add_argument("--target", choices=['all', 'images', 'videos'], default='all', help="Specify which asset types to process (default: all).")
    
    args = parser.parse_args()
    
    # Paths
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[1] # scripts/ -> project_root
    assets_root = project_root / ASSETS_DIR
    content_root = project_root / CONTENT_DIR
    
    if not assets_root.exists():
        print(f"Assets directory not found: {assets_root}")
        return

    # 1. Scan
    print(f"Scanning {assets_root}...")
    images_to_convert = []
    videos_to_convert = []
    
    for path in assets_root.rglob('*'):
        if path.is_file():
            if args.target in ['all', 'images'] and path.suffix.lower() in IMAGE_EXTENSIONS:
                images_to_convert.append(path)
            elif args.target in ['all', 'videos'] and path.suffix.lower() in VIDEO_EXTENSIONS:
                videos_to_convert.append(path)

    print(f"Found {len(images_to_convert)} images and {len(videos_to_convert)} videos.")
    
    total_original_size = 0
    total_new_size = 0
    file_mapping = {} # old_path (Path) -> new_path (Path)
    
    # 2. Convert
    # Images
    if images_to_convert:
        print("Converting images...")
        for img_path in tqdm(images_to_convert, unit="img"):
            # print(f"Converting image: {img_path.name}...") 
            out, orig, new = convert_image(img_path, dry_run=args.dry_run)
            if out:
                total_original_size += orig
                total_new_size += new
                file_mapping[img_path] = out
                if not args.dry_run:
                    try:
                        os.remove(img_path)
                    except OSError as e:
                        tqdm.write(f"Error removing {img_path}: {e}")

    # Videos
    if videos_to_convert:
        print("Converting videos...")
        # Since ffmpeg outputs to stderr, it might mess up tqdm bar.
        # But we want "X out of Y".
        pbar = tqdm(videos_to_convert, unit="vid")
        for vid_path in pbar:
            pbar.set_description(f"Processing {vid_path.name}")
            out, orig, new = convert_video(vid_path, dry_run=args.dry_run)
            if out:
                total_original_size += orig
                total_new_size += new
                file_mapping[vid_path] = out
                if not args.dry_run:
                     # Remove original
                    try:
                        os.remove(vid_path)
                    except OSError as e:
                        tqdm.write(f"Error removing {vid_path}: {e}")

    # 3. Update References
    if file_mapping:
        print(f"Updating references for {len(file_mapping)} converted files...")
        updated_count = update_references(content_root, file_mapping, dry_run=args.dry_run)
        print(f"Markdown files updated: {updated_count}")
    else:
        print("No files converted, skipping reference updates.")

    # 4. Stats
    print("\n" + "="*30)
    print("       CONVERSION STATS       ")
    print("="*30)
    print(f"Total Original Size: {format_size(total_original_size)}")
    
    if args.dry_run:
        print("DRY RUN: New size not accurately calculated (0).")
    else:
        print(f"Total New Size:      {format_size(total_new_size)}")
        saved = total_original_size - total_new_size
        pct = (saved / total_original_size * 100) if total_original_size > 0 else 0
        print(f"Space Saved:         {format_size(saved)} ({pct:.2f}%)")

if __name__ == "__main__":
    main()
