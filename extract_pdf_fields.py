"""
PDF Form Field Extractor
Extracts fillable form fields from a PDF and stores them in hierarchical JSON format.
Uses PyMuPDF (fitz) to extract form field information including page numbers, field names,
types, coordinates, and hierarchical relationships.
"""

import fitz  # PyMuPDF
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class PDFFieldExtractor:
    """Extract form fields from PDF and organize them hierarchically."""
    
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF field extractor.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = None
        self.fields_data = {
            "pdf_name": Path(pdf_path).name,
            "total_pages": 0,
            "pages": []
        }
    
    def extract_fields(self) -> Dict[str, Any]:
        """
        Extract all form fields from the PDF.
        
        Returns:
            Dictionary containing hierarchical field information
        """
        try:
            self.doc = fitz.open(self.pdf_path)
            self.fields_data["total_pages"] = len(self.doc)
            
            # Process each page
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                page_data = self._extract_page_fields(page, page_num + 1)
                if page_data["fields"]:  # Only add pages with fields
                    self.fields_data["pages"].append(page_data)
            
            # Organize fields hierarchically
            self._organize_hierarchy()
            
            return self.fields_data
            
        except Exception as e:
            print(f"Error extracting fields: {e}")
            raise
        finally:
            if self.doc:
                self.doc.close()
    
    def _extract_page_fields(self, page: fitz.Page, page_num: int) -> Dict[str, Any]:
        """
        Extract fields from a single page.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (1-indexed)
            
        Returns:
            Dictionary containing page field information
        """
        page_data = {
            "page_number": page_num,
            "page_dimensions": {
                "width": page.rect.width,
                "height": page.rect.height
            },
            "fields": []
        }
        
        # Get all widgets (form fields) on the page
        widgets = page.widgets()
        
        for widget in widgets:
            field_info = self._extract_field_info(widget, page_num)
            if field_info:
                page_data["fields"].append(field_info)
        
        return page_data
    
    def _extract_field_info(self, widget: fitz.Widget, page_num: int) -> Dict[str, Any]:
        """
        Extract information from a single form field widget.
        
        Args:
            widget: PyMuPDF widget object
            page_num: Page number (1-indexed)
            
        Returns:
            Dictionary containing field information
        """
        try:
            # Get field type
            field_type = self._get_field_type(widget.field_type)
            
            # Extract field name and parse hierarchy
            field_name = widget.field_name or f"unnamed_field_{id(widget)}"
            parent, child = self._parse_field_hierarchy(field_name)
            
            # Get field rectangle (coordinates)
            rect = widget.rect
            
            field_info = {
                "key": field_name,
                "parent": parent,
                "child": child,
                "type": field_type,
                "coordinates": {
                    "x0": round(rect.x0, 2),
                    "y0": round(rect.y0, 2),
                    "x1": round(rect.x1, 2),
                    "y1": round(rect.y1, 2)
                },
                "field_label": widget.field_label or "",
                "field_value": widget.field_value or "",
                "field_flags": widget.field_flags,
                "is_required": bool(widget.field_flags & 2),  # Required flag
                "is_readonly": bool(widget.field_flags & 1),  # Readonly flag
            }
            
            # Add type-specific information
            if field_type == "Choice":
                field_info["choices"] = widget.choice_values or []
            elif field_type == "Button":
                field_info["button_caption"] = widget.button_caption or ""
            
            return field_info
            
        except Exception as e:
            print(f"Error extracting field info: {e}")
            return None
    
    def _get_field_type(self, field_type_code: int) -> str:
        """
        Convert PyMuPDF field type code to readable string.
        
        Args:
            field_type_code: Integer field type code
            
        Returns:
            Human-readable field type string
        """
        field_types = {
            1: "Button",      # Push button, checkbox, radio button
            2: "Text",        # Text field
            3: "Choice",      # Combo box or list box
            4: "Signature",   # Signature field
        }
        return field_types.get(field_type_code, "Unknown")
    
    def _parse_field_hierarchy(self, field_name: str) -> tuple:
        """
        Parse field name to extract parent-child hierarchy.
        Many PDF forms use dot notation (e.g., "Section1.FirstName")
        
        Args:
            field_name: Full field name
            
        Returns:
            Tuple of (parent, child)
        """
        if '.' in field_name:
            parts = field_name.split('.')
            parent = '.'.join(parts[:-1])
            child = parts[-1]
        else:
            parent = "root"
            child = field_name
        
        return parent, child
    
    def _organize_hierarchy(self):
        """
        Organize fields into a hierarchical structure based on parent-child relationships.
        This adds a 'hierarchy' section to the data.
        """
        hierarchy = defaultdict(lambda: {"children": [], "fields": []})
        
        for page in self.fields_data["pages"]:
            for field in page["fields"]:
                parent = field["parent"]
                child = field["child"]
                
                # Add to hierarchy
                if parent not in hierarchy[parent]["fields"]:
                    hierarchy[parent]["fields"].append({
                        "page": page["page_number"],
                        "key": field["key"],
                        "type": field["type"]
                    })
                
                # Track parent-child relationships
                if parent != "root" and parent not in hierarchy["root"]["children"]:
                    hierarchy["root"]["children"].append(parent)
        
        # Convert defaultdict to regular dict for JSON serialization
        self.fields_data["hierarchy"] = {k: dict(v) for k, v in hierarchy.items()}
    
    def save_to_json(self, output_path: str, indent: int = 2):
        """
        Save extracted fields to a JSON file.
        
        Args:
            output_path: Path to output JSON file
            indent: JSON indentation level
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.fields_data, f, indent=indent, ensure_ascii=False)
            print(f"SUCCESS: Fields extracted and saved to: {output_path}")
            print(f"  Total pages: {self.fields_data['total_pages']}")
            print(f"  Pages with fields: {len(self.fields_data['pages'])}")
            
            # Count total fields
            total_fields = sum(len(page['fields']) for page in self.fields_data['pages'])
            print(f"  Total fields: {total_fields}")
            
        except Exception as e:
            print(f"Error saving JSON: {e}")
            raise


def main():
    """Main execution function."""
    import sys
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf_fields.py <pdf_file_path> [output_json_path]")
        print("\nExample:")
        print("  python extract_pdf_fields.py input.pdf")
        print("  python extract_pdf_fields.py input.pdf output.json")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Generate output path if not provided
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = Path(pdf_path).stem + "_fields.json"
    
    # Validate PDF exists
    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    # Extract fields
    print(f"Extracting fields from: {pdf_path}")
    print("-" * 60)
    
    extractor = PDFFieldExtractor(pdf_path)
    fields_data = extractor.extract_fields()
    extractor.save_to_json(output_path)
    
    print("-" * 60)
    print("Extraction complete!")


if __name__ == "__main__":
    main()
