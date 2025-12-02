"""
PDF Form Field Visualizer
Renders a PDF page and highlights all fillable form fields with colored bounding boxes.
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path


def visualize_pdf_fields(pdf_path: str, page_number: int = 1, output_image: str = None):
    """
    Visualize form fields on a PDF page by highlighting them with colored boxes.
    
    Args:
        pdf_path: Path to the PDF file
        page_number: Page number to visualize (1-indexed)
        output_image: Path to save the output image (optional)
    
    Returns:
        Path to the saved image
    """
    # Open PDF
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]  # Convert to 0-indexed
    
    # Render page to image at high resolution
    zoom = 2.0  # Increase resolution
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Create drawing context
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Get all widgets (form fields) on the page
    widgets = list(page.widgets())
    
    print(f"\nVisualizing {len(widgets)} fields on page {page_number}")
    
    # Color scheme for different field types
    colors = {
        1: (255, 0, 0, 100),      # Button - Red
        2: (0, 0, 255, 100),      # Text - Blue
        3: (0, 255, 0, 100),      # Choice - Green
        4: (255, 0, 255, 100),    # Signature - Magenta
    }
    
    outline_colors = {
        1: (255, 0, 0, 255),      # Button - Red
        2: (0, 0, 255, 255),      # Text - Blue
        3: (0, 255, 0, 255),      # Choice - Green
        4: (255, 0, 255, 255),    # Signature - Magenta
    }
    
    default_color = (255, 165, 0, 100)  # Orange for unknown
    default_outline = (255, 165, 0, 255)
    
    # Draw rectangles for each field
    for idx, widget in enumerate(widgets):
        rect = widget.rect
        
        # Scale coordinates by zoom factor
        x0 = rect.x0 * zoom
        y0 = rect.y0 * zoom
        x1 = rect.x1 * zoom
        y1 = rect.y1 * zoom
        
        # Get field type
        field_type = widget.field_type
        fill_color = colors.get(field_type, default_color)
        outline_color = outline_colors.get(field_type, default_outline)
        
        # Draw filled rectangle with transparency
        draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=outline_color, width=3)
        
        # Add field number label
        label_text = f"{idx + 1}"
        
        # Draw label background
        label_bg_coords = [x0, y0 - 25, x0 + 30, y0]
        draw.rectangle(label_bg_coords, fill=(255, 255, 255, 200))
        
        # Draw label text
        draw.text((x0 + 5, y0 - 20), label_text, fill=(0, 0, 0, 255))
    
    # Add legend
    legend_x = 20
    legend_y = 20
    legend_width = 200
    legend_height = 150
    
    # Legend background
    draw.rectangle(
        [legend_x, legend_y, legend_x + legend_width, legend_y + legend_height],
        fill=(255, 255, 255, 230),
        outline=(0, 0, 0, 255),
        width=2
    )
    
    # Legend title
    draw.text((legend_x + 10, legend_y + 10), "Field Types:", fill=(0, 0, 0, 255))
    
    # Legend items
    legend_items = [
        ("Text Fields", (0, 0, 255, 255)),
        ("Buttons/Checkboxes", (255, 0, 0, 255)),
        ("Dropdowns", (0, 255, 0, 255)),
        ("Signatures", (255, 0, 255, 255)),
        ("Unknown", (255, 165, 0, 255))
    ]
    
    y_offset = 35
    for label, color in legend_items:
        # Color box
        draw.rectangle(
            [legend_x + 10, legend_y + y_offset, legend_x + 25, legend_y + y_offset + 15],
            fill=color,
            outline=(0, 0, 0, 255)
        )
        # Label
        draw.text((legend_x + 30, legend_y + y_offset), label, fill=(0, 0, 0, 255))
        y_offset += 22
    
    # Generate output filename if not provided
    if output_image is None:
        output_image = Path(pdf_path).stem + f"_page{page_number}_fields_highlighted.png"
    
    # Save image
    img.save(output_image, "PNG")
    print(f"\nVisualization saved to: {output_image}")
    print(f"Image size: {img.width} x {img.height} pixels")
    
    # Close PDF
    doc.close()
    
    return output_image


def create_field_list_image(json_path: str, page_number: int = 1, output_image: str = None):
    """
    Create an image showing the list of fields on a page.
    
    Args:
        json_path: Path to the extracted fields JSON
        page_number: Page number to list fields for
        output_image: Path to save the output image
    """
    # Load JSON data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find the page
    page_data = None
    for page in data['pages']:
        if page['page_number'] == page_number:
            page_data = page
            break
    
    if not page_data:
        print(f"Page {page_number} not found in JSON")
        return
    
    # Create image
    img_width = 1200
    line_height = 30
    header_height = 80
    img_height = header_height + (len(page_data['fields']) * line_height) + 40
    
    img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw header
    draw.rectangle([0, 0, img_width, header_height], fill=(70, 130, 180))
    draw.text((20, 15), f"Form Fields - Page {page_number}", fill=(255, 255, 255))
    draw.text((20, 45), f"Total Fields: {len(page_data['fields'])}", fill=(255, 255, 255))
    
    # Draw field list
    y_pos = header_height + 20
    for idx, field in enumerate(page_data['fields']):
        # Alternate row colors
        if idx % 2 == 0:
            draw.rectangle([0, y_pos - 5, img_width, y_pos + line_height - 5], fill=(240, 240, 240))
        
        # Field number
        draw.text((20, y_pos), f"{idx + 1}.", fill=(0, 0, 0))
        
        # Field key (truncate if too long)
        field_key = field['key']
        if len(field_key) > 80:
            field_key = field_key[:77] + "..."
        draw.text((60, y_pos), field_key, fill=(0, 0, 0))
        
        # Field type
        type_color = {
            'Text': (0, 0, 255),
            'Button': (255, 0, 0),
            'Choice': (0, 128, 0),
            'Signature': (128, 0, 128)
        }.get(field['type'], (255, 140, 0))
        
        draw.text((1000, y_pos), f"[{field['type']}]", fill=type_color)
        
        y_pos += line_height
    
    # Generate output filename if not provided
    if output_image is None:
        output_image = Path(json_path).stem + f"_page{page_number}_field_list.png"
    
    # Save image
    img.save(output_image, "PNG")
    print(f"Field list saved to: {output_image}")
    
    return output_image


def main():
    """Main execution function."""
    import sys
    
    # Configuration
    pdf_file = "RF401_Updated August 17, 2024_Open Field Fill Form.pdf"
    json_file = "RF401_Updated August 17, 2024_Open Field Fill Form_fields.json"
    page_num = 1
    
    # Check if PDF exists
    if not Path(pdf_file).exists():
        print(f"Error: PDF file not found: {pdf_file}")
        if len(sys.argv) >= 2:
            pdf_file = sys.argv[1]
            if not Path(pdf_file).exists():
                print(f"Error: PDF file not found: {pdf_file}")
                return
    
    # Get page number from command line if provided
    if len(sys.argv) >= 3:
        page_num = int(sys.argv[2])
    
    print(f"{'='*60}")
    print(f"PDF Form Field Visualizer")
    print(f"{'='*60}")
    print(f"PDF: {pdf_file}")
    print(f"Page: {page_num}")
    print(f"{'='*60}")
    
    # Create visualization
    output1 = visualize_pdf_fields(pdf_file, page_num)
    
    # Create field list if JSON exists
    if Path(json_file).exists():
        output2 = create_field_list_image(json_file, page_num)
    
    print(f"\n{'='*60}")
    print("Visualization complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
