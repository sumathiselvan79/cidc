# PDF Form Field Extractor

Extract fillable form fields from PDF documents and save them in hierarchical JSON format.

## Features

- ✅ Extracts all fillable form fields from PDF documents
- ✅ Organizes fields hierarchically (Page → Parent → Child)
- ✅ Captures field metadata:
  - Field type (Text, Button, Choice, Signature)
  - Coordinates (x0, y0, x1, y1)
  - Field labels and values
  - Required/Readonly flags
  - Choice options (for dropdowns)
- ✅ Outputs structured JSON with complete field information
- ✅ Supports complex form hierarchies with dot notation

## Installation

Install the required packages:

```bash
pip install -r requirements_pdf_extractor.txt
```

Or install manually:

```bash
pip install PyMuPDF pdfplumber
```

## Usage

### Basic Usage

```bash
python extract_pdf_fields.py <pdf_file_path>
```

This will create a JSON file with the same name as the PDF (e.g., `form.pdf` → `form_fields.json`)

### Specify Output File

```bash
python extract_pdf_fields.py <pdf_file_path> <output_json_path>
```

### Examples

```bash
# Extract fields from a patient form
python extract_pdf_fields.py patientform-1.pdf

# Extract and save to custom location
python extract_pdf_fields.py patientform-1.pdf extracted_fields.json
```

## Output Format

The JSON output has the following hierarchical structure:

```json
{
  "pdf_name": "example.pdf",
  "total_pages": 2,
  "pages": [
    {
      "page_number": 1,
      "page_dimensions": {
        "width": 612.0,
        "height": 792.0
      },
      "fields": [
        {
          "key": "Section1.FirstName",
          "parent": "Section1",
          "child": "FirstName",
          "type": "Text",
          "coordinates": {
            "x0": 100.5,
            "y0": 200.3,
            "x1": 300.7,
            "y1": 220.5
          },
          "field_label": "First Name",
          "field_value": "",
          "field_flags": 0,
          "is_required": false,
          "is_readonly": false
        }
      ]
    }
  ],
  "hierarchy": {
    "root": {
      "children": ["Section1", "Section2"],
      "fields": []
    },
    "Section1": {
      "children": [],
      "fields": [
        {
          "page": 1,
          "key": "Section1.FirstName",
          "type": "Text"
        }
      ]
    }
  }
}
```

## Field Types

- **Text**: Text input fields
- **Button**: Checkboxes, radio buttons, push buttons
- **Choice**: Dropdown menus and list boxes
- **Signature**: Signature fields

## Hierarchical Organization

Fields are organized in three levels:

1. **Page Number**: Which page the field appears on
2. **Parent**: Parent section/group (parsed from field name using dot notation)
3. **Child**: The actual field name

For example, a field named `PersonalInfo.Address.Street` would be organized as:
- Parent: `PersonalInfo.Address`
- Child: `Street`

## Programmatic Usage

You can also use the extractor in your Python code:

```python
from extract_pdf_fields import PDFFieldExtractor

# Create extractor instance
extractor = PDFFieldExtractor("form.pdf")

# Extract fields
fields_data = extractor.extract_fields()

# Save to JSON
extractor.save_to_json("output.json")

# Or work with the data directly
for page in fields_data["pages"]:
    print(f"Page {page['page_number']} has {len(page['fields'])} fields")
    for field in page["fields"]:
        print(f"  - {field['key']} ({field['type']})")
```

## Notes

- The script uses **PyMuPDF (fitz)** as the primary extraction engine
- Only pages containing form fields are included in the output
- Field coordinates are in PDF coordinate system (bottom-left origin)
- Hierarchical relationships are automatically parsed from field names
- Fields without a parent are assigned to "root"

## Troubleshooting

**No fields extracted?**
- Ensure the PDF actually contains fillable form fields (not just text)
- Some PDFs may have scanned forms without actual form fields

**Missing field names?**
- Some PDFs may have unnamed fields; these will be auto-generated as `unnamed_field_<id>`

**Incorrect hierarchy?**
- The hierarchy is parsed from field names using dot notation
- If your PDF uses a different naming convention, you may need to adjust the `_parse_field_hierarchy` method
