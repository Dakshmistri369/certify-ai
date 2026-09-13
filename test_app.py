"""
test_app.py
Comprehensive integration test suite for Flask Web Application & API endpoints.
Tests multi-format data ingestion, raw clipboard parsing, template palette extraction,
single PDF streaming, and combined multi-page PDF generation & download.
"""

import os
import json
import io
from app import app, GENERATED_DIR, CONFIG_FILE

def test_endpoints():
    app.config['TESTING'] = True
    client = app.test_client()

    print("\n[1] Testing GET web pages...")
    # Test index page
    res = client.get('/')
    assert res.status_code == 200, "GET / failed"
    assert b"Certificate" in res.data
    print("  [PASS] GET / (Home/Generator page) OK")

    # Test preview page
    res = client.get('/preview')
    assert res.status_code == 200, "GET /preview failed"
    print("  [PASS] GET /preview (Inspector page) OK")

    # Test dashboard page
    res = client.get('/dashboard')
    assert res.status_code == 200, "GET /dashboard failed"
    print("  [PASS] GET /dashboard (Admin Dashboard) OK")

    print("\n[2] Testing Sample Data Downloads...")
    for ftype in ['excel', 'csv', 'pdf']:
        res = client.get(f'/sample-data/download/{ftype}')
        assert res.status_code == 200, f"Sample download {ftype} failed"
        assert len(res.data) > 0
        print(f"  [PASS] Sample download {ftype} OK ({len(res.data)} bytes)")

    print("\n[3] Testing API /api/config...")
    res = client.get('/api/config')
    assert res.status_code == 200
    cfg = res.get_json()
    assert "templates" in cfg
    print("  [PASS] GET /api/config OK")

    print("\n[4] Testing API /api/template-palette/<name>...")
    res = client.get('/api/template-palette/classic_gold.png')
    assert res.status_code == 200
    pinfo = res.get_json()
    assert pinfo.get("success") is True
    assert "palette" in pinfo.get("info", {})
    print(f"  [PASS] GET /api/template-palette/classic_gold.png OK: {len(pinfo['info']['palette'])} colors detected")

    print("\n[5] Testing API /api/preview...")
    preview_payload = {
        "template_name": "classic_gold.png",
        "student_data": {
            "NAME": "Alexander Graham",
            "COURSE": "Quantum Computing & Algorithms",
            "DATE": "March 10, 2026",
            "GRADE": "A+",
            "CERT_ID": "CERT-2026-TEST"
        }
    }
    res = client.post('/api/preview', json=preview_payload)
    assert res.status_code == 200
    pdata = res.get_json()
    assert pdata.get("success") is True
    assert pdata.get("preview_image", "").startswith("data:image/jpeg;base64,")
    print("  [PASS] POST /api/preview (Live Single Preview) OK")

    print("\n[6] Testing API /api/generate-single-pdf (Streaming Single PDF)...")
    res = client.post('/api/generate-single-pdf', json=preview_payload)
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert len(res.data) > 0
    print(f"  [PASS] POST /api/generate-single-pdf OK: Received {len(res.data)} bytes PDF stream")

    print("\n[7] Testing API /api/upload-data (Excel, CSV, PDF)...")
    # Excel Upload
    with open(os.path.join("sample_data", "sample_students.xlsx"), "rb") as f:
        data_bytes = f.read()
    res = client.post('/api/upload-data', data={
        'data_file': (io.BytesIO(data_bytes), 'students.xlsx')
    }, content_type='multipart/form-data')
    assert res.status_code == 200
    up_data = res.get_json()
    assert up_data.get("success") is True
    assert up_data.get("total_records") == 10
    print(f"  [PASS] POST /api/upload-data (Excel) OK: {up_data['total_records']} records")

    # PDF Upload
    with open(os.path.join("sample_data", "sample_students.pdf"), "rb") as f:
        pdf_bytes = f.read()
    res = client.post('/api/upload-data', data={
        'data_file': (io.BytesIO(pdf_bytes), 'students.pdf')
    }, content_type='multipart/form-data')
    assert res.status_code == 200
    up_pdf = res.get_json()
    assert up_pdf.get("success") is True
    print(f"  [PASS] POST /api/upload-data (PDF) OK: {up_pdf['total_records']} records extracted")

    print("\n[8] Testing API /api/parse-raw-data (Direct Clipboard Paste)...")
    raw_text = "Name\tCourse\tDate\tGrade\tCertID\nGrace Hopper\tCompiler Design\t2026-03-01\tA+\tCERT-0001\nAlan Turing\tCryptography\t2026-03-02\tA+\tCERT-0002"
    res = client.post('/api/parse-raw-data', json={"raw_text": raw_text})
    assert res.status_code == 200
    paste_data = res.get_json()
    assert paste_data.get("success") is True
    assert paste_data.get("total_records") == 2
    print(f"  [PASS] POST /api/parse-raw-data OK: {paste_data['total_records']} records parsed")

    print("\n[9] Testing API /api/generate (Bulk Generation & Combined PDF Engine)...")
    gen_payload = {
        "template_name": "classic_gold.png",
        "export_format": "both",
        "records": up_data["all_records"]
    }
    res = client.post('/api/generate', json=gen_payload)
    assert res.status_code == 200
    gen_resp = res.get_json()
    assert gen_resp.get("success") is True
    assert gen_resp.get("generated_count") == 10
    batch_id = gen_resp.get("batch_id")
    zip_url = gen_resp.get("zip_url")
    combined_pdf_url = gen_resp.get("combined_pdf_url")
    assert combined_pdf_url is not None
    print(f"  [PASS] POST /api/generate OK: Batch {batch_id}, Combined PDF: {combined_pdf_url}")

    print("\n[10] Testing Combined Multi-Page PDF & ZIP Downloads...")
    # Combined PDF download
    res = client.get(combined_pdf_url)
    assert res.status_code == 200
    assert res.mimetype == "application/pdf"
    assert len(res.data) > 0
    print(f"  [PASS] GET {combined_pdf_url} (Combined Multi-Page PDF) OK: {len(res.data)} bytes")

    # ZIP download
    res = client.get(zip_url)
    assert res.status_code == 200
    assert len(res.data) > 0
    print(f"  [PASS] GET {zip_url} (ZIP bulk download) OK: {len(res.data)} bytes")

    # Individual file download
    first_rec = gen_resp["generated_records"][0]
    pdf_file = first_rec["files"]["pdf"]
    res = client.get(f"/download/certificate/{batch_id}/{pdf_file}")
    assert res.status_code == 200
    print(f"  [PASS] GET /download/certificate/{batch_id}/{pdf_file} OK: {len(res.data)} bytes")

    print("\n[11] Testing MongoDB Atlas API Endpoints & Verification...")
    # Test DB status endpoint
    res = client.get('/api/db-status')
    assert res.status_code == 200
    db_st = res.get_json()
    assert "connected" in db_st
    print(f"  [PASS] GET /api/db-status OK: (Connected: {db_st.get('connected')}, Database: '{db_st.get('database')}')")

    # Test Certificates search endpoint
    res = client.get(f'/api/certificates?batch_id={batch_id}')
    assert res.status_code == 200
    c_data = res.get_json()
    assert c_data.get("success") is True
    print(f"  [PASS] GET /api/certificates OK: {c_data.get('count', 0)} certificates queried")

    # Test Certificate ID verification
    test_cid = first_rec.get("cert_id")
    if test_cid:
        res = client.get(f'/api/verify/{test_cid}')
        assert res.status_code in [200, 404]
        print(f"  [PASS] GET /api/verify/{test_cid} OK: Verification endpoint responsive")

        # Test Web verification page
        res = client.get(f'/verify/{test_cid}')
        assert res.status_code == 200
        print(f"  [PASS] GET /verify/{test_cid} (Verification Web Page) OK")

    print("\n=======================================================")
    print("   ALL INTEGRATION & API TESTS PASSED 100%!   ")
    print("=======================================================\n")

if __name__ == "__main__":
    test_endpoints()

