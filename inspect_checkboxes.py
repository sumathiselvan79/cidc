"""
Inspect Checkbox Properties
Analyzes button widgets to determine correct 'on' states for filling.
"""

import fitz

def inspect_checkboxes(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"Inspecting checkboxes in: {pdf_path}\n")
    
    count = 0
    for page in doc:
        for widget in page.widgets():
            print(f"Field: {widget.field_name}")
            print(f"  Type Code: {widget.field_type}")
            print(f"  Rect: {widget.rect}")
            
            # If it looks like a checkbox (small square-ish), let's inspect it deeper
            if widget.rect.width < 20 and widget.rect.height < 20:
                print("  -> Potential Checkbox based on size")
                xref = widget.xref
                print(f"  XREF: {xref}")
                # Check for On/Off states in AP or AS
                print(f"  Field Value: {widget.field_value}")
                print(f"  Field Flags: {widget.field_flags}")
            
            count += 1
            if count >= 20: # Check first 20 fields
                return

if __name__ == "__main__":
    inspect_checkboxes("RF401_Updated August 17, 2024_Open Field Fill Form.pdf")
