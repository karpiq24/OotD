
import json
import os
from pathlib import Path

def aggregate_chapter(start_idx, end_idx, output_file):
    input_dir = Path("input/processed_pdf")
    all_text = []
    
    print(f"Aggregating pages {start_idx} to {end_idx}...")
    
    for i in range(start_idx, end_idx + 1):
        filename = f"page_{i:04d}.json"
        file_path = input_dir / filename
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_text.append(f"--- Page {data['page_number']} ---")
                all_text.append(data['text'])
                all_text.append("\n")
        else:
            print(f"Warning: {filename} not found.")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(all_text))
    
    print(f"Saved aggregated text to {output_file}")

if __name__ == "__main__":
    # Remaining Pages: Page 56(0055) to 67(0066)
    aggregate_chapter(55, 66, "input/remaining_text.txt")
