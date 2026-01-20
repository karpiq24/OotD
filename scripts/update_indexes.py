import os
import re

# Configuration
ROOT_DIR = 'content'
EXCLUDED_DIR = 'assets'

def get_clean_folder_title(folder_name):
    """
    Generates a pretty title from the folder name.
    e.g. "02-People" -> "People"
    """
    if folder_name == ROOT_DIR:
        return "Index"
    
    # Remove leading numbers and hyphens (e.g., "01-")
    name = re.sub(r'^\d+[-_]', '', folder_name)
    # Replace remaining dashes/underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    # Capitalize words
    return name.title()

def extract_frontmatter_title(file_path):
    """
    Reads a markdown file and extracts the 'title' from frontmatter.
    Returns the title string if found, otherwise None.
    Uses utf-8-sig to handle BOM and reads safely.
    """
    if not os.path.exists(file_path):
        return None

    try:
        # Use utf-8-sig to automatically handle BOM if present
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            # Read first 2KB - enough for any reasonable frontmatter
            content = f.read(2048)
            
        # Regex to find frontmatter block between --- and ---
        # Matches start of string (^), ---, newline, content, newline, ---
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if match:
            frontmatter = match.group(1)
            # Find the title line (case insensitive key search)
            title_match = re.search(r'^title:\s*(.*)$', frontmatter, re.MULTILINE | re.IGNORECASE)
            if title_match:
                # Return the title, stripping quotes and spaces
                return title_match.group(1).strip().strip('"').strip("'")
    except Exception as e:
        # Silently fail on read errors (binary files etc)
        pass
        
    return None

def generate_list_content(items):
    """
    Generates just the string list of links.
    items: list of tuples (filename, display_title)
    """
    lines = []
    for filename, display_text in items:
        # If the filename (without ext) is exactly the same as the title, use short link
        if filename == display_text:
             lines.append(f"- [[{filename}]]")
        else:
             lines.append(f"- [[{filename}|{display_text}]]")
    return "\n".join(lines)

def create_new_index_file(output_path, title, list_content):
    """
    Creates a brand new index.md file from scratch.
    """
    content = (
        "---\n"
        f"title: {title}\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{list_content}\n"
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created new: {output_path}")

def update_existing_index_file(output_path, list_content):
    """
    Reads existing file, keeps Frontmatter and H1 Header, updates the list.
    """
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        # If read fails, treat as new file logic might apply, but let's just abort this file
        return

    # 1. Find end of frontmatter
    fm_end_match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
    
    split_index = 0
    
    if fm_end_match:
        fm_end_index = fm_end_match.end()
        # Search for H1 only AFTER the frontmatter
        body = content[fm_end_index:]
        h1_match = re.search(r'^#\s.*$', body, re.MULTILINE)
        
        if h1_match:
            # Keep Frontmatter + Body text up to end of H1
            split_index = fm_end_index + h1_match.end()
        else:
            # Frontmatter exists, but no H1. Keep Frontmatter.
            split_index = fm_end_index
            existing_title = extract_frontmatter_title(output_path) or "Index"
            content = content[:split_index] + f"\n# {existing_title}"
            split_index = len(content)
    else:
        # No frontmatter? Try to find just an H1
        h1_match = re.search(r'^#\s.*$', content, re.MULTILINE)
        if h1_match:
            split_index = h1_match.end()
        else:
            # No structure. Prepend generic header.
            content = f"# Index\n{content}"
            split_index = len(content)

    # Reassemble: Old Top Part + 2 Newlines + New List
    top_part = content[:split_index].rstrip()
    new_content = f"{top_part}\n\n{list_content}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated: {output_path}")

def process_directory(current_path, dirs, files):
    output_file = os.path.join(current_path, 'index.md')
    folder_name = os.path.basename(current_path)

    # --- 1. Gather Link Data ---
    link_data = [] 
    
    # Subdirectories
    for d in dirs:
        if d == EXCLUDED_DIR:
            continue
        
        subdir_path = os.path.join(current_path, d)
        subdir_index = os.path.join(subdir_path, 'index.md')
        
        # Try to get title from subdir/index.md, else guess
        subdir_title = extract_frontmatter_title(subdir_index)
        if not subdir_title:
            subdir_title = get_clean_folder_title(d)
            
        link_data.append((d, subdir_title))
        
    # Files
    for f in files:
        if f == 'index.md': continue
        if f.endswith('.md'):
            file_path = os.path.join(current_path, f)
            filename_no_ext = f[:-3]
            
            # Get title from file
            file_title = extract_frontmatter_title(file_path)
            
            # Fallback to filename if no title in frontmatter
            if not file_title:
                file_title = filename_no_ext
                
            link_data.append((filename_no_ext, file_title))

    # Sort
    link_data.sort(key=lambda x: x[1].lower())
    
    # Generate the bullet points string
    list_content = generate_list_content(link_data)

    # --- 2. Write File ---
    if os.path.exists(output_file):
        update_existing_index_file(output_file, list_content)
    else:
        # New file: Generate Title from folder name
        title = get_clean_folder_title(folder_name)
        create_new_index_file(output_file, title, list_content)

def main():
    if not os.path.exists(ROOT_DIR):
        print(f"Error: Directory '{ROOT_DIR}' not found.")
        return

    for root, dirs, files in os.walk(ROOT_DIR):
        if EXCLUDED_DIR in dirs:
            dirs.remove(EXCLUDED_DIR)
        process_directory(root, dirs, files)

if __name__ == "__main__":
    main()