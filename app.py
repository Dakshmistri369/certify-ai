"""
app.py
Main Flask Application for CertifyAI - AI Certificate Generator Studio.
Provides REST API, Web Interfaces, and MongoDB Atlas persistence for data extraction,
template design, live previews, high-resolution bulk certificate generation, and instant verification.
"""

import os
import json
import uuid
import time
import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

from utils.data_extractor import extract_student_data, extract_from_raw_text
from utils.certificate_maker import (
    generate_single_certificate,
    generate_preview_base64,
    open_template_image,
    extract_template_palette,
    sanitize_filename
)
from utils.pdf_helper import create_combined_pdf
from utils.zip_helper import create_certificates_zip
from utils.sample_generator import initialize_all_sample_assets
from utils.db import (
    get_db,
    get_db_status,
    save_config_db,
    load_config_db,
    record_batch_db,
    load_batches_db,
    clear_batches_db,
    record_certificates_db,
    get_certificates_db,
    verify_certificate_db
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "certify-ai-secret-2026")
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64 MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
UPLOADS_DATA_DIR = os.path.join(BASE_DIR, "uploads", "data_files")
UPLOADS_TPL_DIR = os.path.join(BASE_DIR, "uploads", "template_files")
GENERATED_DIR = os.path.join(BASE_DIR, "generated_certificates")
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_data")
SAMPLE_TPL_DIR = os.path.join(BASE_DIR, "static", "sample_templates")
BATCH_LOGS_FILE = os.path.join(GENERATED_DIR, "batches.json")

for folder in [UPLOADS_DATA_DIR, UPLOADS_TPL_DIR, GENERATED_DIR, SAMPLE_DATA_DIR, SAMPLE_TPL_DIR]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_DATA_EXTS = {'.xlsx', '.xls', '.xlsm', '.csv', '.tsv', '.txt', '.pdf', '.json'}
ALLOWED_TPL_EXTS = {'.png', '.jpg', '.jpeg', '.pdf'}


@app.context_processor
def inject_db_status():
    """Inject MongoDB connection info into all Jinja templates."""
    try:
        return dict(db_status=get_db_status())
    except Exception:
        return dict(db_status={"connected": False})


DEFAULT_CONFIG = {
    "default_template": "classic_gold.png",
    "templates": {
        "classic_gold.png": {
            "name": "Classic Gold Certificate",
            "width": 1920,
            "height": 1080,
            "clean_dummy_text": True,
            "fields": {
                "NAME": {"label": "Student Name", "x": 960, "y": 450, "font_family": "Montserrat-Bold.ttf", "font_size": 52, "color": "#0C0C0C", "alignment": "center"},
                "COURSE": {"label": "Course Name", "x": 960, "y": 550, "font_family": "Montserrat-Bold.ttf", "font_size": 24, "color": "#9B3922", "alignment": "center", "transform": "uppercase", "max_width": 1400},
                "GRADE": {"label": "Grade / Distinction", "x": 960, "y": 610, "font_family": "Montserrat-Regular.ttf", "font_size": 18, "color": "#481E14", "alignment": "center", "prefix": "With Distinction — "},
                "DATE": {"label": "Issue Date", "x": 455, "y": 770, "font_family": "Roboto-Regular.ttf", "font_size": 16, "color": "#481E14", "alignment": "center", "prefix": "Date: "},
                "CERT_ID": {"label": "Certificate ID", "x": 1465, "y": 770, "font_family": "Roboto-Regular.ttf", "font_size": 16, "color": "#481E14", "alignment": "center", "prefix": "ID: "}
            }
        },
        "modern_blue.png": {
            "name": "Modern Tech Blue",
            "width": 1920,
            "height": 1080,
            "clean_dummy_text": True,
            "fields": {
                "NAME": {"label": "Student Name", "x": 960, "y": 440, "font_family": "Montserrat-Bold.ttf", "font_size": 52, "color": "#0F172A", "alignment": "center"},
                "COURSE": {"label": "Course Name", "x": 960, "y": 540, "font_family": "Montserrat-Bold.ttf", "font_size": 24, "color": "#2563EB", "alignment": "center", "transform": "uppercase", "max_width": 1400},
                "GRADE": {"label": "Grade", "x": 960, "y": 600, "font_family": "Roboto-Regular.ttf", "font_size": 18, "color": "#334155", "alignment": "center"},
                "DATE": {"label": "Date", "x": 430, "y": 770, "font_family": "Roboto-Regular.ttf", "font_size": 16, "color": "#475569", "alignment": "center", "prefix": "Date: "},
                "CERT_ID": {"label": "ID", "x": 1490, "y": 770, "font_family": "Roboto-Regular.ttf", "font_size": 16, "color": "#475569", "alignment": "center", "prefix": "ID: "}
            }
        }
    }
}


