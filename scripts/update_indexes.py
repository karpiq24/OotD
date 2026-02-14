import os
import re

# Configuration
ROOT_DIR = 'content'
EXCLUDED_DIR = 'assets'

ROOT_DESCRIPTIONS = {
    "01-Sessions": ("Sesje", "Logi z naszych przygód w Thylei."),
    "02-People": ("Frakcje, bohaterowie i postacie niezależne", "Kluczowe postacie i organizacje."),
    "03-Locations": ("Miejsca", "Geografia i ważne lokacje."),
    "04-Items-and-Loot": ("Przedmioty i Łupy", "Magiczne artefakty i zdobyte skarby."),
    "05-Lore": ("Wiedza o Świecie", "Historia, mitologia i kultura Thylei."),
    "06-Rules": ("Zasady", "Mechanika gry i zasady domowe."),
    "07-Handouts": ("Materiały Pomocnicze", "Mapy, listy i inne pomoce."),
    "Timeline": ("Oś Czasu", "Chronologiczny zapis wydarzeń."),
}

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

def extract_file_data(file_path):
    """
    Reads a markdown file and extracts metadata from frontmatter.
    Returns a tuple (title, is_draft).
    title: str or None
    is_draft: bool
    """
    if not os.path.exists(file_path):
        return None, False

    try:
        # Use utf-8-sig to automatically handle BOM if present
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            # Read first 4KB - enough for any reasonable frontmatter
            content = f.read(4096)
            
        # Look for frontmatter title block between --- and ---
        fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if fm_match:
            frontmatter = fm_match.group(1)
            
            title = None
            is_draft = False
            
            # Find the title line (case insensitive key search)
            title_match = re.search(r'^title:\s*(.*)$', frontmatter, re.MULTILINE | re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip().strip('"').strip("'")
            
            # Find draft status
            draft_match = re.search(r'^draft:\s*(true|yes|on|1)\s*$', frontmatter, re.MULTILINE | re.IGNORECASE)
            if draft_match:
                is_draft = True
                
            return title, is_draft

    except Exception as e:
        # Silently fail on read errors (binary files etc)
        pass
        
    return None, False

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

def generate_root_content(items):
    """
    Generates rich content for the root index page.
    items: list of tuples (link_target, display_title)
    """
    lines = []
    for link_target, display_text in items:
        # Check if we have a description for this item
        # link_target might be "01-Sessions" or "Timeline"
        key = link_target
        if key in ROOT_DESCRIPTIONS:
            title, desc = ROOT_DESCRIPTIONS[key]
            # Use the title from our dictionary to ensure it matches
            display_text = title
        else:
            desc = ""
        
        # Format: ### 📜 [[Target|Title]]
        #         Description
        
        # Choose an icon based on the folder maybe? Or just generic.
        # Let's keep it simple for now or random icons if user wanted "pretty".
        # User asked for "headers and descriptions".
        
        lines.append(f"### [[{link_target}|{display_text}]]")
        if desc:
            lines.append(f"{desc}\n")
        else:
            lines.append("")
            
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

def update_root_index_file(output_path, current_items):
    """
    Special handler for root index to ensure rich content is preserved/updated.
    We just overwrite the body part after frontmatter because we control the structure.
    """
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return

    # Extract frontmatter
    fm_match = re.match(r'^(---\s*\n.*?\n---)', content, re.DOTALL | re.MULTILINE)
    if fm_match:
        frontmatter = fm_match.group(1)
    else:
        # If no frontmatter, create default
        frontmatter = "---\ntitle: Strona główna\n---"

    # Generate new body
    # Sort items based on our preferred order if needed, or just natural sort
    # Actually, specific order might be better for Home Page.
    # Let's use the order predefined in ROOT_DESCRIPTIONS keys if possible, then others.
    
    ordered_items = []
    # 1. Add items present in ROOT_DESCRIPTIONS in order
    for key in ROOT_DESCRIPTIONS:
        # Find if this key exists in current_items
        found = next((item for item in current_items if item[0] == key), None)
        if found:
            ordered_items.append(found)
            
    # 2. Add remaining items
    seen_keys = set(ROOT_DESCRIPTIONS.keys())
    remaining = [item for item in current_items if item[0] not in seen_keys]
    remaining.sort(key=lambda x: natural_sort_key(x[0]))
    ordered_items.extend(remaining)
    
    body = generate_root_content(ordered_items)
    
    # Add banner image if configured
    banner_markdown = ""
    # We assume the script is run from project root, so we check if the file exists
    if os.path.exists(os.path.join(ROOT_DIR, EXCLUDED_DIR, "ootd_background.png")):
         banner_markdown = f"![Banner]({EXCLUDED_DIR}/ootd_background.png)\n\n"

    new_content = f"{frontmatter}\n\n{banner_markdown}{body}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated Root: {output_path}")

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
        if d == EXCLUDED_DIR or d == '99-DM-Corner':
            continue
        
        subdir_path = os.path.join(current_path, d)
        subdir_index = os.path.join(subdir_path, 'index.md')
        
        # Build full link path from content root
        if rel_path:
            link_path = f"{rel_path}/{d}"
        else:
            link_path = d
        
        # Try to get title from subdir/index.md, else guess
        subdir_title, subdir_is_draft = extract_file_data(subdir_index)
        
        # Skip if directory index is marked as draft
        if subdir_is_draft:
            continue

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
            file_title, file_is_draft = extract_file_data(file_path)
            
            # Skip draft files
            if file_is_draft:
                continue
            
            # Fallback to filename if no title in frontmatter
            if not file_title:
                file_title = filename_no_ext
                
            link_data.append((filename_no_ext, file_title))

    # Sort
    link_data.sort(key=lambda x: natural_sort_key(x[0]))
    
    # Generate the bullet points string (fallback/new file)
    # Generate the bullet points string (fallback/new file)
    if not rel_path:
        # Root directory - specific formatting
        list_content = generate_root_content(link_data)
    else:
        list_content = generate_list_content(link_data)

    # --- 2. Write File ---
    if os.path.exists(output_file):
        if not rel_path:
             update_root_index_file(output_file, link_data)
        else:
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
        if '99-DM-Corner' in dirs:
            dirs.remove('99-DM-Corner')
        process_directory(root, dirs, files)

if __name__ == "__main__":
    main()