"""
PDF Form Filler with Dummy Data
Fills a PDF form with realistic dummy data based on field names and types.
"""

import fitz  # PyMuPDF
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
try:
    from faker import Faker
    fake = Faker()
except ImportError:
    print("Faker not installed. Using simple dummy data.")
    fake = None

class PDFFormFiller:
    def __init__(self, pdf_path: str, json_path: str):
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.doc = fitz.open(pdf_path)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.field_data = json.load(f)

    def generate_value_for_field(self, field_info: dict):
        """Generate appropriate dummy data based on field metadata."""
        key = field_info['key'].lower()
        field_type = field_info['type']
        
        # Handle Checkboxes/Radio Buttons (Type 1: Button)
        if field_type == 'Button':
            # For checkboxes, we usually want to set them to 'Yes', 'On', or their export value
            # Randomly decide to check or not (bias towards checking for demo)
            return True if random.random() > 0.3 else False

        # Handle Choice/Dropdowns (Type 3: Choice)
        if field_type == 'Choice':
            choices = field_info.get('choices', [])
            if choices:
                return random.choice(choices)
            return "Option 1"

        # Handle Text Fields (Type 2: Text) and others
        if fake:
            if 'date' in key or 'day' in key or 'month' in key or 'year' in key:
                return fake.date_this_year().strftime("%m/%d/%Y")
            elif 'name' in key or 'seller' in key or 'buyer' in key:
                return fake.name()
            elif 'address' in key or 'city' in key or 'zip' in key or 'state' in key:
                if 'zip' in key: return fake.zipcode()
                if 'city' in key: return fake.city()
                if 'state' in key: return fake.state()
                return fake.address().replace('\n', ', ')
            elif 'price' in key or 'amount' in key or 'dollar' in key:
                return f"{random.randint(1000, 1000000):,}"
            elif 'phone' in key or 'number' in key:
                return fake.phone_number()
            elif 'email' in key:
                return fake.email()
            elif 'company' in key or 'firm' in key:
                return fake.company()
            else:
                return fake.sentence(nb_words=3).rstrip('.')
        else:
            # Fallback if Faker is not available
            if 'date' in key: return "01/01/2025"
            return f"Dummy {field_info['child']}"

    def fill_form(self, output_path: str):
        """Fill the form fields and save to output path."""
        print(f"Filling form: {self.pdf_path}")
        
        filled_count = 0
        
        # Iterate through pages in the PDF
        for page_num, page in enumerate(self.doc):
            # Find corresponding page data in JSON
            page_data = next((p for p in self.field_data['pages'] if p['page_number'] == page_num + 1), None)
            
            if not page_data:
                continue

            # Get widgets for this page
            widgets = page.widgets()
            
            for widget in widgets:
                # Find field info in our JSON to get context (optional, but good for consistency)
                # We match by field name (key)
                field_info = next((f for f in page_data['fields'] if f['key'] == widget.field_name), None)
                
                if not field_info:
                    # If not in JSON (maybe filtered out?), try to guess from widget
                    field_info = {
                        'key': widget.field_name or "unknown",
                        'type': self._get_field_type_str(widget.field_type),
                        'child': widget.field_name.split('.')[-1] if widget.field_name else "unknown"
                    }

                value = self.generate_value_for_field(field_info)
                
                # Check for "pseudo-checkboxes" - fields that are small but not typed as buttons
                is_pseudo_checkbox = False
                if widget.rect.width < 30 and widget.rect.height < 30:
                    is_pseudo_checkbox = True
                
                try:
                    if field_info['type'] == 'Button':
                        if value:
                            widget.field_value = True # For checkboxes/radio
                            widget.update() 
                    elif is_pseudo_checkbox:
                        # It's likely a text field acting as a checkbox
                        print(f"DEBUG: Filling pseudo-checkbox '{widget.field_name}' with 'X'")
                        widget.field_value = "X"
                        widget.update()
                        
                        # FORCE VISUAL FILL: Insert text directly on the page at these coordinates
                        # This ensures it looks filled even if the form widget behaves oddly
                        rect = widget.rect
                        # Center the X
                        x = rect.x0 + (rect.width / 2) - 3
                        y = rect.y1 - 2
                        page.insert_text((x, y), "X", fontsize=10, color=(0, 0, 0))
                    elif field_info['type'] == 'Choice':
                        if isinstance(value, list): value = value[0]
                        widget.field_value = str(value)
                        widget.update()
                    else:
                        widget.field_value = str(value)
                        widget.update()
                    
                    filled_count += 1
                except Exception as e:
                    print(f"Failed to fill field {widget.field_name}: {e}")

        self.doc.save(output_path)
        print(f"Successfully filled {filled_count} fields.")
        print(f"Saved to: {output_path}")

    def _get_field_type_str(self, type_int):
        types = {1: 'Button', 2: 'Text', 3: 'Choice', 4: 'Signature'}
        return types.get(type_int, 'Unknown')

def main():
    pdf_file = "RF401_Updated August 17, 2024_Open Field Fill Form.pdf"
    json_file = "RF401_Updated August 17, 2024_Open Field Fill Form_fields.json"
    output_file = "RF401_Filled_Form.pdf"
    
    if not Path(pdf_file).exists() or not Path(json_file).exists():
        print("Error: Input files not found.")
        return

    filler = PDFFormFiller(pdf_file, json_file)
    filler.fill_form(output_file)

if __name__ == "__main__":
    main()
