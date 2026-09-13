"""
test_core.py
Unit test for data extraction, certificate rendering, combined multi-page PDF, and zip archiving.
"""

import os
import json
from utils.data_extractor import extract_student_data, extract_from_raw_text
from utils.certificate_maker import (
    generate_single_certificate, 
    generate_preview_base64,
    extract_template_palette
)
from utils.pdf_helper import create_combined_pdf
from utils.zip_helper import create_certificates_zip

def run_tests():
    print("Testing data extraction...")
    excel_path = os.path.join("sample_data", "sample_students.xlsx")
    csv_path = os.path.join("sample_data", "sample_students.csv")
    pdf_path = os.path.join("sample_data", "sample_students.pdf")

    # 1. Test Excel extraction
    records_xlsx, stats_xlsx = extract_student_data(excel_path)
    print(f"Excel Extraction: {len(records_xlsx)} records extracted. Stats: {stats_xlsx['valid_rows']} valid.")
    assert len(records_xlsx) == 10, f"Expected 10 records, got {len(records_xlsx)}"

    # 2. Test CSV extraction
    records_csv, stats_csv = extract_student_data(csv_path)
    print(f"CSV Extraction: {len(records_csv)} records extracted.")
    assert len(records_csv) == 10, f"Expected 10 records, got {len(records_csv)}"

    # 3. Test PDF extraction
    records_pdf, stats_pdf = extract_student_data(pdf_path)
    print(f"PDF Extraction: {len(records_pdf)} records extracted.")
    assert len(records_pdf) == 10, f"Expected 10 records, got {len(records_pdf)}"

    # 4. Test Raw Text / Clipboard Extraction
    raw_sample = "Name\tCourse\tDate\tGrade\tCertID\nAlice Vance\tData Science\t2026-03-01\tA+\tCERT-9901\nBob Smith\tCybersecurity\t2026-03-02\tA\tCERT-9902"
    records_raw, stats_raw = extract_from_raw_text(raw_sample)
    print(f"Raw Text Extraction: {len(records_raw)} records extracted.")
    assert len(records_raw) == 2, f"Expected 2 records, got {len(records_raw)}"
    assert records_raw[0]["NAME"] == "Alice Vance"

    # 5. Test Template Palette Extraction
    template_path = os.path.join("static", "sample_templates", "classic_gold.png")
    palette_info = extract_template_palette(template_path)
    assert "palette" in palette_info and len(palette_info["palette"]) > 0
    print(f"Template Palette Extracted: {palette_info['palette'][:3]} ({palette_info['width']}x{palette_info['height']})")

    # 6. Test Certificate Generation with Dynamic Fields & QR
    with open("config.json", "r") as f:
        config = json.load(f)
    
    fields_config = config["templates"]["classic_gold.png"]["fields"].copy()
    fields_config["INSTITUTE"] = { "x": 960, "y": 800, "font_size": 22, "color": "#1A2530", "alignment": "center" }
    fields_config["QR_CODE"] = { "x": 300, "y": 850, "type": "qr", "font_size": 120 }

    output_dir = os.path.join("generated_certificates", "test_batch")
    gen_results_1 = generate_single_certificate(
        template_path=template_path,
        student_data=records_xlsx[0],
        config_fields=fields_config,
        output_dir=output_dir,
        export_format="both"
    )
    gen_results_2 = generate_single_certificate(
        template_path=template_path,
        student_data=records_xlsx[1],
        config_fields=fields_config,
        output_dir=output_dir,
        export_format="both"
    )
    print(f"Generated single certificate outputs: {gen_results_1}")
    assert os.path.exists(gen_results_1["pdf"]), "PDF certificate was not generated"
    assert os.path.exists(gen_results_1["png"]), "PNG certificate was not generated"

    # 7. Test Combined Multi-Page PDF Creation
    combined_pdf_path = os.path.join("generated_certificates", "test_combined.pdf")
    create_combined_pdf([gen_results_1["pdf"], gen_results_2["pdf"]], combined_pdf_path)
    assert os.path.exists(combined_pdf_path), "Combined multi-page PDF was not created"
    print(f"Combined Multi-Page PDF generated at: {combined_pdf_path} ({os.path.getsize(combined_pdf_path)} bytes)")

    # 8. Test Preview Base64 Generation
    preview_b64 = generate_preview_base64(template_path, records_xlsx[1], fields_config)
    assert preview_b64.startswith("data:image/jpeg;base64,"), "Preview data URI invalid"
    print(f"Preview Base64 generated successfully (length: {len(preview_b64)})")

    # 9. Test ZIP Helper
    zip_path = os.path.join("generated_certificates", "test_batch.zip")
    create_certificates_zip([gen_results_1["pdf"], gen_results_1["png"], gen_results_2["pdf"], gen_results_2["png"]], zip_path)
    assert os.path.exists(zip_path), "ZIP archive was not generated"
    print(f"ZIP archive verified at: {zip_path}")

    print("\n--- ALL CORE TESTS PASSED SUCCESSFULLY! ---")

if __name__ == "__main__":
    run_tests()
