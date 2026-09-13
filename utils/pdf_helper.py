"""
pdf_helper.py
High-Performance PDF Merging Engine.
Combines individual certificate PDFs into a single, multi-page PDF document.
"""

import os
import datetime
from typing import List
from PIL import Image

try:
    from pypdf import PdfWriter, PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfWriter, PdfReader
    except ImportError:
        PdfWriter = None
        PdfReader = None


def create_combined_pdf(pdf_filepaths: List[str], output_pdf_path: str, title: str = "Student Certificates") -> str:
    """Merge individual PDF files into a single multi-page PDF."""
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    valid_pdfs = [p for p in pdf_filepaths if p and os.path.exists(p) and p.lower().endswith('.pdf')]
    
    if not valid_pdfs:
        png_files = [p for p in pdf_filepaths if p and os.path.exists(p) and p.lower().endswith('.png')]
        if png_files:
            return convert_images_to_pdf(png_files, output_pdf_path)
        raise ValueError("No valid PDF certificate files provided for merging.")

    if PdfWriter is not None and PdfReader is not None:
        try:
            writer = PdfWriter()
            for p in valid_pdfs:
                reader = PdfReader(p)
                for page in reader.pages:
                    writer.add_page(page)
            writer.add_metadata({
                "/Title": title,
                "/Producer": "CertifyAI Engine",
                "/CreationDate": datetime.datetime.now().strftime("D:%Y%m%d%H%M%S")
            })
            with open(output_pdf_path, "wb") as f_out:
                writer.write(f_out)
            return output_pdf_path
        except Exception:
            pass

    return convert_images_to_pdf(valid_pdfs, output_pdf_path)


def convert_images_to_pdf(paths: List[str], output_pdf_path: str) -> str:
    """Fallback: Convert images or PDF pages to multi-page PDF using PIL."""
    pil_images: List[Image.Image] = []
    for path in paths:
        if not os.path.exists(path):
            continue
        try:
            if path.lower().endswith('.pdf'):
                import pdfplumber
                with pdfplumber.open(path) as pdf:
                    for page in pdf.pages:
                        pil_images.append(page.to_image(resolution=300).original.convert("RGB"))
            else:
                pil_images.append(Image.open(path).convert("RGB"))
        except Exception:
            continue

    if not pil_images:
        raise ValueError("Could not open any images/pages to create combined PDF.")

    pil_images[0].save(output_pdf_path, save_all=True, append_images=pil_images[1:], resolution=300.0, quality=95)
    return output_pdf_path
