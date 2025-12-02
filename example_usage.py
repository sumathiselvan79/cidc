"""
Example Usage of PDF Field Extractor
Demonstrates how to use the PDFFieldExtractor class programmatically.
"""

from extract_pdf_fields import PDFFieldExtractor
import json
from pathlib import Path


def analyze_pdf_fields(pdf_path: str):
    """
    Analyze a PDF and print statistics about its fields.
    
    Args:
        pdf_path: Path to the PDF file
    """
    print(f"\n{'='*60}")
    print(f"Analyzing PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    # Create extractor and extract fields
    extractor = PDFFieldExtractor(pdf_path)
    fields_data = extractor.extract_fields()
    
    # Print summary statistics
    print(f"PDF Name: {fields_data['pdf_name']}")
    print(f"Total Pages: {fields_data['total_pages']}")
    print(f"Pages with Fields: {len(fields_data['pages'])}")
    
    # Count total fields
    total_fields = sum(len(page['fields']) for page in fields_data['pages'])
    print(f"Total Fields: {total_fields}\n")
    
    # Analyze field types
    field_types = {}
    for page in fields_data['pages']:
        for field in page['fields']:
            field_type = field['type']
            field_types[field_type] = field_types.get(field_type, 0) + 1
    
    print("Field Types Distribution:")
    for field_type, count in sorted(field_types.items()):
        print(f"  - {field_type}: {count}")
    
    # Show fields by page
    print("\nFields per Page:")
    for page in fields_data['pages']:
        print(f"  Page {page['page_number']}: {len(page['fields'])} fields")
    
    # Show hierarchy
    print("\nHierarchical Structure:")
    hierarchy = fields_data.get('hierarchy', {})
    for parent, info in hierarchy.items():
        if parent == 'root':
            print(f"  Root level has {len(info['children'])} parent sections")
        else:
            print(f"  - {parent}: {len(info['fields'])} fields")
    
    return fields_data


def export_field_names_only(fields_data: dict, output_path: str):
    """
    Export only field names in a simplified format.
    
    Args:
        fields_data: Extracted fields data
        output_path: Path to output JSON file
    """
    simplified = {
        "pdf_name": fields_data["pdf_name"],
        "fields_by_page": []
    }
    
    for page in fields_data["pages"]:
        page_info = {
            "page_number": page["page_number"],
            "field_keys": [field["key"] for field in page["fields"]]
        }
        simplified["fields_by_page"].append(page_info)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, indent=2, ensure_ascii=False)
    
    print(f"\nSimplified field names exported to: {output_path}")


def export_hierarchical_structure(fields_data: dict, output_path: str):
    """
    Export fields organized by parent-child hierarchy.
    
    Args:
        fields_data: Extracted fields data
        output_path: Path to output JSON file
    """
    hierarchical = {
        "pdf_name": fields_data["pdf_name"],
        "structure": {}
    }
    
    for page in fields_data["pages"]:
        for field in page["fields"]:
            parent = field["parent"]
            
            if parent not in hierarchical["structure"]:
                hierarchical["structure"][parent] = []
            
            hierarchical["structure"][parent].append({
                "page": page["page_number"],
                "key": field["key"],
                "child": field["child"],
                "type": field["type"],
                "coordinates": field["coordinates"]
            })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(hierarchical, f, indent=2, ensure_ascii=False)
    
    print(f"Hierarchical structure exported to: {output_path}")


def main():
    """Main execution function."""
    # Example 1: Analyze a PDF
    pdf_file = "RF401_Updated August 17, 2024_Open Field Fill Form.pdf"
    
    if not Path(pdf_file).exists():
        print(f"Error: PDF file not found: {pdf_file}")
        print("\nPlease update the 'pdf_file' variable with your PDF path.")
        return
    
    # Extract and analyze fields
    fields_data = analyze_pdf_fields(pdf_file)
    
    # Example 2: Save full extraction
    full_output = Path(pdf_file).stem + "_full_extraction.json"
    extractor = PDFFieldExtractor(pdf_file)
    extractor.extract_fields()
    extractor.save_to_json(full_output)
    
    # Example 3: Export simplified field names only
    simplified_output = Path(pdf_file).stem + "_field_names.json"
    export_field_names_only(fields_data, simplified_output)
    
    # Example 4: Export hierarchical structure
    hierarchical_output = Path(pdf_file).stem + "_hierarchical.json"
    export_hierarchical_structure(fields_data, hierarchical_output)
    
    print(f"\n{'='*60}")
    print("All exports completed successfully!")
    print(f"{'='*60}\n")
    
    # Example 5: Access specific field data
    print("Example: Accessing specific field data")
    print("-" * 60)
    first_page = fields_data['pages'][0]
    if first_page['fields']:
        first_field = first_page['fields'][0]
        print(f"First field on page 1:")
        print(f"  Key: {first_field['key']}")
        print(f"  Type: {first_field['type']}")
        print(f"  Parent: {first_field['parent']}")
        print(f"  Child: {first_field['child']}")
        print(f"  Coordinates: {first_field['coordinates']}")


if __name__ == "__main__":
    main()
