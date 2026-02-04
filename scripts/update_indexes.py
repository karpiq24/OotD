import os
import re

# Configuration
ROOT_DIR = 'content'
EXCLUDED_DIR = 'assets'

def natural_sort_key(s):
    """
    Returns a key for natural sorting (e.g. "Sesja 2" < "Sesja 10").
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r'(\d+)', s)]

def get_clean_folder_title(folder_name):
    """
    Generates a pretty title from the folder name.
    e.g. "02-People" -> "People"
    """
    if folder_name == ROOT_DIR:
        return "Strona główna"
    
    # Remove leading numbers and hyphens (e.g., "01-")
    name = re.sub(r'^\d+[-_]', '', folder_name)
    # Replace remaining dashes/underscores with spaces
    name = name.replace('-', ' ').replace('_', ' ')
    # Capitalize words
    return name.title()

def extract_title(file_path):
    """
    Reads a markdown file and extracts the title from frontmatter only.
    Returns the title string if found, otherwise None.
    Uses utf-8-sig to handle BOM and reads safely.
    
    Note: We no longer use H1 headers as fallback since Quartz renders
    the frontmatter title and we've removed duplicate H1s.
    """
    if not os.path.exists(file_path):
        return None

    try:
        # Use utf-8-sig to automatically handle BOM if present
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            # Read first 4KB - enough for any reasonable frontmatter
            content = f.read(4096)
            
        # Look for frontmatter title block between --- and ---
        fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if fm_match:
            frontmatter = fm_match.group(1)
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
    items: list of tuples (link_target, display_title)
    link_target can be a filename or a path (for directories)
    """
    lines = []
    for link_target, display_text in items:
        # If the link target is exactly the same as the title, use short link
        if link_target == display_text:
             lines.append(f"- [[{link_target}]]")
        else:
             lines.append(f"- [[{link_target}|{display_text}]]")
    return "\n".join(lines)

def create_new_index_file(output_path, title, list_content):
    """
    Creates a brand new index.md file from scratch.
    Note: We don't include an H1 header because Quartz renders 
    the frontmatter title as the page heading.
    """
    content = (
        "---\n"
        f"title: {title}\n"
        "---\n\n"
        f"{list_content}\n"
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created new: {output_path}")

def update_existing_index_file(output_path, current_items):
    """
    Reads existing file, keeps Frontmatter and H1 Header, updates the list.
    Preserves non-list content and existing order of links if found.
    """
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return

    item_dict = {f: t for f, t in current_items}
    lines = content.splitlines()
    
    # Regex for markdown list item with wikilink
    list_item_pattern = r'^\s*- \[\[([^|\]\n]+)(?:\|[^\]\n]+)?\]\]'
    list_indices = [i for i, line in enumerate(lines) if re.match(list_item_pattern, line)]
    
    if list_indices:
        # 1. Parse existing filenames in order
        existing_filenames = []
        for idx in list_indices:
            m = re.match(list_item_pattern, lines[idx])
            if m:
                existing_filenames.append(m.group(1))
        
        # 2. Build final order
        # Files that exist in BOTH existing index and current directory
        final_filenames = []
        seen = set()
        for f in existing_filenames:
            if f in item_dict and f not in seen:
                final_filenames.append(f)
                seen.add(f)
        
        # Files that are in the directory but NOT in the index
        new_files = [f for f, t in current_items if f not in seen]
        new_files.sort(key=natural_sort_key)
        
        # Add new files at the end
        final_filenames.extend(new_files)
        
        # 3. Generate new list content
        final_items_data = [(f, item_dict[f]) for f in final_filenames]
        new_list_content = generate_list_content(final_items_data)
        
        # 4. Replace the old list block
        first_idx = list_indices[0]
        last_idx = list_indices[-1]
        
        new_lines = lines[:first_idx] + [new_list_content] + lines[last_idx+1:]
        new_content = "\n".join(new_lines).strip() + "\n"
        
    else:
        # Fallback: Find H1 and insert after it, or append
        h1_match = re.search(r'^#\s.*$', content, re.MULTILINE)
        sorted_items = sorted(current_items, key=lambda x: natural_sort_key(x[0]))
        list_str = generate_list_content(sorted_items)
        
        if h1_match:
            split_index = h1_match.end()
            top = content[:split_index].rstrip()
            bottom = content[split_index:].lstrip()
            
            if bottom:
                new_content = f"{top}\n\n{list_str}\n\n{bottom}".strip() + "\n"
            else:
                new_content = f"{top}\n\n{list_str}\n"
        else:
            # Just append
            new_content = content.strip() + "\n\n" + list_str + "\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated: {output_path}")

def process_directory(current_path, dirs, files):
    output_file = os.path.join(current_path, 'index.md')
    folder_name = os.path.basename(current_path)
    
    # Get path relative to content root (e.g., "02-People/NPCs")
    rel_path = os.path.relpath(current_path, ROOT_DIR)
    if rel_path == '.':
        rel_path = ''

    # --- 1. Gather Link Data ---
    link_data = [] 
    
    # Subdirectories - use full path from content root
    for d in dirs:
        if d == EXCLUDED_DIR:
            continue
        
        subdir_path = os.path.join(current_path, d)
        subdir_index = os.path.join(subdir_path, 'index.md')
        
        # Build full link path from content root
        if rel_path:
            link_path = f"{rel_path}/{d}"
        else:
            link_path = d
        
        # Try to get title from subdir/index.md, else guess
        subdir_title = extract_title(subdir_index)
        if not subdir_title:
            subdir_title = get_clean_folder_title(d)
            
        link_data.append((link_path, subdir_title))
        
    # Files
    for f in files:
        if f == 'index.md': continue
        if f.endswith('.md'):
            file_path = os.path.join(current_path, f)
            filename_no_ext = f[:-3]
            
            # Get title from file
            file_title = extract_title(file_path)
            
            # Fallback to filename if no title in frontmatter
            if not file_title:
                file_title = filename_no_ext
                
            link_data.append((filename_no_ext, file_title))

    # Sort
    link_data.sort(key=lambda x: natural_sort_key(x[0]))
    
    # Generate the bullet points string (fallback/new file)
    list_content = generate_list_content(link_data)

    # --- 2. Write File ---
    if os.path.exists(output_file):
        update_existing_index_file(output_file, link_data)
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