"""
zip_helper.py
Helper module to archive generated certificates into a ZIP file.
"""

import os
import zipfile
from typing import List, Optional


def create_certificates_zip(file_paths: List[str], zip_output_path: str, compression: int = zipfile.ZIP_DEFLATED) -> str:
    """Compress list of file paths into a single zip file."""
    os.makedirs(os.path.dirname(os.path.abspath(zip_output_path)), exist_ok=True)
    with zipfile.ZipFile(zip_output_path, 'w', compression=compression) as zipf:
        for f in file_paths:
            if os.path.exists(f):
                zipf.write(f, arcname=os.path.basename(f))
    return zip_output_path


def zip_directory_contents(directory_path: str, zip_output_path: str, allowed_extensions: Optional[List[str]] = None) -> str:
    """Archive matching files in directory into a zip file."""
    allowed = [e.lower() for e in allowed_extensions] if allowed_extensions else ['.pdf', '.png', '.jpg', '.jpeg']
    files_to_zip = []
    if os.path.exists(directory_path):
        for root, _, files in os.walk(directory_path):
            for file in files:
                if os.path.splitext(file)[1].lower() in allowed:
                    files_to_zip.append(os.path.join(root, file))
    return create_certificates_zip(files_to_zip, zip_output_path)
