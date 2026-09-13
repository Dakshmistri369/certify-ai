"""
sample_generator.py
Utility script to generate sample certificate templates, fonts, and test student datasets.
"""

import os
import datetime
from typing import List, Dict, Any
import requests
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "static", "fonts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "sample_templates")
SAMPLE_DATA_DIR = os.path.join(BASE_DIR, "sample_data")


def download_free_fonts():
    """Download Google TTF fonts (Montserrat, Roboto, GreatVibes) if missing."""
    os.makedirs(FONTS_DIR, exist_ok=True)
    urls = {
        "GreatVibes-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/greatvibes/GreatVibes-Regular.ttf",
        "Montserrat-Bold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
        "Montserrat-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
        "Roboto-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/apache/roboto/Roboto-Regular.ttf"
    }
    for name, url in urls.items():
        dest = os.path.join(FONTS_DIR, name)
        if not os.path.exists(dest):
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    with open(dest, "wb") as f:
                        f.write(res.content)
            except Exception:
                pass


def create_classic_gold_template(output_path: str):
    """Generate 1920x1080 Classic Gold Template."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#FAF8F2")
    draw = ImageDraw.Draw(img)

    # Borders
    draw.rectangle([45, 45, w - 45, h - 45], outline="#1E293B", width=8)
    draw.rectangle([65, 65, w - 65, h - 65], outline="#C5A059", width=4)
    draw.rectangle([75, 75, w - 75, h - 75], outline="#E2C992", width=1)

    # Corners
    for cx, cy in [(55, 55), (w - 105, 55), (55, h - 105), (w - 105, h - 105)]:
        draw.rectangle([cx, cy, cx + 50, cy + 50], outline="#C5A059", width=2)

    # Header and static texts
    try:
        f_title = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"), 48)
        f_sub = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Regular.ttf"), 20)
        f_foot = ImageFont.truetype(os.path.join(FONTS_DIR, "Roboto-Regular.ttf"), 16)
    except Exception:
        f_title = f_sub = f_foot = ImageFont.load_default()

    draw.text((w / 2, 180), "CERTIFICATE OF ACHIEVEMENT", fill="#C5A059", font=f_title, anchor="mm")
    draw.text((w / 2, 270), "THIS IS PROUDLY PRESENTED TO", fill="#64748B", font=f_sub, anchor="mm")
    draw.line([(w / 2 - 250, 320), (w / 2 + 250, 320)], fill="#C5A059", width=2)
    draw.ellipse([w / 2 - 6, 314, w / 2 + 6, 326], fill="#C5A059")

    # Signatures
    draw.line([(380, 920), (780, 920)], fill="#94A3B8", width=2)
    draw.line([(1140, 920), (1540, 920)], fill="#94A3B8", width=2)
    draw.text((580, 935), "AUTHORIZED SIGNATURE", fill="#64748B", font=f_foot, anchor="mm")
    draw.text((1340, 935), "PROGRAM DIRECTOR", fill="#64748B", font=f_foot, anchor="mm")

    # Gold Seal Badge
    draw.ellipse([w / 2 - 55, 880 - 55, w / 2 + 55, 880 + 55], fill="#C5A059", outline="#946C15", width=3)
    draw.ellipse([w / 2 - 47, 880 - 47, w / 2 + 47, 880 + 47], outline="#FAF8F2", width=2)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created Classic Gold Template at: {output_path}")


def create_modern_blue_template(output_path: str):
    """Generate 1920x1080 Modern Tech Blue Template."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Bars and geometric framing
    draw.rectangle([0, 0, w, 35], fill="#0F172A")
    draw.rectangle([0, 35, w, 45], fill="#2563EB")
    draw.rectangle([0, h - 35, w, h], fill="#0F172A")
    draw.rectangle([0, h - 45, w, h - 35], fill="#3B82F6")

    draw.polygon([(0, 45), (140, 45), (0, 320)], fill="#1E40AF")
    draw.polygon([(0, 45), (60, 45), (0, 180)], fill="#60A5FA")
    draw.polygon([(w, h - 45), (w - 140, h - 45), (w, h - 320)], fill="#1E40AF")
    draw.polygon([(w, h - 45), (w - 60, h - 45), (w, h - 180)], fill="#60A5FA")
    draw.rectangle([60, 60, w - 60, h - 60], outline="#E2E8F0", width=2)

    try:
        f_title = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"), 52)
        f_sub = ImageFont.truetype(os.path.join(FONTS_DIR, "Montserrat-Regular.ttf"), 22)
        f_foot = ImageFont.truetype(os.path.join(FONTS_DIR, "Roboto-Regular.ttf"), 16)
    except Exception:
        f_title = f_sub = f_foot = ImageFont.load_default()

    draw.text((w / 2, 160), "CERTIFICATE OF RECOGNITION", fill="#0F172A", font=f_title, anchor="mm")
    draw.text((w / 2, 255), "THIS CERTIFIES THAT", fill="#64748B", font=f_sub, anchor="mm")
    draw.line([(w / 2 - 180, 295), (w / 2 + 180, 295)], fill="#2563EB", width=3)

    # Signatures
    draw.line([(340, 910), (740, 910)], fill="#94A3B8", width=2)
    draw.line([(1180, 910), (1580, 910)], fill="#94A3B8", width=2)
    draw.text((540, 925), "INSTRUCTOR SIGNATURE", fill="#64748B", font=f_foot, anchor="mm")
    draw.text((1380, 925), "DEAN OF ACADEMICS", fill="#64748B", font=f_foot, anchor="mm")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created Modern Blue Template at: {output_path}")


