#!/usr/bin/env python3
"""
============================================================================
CONSTITUTIONAL DOCUMENT DOWNLOADER
============================================================================
Downloads constitutional documents from official government sources.
Countries: United States, France, Germany, Pakistan, Norway, Canada

Usage:
    python scripts/download_docs.py              # Download all PDFs
    python scripts/download_docs.py --verify     # Verify existing downloads
    python scripts/download_docs.py --country usa  # Download single country

Author: [Your Name]
Date: 2026
============================================================================
"""

import argparse
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# DOCUMENT SOURCES
# Each country has a primary URL and fallback alternatives
# ============================================================

DOCUMENTS: Dict[str, Dict] = {
    "united_states": {
        "filename": "constitution_usa.pdf",
        "description": "Constitution of the United States of America",
        "primary_url": "https://www.govinfo.gov/content/pkg/CDOC-110hdoc50/pdf/CDOC-110hdoc50.pdf",
        "alternative_urls": [
            "https://constitutioncenter.org/media/files/constitution.pdf",
            "https://www.senate.gov/civics/resources/pdf/US_Constitution-Senate.pdf"
        ],
        "min_size_bytes": 500_000,  # 500 KB minimum
        "source": "U.S. Government Publishing Office"
    },
    "france": {
        "filename": "constitution_france.pdf",
        "description": "Constitution of France (Fifth Republic, 1958)",
        "primary_url": "https://www.conseil-constitutionnel.fr/sites/default/files/as/root/bank_mm/anglais/constiution_anglais_oct2009.pdf",
        "alternative_urls": [
            "https://www.elysee.fr/en/french-presidency/constitution-of-4-october-1958"
        ],
        "min_size_bytes": 200_000,
        "source": "Conseil Constitutionnel (France)"
    },
    "germany": {
        "filename": "constitution_germany.pdf",
        "description": "Basic Law for the Federal Republic of Germany",
        "primary_url": "https://www.btg-bestellservice.de/pdf/80201000.pdf",
        "alternative_urls": [
            "https://www.gesetze-im-internet.de/englisch_gg/englisch_gg.pdf"
        ],
        "min_size_bytes": 300_000,
        "source": "German Bundestag"
    },
    "pakistan": {
        "filename": "constitution_pakistan.pdf",
        "description": "Constitution of the Islamic Republic of Pakistan (1973)",
        "primary_url": "https://na.gov.pk/uploads/documents/1333523681_951.pdf",
        "alternative_urls": [
            "https://senate.gov.pk/uploads/documents/Constitution_of_Pakistan.pdf"
        ],
        "min_size_bytes": 500_000,
        "source": "National Assembly of Pakistan"
    },
    "norway": {
        "filename": "constitution_norway.pdf",
        "description": "Constitution of the Kingdom of Norway (1814)",
        "primary_url": "https://www.stortinget.no/globalassets/pdf/english/constitutionenglish.pdf",
        "alternative_urls": [
            "https://lovdata.no/dokument/NLE/lov/1814-05-17"
        ],
        "min_size_bytes": 200_000,
        "source": "Norwegian Parliament (Stortinget)"
    },
    "canada": {
        "filename": "constitution_canada.pdf",
        "description": "Constitution of Canada (Constitution Act, 1982)",
        "primary_url": "https://laws-lois.justice.gc.ca/PDF/CONST_E.pdf",
        "alternative_urls": [
            "https://laws-lois.justice.gc.ca/eng/const/"
        ],
        "min_size_bytes": 500_000,
        "source": "Justice Laws Website (Canada)"
    }
}
