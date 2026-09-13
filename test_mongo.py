"""
test_mongo.py
Comprehensive test suite for MongoDB Atlas integration in CertifyAI.
Tests connection ping, config persistence, batch metadata, certificate records,
and certificate verification lookups.
"""

import sys
import uuid
import datetime
from utils.db import (
    get_db,
    get_db_status,
    save_config_db,
    load_config_db,
    record_batch_db,
    load_batches_db,
    record_certificates_db,
    get_certificates_db,
    verify_certificate_db,
    clear_batches_db
)

def test_mongodb():
    print("=" * 60)
    print(" TESTING MONGODB ATLAS INTEGRATION FOR CERTIFYAI ")
    print("=" * 60)

    # 1. Test Connection Status
    print("\n[1] Testing MongoDB Atlas Connection...")
    status = get_db_status()
    print(f"  Connection Status: {status}")
    assert status["connected"] is True, f"MongoDB connection failed: {status.get('error')}"
    print(f"  [PASS] Successfully connected to MongoDB database '{status['database']}'")

    # 2. Test Configuration Persistence
    print("\n[2] Testing Config Persistence in MongoDB...")
    current_cfg = load_config_db() or {}
    test_key_val = f"test_val_{uuid.uuid4().hex[:6]}"
    test_config = dict(current_cfg)
    test_config["test_key"] = test_key_val
    if "default_template" not in test_config:
        test_config["default_template"] = "classic_gold.png"

    saved = save_config_db(test_config)
    assert saved is True, "Failed to save config to MongoDB"
    loaded = load_config_db()
    assert loaded is not None, "Failed to load config from MongoDB"
    assert loaded.get("test_key") == test_key_val
    print(f"  [PASS] Config saved and verified in MongoDB: {loaded.get('test_key')}")

    # 3. Test Batch Persistence
    print("\n[3] Testing Batch Generation Logging in MongoDB...")
    test_batch_id = f"test_batch_{uuid.uuid4().hex[:8]}"
    test_meta = {
        "batch_id": test_batch_id,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "template_name": "classic_gold.png",
        "total_records": 5,
        "success_count": 5,
        "failed_count": 0,
        "export_format": "pdf",
        "elapsed_seconds": 0.42,
        "zip_file": f"certificates_{test_batch_id}.zip",
        "combined_pdf_file": f"all_certificates_{test_batch_id}.pdf"
    }
    batch_recorded = record_batch_db(test_meta)
    assert batch_recorded is True, "Failed to record batch in MongoDB"
    batches = load_batches_db(limit=10)
    assert batches is not None and len(batches) > 0, "No batches returned from MongoDB"
    assert any(b.get("batch_id") == test_batch_id for b in batches)
    print(f"  [PASS] Batch metadata recorded and retrieved: {test_batch_id}")

    # 4. Test Certificate Records & Instant Verification
    print("\n[4] Testing Individual Certificate Storage & Verification...")
    test_cert_id = f"CERT-MONGO-{uuid.uuid4().hex[:6].upper()}"
    records = [
        {
            "student_name": "Alan Turing",
            "cert_id": test_cert_id,
            "course": "Theoretical Computer Science",
            "date": "March 15, 2026",
            "grade": "Distinction (A+)",
            "files": {"pdf": "Alan_Turing_Certificate.pdf", "png": "Alan_Turing_Certificate.png"}
        },
        {
            "student_name": "Ada Lovelace",
            "cert_id": f"CERT-MONGO-ADA-{uuid.uuid4().hex[:4].upper()}",
            "course": "Analytical Engine Computing",
            "date": "March 15, 2026",
            "grade": "First Class Honours",
            "files": {"pdf": "Ada_Lovelace_Certificate.pdf"}
        }
    ]
    inserted_count = record_certificates_db(test_batch_id, records, template_name="classic_gold.png")
    assert inserted_count == 2, f"Expected 2 inserted certificates, got {inserted_count}"
    print(f"  [PASS] Inserted {inserted_count} certificate documents into 'certificates' collection")

    # 5. Query Certificates & Verification
    print("\n[5] Testing Certificate Search & Verification Query...")
    # Search by cert_id
    verified = verify_certificate_db(test_cert_id)
    assert verified is not None, f"Could not verify certificate ID: {test_cert_id}"
    assert verified.get("student_name") == "Alan Turing"
    assert verified.get("course") == "Theoretical Computer Science"
    print(f"  [PASS] Certificate ID '{test_cert_id}' verified successfully: {verified['student_name']} - {verified['course']}")

    # Search by student name
    queried = get_certificates_db(query="Lovelace")
    assert len(queried) >= 1, "Student search by name failed"
    assert queried[0]["student_name"] == "Ada Lovelace"
    print(f"  [PASS] Certificate queried by student name 'Lovelace': found {queried[0]['cert_id']}")

    print("\n" + "=" * 60)
    print(" ALL MONGODB ATLAS TESTS PASSED WITH 100% SUCCESS! ")
    print("=" * 60)

if __name__ == "__main__":
    test_mongodb()
