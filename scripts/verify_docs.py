#!/usr/bin/env python3
"""
Verify downloaded constitutional documents.
Checks file existence, size, and PDF validity.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REQUIRED_DOCUMENTS = {
    "constitution_usa.pdf": {
        "country": "United States",
        "min_size": 500_000,
        "description": "US Constitution"
    },
    "constitution_france.pdf": {
        "country": "France",
        "min_size": 200_000,
        "description": "French Constitution (1958)"
    },
    "constitution_germany.pdf": {
        "country": "Germany",
        "min_size": 300_000,
        "description": "German Basic Law"
    },
    "constitution_pakistan.pdf": {
        "country": "Pakistan",
        "min_size": 500_000,
        "description": "Constitution of Pakistan"
    },
    "constitution_norway.pdf": {
        "country": "Norway",
        "min_size": 200_000,
        "description": "Norwegian Constitution"
    },
    "constitution_canada.pdf": {
        "country": "Canada",
        "min_size": 500_000,
        "description": "Constitution of Canada"
    }
}

def verify_pdf(filepath: Path) -> Tuple[bool, str]:
    """Verify that a file is a valid PDF."""
    if not filepath.exists():
        return False, "File does not exist"
    
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False, "Not a valid PDF (missing PDF header)"
            
            # Check for EOF marker
            f.seek(-32, os.SEEK_END)
            footer = f.read()
            if b'%%EOF' not in footer:
                return False, "Not a valid PDF (missing EOF marker)"
        
        size = filepath.stat().st_size
        return True, f"Valid PDF ({size:,} bytes)"
    
    except Exception as e:
        return False, f"Error: {str(e)}"



def verify_all(data_dir: str = "data/documents") -> Dict:
    """Verify all required documents."""
    print("=" * 70)
    print("DOCUMENT VERIFICATION REPORT")
    print("=" * 70)
    
    results = {}
    
    for filename, info in REQUIRED_DOCUMENTS.items():
        filepath = Path(data_dir) / filename
        
        # Check existence
        if not filepath.exists():
            results[filename] = {
                'exists': False,
                'valid_pdf': False,
                'size_ok': False,
                'message': 'MISSING'
            }
            print(f"\n  [MISSING] {filename}")
            print(f"    Country: {info['country']}")
            print(f"    Expected: {info['description']}")
            print(f"    Min size: {info['min_size']:,} bytes")
            continue
        
        # Check size
        size = filepath.stat().st_size
        size_ok = size >= info['min_size']
        
        # Check PDF validity
        valid, pdf_message = verify_pdf(filepath)
        
        results[filename] = {
            'exists': True,
            'size': size,
            'valid_pdf': valid,
            'size_ok': size_ok,
            'message': pdf_message
        }
        
        # Print result
        status = "VALID" if (valid and size_ok) else "PROBLEM"
        print(f"\n  [{status}] {filename}")
        print(f"    Country: {info['country']}")
        print(f"    Size: {size:,} bytes (min: {info['min_size']:,})")
        print(f"    PDF Check: {pdf_message}")
        
        if not size_ok:
            print(f"    WARNING: File may be incomplete or truncated")
    
    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print("=" * 70)
    
    total = len(REQUIRED_DOCUMENTS)
    valid = sum(1 for r in results.values() if r.get('exists') and r.get('valid_pdf') and r.get('size_ok'))
    
    print(f"  Total required: {total}")
    print(f"  Valid documents: {valid}")
    print(f"  Missing/Invalid: {total - valid}")
    
    if valid == total:
        print("\n  ALL DOCUMENTS READY.")
        print("  Next step: python src/ingest.py")
        return results
    
    print("\n  DOCUMENTS NEEDING ATTENTION:")
    for filename, result in results.items():
        if not (result.get('exists') and result.get('valid_pdf') and result.get('size_ok')):
            print(f"    - {filename}")
    
    return results


if __name__ == "__main__":
    verify_all()