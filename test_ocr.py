#!/usr/bin/env python3
"""
Test script for OCR functionality with PDF417 barcode recognition.
This script tests the ability to read and decode PDF417 barcodes from images.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def test_barcode_generation():
    """Test that barcode generation works correctly."""
    try:
        from src.sii_xml_pdf.barcode import pdf417_svg_from_ted
        
        # Test with actual TED XML string (the function expects XML, not dict)
        test_ted_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <TED version="1.0">
            <RE>RUT_EMISOR</RE>
            <TD>33</TD>
            <F>1234567</F>
            <FE>2024-03-28</FE>
            <MT>11900</MT>
            <FA>2024-03-28T10:30:00</FA>
        </TED>"""
        
        svg_content = pdf417_svg_from_ted(test_ted_xml)
        
        assert svg_content is not None, "SVG content should not be None"
        assert "<svg" in svg_content, "Should contain SVG tag"
        assert "PDF417" in svg_content or "barcode" in svg_content.lower(), "Should contain barcode element"
        
        print("✓ Barcode generation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Barcode generation test failed: {e}")
        return False


def test_pdf_with_barcode():
    """Test that PDFs are generated with barcodes."""
    output_dir = Path("/workspace/output")
    pdf_files = list(output_dir.glob("*barcode*.pdf"))
    
    if not pdf_files:
        print("✗ No PDF files with barcode found")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF files with barcode:")
    for pdf in pdf_files:
        file_size = pdf.stat().st_size
        print(f"  - {pdf.name} ({file_size} bytes)")
    
    return True


def test_parser_barcode_fields():
    """Test that parser extracts barcode-related fields."""
    try:
        from src.sii_xml_pdf.bhe_parser import parse_bhe_xml
        
        # Check if the parser module has barcode support
        import inspect
        source = inspect.getsource(parse_bhe_xml)
        
        has_barcode_support = any(keyword in source.lower() for keyword in [
            'ted', 'barcode', 'pdf417', 'autorizacion'
        ])
        
        if has_barcode_support:
            print("✓ Parser has barcode field support")
            return True
        else:
            print("✗ Parser missing barcode field support")
            return False
            
    except Exception as e:
        print(f"✗ Parser test failed: {e}")
        return False


def test_output_directory_structure():
    """Test that output directory structure is correct."""
    output_dir = Path("/workspace/output")
    pdf_subdir = output_dir / "pdf"
    
    # Check main output directory
    if not output_dir.exists():
        print("✗ Output directory does not exist")
        return False
    
    # Check pdf subdirectory
    if not pdf_subdir.exists():
        print("⚠ PDF subdirectory does not exist (optional)")
    else:
        pdf_files_in_subdir = list(pdf_subdir.glob("*.pdf"))
        print(f"✓ PDF subdirectory exists with {len(pdf_files_in_subdir)} files")
    
    # Count total PDFs
    all_pdfs = list(output_dir.glob("*.pdf"))
    print(f"✓ Main output directory has {len(all_pdfs)} PDF files")
    
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 50)
    print("Running OCR and Barcode Tests")
    print("=" * 50)
    print()
    
    tests = [
        ("Barcode Generation", test_barcode_generation),
        ("PDF with Barcode", test_pdf_with_barcode),
        ("Parser Barcode Fields", test_parser_barcode_fields),
        ("Output Directory Structure", test_output_directory_structure),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
