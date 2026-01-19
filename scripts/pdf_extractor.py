
import pdfplumber
import argparse
import json
import os
from pathlib import Path
from tqdm import tqdm

def extract_text_from_pdf(pdf_path, output_dir, start_page=0, limit=None):
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    progress_file = output_dir / "progress.json"
    
    # Load progress if exists
    if progress_file.exists():
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            last_processed_page = progress.get('last_processed_page', -1)
            print(f"Resuming from page {last_processed_page + 1}")
            start_page = max(start_page, last_processed_page + 1)
    else:
        print("Starting fresh extraction")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            end_page = total_pages
            if limit:
                end_page = min(start_page + limit, total_pages)
            
            print(f"Processing pages {start_page} to {end_page} of {total_pages}")
            
            for i in tqdm(range(start_page, end_page)):
                page = pdf.pages[i]
                text = page.extract_text()
                
                # Simple extraction: One file per page or appended? 
                # Let's do one JSON file per page to easily resume/retry and keep structure
                page_output = output_dir / f"page_{i:04d}.json"
                
                data = {
                    "page_number": i + 1,
                    "text": text,
                    # We could add more extracted data here like tables later
                }
                
                with open(page_output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Update progress
                with open(progress_file, 'w') as f:
                    json.dump({'last_processed_page': i}, f)
                    
    except Exception as e:
        print(f"Error occurred: {e}")
        # Progress is saved in the loop, so we are safe
        raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text from PDF with progress tracking.")
    parser.add_argument("input_pdf", help="Path to input PDF file")
    parser.add_argument("--output_dir", default="input/processed_pdf", help="Directory to save extracted text")
    parser.add_argument("--start_page", type=int, default=0, help="Page number to start from (0-indexed)")
    parser.add_argument("--limit", type=int, default=None, help="Number of pages to process")
    
    args = parser.parse_args()
    
    extract_text_from_pdf(args.input_pdf, args.output_dir, args.start_page, args.limit)
