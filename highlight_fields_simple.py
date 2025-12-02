"""
Simple PDF Field Highlighter - Shows only the PDF page with highlighted fillable fields.
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw


def highlight_fields_simple(pdf_path: str, page_number: int = 1, output_path: str = None):
    """
    Create a simple visualization showing only the PDF page with highlighted form fields.
    No text, no labels - just the fields highlighted with colored boxes.
    
    Args:
        pdf_path: Path to PDF file
        page_number: Page number (1-indexed)
        output_path: Output image path
    """
    # Open PDF
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    
    # Render at high resolution
    zoom = 2.5
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Create overlay for highlights
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Get widgets
    widgets = list(page.widgets())
    
    print(f"\nHighlighting {len(widgets)} fillable fields on page {page_number}")
    
    # Color scheme - semi-transparent highlights
    field_colors = {
        1: (255, 100, 100, 120),    # Button - Light Red
        2: (100, 150, 255, 120),    # Text - Light Blue  
        3: (100, 255, 150, 120),    # Choice - Light Green
        4: (255, 100, 255, 120),    # Signature - Light Magenta
    }
    
    # Border colors - more opaque
    border_colors = {
        1: (255, 0, 0, 255),        # Button - Red
        2: (0, 100, 255, 255),      # Text - Blue
        3: (0, 200, 100, 255),      # Choice - Green
        4: (200, 0, 200, 255),      # Signature - Magenta
    }
    
    default_fill = (255, 165, 0, 120)    # Orange
    default_border = (255, 140, 0, 255)
    
    # Draw highlights for each field
    for widget in widgets:
        rect = widget.rect
        x0 = rect.x0 * zoom
        y0 = rect.y0 * zoom
        x1 = rect.x1 * zoom
        y1 = rect.y1 * zoom
        
        field_type = widget.field_type
        fill = field_colors.get(field_type, default_fill)
        border = border_colors.get(field_type, default_border)
        
        # Draw filled rectangle with border
        draw.rectangle([x0, y0, x1, y1], fill=fill, outline=border, width=5)
    
    # Composite the overlay onto the original image
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    
    # Add a subtle legend in corner
    legend_x = 30
    legend_y = img.height - 180
    legend_bg = Image.new('RGBA', (280, 160), (255, 255, 255, 230))
    img.paste(legend_bg, (legend_x, legend_y), legend_bg)
    
    draw_final = ImageDraw.Draw(img)
    
    # Legend title
    draw_final.text((legend_x + 15, legend_y + 10), "Fillable Field Types:", fill=(0, 0, 0))
    
    # Legend items
    legend_items = [
        ("Text Input Fields", (0, 100, 255)),
        ("Checkboxes/Buttons", (255, 0, 0)),
        ("Dropdown Lists", (0, 200, 100)),
        ("Signature Fields", (200, 0, 200)),
    ]
    
    y = legend_y + 35
    for label, color in legend_items:
        # Color box
        draw_final.rectangle([legend_x + 15, y, legend_x + 35, y + 15], 
                           fill=color, outline=(0, 0, 0))
        # Label
        draw_final.text((legend_x + 45, y - 2), label, fill=(0, 0, 0))
        y += 28
    
    # Generate output path
    if output_path is None:
        from pathlib import Path
        output_path = Path(pdf_path).stem + f"_page{page_number}_fields_only.png"
    
    # Save
    img.save(output_path, "PNG", quality=95)
    
    print(f"SUCCESS: Saved to: {output_path}")
    print(f"  Image size: {img.width} x {img.height} pixels")
    print(f"  Fields highlighted: {len(widgets)}")
    
    doc.close()
    return output_path


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Default file
    pdf_file = "RF401_Updated August 17, 2024_Open Field Fill Form.pdf"
    page_num = 1
    
    # Check command line args
    if len(sys.argv) >= 2:
        pdf_file = sys.argv[1]
    if len(sys.argv) >= 3:
        page_num = int(sys.argv[2])
    
    if not Path(pdf_file).exists():
        print(f"Error: PDF not found: {pdf_file}")
        sys.exit(1)
    
    print("="*70)
    print("PDF Form Field Highlighter - Simple View")
    print("="*70)
    print(f"PDF: {pdf_file}")
    print(f"Page: {page_num}")
    print("="*70)
    
    highlight_fields_simple(pdf_file, page_num)
    
    print("="*70)
    print("Done!")
    print("="*70)