def get_50_sample_students() -> List[Dict[str, Any]]:
    """Return 50 diverse student records."""
    names = [
        "Sophia Laurent", "José García Müller", "Aarav Sharma", "Emily Watson", "Kenji Takahashi",
        "Fatima Al-Mansoor", "Lucas Silva Santos", "Elena Rostova", "Liam O'Connor", "Zoe Chen",
        "Mahi Dhaval Kumar Patel", "Kazmeenkhan Safdarkhan Pathan", "Patel Pal Vinodkumar", "Suthar Bhavy Kumar Joitabhai", "Patel Krisa Jayeshkumar",
        "Patel Khushi Vishnubhai", "Thakor Yash Kumar Jayantiji", "Kashish Mukeshbhai Mudethiya", "Mistri Daksh Ashokkumar", "Prajapati Bhavik Kantilal",
        "Shravan Deoghare Rajubhai", "Patel Mankumar Navinkumar", "Maharsh Manishbhai Patel", "Dhruvil R. Prajapati", "Ananya Deshmukh",
        "Gabriel Rodriguez", "Mei-Ling Zhou", "Alexander Wright", "Chloe Dubois", "Tariq Mahmoud",
        "Vikram Singhania", "Isabella Rossi", "Mateo Hernandez", "Hana Al-Hashimi", "Oliver Bennett",
        "Pooja Venkatesh", "Sebastian Vance", "Aoi Tanaka", "Dmitri Volkov", "Camila Santos",
        "Devang Dave", "Priyanka Nambiar", "Noah van der Berg", "Amara Okafor", "Felix Moreau",
        "Tanvi Agarwal", "Diego Morales", "Nadia Petrova", "Ethan Harper", "Zara Qureshi"
    ]
    courses = [
        "Artificial Intelligence & Neural Architectures", "Full-Stack Web Development Mastery",
        "Data Science & Predictive Modeling", "Cloud Computing & DevOps Engineering",
        "Cybersecurity & Threat Intelligence", "UI/UX Design Systems & Interfaces"
    ]
    grades = ["A+ Distinction", "Grade A", "With Honors (A+)", "First Class Distinction", "Grade A+"]
    base_date = datetime.date(2026, 9, 8)

    return [{
        "Sr. No.": str(i + 1),
        "Full Name (First Name Father Name Surname)": name,
        "Name": name,
        "Course": courses[i % len(courses)],
        "Date": (base_date - datetime.timedelta(days=i % 15)).strftime("%B %d, %Y"),
        "Grade": grades[i % len(grades)],
        "Certificate_ID": f"CERT-2026-{i + 1:04d}",
        "Roll Number": f"{101 + i}",
        "Email": f"{name.lower().replace(' ', '.').replace('-', '')[:15]}@university.edu",
        "Phone Number": f"+91 {9800000000 + (i * 123456 % 199999999)}"
    } for i, name in enumerate(names)]


def generate_sample_datasets():
    """Create sample Excel, CSV, and PDF datasets."""
    os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
    s50 = get_50_sample_students()
    s10 = s50[:10]

    # 1. 10 students
    df10 = pd.DataFrame([{"Name": s["Name"], "Course": s["Course"], "Date": s["Date"], "Grade": s["Grade"], "Certificate_ID": s["Certificate_ID"]} for s in s10])
    df10.to_excel(os.path.join(SAMPLE_DATA_DIR, "sample_students.xlsx"), index=False, engine="openpyxl")
    df10.to_csv(os.path.join(SAMPLE_DATA_DIR, "sample_students.csv"), index=False, encoding="utf-8")

    # 2. 50 students
    df50 = pd.DataFrame(s50)
    df50.to_excel(os.path.join(SAMPLE_DATA_DIR, "sample_50_students.xlsx"), index=False, engine="openpyxl")
    df50.to_csv(os.path.join(SAMPLE_DATA_DIR, "sample_50_students.csv"), index=False, encoding="utf-8")

    # 3. PDF datasets
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        style = ParagraphStyle('Title', parent=getSampleStyleSheet()['Heading1'], fontSize=16, spaceAfter=10, textColor=colors.HexColor("#1E293B"))

        # 10 PDF
        doc10 = SimpleDocTemplate(os.path.join(SAMPLE_DATA_DIR, "sample_students.pdf"), pagesize=landscape(letter), margin=25)
        t10_data = [["Name", "Course", "Date", "Grade", "Certificate_ID"]] + [[s["Name"], s["Course"], s["Date"], s["Grade"], s["Certificate_ID"]] for s in s10]
        t10 = Table(t10_data, colWidths=[120, 260, 90, 100, 130])
        t10.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
        ]))
        doc10.build([Paragraph("Student Certificate Roster (10 Students)", style), Spacer(1, 10), t10])

        # 50 PDF
        doc50 = SimpleDocTemplate(os.path.join(SAMPLE_DATA_DIR, "sample_50_students.pdf"), pagesize=landscape(letter), margin=25)
        t50_data = [["Sr No", "Name", "Course", "Date", "Grade", "Cert ID"]] + [[s["Sr. No."], s["Name"], s["Course"], s["Date"], s["Grade"], s["Certificate_ID"]] for s in s50]
        t50 = Table(t50_data, colWidths=[45, 140, 220, 90, 85, 110], repeatRows=1)
        t50.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
        ]))
        doc50.build([Paragraph("Master Student Certificate Roster (50 Students)", style), Spacer(1, 10), t50])
    except Exception as e:
        print(f"ReportLab note: {e}")


def initialize_all_sample_assets():
    """Ensure all sample templates, fonts, and datasets exist."""
    download_free_fonts()
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    create_classic_gold_template(os.path.join(TEMPLATES_DIR, "classic_gold.png"))
    create_modern_blue_template(os.path.join(TEMPLATES_DIR, "modern_blue.png"))
    generate_sample_datasets()


if __name__ == "__main__":
    initialize_all_sample_assets()
