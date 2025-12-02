# Quick Start Guide - PDF Form Field Extractor

## 📋 What This Does
Extracts fillable form fields from PDF documents and saves them in hierarchical JSON format with:
- Page numbers
- Parent-child relationships
- Field types (Text, Button, Choice, Signature)
- Coordinates (x0, y0, x1, y1)
- Field metadata (labels, values, flags)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install PyMuPDF pdfplumber
```

### 2. Extract Fields from a PDF
```bash
python extract_pdf_fields.py "your_form.pdf"
```

This creates: `your_form_fields.json`

### 3. Specify Custom Output
```bash
python extract_pdf_fields.py "your_form.pdf" "output.json"
```

## 📁 Files Created

### Core Scripts
- **extract_pdf_fields.py** - Main extraction script
- **example_usage.py** - Advanced usage examples

### Documentation
- **README_PDF_EXTRACTOR.md** - Full documentation
- **EXTRACTION_SUMMARY.md** - Detailed summary
- **THIS FILE** - Quick reference

### Requirements
- **requirements_pdf_extractor.txt** - Package dependencies

## 📊 Test Results (Your PDF)

**File**: RF401_Updated August 17, 2024_Open Field Fill Form.pdf
- ✅ Total Pages: 11
- ✅ Pages with Fields: 11
- ✅ Total Fields Extracted: 145
- ✅ Field Types: Text (34), Unknown (111)

### Generated Output Files:
1. **_fields.json** (98 KB) - Full extraction
2. **_field_names.json** (8 KB) - Simplified field list
3. **_hierarchical.json** (45 KB) - Parent-child structure
4. **_full_extraction.json** (98 KB) - Complete with hierarchy

## 🔍 JSON Structure

### Basic Structure
```json
{
  "pdf_name": "form.pdf",
  "total_pages": 11,
  "pages": [
    {
      "page_number": 1,
      "fields": [
        {
          "key": "field_name",
          "parent": "section_name",
          "child": "field_name",
          "type": "Text",
          "coordinates": {"x0": 72.96, "y0": 164.04, "x1": 427.92, "y1": 174.6},
          "field_label": "Field Label",
          "is_required": false,
          "is_readonly": false
        }
      ]
    }
  ]
}
```

## 💻 Programmatic Usage

```python
from extract_pdf_fields import PDFFieldExtractor

# Extract fields
extractor = PDFFieldExtractor("form.pdf")
data = extractor.extract_fields()

# Save to JSON
extractor.save_to_json("output.json")

# Access fields
for page in data["pages"]:
    print(f"Page {page['page_number']}: {len(page['fields'])} fields")
    for field in page["fields"]:
        print(f"  - {field['key']} ({field['type']})")
```

## 📝 Field Information Captured

Each field includes:
- **key**: Full field identifier
- **parent**: Parent section (or "root")
- **child**: Child field name
- **type**: Text, Button, Choice, Signature, Unknown
- **coordinates**: Position on page (x0, y0, x1, y1)
- **field_label**: Human-readable label
- **field_value**: Current value (if any)
- **is_required**: Required flag
- **is_readonly**: Readonly flag
- **choices**: Options (for dropdown/choice fields)

## 🎯 Use Cases

1. **Form Analysis**: Understand form structure
2. **Data Mapping**: Map fields to database schemas
3. **Automation**: Auto-fill forms programmatically
4. **Documentation**: Generate field inventories
5. **Validation**: Verify form completeness

## ⚙️ Advanced Features

### Run Example Script
```bash
python example_usage.py
```

This generates:
- Full extraction with statistics
- Simplified field names
- Hierarchical structure
- Field analysis report

### Custom Hierarchy Parsing
Edit `_parse_field_hierarchy()` method in `extract_pdf_fields.py` to customize how parent-child relationships are detected.

## 🔧 Troubleshooting

**No fields extracted?**
- Ensure PDF has actual fillable form fields (not just scanned images)

**Wrong hierarchy?**
- Check if PDF uses dot notation (e.g., "Section.Field")
- Modify `_parse_field_hierarchy()` for custom patterns

**Unknown field types?**
- These are custom or non-standard PDF widgets
- Check the field_flags value for more info

## 📚 More Information

See **README_PDF_EXTRACTOR.md** for:
- Detailed usage instructions
- Output format specifications
- Troubleshooting guide
- Programmatic examples

See **EXTRACTION_SUMMARY.md** for:
- Technical details
- Test results
- Feature overview
- Enhancement ideas

## 🎉 Success!

Your PDF form fields have been successfully extracted and organized hierarchically!

**Next Steps:**
1. Review the generated JSON files
2. Use the data for your application
3. Customize the extraction as needed
4. Integrate into your workflow
