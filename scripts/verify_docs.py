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

