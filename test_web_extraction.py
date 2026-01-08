#!/usr/bin/env python3
"""Test script to simulate web interface extraction and check folder creation."""

import os
import tempfile
import shutil
import zipfile
from app import CodeBlockExtractor

def test_web_extraction():
    """Simulate what the web interface does."""
    
    # Create temporary directories (like web interface does)
    temp_dir = tempfile.mkdtemp(prefix='test_code_extractor_')
    input_dir = os.path.join(temp_dir, 'input')
    output_dir = os.path.join(temp_dir, 'output')
    
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 Temp directory: {temp_dir}")
    print(f"📥 Input directory: {input_dir}")
    print(f"📤 Output directory: {output_dir}\n")
    
    # Copy test file to input
    test_file = 'AdGen2_formatted.md'
    shutil.copy(test_file, os.path.join(input_dir, test_file))
    
    # Process the file (like web interface does)
    extractor = CodeBlockExtractor(input_dir, output_dir)
    md_path = os.path.join(input_dir, test_file)
    extracted = extractor.extract_code_blocks(md_path)
    
    print(f"✅ Extracted {len(extracted)} code blocks\n")
    
    # Write files (like web interface does)
    stats = extractor.write_code_files(extracted)
    
    print(f"\n📊 Statistics:")
    print(f"   Total: {stats['total']}")
    print(f"   New files: {stats['new_files']}")
    print(f"   Modifications: {stats['modifications']}")
    print(f"   Generated: {stats['generated']}\n")
    
    # Check directory structure
    print("📂 Checking output directory structure:")
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = '  ' * level
        folder_name = os.path.basename(root)
        if folder_name == 'output':
            print(f"{indent}output/")
        else:
            print(f"{indent}├── {folder_name}/")
        
        sub_indent = '  ' * (level + 1)
        for file in files[:5]:  # Show first 5 files in each folder
            print(f"{sub_indent}├── {file}")
        if len(files) > 5:
            print(f"{sub_indent}└── ... ({len(files) - 5} more files)")
    
    # Create ZIP file (like web interface does)
    zip_path = os.path.join(temp_dir, 'test_output.zip')
    print(f"\n📦 Creating ZIP file: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
                print(f"   Added to ZIP: {arcname}")
    
    print(f"\n✅ ZIP file created: {zip_path}")
    print(f"   ZIP file size: {os.path.getsize(zip_path)} bytes")
    
    # List contents of ZIP to verify folder structure
    print(f"\n📋 Contents of ZIP file:")
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        for name in zipf.namelist()[:20]:  # Show first 20 files
            print(f"   {name}")
        if len(zipf.namelist()) > 20:
            print(f"   ... ({len(zipf.namelist()) - 20} more files)")
    
    print(f"\n🧹 Cleaning up temporary directory: {temp_dir}")
    # Don't clean up yet so user can inspect
    print(f"⚠️  NOT deleting temp dir so you can inspect it!")
    print(f"   To delete manually: rm -rf {temp_dir}")
    
    return temp_dir, zip_path

if __name__ == "__main__":
    print("🧪 Testing Web Interface Extraction\n")
    print("="*60)
    temp_dir, zip_path = test_web_extraction()
    print("="*60)
    print(f"\n✅ Test complete!")
    print(f"\n📍 Check these locations:")
    print(f"   Output folder: {os.path.join(temp_dir, 'output')}")
    print(f"   ZIP file: {zip_path}")

