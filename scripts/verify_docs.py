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


