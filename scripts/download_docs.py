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


class DocumentDownloader:
    """Professional downloader with retry, verification, and reporting."""
    
    def __init__(self, output_dir: str = "data/documents", verbose: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        # SSL context (government sites may have certificate issues)
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,application/octet-stream,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        }
    
    def log(self, message: str, level: str = "info"):
        """Conditional logging based on verbosity."""
        if self.verbose:
            print(message)
    
    def download_file(self, url: str, filepath: Path, description: str) -> Tuple[bool, str]:
        """
        Download a single file with progress tracking.
        
        Returns:
            Tuple of (success, message)
        """
        self.log(f"\n  Downloading: {description}")
        self.log(f"  URL: {url[:100]}...")
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=90) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                content_type = response.headers.get('Content-Type', 'unknown')
                
                # Verify it's a PDF or binary file
                if 'html' in content_type.lower():
                    return False, "Received HTML instead of PDF (possible redirect)"
                
                block_size = 16384
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    while True:
                        block = response.read(block_size)
                        if not block:
                            break
                        f.write(block)
                        downloaded += len(block)
                        
                        if total_size > 0 and self.verbose:
                            percent = (downloaded / total_size) * 100
                            bar_length = 40
                            filled = int(bar_length * downloaded // total_size)
                            bar = '█' * filled + '░' * (bar_length - filled)
                            sys.stdout.write(f'\r  [{bar}] {percent:6.1f}% ({downloaded:>10,} / {total_size:>10,} bytes)')
                            sys.stdout.flush()
                
                if total_size > 0:
                    sys.stdout.write('\n')
                
                actual_size = filepath.stat().st_size
                self.log(f"  SUCCESS: {actual_size:,} bytes downloaded")
                return True, f"Downloaded {actual_size:,} bytes"
                
        except urllib.error.HTTPError as e:
            return False, f"HTTP Error {e.code}: {e.reason}"
        except urllib.error.URLError as e:
            return False, f"URL Error: {e.reason}"
        except TimeoutError:
            return False, "Connection timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def verify_file(self, filepath: Path, min_size: int) -> Tuple[bool, str]:
        """Verify that a downloaded file is valid."""
        if not filepath.exists():
            return False, "File does not exist"
        
        size = filepath.stat().st_size
        if size < min_size:
            return False, f"File too small ({size:,} bytes < {min_size:,} bytes minimum)"
        
        # Check if it starts with PDF magic bytes
        with open(filepath, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                return False, "File is not a valid PDF (wrong file format)"
        
        return True, f"Valid PDF ({size:,} bytes)"
    
    def download_country(self, country_key: str) -> Tuple[bool, str]:
        """
        Download a single country's constitution.
        
        Returns:
            Tuple of (success, message)
        """
        if country_key not in DOCUMENTS:
            return False, f"Unknown country: {country_key}"
        
        doc = DOCUMENTS[country_key]
        filepath = self.output_dir / doc['filename']
        
        # Check if already exists and valid
        valid, message = self.verify_file(filepath, doc['min_size_bytes'])
        if valid:
            return True, f"Already exists — {message}"
        
        # Try primary URL
        success, message = self.download_file(
            doc['primary_url'],
            filepath,
            f"{doc['description']} (from {doc['source']})"
        )
        
        if success and self.verify_file(filepath, doc['min_size_bytes'])[0]:
            return True, message
        
        # Try alternatives
        for i, alt_url in enumerate(doc['alternative_urls'], 1):
            self.log(f"\n  Primary failed. Trying alternative {i}...")
            success, message = self.download_file(
                alt_url,
                filepath,
                f"{doc['description']} (alternative {i})"
            )
            
            if success and self.verify_file(filepath, doc['min_size_bytes'])[0]:
                return True, f"Downloaded via alternative {i}"
        
        # Clean up partial download
        if filepath.exists():
            filepath.unlink()
        
        return False, "All download attempts failed"
    
    def download_all(self) -> Dict[str, Tuple[bool, str]]:
        """Download all constitutional documents."""
        print("=" * 70)
        print("CONSTITUTIONAL DOCUMENT DOWNLOADER")
        print("=" * 70)
        print(f"Countries: {', '.join(DOCUMENTS.keys())}")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Total documents: {len(DOCUMENTS)}")
        print("=" * 70)
        
        results = {}
        
        for country_key in DOCUMENTS:
            print(f"\n{'─' * 70}")
            print(f"[{country_key.upper()}]")
            
            success, message = self.download_country(country_key)
            results[country_key] = (success, message)
            
            status = "DONE" if success else "FAILED"
            print(f"  STATUS: {status}")
            print(f"  DETAIL: {message}")
        
        return results
    
    