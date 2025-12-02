"""
Verify Checkbox Filling
Checks if specific small fields identified as checkboxes have been filled correctly.
"""

import fitz

def verify_fill(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Verifying filled values in: {pdf_path}\n")
    
    # Fields we identified as potential checkboxes in the inspection
    target_fields = [
        "full by Seller at or before Closing",
        "remote controls any wired electric vehicle wall charging stations swimming pool and its equipment awnings"
    ]
    
    found_count = 0
    for page in doc:
        for widget in page.widgets():
            if widget.field_name in target_fields:
                print(f"Field: {widget.field_name}")
                print(f"  Value: '{widget.field_value}'")
                print(f"  Rect: {widget.rect}")
                print(f"  Status: {'[FILLED]' if widget.field_value else '[EMPTY]'}")
                print("-" * 40)
                found_count += 1
    
    if found_count == 0:
        print("Warning: Target fields not found in the PDF.")

if __name__ == "__main__":
    verify_fill("RF401_Filled_Form.pdf")
