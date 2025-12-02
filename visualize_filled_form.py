"""
Visualize Filled PDF Form
Renders the first page of the filled PDF to verify data entry.
"""

import fitz  # PyMuPDF
from PIL import Image

def visualize_filled_pdf(pdf_path: str, output_image: str):
    doc = fitz.open(pdf_path)
    page = doc[0]  # First page
    
    # Render at high resolution
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    # Crop to the area of interest (full by Seller field)
    # Rect: (91.23, 517.87, 96.91, 524.89)
    # Add some padding
    crop_box = (50, 480, 150, 560)
    
    # Scale crop box by zoom
    crop_coords = (
        int(crop_box[0] * zoom),
        int(crop_box[1] * zoom),
        int(crop_box[2] * zoom),
        int(crop_box[3] * zoom)
    )
    
    img_cropped = img.crop(crop_coords)
    img_cropped.save(output_image)
    print(f"Saved zoomed visualization to: {output_image}")

if __name__ == "__main__":
    visualize_filled_pdf("RF401_Filled_Form.pdf", "RF401_Filled_Form_Page1.png")
