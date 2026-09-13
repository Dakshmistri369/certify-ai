# 🎓 AI-Based Bulk Certificate Generator

A complete, production-ready, full-stack **AI-Based Certificate Generator** web application built with **Python (Flask)**, **Pillow (PIL)**, **ReportLab**, **Pandas**, **pdfplumber**, and modern **Bootstrap 5 UI**.

Generate thousands of personalized, high-resolution (300 DPI) certificates in seconds from student rosters (Excel, CSV, PDF), featuring a **visual coordinate editor**, **live preview inspector**, **Unicode / multilingual support**, **bulk ZIP export**, and an **Admin Dashboard**.

---

## 🌟 Key Features

1. **Multi-Format Student Data Ingestion**
   - Ingest student rosters from **Excel (.xlsx, .xls)**, **CSV (.csv)**, and **PDF (.pdf)** tables.
   - Smart header normalization (automatically maps column variants like *Full Name*, *Student Name*, *Course Title*, *Completion Date*, *Grade*, *Cert ID*).
   - Optical Character Recognition (OCR) fallback for scanned PDFs via `pytesseract`.
   - Robust validation: skips empty rows, cleans whitespace, auto-generates sequential/timestamped Certificate IDs when omitted.

2. **Interactive Visual Coordinate & Placeholder System**
   - Live Canvas with draggable and click-to-place coordinate pins.
   - Configure precise (X, Y) coordinates, typography, font family, font size, text alignment (Center, Left, Right), and hex colors for placeholders:
     - `{NAME}`: Student Full Name
     - `{COURSE}`: Course / Program Title (with auto multiline wrapping)
     - `{DATE}`: Award / Completion Date
     - `{GRADE}`: Performance / Grade / Distinction
     - `{CERT_ID}`: Unique Credential Identification Number
   - Presets stored and updated in `config.json`.

3. **High-DPI Certificate Rendering Engine**
   - High-resolution (300 DPI) vector/raster compositing with Pillow.
   - Full Unicode character rendering (supports international names, accents, and special characters, e.g., *José García Müller*, *Aarav Sharma*).
   - Dual export options: **PDF** (single-page print-ready) and **PNG** (high-res image).

4. **Live Real-Time Preview**
   - Instant single-certificate preview generator to verify font placement and styling before running bulk processing.

5. **Bulk ZIP Compression & Export**
   - In-memory/streamed batch archiving of all generated certificate files into a single structured ZIP file for instant one-click download.

6. **Admin Dashboard & Analytics**
   - Live metrics: Total certificates generated, total batches run, success rate, and last generation run time.
   - Searchable certificate roster table with inline viewing and individual file download.
   - Batch history logs with ZIP size and duration analytics.

---

## 📂 Project Structure

```
ai certificate project/
│
├── app.py                         # Main Flask application & REST API routes
├── config.json                    # Placeholder coordinates & styling configuration
├── requirements.txt               # Dependencies list
├── test_core.py                   # Core engine unit tests
├── test_app.py                    # End-to-end integration tests
│
├── sample_data/                   # Pre-packaged sample student test rosters
│   ├── sample_students.xlsx       # Sample 10-student Excel roster
│   ├── sample_students.csv        # Sample 10-student CSV roster
│   └── sample_students.pdf        # Sample 10-student PDF roster table
│
├── static/
│   ├── css/
│   │   └── style.css              # Custom modern UI styling & glassmorphism
│   ├── js/
│   │   └── main.js                # Canvas drag-and-drop coordinate editor & AJAX
│   ├── fonts/                     # TTF Fonts (GreatVibes, Montserrat, Roboto)
│   │   ├── GreatVibes-Regular.ttf
│   │   ├── Montserrat-Bold.ttf
│   │   ├── Montserrat-Regular.ttf
│   │   └── Roboto-Regular.ttf
│   └── sample_templates/          # High-resolution built-in certificate templates
│       ├── classic_gold.png       # 1920x1080 Classic Gold Luxury Template
│       └── modern_blue.png        # 1920x1080 Modern Tech Blue Template
│
├── templates/
│   ├── base.html                  # Base layout with navbar and sample asset dropdowns
│   ├── index.html                 # Upload page + Live Canvas Coordinate Editor
│   ├── preview.html               # Dedicated live certificate inspector
│   └── dashboard.html             # Admin dashboard with batch analytics & downloads
│
├── uploads/
│   ├── data_files/                # Uploaded Excel/CSV/PDF files
│   └── template_files/            # Uploaded custom templates
│
├── generated_certificates/        # Output directory for batches and ZIP archives
│
├── utils/
│   ├── __init__.py
│   ├── data_extractor.py          # Universal parser (Excel, CSV, PDF, OCR)
│   ├── certificate_maker.py       # High-DPI Pillow text renderer & preview maker
│   ├── zip_helper.py              # ZIP compression utility
│   └── sample_generator.py        # Generates sample templates, datasets, and fonts
│
└── README.md                      # Documentation & instructions
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13 supported)
- pip package manager

### 2. Installation

1. Open your terminal in the project root:
   ```bash
   cd "d:/ai certificate project"
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Initialize sample assets:
   ```bash
   python utils/sample_generator.py
   ```

### 3. Run the Web Application

Start the Flask development server:
```bash
python app.py
```

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

To run the core engine tests (data extraction, Pillow rendering, Unicode names, and ZIP archiving):
```bash
python test_core.py
```

To run the complete Flask application integration tests:
```bash
python test_app.py
```

---

## 📋 Sample Data Structure

The system automatically recognizes diverse column headers. Standard supported format:

| Name | Course | Date | Grade | Certificate_ID |
| :--- | :--- | :--- | :--- | :--- |
| **Sophia Laurent** | Advanced Deep Learning & Neural Networks | 2026-02-15 | A+ Distinction | CERT-2026-001 |
| **José García Müller** | Full-Stack Web Development Mastery | 2026-02-15 | A | CERT-2026-002 |
| **Aarav Sharma** | Python for Data Science & Machine Learning | 2026-02-16 | A+ | CERT-2026-003 |

*Pre-generated sample test files are located in `sample_data/` and can also be downloaded directly from the top navigation dropdown in the UI.*

---

## ⚙️ Customizing Coordinates (`config.json`)

Coordinates and styling for templates can be updated visually using the **Live Canvas Editor** or directly inside `config.json`:

```json
{
  "templates": {
    "classic_gold.png": {
      "width": 1920,
      "height": 1080,
      "fields": {
        "NAME": {
          "x": 960,
          "y": 500,
          "font_family": "GreatVibes-Regular.ttf",
          "font_size": 76,
          "color": "#1A2530",
          "alignment": "center"
        },
        "COURSE": {
          "x": 960,
          "y": 660,
          "font_family": "Montserrat-Bold.ttf",
          "font_size": 34,
          "color": "#946C15",
          "alignment": "center",
          "transform": "uppercase",
          "max_width": 1400
        }
      }
    }
  }
}
```

---

## 🔍 OCR Support for Scanned PDFs

For scanned PDFs containing images of student tables, `pdfplumber` and `pytesseract` automatically attempt OCR extraction.
If using Tesseract on Windows:
1. Download and install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
2. Ensure `tesseract.exe` is added to your system `PATH` (typically `C:\Program Files\Tesseract-OCR`).

---

## 📜 License
MIT License - Open for academic, personal, and commercial certificate generation.
