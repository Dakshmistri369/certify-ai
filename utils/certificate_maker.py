"""
certificate_maker.py
High-DPI Certificate Rendering Engine using Pillow, ReportLab, and PyPDF.
Supports dynamic text placement, custom fonts, auto-scaling, QR codes, and export to PDF/PNG.
"""

import os
import re
import io
import base64
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont

try:
    import qrcode
except ImportError:
    qrcode = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "static", "fonts")
_FONT_CACHE: Dict[Tuple[str, int], ImageFont.ImageFont] = {}

FIELD_ALIASES: Dict[str, List[str]] = {
    "NAME": ["FULL_NAME", "FULLNAME", "STUDENT_NAME", "CANDIDATE_NAME", "NAME_OF_STUDENT", "PARTICIPANT_NAME", "STUDENT", "RECIPIENT"],
    "COURSE": ["COURSE_NAME", "COURSE_TITLE", "STREAM", "BRANCH", "SUBJECT", "PROGRAM", "WORKSHOP", "DEGREE"],
    "GRADE": ["GRADUATION_MARKS", "MARKS", "SCORE", "CGPA", "GPA", "PERCENTAGE", "RESULT", "PERFORMANCE"],
    "CERT_ID": ["ROLL_NUMBER", "ROLL_NO", "REG_NO", "REGISTRATION_NO", "STUDENT_ID", "ID", "SERIAL_NO", "CREDENTIAL_ID"],
    "EMAIL": ["EMAIL_ID", "EMAIL_ADDRESS", "MAIL"],
    "PHONE": ["PHONE_NUMBER", "MOBILE", "MOBILE_NUMBER", "CONTACT", "WHATSAPP"],
    "INSTITUTE": ["INSTITUTION", "UNIVERSITY", "COLLEGE", "SCHOOL", "ACADEMY", "ORGANIZATION"],
    "INSTRUCTOR": ["TRAINER", "TEACHER", "PROFESSOR", "MENTOR", "SIGNATORY", "DIRECTOR"]
}


def sanitize_filename(name: str) -> str:
    """Sanitize student name or ID for safe file naming."""
    clean = re.sub(r'[\\/*?:"<>|\r\n\t]+', '_', str(name or "Student").strip())
    clean = re.sub(r'[\s_]+', '_', clean).strip('_')
    return clean or "Student"


