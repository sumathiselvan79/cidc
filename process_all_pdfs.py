"""
Process All PDFs
Automatically finds all PDF files in the directory, extracts fields, fills them with dummy data,
and generates visualizations.
"""

import os
from pathlib import Path
import sys

# Import our existing tools
# We need to make sure we can import them even if they are scripts
try:
    from extract_pdf_fields import PDFFieldExtractor
    from fill_pdf_form import PDFFormFiller
    from highlight_fields_simple import highlight_fields_simple
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure extract_pdf_fields.py, fill_pdf_form.py, and highlight_fields_simple.py are in the same directory.")
    sys.exit(1)

def process_pdf(pdf_path: Path):
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_path.name}")
    print(f"{'='*60}")

    # 1. Extract Fields
    print("\n--- Step 1: Extracting Fields ---")
    json_path = pdf_path.with_name(pdf_path.stem + "_fields.json")
    try:
        extractor = PDFFieldExtractor(str(pdf_path))
        extractor.extract_fields()
        extractor.save_to_json(str(json_path))
    except Exception as e:
        print(f"Error extracting fields: {e}")
        return

    # 2. Fill Form
    print("\n--- Step 2: Filling Form ---")
    output_pdf_path = pdf_path.with_name(pdf_path.stem + "_Filled.pdf")
    try:
        filler = PDFFormFiller(str(pdf_path), str(json_path))
        filler.fill_form(str(output_pdf_path))
    except Exception as e:
        print(f"Error filling form: {e}")
        return

    # 3. Visualize Fields (Page 1)
    print("\n--- Step 3: Generating Visualization ---")
    try:
        highlight_fields_simple(str(pdf_path), page_number=1)
    except Exception as e:
        print(f"Error visualizing fields: {e}")

    print(f"\nSuccessfully processed {pdf_path.name}")
    print(f"Outputs:")
    print(f"  - JSON: {json_path.name}")
    print(f"  - Filled PDF: {output_pdf_path.name}")

def main():
    # Get current directory
    current_dir = Path(".")
    
    # Find all PDF files
    all_pdfs = list(current_dir.glob("*.pdf"))
    
    # Filter out generated files to avoid reprocessing
    pdfs_to_process = []
    for pdf in all_pdfs:
        # Skip files that end with _Filled.pdf or contain "Filled_Form" (legacy naming)
        if pdf.name.endswith("_Filled.pdf") or "Filled_Form" in pdf.name:
            continue
        pdfs_to_process.append(pdf)
    
    if not pdfs_to_process:
        print("No new PDF files found to process.")
        return

    print(f"Found {len(pdfs_to_process)} PDF(s) to process.")
    
    for pdf in pdfs_to_process:
        process_pdf(pdf)

    print(f"\n{'='*60}")
    print("All processing complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