def load_config() -> Dict[str, Any]:
    """Load configuration from MongoDB with local config.json fallback and default merging."""
    cfg = load_config_db()
    if not cfg:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception:
                cfg = None
    
    if not cfg:
        cfg = DEFAULT_CONFIG.copy()
    else:
        if "templates" not in cfg or not cfg["templates"]:
            cfg["templates"] = DEFAULT_CONFIG["templates"].copy()
        if "default_template" not in cfg:
            cfg["default_template"] = DEFAULT_CONFIG["default_template"]
    
    # Sync both local file and MongoDB
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass
    save_config_db(cfg)
    return cfg


def save_config(cfg: Dict[str, Any]) -> None:
    """Save configuration to MongoDB and local config.json."""
    if "templates" not in cfg:
        cfg["templates"] = DEFAULT_CONFIG["templates"].copy()
    save_config_db(cfg)
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


def load_batches() -> list:
    """Load batch generation history from MongoDB with local JSON fallback."""
    batches = load_batches_db()
    if batches is not None and len(batches) > 0:
        return batches
    if os.path.exists(BATCH_LOGS_FILE):
        try:
            with open(BATCH_LOGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def record_batch(meta: dict) -> None:
    """Record batch metadata in MongoDB and local history."""
    record_batch_db(meta)
    history = load_batches()
    if not history or history[0].get("batch_id") != meta.get("batch_id"):
        history.insert(0, meta)
    try:
        with open(BATCH_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(history[:50], f, indent=2)
    except Exception:
        pass


def resolve_template_path(tpl_name: str) -> str:
    """Resolve template file path from sample templates or user uploads."""
    if not tpl_name or str(tpl_name).lower() in ["default", "null", "undefined"]:
        return os.path.join(SAMPLE_TPL_DIR, "classic_gold.png")
    if os.path.isabs(tpl_name) and os.path.exists(tpl_name):
        return tpl_name
    for base in [SAMPLE_TPL_DIR, UPLOADS_TPL_DIR]:
        p = os.path.join(base, tpl_name)
        if os.path.exists(p):
            return p
        # PDF to PNG mapping check
        if tpl_name.lower().endswith('.pdf') and os.path.exists(os.path.join(base, f"{os.path.splitext(tpl_name)[0]}.png")):
            return os.path.join(base, f"{os.path.splitext(tpl_name)[0]}.png")
        if tpl_name.lower().endswith(('.png', '.jpg', '.jpeg')) and os.path.exists(os.path.join(base, f"{os.path.splitext(tpl_name)[0]}.pdf")):
            return os.path.join(base, f"{os.path.splitext(tpl_name)[0]}.pdf")
    
    if tpl_name.startswith("custom") and os.path.exists(UPLOADS_TPL_DIR):
        uploads = [os.path.join(UPLOADS_TPL_DIR, f) for f in os.listdir(UPLOADS_TPL_DIR) if f.lower().endswith(tuple(ALLOWED_TPL_EXTS))]
        if uploads:
            uploads.sort(key=os.path.getmtime, reverse=True)
            return uploads[0]

    return os.path.join(SAMPLE_TPL_DIR, "classic_gold.png")


# --- WEB ROUTES ---

@app.route('/')
def index():
    return render_template('index.html', config=load_config())


@app.route('/preview')
def preview_page():
    return render_template('preview.html', config=load_config())


@app.route('/dashboard')
def dashboard():
    batches = load_batches()
    total_gen = sum(b.get("success_count", 0) for b in batches)
    certs = []
    
    # Query certificates from MongoDB first
    db_certs = get_certificates_db(limit=300)
    if db_certs:
        for c in db_certs:
            certs.append({
                "batch_id": c.get("batch_id", ""),
                "cert_id": c.get("cert_id", ""),
                "student_name": c.get("student_name", ""),
                "course": c.get("course", ""),
                "date": c.get("date", ""),
                "grade": c.get("grade", ""),
                "filename": (c.get("files", {}).get("pdf") or c.get("files", {}).get("png") or ""),
                "size_kb": 0,
                "created_at": c.get("created_at", ""),
                "template": c.get("template_name", ""),
                "ext": "PDF" if (c.get("files", {}).get("pdf")) else "PNG"
            })
    else:
        for b in batches:
            b_id = b.get("batch_id")
            b_dir = os.path.join(GENERATED_DIR, b_id)
            if os.path.exists(b_dir):
                for file in os.listdir(b_dir):
                    if file.endswith(('.pdf', '.png')):
                        certs.append({
                            "batch_id": b_id,
                            "filename": file,
                            "size_kb": round(os.path.getsize(os.path.join(b_dir, file)) / 1024, 1),
                            "created_at": b.get("timestamp", ""),
                            "template": b.get("template_name", ""),
                            "ext": os.path.splitext(file)[1].lstrip('.').upper()
                        })
    return render_template(
        'dashboard.html',
        batches=batches,
        total_generated=total_gen,
        total_batches=len(batches),
        latest_batch=batches[0] if batches else None,
        certificates=certs
    )


@app.route('/verify')
@app.route('/verify/<cert_id>')
def verify_page(cert_id=None):
    if not cert_id:
        cert_id = request.args.get('cert_id', '').strip()
    cert = None
    if cert_id:
        cert = verify_certificate_db(cert_id)
    return render_template('verify.html', cert_id=cert_id, certificate=cert)


# --- FILE SERVING ---

@app.route('/uploads/template_files/<path:filename>')
def serve_template_file(filename):
    return send_from_directory(UPLOADS_TPL_DIR, filename)


@app.route('/uploads/data_files/<path:filename>')
def serve_data_file(filename):
    return send_from_directory(UPLOADS_DATA_DIR, filename)


@app.route('/api/template-image/<path:template_name>')
def serve_template_image(template_name):
    """Serve template image as PNG/JPEG, rendering PDF on-the-fly if needed."""
    try:
        path = resolve_template_path(template_name)
        if path.lower().endswith('.pdf'):
            png_p = f"{os.path.splitext(path)[0]}.png"
            if not os.path.exists(png_p):
                open_template_image(path).save(png_p, "PNG")
            return send_file(png_p, mimetype="image/png")
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else ("image/jpeg" if ext in [".jpg", ".jpeg"] else "application/octet-stream")
        return send_file(path, mimetype=mime)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- REST API ---

@app.route('/api/db-status', methods=['GET'])
def api_db_status():
    """Return MongoDB Atlas connection health and statistics."""
    return jsonify(get_db_status())


@app.route('/api/certificates', methods=['GET'])
def api_certificates():
    """Query certificate records from MongoDB by batch ID or search query."""
    batch_id = request.args.get('batch_id')
    query = request.args.get('q')
    limit = int(request.args.get('limit', 100))
    certs = get_certificates_db(batch_id=batch_id, query=query, limit=limit)
    return jsonify({"success": True, "count": len(certs), "certificates": certs})


@app.route('/api/verify/<cert_id>', methods=['GET'])
def api_verify(cert_id):
    """Look up certificate authenticity in MongoDB Atlas by Certificate ID."""
    cert = verify_certificate_db(cert_id)
    if cert:
        return jsonify({"success": True, "valid": True, "certificate": cert})
    return jsonify({"success": True, "valid": False, "message": f"Certificate ID '{cert_id}' not found."}), 404


@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    if request.method == 'POST':
        cfg = request.get_json()
        if not cfg:
            return jsonify({"success": False, "error": "Invalid JSON"}), 400
        save_config(cfg)
        return jsonify({"success": True, "message": "Config saved successfully."})
    return jsonify(load_config())


@app.route('/api/upload-data', methods=['POST'])
def api_upload_data():
    if 'data_file' not in request.files or not request.files['data_file'].filename:
        return jsonify({"success": False, "error": "No file attached."}), 400
    file = request.files['data_file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_DATA_EXTS:
        return jsonify({"success": False, "error": f"Invalid format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_DATA_EXTS))}"}), 400

    safe_name = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    path = os.path.join(UPLOADS_DATA_DIR, safe_name)
    file.save(path)

    try:
        records, stats = extract_student_data(path)
        return jsonify({
            "success": True,
            "filename": safe_name,
            "original_name": file.filename,
            "total_records": len(records),
            "stats": stats,
            "preview_records": records[:10],
            "all_records": records,
            "columns_found": stats.get("columns_found", []),
            "all_fields": stats.get("all_fields", [])
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Extraction failed: {str(e)}"}), 500


@app.route('/api/parse-raw-data', methods=['POST'])
def api_parse_raw_data():
    data = request.get_json() or {}
    raw_text = data.get("raw_text", "").strip()
    if not raw_text:
        return jsonify({"success": False, "error": "Text is empty."}), 400
    try:
        records, stats = extract_from_raw_text(raw_text)
        if not records:
            return jsonify({"success": False, "error": "No valid student records found in text."}), 400
        return jsonify({
            "success": True,
            "filename": "pasted_data.tsv",
            "original_name": "Pasted Data",
            "total_records": len(records),
            "stats": stats,
            "preview_records": records[:10],
            "all_records": records,
            "columns_found": stats.get("columns_found", []),
            "all_fields": stats.get("all_fields", [])
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/sample-data/<dataset_type>', methods=['GET'])
def api_sample_data(dataset_type):
    try:
        target = "sample_50_students.xlsx" if dataset_type in ["50", "sample_50", "fifty"] else "sample_students.xlsx"
        path = os.path.join(SAMPLE_DATA_DIR, target)
        if not os.path.exists(path):
            initialize_all_sample_assets()
        records, stats = extract_student_data(path)
        return jsonify({
            "success": True,
            "filename": target,
            "original_name": f"Sample {'50' if '50' in target else '10'} Students",
            "total_records": len(records),
            "stats": stats,
            "preview_records": records[:10],
            "all_records": records,
            "columns_found": stats.get("columns_found", []),
            "all_fields": stats.get("all_fields", [])
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/upload-template', methods=['POST'])
def api_upload_template():
    if 'template_file' not in request.files or not request.files['template_file'].filename:
        return jsonify({"success": False, "error": "No template file attached."}), 400
    file = request.files['template_file']
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_TPL_EXTS:
        return jsonify({"success": False, "error": f"Invalid format '{ext}'. Allowed: .png, .jpg, .jpeg, .pdf"}), 400

    safe_name = f"custom_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    path = os.path.join(UPLOADS_TPL_DIR, safe_name)
    file.save(path)

    try:
        img = open_template_image(path)
        w, h = img.size
        preview_name = safe_name
        if ext == '.pdf':
            preview_name = f"{os.path.splitext(safe_name)[0]}.png"
            img.save(os.path.join(UPLOADS_TPL_DIR, preview_name), "PNG")

        palette = extract_template_palette(path)
        primary_dark = palette.get("primary_dark", "#0C0C0C")
        accent = palette.get("accent", "#9B3922")

        cfg = load_config()
        if "templates" not in cfg:
            cfg["templates"] = {}

        cx = round(w / 2)
        cfg["templates"][preview_name] = {
            "name": file.filename,
            "width": w,
            "height": h,
            "clean_dummy_text": True,
            "fields": {
                "NAME": {"label": "Student Name", "x": cx, "y": round(h * 0.42), "font_family": "Montserrat-Bold.ttf", "font_size": max(48, round(h * 0.055)), "color": primary_dark, "alignment": "center"},
                "COURSE": {"label": "Course Name", "x": cx, "y": round(h * 0.505), "font_family": "Montserrat-Bold.ttf", "font_size": max(22, round(h * 0.022)), "color": accent, "alignment": "center", "transform": "uppercase", "max_width": round(w * 0.70)},
                "GRADE": {"label": "Grade", "x": cx, "y": round(h * 0.558), "font_family": "Georgia-Regular.ttf", "font_size": max(18, round(h * 0.017)), "color": "#481E14", "alignment": "center", "prefix": "With Distinction — "},
                "DATE": {"label": "Date", "x": round(w * 0.237), "y": round(h * 0.712), "font_family": "Roboto-Regular.ttf", "font_size": max(16, round(h * 0.015)), "color": "#481E14", "alignment": "center", "prefix": "Date: "},
                "CERT_ID": {"label": "ID", "x": round(w * 0.763), "y": round(h * 0.712), "font_family": "Roboto-Regular.ttf", "font_size": max(16, round(h * 0.015)), "color": "#481E14", "alignment": "center", "prefix": "ID: "}
            }
        }
        save_config(cfg)

        return jsonify({
            "success": True,
            "template_name": preview_name,
            "original_name": file.filename,
            "width": w,
            "height": h,
            "palette_info": palette,
            "image_url": f"/api/template-image/{preview_name}",
            "fields": cfg["templates"][preview_name]["fields"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Template processing error: {str(e)}"}), 500


@app.route('/api/template-palette/<path:template_name>')
def api_template_palette(template_name):
    try:
        path = resolve_template_path(template_name)
        return jsonify({"success": True, "info": extract_template_palette(path)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def api_preview():
    try:
        data = request.get_json() or {}
        tpl_name = data.get("template_name", "classic_gold.png")
        tpl_path = resolve_template_path(tpl_name)
        fields = data.get("fields_config")
        if not fields:
            cfg = load_config().get("templates", {})
            fields = (cfg.get(tpl_name) or cfg.get("classic_gold.png", {})).get("fields", {})

        b64 = generate_preview_base64(tpl_path, data.get("student_data"), fields, clean_dummy_text=data.get("clean_dummy_text", True))
        return jsonify({"success": True, "preview_image": b64})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate-single-pdf', methods=['POST'])
def api_generate_single_pdf():
    try:
        data = request.get_json() or {}
        tpl_name = data.get("template_name", "classic_gold.png")
        tpl_path = resolve_template_path(tpl_name)
        student = data.get("student_data") or {"NAME": "Alexander Morgan", "COURSE": "Certificate of Achievement", "DATE": datetime.date.today().strftime("%B %d, %Y"), "GRADE": "A+", "CERT_ID": "CERT-2026-001"}
        fields = data.get("fields_config") or load_config().get("templates", {}).get(tpl_name, {}).get("fields", {})

        tmp_dir = os.path.join(GENERATED_DIR, "single_downloads")
        res = generate_single_certificate(tpl_path, student, fields, tmp_dir, export_format="pdf", clean_dummy_text=data.get("clean_dummy_text", True))
        pdf_path = res.get("pdf")
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify({"success": False, "error": "PDF generation failed"}), 500

        safe_name = sanitize_filename(student.get("NAME", "Certificate"))
        return send_file(pdf_path, as_attachment=True, download_name=f"{safe_name}_Certificate.pdf", mimetype="application/pdf")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def api_generate():
    t0 = time.time()
    data = request.get_json() or {}
    tpl_name = data.get("template_name", "classic_gold.png")
    tpl_path = resolve_template_path(tpl_name)
    export_fmt = data.get("export_format", "pdf")
    records = data.get("records", [])
    fields = data.get("fields_config")
    clean_dummy = data.get("clean_dummy_text", True)

    if not records and data.get("data_filename"):
        dp = os.path.join(UPLOADS_DATA_DIR, data["data_filename"])
        if os.path.exists(dp):
            records, _ = extract_student_data(dp)

    if not records:
        return jsonify({"success": False, "error": "No student records found."}), 400

    if not fields:
        cfg = load_config().get("templates", {})
        fields = (cfg.get(tpl_name) or cfg.get("classic_gold.png", {})).get("fields", {})

    batch_id = f"batch_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    batch_dir = os.path.join(GENERATED_DIR, batch_id)
    os.makedirs(batch_dir, exist_ok=True)

    gen_files, pdf_files, failed, gen_records = [], [], [], []

    for rec in records:
        try:
            res = generate_single_certificate(tpl_path, rec, fields, batch_dir, export_format=export_fmt, clean_dummy_text=clean_dummy)
            for k, p in res.items():
                gen_files.append(p)
                if k == "pdf":
                    pdf_files.append(p)
            gen_records.append({
                "student_name": rec.get("NAME"),
                "cert_id": rec.get("CERT_ID"),
                "course": rec.get("COURSE"),
                "date": rec.get("DATE"),
                "grade": rec.get("GRADE"),
                "files": {k: os.path.basename(p) for k, p in res.items()}
            })
        except Exception as err:
            failed.append({"record": rec, "error": str(err)})

    # ZIP & Combined PDF
    zip_name = f"certificates_{batch_id}.zip"
    zip_path = os.path.join(GENERATED_DIR, zip_name)
    create_certificates_zip(gen_files, zip_path)

    comb_pdf_name = f"all_certificates_{batch_id}.pdf"
    comb_pdf_path = os.path.join(GENERATED_DIR, comb_pdf_name)
    comb_created = False
    if pdf_files:
        try:
            create_combined_pdf(pdf_files, comb_pdf_path, title=f"Certificates - {batch_id}")
            comb_created = os.path.exists(comb_pdf_path)
        except Exception as e:
            print(f"Combined PDF note: {e}")

    meta = {
        "batch_id": batch_id,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "template_name": tpl_name,
        "total_records": len(records),
        "success_count": len(gen_records),
        "failed_count": len(failed),
        "export_format": export_fmt,
        "elapsed_seconds": round(time.time() - t0, 2),
        "zip_file": zip_name,
        "zip_size_kb": round(os.path.getsize(zip_path) / 1024, 1) if os.path.exists(zip_path) else 0,
        "combined_pdf_file": comb_pdf_name if comb_created else None,
        "combined_pdf_size_kb": round(os.path.getsize(comb_pdf_path) / 1024, 1) if comb_created else 0
    }
    
    # Store batch metadata and individual certificates in MongoDB Atlas
    record_batch(meta)
    if gen_records:
        record_certificates_db(batch_id, gen_records, template_name=tpl_name)

    return jsonify({
        "success": True,
        "batch_id": batch_id,
        "batch_meta": meta,
        "generated_count": len(gen_records),
        "failed_count": len(failed),
        "zip_url": f"/download/zip/{batch_id}",
        "combined_pdf_url": f"/download/combined-pdf/{batch_id}" if comb_created else None,
        "generated_records": gen_records,
        "failed_records": failed
    })


# --- DOWNLOADS ---

@app.route('/download/zip/<batch_id>')
def download_zip(batch_id):
    path = os.path.join(GENERATED_DIR, f"certificates_{batch_id}.zip")
    if not os.path.exists(path):
        flash("ZIP archive not found or expired.", "danger")
        return redirect(url_for('dashboard'))
    return send_file(path, as_attachment=True, download_name=f"certificates_{batch_id}.zip")


@app.route('/download/combined-pdf/<batch_id>')
def download_combined_pdf(batch_id):
    path = os.path.join(GENERATED_DIR, f"all_certificates_{batch_id}.pdf")
    if not os.path.exists(path):
        b_dir = os.path.join(GENERATED_DIR, batch_id)
        if os.path.exists(b_dir):
            pdfs = [os.path.join(b_dir, f) for f in sorted(os.listdir(b_dir)) if f.lower().endswith('.pdf')]
            if pdfs:
                create_combined_pdf(pdfs, path)
    if not os.path.exists(path):
        flash("Combined PDF not found.", "danger")
        return redirect(url_for('dashboard'))
    return send_file(path, as_attachment=(request.args.get("view") != "true"), download_name=f"all_certificates_{batch_id}.pdf", mimetype="application/pdf")


@app.route('/download/certificate/<batch_id>/<filename>')
def download_certificate(batch_id, filename):
    safe_f = secure_filename(filename)
    path = os.path.join(GENERATED_DIR, batch_id, safe_f)
    if not os.path.exists(path):
        flash("Certificate file not found.", "danger")
        return redirect(url_for('dashboard'))
    mime = "application/pdf" if safe_f.lower().endswith('.pdf') else "image/png"
    return send_file(path, as_attachment=(request.args.get("view") != "true"), download_name=safe_f, mimetype=mime)


@app.route('/sample-data/download/<file_type>')
def download_sample_data(file_type):
    mapping = {"excel": "sample_students.xlsx", "csv": "sample_students.csv", "pdf": "sample_students.pdf"}
    target = mapping.get(file_type.lower())
    if not target:
        return "Invalid file type", 400
    path = os.path.join(SAMPLE_DATA_DIR, target)
    if not os.path.exists(path):
        initialize_all_sample_assets()
    return send_file(path, as_attachment=True, download_name=target)


@app.route('/sample-template/download/<template_name>')
def download_sample_template(template_name):
    path = os.path.join(SAMPLE_TPL_DIR, secure_filename(template_name))
    if not os.path.exists(path):
        return "Template not found", 404
    return send_file(path, as_attachment=True, download_name=secure_filename(template_name))


@app.route('/api/clear-history', methods=['POST'])
def api_clear_history():
    try:
        clear_batches_db()
        with open(BATCH_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return jsonify({"success": True, "message": "History and MongoDB records cleared."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


with app.app_context():
    initialize_all_sample_assets()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting CertifyAI on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