def get_font(font_family: str, font_size: int) -> ImageFont.ImageFont:
    """Load TTF font with caching and system fallbacks."""
    key = (font_family, font_size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    clean_name = os.path.basename(font_family)
    candidates = [
        os.path.join(FONTS_DIR, clean_name),
        os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"),
        os.path.join(FONTS_DIR, "Roboto-Regular.ttf"),
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\georgia.ttf",
        "C:\\Windows\\Fonts\\times.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, font_size)
                _FONT_CACHE[key] = font
                return font
            except Exception:
                continue
    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    if not isinstance(hex_color, str):
        return (0, 0, 0)
    c = hex_color.lstrip('#')
    if len(c) == 3:
        c = ''.join(ch * 2 for ch in c)
    if len(c) == 6:
        try:
            return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
        except ValueError:
            pass
    return (0, 0, 0)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex string."""
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def wrap_text(text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    """Wrap text to fit within max_width pixels."""
    if not max_width or max_width <= 0:
        return [text]
    words = text.split()
    if not words:
        return [""]
    lines, current = [], []
    for word in words:
        test_line = ' '.join(current + [word])
        try:
            w = font.getbbox(test_line)[2] - font.getbbox(test_line)[0]
        except Exception:
            w = len(test_line) * 10
        if w <= max_width or not current:
            current.append(word)
        else:
            lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines


def open_template_image(template_path: str) -> Image.Image:
    """Open template image; renders first page if template is PDF."""
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    if template_path.lower().endswith('.pdf'):
        try:
            import pdfplumber
            with pdfplumber.open(template_path) as pdf:
                if pdf.pages:
                    return pdf.pages[0].to_image(resolution=300).original.convert("RGB")
        except Exception as e:
            raise RuntimeError(f"Could not render PDF template: {e}")
    return Image.open(template_path).convert("RGB")


def find_student_value(student_data: Dict[str, Any], field_key: str) -> Optional[str]:
    """Lookup student value using exact, uppercase, lowercase, slug, or alias matching."""
    if not student_data:
        return None
    for k in (field_key, field_key.upper(), field_key.lower()):
        if k in student_data and student_data[k] is not None:
            return str(student_data[k])
    clean_k = re.sub(r'[^a-zA-Z0-9]', '', field_key).lower()
    for sk, sv in student_data.items():
        if re.sub(r'[^a-zA-Z0-9]', '', str(sk)).lower() == clean_k and sv is not None:
            return str(sv)
    k_upper = field_key.upper()
    if k_upper in FIELD_ALIASES:
        for alias in FIELD_ALIASES[k_upper]:
            if alias in student_data and student_data[alias] is not None:
                return str(student_data[alias])
    return None


def generate_qr_code_image(data_text: str, size: int = 150) -> Image.Image:
    """Generate high-contrast QR code image."""
    if qrcode is not None:
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(data_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        return img.resize((size, size), Image.Resampling.LANCZOS)
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, size-1, size-1], outline=(0, 0, 0, 255), width=2)
    d.text((10, size//2 - 10), "QR CODE", fill=(0, 0, 0, 255))
    return img


def extract_template_palette(template_path: str) -> Dict[str, Any]:
    """Extract dominant colors and dimensions from template."""
    img = open_template_image(template_path)
    w, h = img.size
    thumb = img.copy().resize((200, 200), Image.Resampling.BILINEAR)
    quant = thumb.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
    palette_raw = quant.getpalette()[:48]
    
    rgbs = [(palette_raw[i], palette_raw[i+1], palette_raw[i+2]) for i in range(0, len(palette_raw), 3)]
    unique = []
    for c in rgbs:
        if not any(sum((a - b) ** 2 for a, b in zip(c, u)) ** 0.5 < 40 for u in unique):
            unique.append(c)
    
    hex_colors = [rgb_to_hex(c) for c in unique]
    dark_colors = [c for c in unique if (c[0]*299 + c[1]*587 + c[2]*114)/1000 < 130]
    primary_dark = rgb_to_hex(dark_colors[0]) if dark_colors else "#0C0C0C"
    
    defaults = ["#0C0C0C", "#481E14", "#9B3922", "#A8A492", "#B54328"]
    for d in defaults:
        if d not in hex_colors and len(hex_colors) < 5:
            hex_colors.append(d)

    return {
        "width": w,
        "height": h,
        "orientation": "landscape" if w >= h else "portrait",
        "aspect_ratio": f"{round(w/h, 2)}:1",
        "palette": hex_colors[:5],
        "primary_dark": primary_dark,
        "accent": hex_colors[0] if hex_colors else "#9B3922"
    }


def clean_template_background(img: Image.Image, clean_box: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
    """Erase baked-in placeholder text by sampling background color."""
    w, h = img.size
    try:
        bg_rgb = img.getpixel((int(w * 0.35), int(h * 0.44)))[:3]
    except Exception:
        bg_rgb = (255, 255, 255)
    box = clean_box or (int(w * 0.175), int(h * 0.395), int(w * 0.825), int(h * 0.630))
    ImageDraw.Draw(img).rectangle(box, fill=bg_rgb)
    return img


def render_certificate(
    template_image: Image.Image,
    student_data: Dict[str, Any],
    config_fields: Dict[str, Any],
    clean_dummy_text: bool = True
) -> Image.Image:
    """Render dynamic text and QR fields onto template image."""
    cert_img = template_image.copy()
    if clean_dummy_text:
        cert_img = clean_template_background(cert_img)

    draw = ImageDraw.Draw(cert_img)

    for field_key, cfg in config_fields.items():
        if field_key.startswith("_") or not isinstance(cfg, dict):
            continue

        is_qr = cfg.get("type") == "qr" or field_key.upper() in ["QR", "QR_CODE", "QRCODE"]
        if is_qr:
            qr_val = find_student_value(student_data, field_key) or find_student_value(student_data, "CERT_ID") or "https://certifyai.local/verify"
            size = max(50, int(cfg.get("font_size", 140)))
            qr_img = generate_qr_code_image(str(qr_val), size=size)
            x, y = int(cfg.get("x", 100)), int(cfg.get("y", 100))
            draw_x = x - (size // 2) if cfg.get("alignment") == "center" else (x - size if cfg.get("alignment") == "right" else x)
            cert_img.paste(qr_img, (draw_x, y), mask=qr_img)
            continue

        val = find_student_value(student_data, field_key)
        if val is None or str(val).strip() == "":
            continue

        raw = str(val).strip()
        transform = cfg.get("transform", "none")
        if transform == "uppercase":
            raw = raw.upper()
        elif transform == "lowercase":
            raw = raw.lower()
        elif transform == "title":
            raw = raw.title()

        full_text = f"{cfg.get('prefix', '')}{raw}{cfg.get('suffix', '')}"
        x, y = int(cfg.get("x", 100)), int(cfg.get("y", 100))
        font_size = int(cfg.get("font_size", 32))
        font_family = cfg.get("font_family", "Montserrat-Bold.ttf")
        color_rgb = hex_to_rgb(cfg.get("color", "#0C0C0C"))
        alignment = cfg.get("alignment", "center").lower()
        max_width = int(cfg.get("max_width", 0))

        # Dynamic auto-scaling for single-line / long names
        allowed_max_w = max_width if max_width > 0 else int(cert_img.width * 0.75)
        font = get_font(font_family, font_size)
        if field_key.upper() == "NAME" or max_width == 0:
            sz = font_size
            while sz > 20:
                test_font = get_font(font_family, sz)
                try:
                    tb = test_font.getbbox(full_text)
                    tw = tb[2] - tb[0]
                except Exception:
                    tw = len(full_text) * (sz * 0.6)
                if tw <= allowed_max_w:
                    font, font_size = test_font, sz
                    break
                sz -= 2

        lines = wrap_text(full_text, font, max_width)
        offset_y = 0
        for line in lines:
            try:
                bbox = font.getbbox(line)
                lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
            except Exception:
                lw, lh = len(line) * (font_size * 0.6), font_size

            draw_x = x - (lw / 2) if alignment == "center" else (x - lw if alignment == "right" else x)
            draw.text((draw_x, y + offset_y), line, fill=color_rgb, font=font)
            offset_y += int(lh * 1.3)

    return cert_img


def generate_single_certificate(
    template_path: str,
    student_data: Dict[str, Any],
    config_fields: Dict[str, Any],
    output_dir: str,
    export_format: str = "pdf",
    clean_dummy_text: bool = True
) -> Dict[str, str]:
    """Generate and save single student certificate."""
    os.makedirs(output_dir, exist_ok=True)
    tpl_img = open_template_image(template_path)
    rendered = render_certificate(tpl_img, student_data, config_fields, clean_dummy_text=clean_dummy_text)

    name = sanitize_filename(find_student_value(student_data, "NAME") or "Student")
    cid = sanitize_filename(find_student_value(student_data, "CERT_ID") or "ID")
    base_name = f"{name}_{cid}"
    results = {}

    if export_format in ["png", "both"]:
        png_path = os.path.join(output_dir, f"{base_name}.png")
        rendered.save(png_path, format="PNG", dpi=(300, 300))
        results["png"] = png_path

    if export_format in ["pdf", "both"]:
        pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
        rendered.save(pdf_path, format="PDF", resolution=300.0)
        results["pdf"] = pdf_path

    return results


def generate_preview_base64(
    template_path: str,
    student_data: Optional[Dict[str, Any]],
    config_fields: Dict[str, Any],
    clean_dummy_text: bool = True
) -> str:
    """Generate in-memory preview image as base64 JPEG data URI."""
    data = student_data or {
        "NAME": "Alexander Morgan",
        "COURSE": "Artificial Intelligence & Neural Architectures",
        "DATE": "February 18, 2026",
        "GRADE": "Grade A+",
        "CERT_ID": "CERT-2026-9901"
    }
    tpl_img = open_template_image(template_path)
    rendered = render_certificate(tpl_img, data, config_fields, clean_dummy_text=clean_dummy_text)

    if max(rendered.size) > 1600:
        ratio = 1600 / max(rendered.size)
        rendered = rendered.resize((int(rendered.width * ratio), int(rendered.height * ratio)), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    rendered.save(buf, format="JPEG", quality=92, optimize=True)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
