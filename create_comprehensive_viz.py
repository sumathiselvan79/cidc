"""
Create a comprehensive visualization combining PDF page with field highlights and detailed field information.
"""

import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path


def create_comprehensive_visualization(pdf_path: str, json_path: str, page_number: int = 1):
    """
    Create a comprehensive visualization showing the PDF page with highlighted fields
    and a detailed field information panel.
    """
    # Open PDF
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    
    # Render page to image
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    pdf_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Load field data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find page data
    page_data = None
    for p in data['pages']:
        if p['page_number'] == page_number:
            page_data = p
            break
    
    if not page_data:
        print(f"No field data found for page {page_number}")
        return
    
    # Get widgets
    widgets = list(page.widgets())
    
    # Create drawing context for PDF image
    draw = ImageDraw.Draw(pdf_img, 'RGBA')
    
    # Color scheme
    type_colors = {
        1: ((255, 0, 0, 80), (255, 0, 0, 255), "Button"),
        2: ((0, 100, 255, 80), (0, 100, 255, 255), "Text"),
        3: ((0, 200, 0, 80), (0, 200, 0, 255), "Choice"),
        4: ((200, 0, 200, 80), (200, 0, 200, 255), "Signature"),
    }
    default_colors = ((255, 165, 0, 80), (255, 165, 0, 255), "Unknown")
    
    # Draw field highlights
    for idx, widget in enumerate(widgets):
        rect = widget.rect
        x0, y0, x1, y1 = rect.x0 * zoom, rect.y0 * zoom, rect.x1 * zoom, rect.y1 * zoom
        
        field_type = widget.field_type
        fill_color, outline_color, _ = type_colors.get(field_type, default_colors)
        
        # Draw rectangle
        draw.rectangle([x0, y0, x1, y1], fill=fill_color, outline=outline_color, width=4)
        
        # Draw field number in a circle
        circle_radius = 18
        circle_x = x0 + 5
        circle_y = y0 - 25
        
        # Draw circle background
        draw.ellipse(
            [circle_x - circle_radius, circle_y - circle_radius, 
             circle_x + circle_radius, circle_y + circle_radius],
            fill=(255, 255, 255, 255),
            outline=(0, 0, 0, 255),
            width=2
        )
        
        # Draw number
        label = str(idx + 1)
        # Center the text in the circle
        bbox = draw.textbbox((0, 0), label)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = circle_x - text_width // 2
        text_y = circle_y - text_height // 2 - 2
        draw.text((text_x, text_y), label, fill=(0, 0, 0, 255))
    
    # Create info panel
    panel_width = 800
    panel_height = pdf_img.height
    info_panel = Image.new('RGB', (panel_width, panel_height), color=(250, 250, 250))
    info_draw = ImageDraw.Draw(info_panel)
    
    # Draw header
    header_height = 100
    info_draw.rectangle([0, 0, panel_width, header_height], fill=(41, 128, 185))
    
    # Title
    info_draw.text((20, 15), f"Form Fields - Page {page_number}", fill=(255, 255, 255))
    info_draw.text((20, 45), f"Total Fields: {len(widgets)}", fill=(255, 255, 255))
    info_draw.text((20, 70), f"PDF: {Path(pdf_path).name[:50]}...", fill=(255, 255, 255))
    
    # Draw legend
    legend_y = header_height + 10
    info_draw.text((20, legend_y), "Legend:", fill=(0, 0, 0))
    
    legend_items = [
        ("Text Fields", (0, 100, 255)),
        ("Buttons/Checkboxes", (255, 0, 0)),
        ("Dropdowns/Choice", (0, 200, 0)),
        ("Signatures", (200, 0, 200)),
        ("Unknown Type", (255, 165, 0))
    ]
    
    legend_y += 25
    for label, color in legend_items:
        info_draw.rectangle([20, legend_y, 35, legend_y + 12], fill=color, outline=(0, 0, 0))
        info_draw.text((45, legend_y - 2), label, fill=(0, 0, 0))
        legend_y += 20
    
    # Draw field list
    list_start_y = legend_y + 20
    info_draw.rectangle([0, list_start_y, panel_width, list_start_y + 30], fill=(52, 73, 94))
    info_draw.text((20, list_start_y + 5), "Field Details", fill=(255, 255, 255))
    
    y_pos = list_start_y + 40
    line_height = 85
    
    for idx, field in enumerate(page_data['fields']):
        if y_pos + line_height > panel_height - 10:
            break  # Stop if we run out of space
        
        # Alternating background
        if idx % 2 == 0:
            info_draw.rectangle([0, y_pos - 5, panel_width, y_pos + line_height - 5], 
                              fill=(245, 245, 245))
        
        # Field number
        circle_x = 30
        circle_y = y_pos + 10
        circle_radius = 16
        
        field_type_num = 0
        for widget in widgets:
            if widget.field_name == field['key']:
                field_type_num = widget.field_type
                break
        
        _, circle_color, _ = type_colors.get(field_type_num, default_colors)
        
        info_draw.ellipse(
            [circle_x - circle_radius, circle_y - circle_radius,
             circle_x + circle_radius, circle_y + circle_radius],
            fill=circle_color,
            outline=(0, 0, 0),
            width=2
        )
        
        label = str(idx + 1)
        bbox = info_draw.textbbox((0, 0), label)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        info_draw.text((circle_x - text_width // 2, circle_y - text_height // 2 - 2), 
                      label, fill=(255, 255, 255))
        
        # Field information
        x_offset = 60
        
        # Field key (truncated)
        key_text = field['key']
        if len(key_text) > 60:
            key_text = key_text[:57] + "..."
        info_draw.text((x_offset, y_pos), f"Key: {key_text}", fill=(0, 0, 0))
        
        # Field type
        type_color = {
            'Text': (0, 100, 255),
            'Button': (255, 0, 0),
            'Choice': (0, 200, 0),
            'Signature': (200, 0, 200)
        }.get(field['type'], (255, 140, 0))
        
        info_draw.text((x_offset, y_pos + 20), f"Type: {field['type']}", fill=type_color)
        
        # Coordinates
        coords = field['coordinates']
        coord_text = f"Position: ({coords['x0']:.0f}, {coords['y0']:.0f}) to ({coords['x1']:.0f}, {coords['y1']:.0f})"
        info_draw.text((x_offset, y_pos + 40), coord_text, fill=(100, 100, 100))
        
        # Parent/Child
        parent_child = f"Parent: {field['parent'][:30]}"
        info_draw.text((x_offset, y_pos + 60), parent_child, fill=(100, 100, 100))
        
        y_pos += line_height
    
    # Combine images side by side
    total_width = pdf_img.width + panel_width
    combined = Image.new('RGB', (total_width, panel_height), color=(255, 255, 255))
    combined.paste(pdf_img, (0, 0))
    combined.paste(info_panel, (pdf_img.width, 0))
    
    # Save
    output_path = Path(pdf_path).stem + f"_page{page_number}_comprehensive.png"
    combined.save(output_path, "PNG")
    
    print(f"\nComprehensive visualization saved to: {output_path}")
    print(f"Image dimensions: {combined.width} x {combined.height} pixels")
    
    doc.close()
    return output_path


if __name__ == "__main__":
    pdf_file = "RF401_Updated August 17, 2024_Open Field Fill Form.pdf"
    json_file = "RF401_Updated August 17, 2024_Open Field Fill Form_fields.json"
    
    print("="*70)
    print("Creating Comprehensive Field Visualization")
    print("="*70)
    
    create_comprehensive_visualization(pdf_file, json_file, page_number=1)
    
    print("="*70)
    print("Complete!")
    print("="*70)
