"""
Cleanup Workspace
Removes generated files (JSON, PNG, Filled PDFs) to clean up the directory.
Keeps source code (.py), documentation (.md), and original PDFs.
"""

import os
from pathlib import Path

def cleanup():
    current_dir = Path(".")
    print(f"Cleaning up directory: {current_dir.absolute()}")
    print("-" * 60)
    
    # patterns to remove
    patterns = [
        "*_fields.json",           # Extracted fields
        "*_field_names.json",      # Simplified field lists
        "*_hierarchical.json",     # Hierarchical data
        "*_full_extraction.json",  # Full extraction data
        "*_Filled.pdf",            # Filled PDFs
        "RF401_Filled_Form.pdf",   # Legacy filled PDF name
        "*.png",                   # All visualizations
        "__pycache__"              # Python cache
    ]
    
    removed_count = 0
    
    for pattern in patterns:
        for file_path in current_dir.glob(pattern):
            try:
                if file_path.is_dir():
                    # Handle directories like __pycache__
                    import shutil
                    shutil.rmtree(file_path)
                    print(f"Removed directory: {file_path.name}")
                else:
                    os.remove(file_path)
                    print(f"Removed file: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing {file_path.name}: {e}")
    
    print("-" * 60)
    print(f"Cleanup complete! Removed {removed_count} items.")
    print("Kept source code, documentation, and original PDFs.")

if __name__ == "__main__":
    cleanup()
