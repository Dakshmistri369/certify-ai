"""
sustainability_generator.py
High-resolution 1920x1080 master template generator for CertifyAI.
Faithfully recreates the 6 certificate styles from user specifications:
1. Midnight Luxury Navy (sustainability_midnight.png)
2. Classic Cyan Guilloche (sustainability_cyan.png)
3. Vintage Slate Filigree & Gold (sustainability_slate.png)
4. Modern Corporate Geometric Facets (sustainability_modern.png)
5. Royal Academic Navy & Rosette (sustainability_academic.png)
6. Traditional Security Lace Guilloche (sustainability_lace.png)
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, "static", "fonts")
TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "sample_templates")


def get_font_safe(name: str, size: int) -> ImageFont.ImageFont:
    """Load TTF font with fallback to system fonts."""
    candidates = [
        os.path.join(FONTS_DIR, name),
        os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"),
        os.path.join(FONTS_DIR, "Roboto-Regular.ttf"),
        "C:\\Windows\\Fonts\\georgia.ttf",
        "C:\\Windows\\Fonts\\times.ttf",
        "C:\\Windows\\Fonts\\arial.ttf"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_vector_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, r_outer: float, r_inner: float, fill: str = "#754E05"):
    """Draw a vector 5-pointed star."""
    pts = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=fill)


def draw_metallic_gold_seal(cx: float, cy: float, radius: float = 72) -> Image.Image:
    """
    Render an ultra-crisp, photorealistic metallic embossed gold medallion badge.
    Includes ribbon tails, scalloped starburst teeth, embossed metallic rings, beads,
    5 vector gold stars, and embossed typography.
    """
    size = int(radius * 2.6)
    badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    bcx, bcy = size / 2, size / 2

    # Ribbon tails behind the seal
    r_len = radius * 1.35
    pts_left = [
        (bcx - radius * 0.35, bcy + radius * 0.4),
        (bcx - radius * 0.78, bcy + r_len),
        (bcx - radius * 0.58, bcy + r_len * 0.88),
        (bcx - radius * 0.36, bcy + r_len),
        (bcx - radius * 0.05, bcy + radius * 0.6)
    ]
    d.polygon(pts_left, fill="#B8860B", outline="#785304")
    
    pts_right = [
        (bcx + radius * 0.05, bcy + radius * 0.6),
        (bcx + radius * 0.36, bcy + r_len),
        (bcx + radius * 0.58, bcy + r_len * 0.88),
        (bcx + radius * 0.78, bcy + r_len),
        (bcx + radius * 0.35, bcy + radius * 0.4)
    ]
    d.polygon(pts_right, fill="#B8860B", outline="#785304")

    # Scalloped Starburst teeth (40 teeth)
    teeth = 40
    star_pts = []
    for i in range(teeth * 2):
        angle = i * math.pi / teeth
        r = radius if i % 2 == 0 else radius * 0.91
        star_pts.append((bcx + r * math.cos(angle), bcy + r * math.sin(angle)))
    d.polygon(star_pts, fill="#C59B27", outline="#7E5806")

    # Concentric embossed rings with metallic shading
    d.ellipse([bcx - radius * 0.90, bcy - radius * 0.90, bcx + radius * 0.90, bcy + radius * 0.90], fill="#E5BB43", outline="#966C12", width=2)
    d.ellipse([bcx - radius * 0.82, bcy - radius * 0.82, bcx + radius * 0.82, bcy + radius * 0.82], fill="#F3D36C", outline="#7E5806", width=2)
    d.ellipse([bcx - radius * 0.77, bcy - radius * 0.77, bcx + radius * 0.77, bcy + radius * 0.77], outline="#FFF7CF", width=2)
    d.ellipse([bcx - radius * 0.72, bcy - radius * 0.72, bcx + radius * 0.72, bcy + radius * 0.72], fill="#D8A52C", outline="#875F09", width=2)

    # Beaded ring
    beads = 32
    b_rad = radius * 0.64
    for i in range(beads):
        ang = i * 2 * math.pi / beads
        bx = bcx + b_rad * math.cos(ang)
        by = bcy + b_rad * math.sin(ang)
        d.ellipse([bx - 2.5, by - 2.5, bx + 2.5, by + 2.5], fill="#FFF9DF", outline="#B8860B")

    # Core medallion disc
    d.ellipse([bcx - radius * 0.58, bcy - radius * 0.58, bcx + radius * 0.58, bcy + radius * 0.58], fill="#E8C04D", outline="#8C630A", width=2)
    d.ellipse([bcx - radius * 0.53, bcy - radius * 0.53, bcx + radius * 0.53, bcy + radius * 0.53], outline="#FFF5B8", width=1)

    # 5 Crisp Vector Gold Stars at top inside core
    star_offsets = [-0.34, -0.17, 0.0, 0.17, 0.34]
    for idx, off in enumerate(star_offsets):
        sx = bcx + radius * off
        sy = bcy - radius * (0.28 if idx in [1, 2, 3] else 0.24)
        draw_vector_star(d, sx, sy, radius * 0.08, radius * 0.035, fill="#754E05")

    # Medallion text
    f_badge = get_font_safe("Montserrat-Bold.ttf", int(radius * 0.14))
    f_year = get_font_safe("Montserrat-Bold.ttf", int(radius * 0.22))
    
    d.text((bcx, bcy - radius * 0.04), "OFFICIAL", fill="#754E05", font=f_badge, anchor="mm")
    d.text((bcx, bcy + radius * 0.14), "CERTIFICATE", fill="#754E05", font=f_badge, anchor="mm")
    d.text((bcx, bcy + radius * 0.34), "2026", fill="#634102", font=f_year, anchor="mm")

    return badge


def draw_footer_elements(img: Image.Image, text_color: str, sig_color: str):
    """Draw the Date baseline, Issue Date label, Cursive Signature 'A. Smith', and Gold Seal badge."""
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # Seal at (960, 875)
    seal = draw_metallic_gold_seal(w / 2, 875, radius=72)
    sw, sh = seal.size
    img.paste(seal, (int(w / 2 - sw / 2), int(875 - sh / 2 + 10)), mask=seal)

    draw = ImageDraw.Draw(img)

    # Left: Date Area
    f_label = get_font_safe("Montserrat-Regular.ttf", 15)
    draw.line([(320, 825), (520, 825)], fill=text_color, width=1)
    draw.text((420, 842), "Issue Date", fill=text_color, font=f_label, anchor="mm")

    # Right: Signature Area
    f_sig = get_font_safe("GreatVibes-Regular.ttf", 46)
    draw.text((1500, 800), "A. Smith", fill=sig_color, font=f_sig, anchor="mm")
    draw.line([(1400, 825), (1600, 825)], fill=text_color, width=1)
    draw.text((1500, 842), "Certificate Signatory", fill=text_color, font=f_label, anchor="mm")


# ==============================================================================
# 1. TEMPLATE: MIDNIGHT LUXURY NAVY (sustainability_midnight.png)
# ==============================================================================
def create_midnight_navy_template(output_path: str):
    """Deep navy luxury certificate with subtle diamond guilloche lattice, gold accents, and gold seal."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#0D1630")
    draw = ImageDraw.Draw(img)

    # Subtle gradient feel
    for i in range(h):
        ratio = abs(i - h / 2) / (h / 2)
        r = int(13 - ratio * 4)
        g = int(22 - ratio * 7)
        b = int(48 - ratio * 15)
        draw.line([(0, i), (w, i)], fill=(max(7, r), max(12, g), max(26, b)))

    # Geometric diamond lattice pattern across background
    step = 50
    for y in range(0, h + step * 2, step):
        for x in range(0, w + step * 2, step):
            pts1 = [(x, y - step // 2), (x + step // 2, y), (x, y + step // 2), (x - step // 2, y)]
            draw.polygon(pts1, outline="#182752", width=1)
            pts2 = [(x, y - step // 4), (x + step // 4, y), (x, y + step // 4), (x - step // 4, y)]
            draw.polygon(pts2, outline="#142045", width=1)

    # Gold double-frame borders
    draw.rectangle([45, 45, w - 45, h - 45], outline="#C5A059", width=3)
    draw.rectangle([62, 62, w - 62, h - 62], outline="#D4AF37", width=1)

    # Corner diamond ornaments
    corners = [(45, 45), (w - 45, 45), (45, h - 45), (w - 45, h - 45)]
    for cx, cy in corners:
        d_pts = [(cx, cy - 14), (cx + 14, cy), (cx, cy + 14), (cx - 14, cy)]
        draw.polygon(d_pts, fill="#C5A059", outline="#E5C07B")
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill="#FAF8F2")

    # Header Text
    f_title = get_font_safe("Times-Bold.ttf", 46)
    f_sub = get_font_safe("Georgia-Regular.ttf", 20)

    draw.text((w / 2, 145), "TWO-DAY SUSTAINABILITY", fill="#E5C07B", font=f_title, anchor="mm")
    draw.text((w / 2, 205), "CERTIFICATE", fill="#E5C07B", font=f_title, anchor="mm")
    draw.text((w / 2, 260), "Presented in recognition of attendance", fill="#94A3B8", font=f_sub, anchor="mm")

    # Subtle gold horizontal divider rules for recipient area
    draw.line([(w / 2 - 320, 395), (w / 2 + 320, 395)], fill="#2E4077", width=1)
    draw.line([(w / 2 - 200, 395), (w / 2 + 200, 395)], fill="#C5A059", width=2)
    draw.ellipse([w / 2 - 5, 395 - 5, w / 2 + 5, 395 + 5], fill="#C5A059")

    # Footer elements
    draw_footer_elements(img, text_color="#94A3B8", sig_color="#E2E8F0")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created: {output_path}")


# ==============================================================================
# 2. TEMPLATE: CLASSIC CYAN GUILLOCHE (sustainability_cyan.png)
# ==============================================================================
def create_cyan_guilloche_template(output_path: str):
    """Crisp white certificate with cyan security guilloche wavy border, central rosette, and gold seal."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Central faint cyan radial rosette watermark
    cx, cy = w / 2, h / 2 + 20
    num_petals = 16
    curves_per_petal = 42
    for k in range(curves_per_petal):
        phase = k * (2 * math.pi / curves_per_petal)
        pts = []
        for a in range(0, 360, 4):
            rad = math.radians(a)
            r = 340 + 65 * math.sin(num_petals * rad + phase)
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        draw.polygon(pts, outline="#EDF7FE", width=1)

    # Perimeter Guilloche Security Wavy Border
    margin = 40
    bw = 36
    steps = 400
    for layer in range(12):
        freq = 28 + (layer % 4) * 2
        amp = 14 + (layer % 3) * 4
        phase = layer * 0.45
        alpha_color = "#1D70B8" if layer % 2 == 0 else "#38BDF8"

        pts_top, pts_bot = [], []
        for i in range(steps + 1):
            px = margin + i * (w - 2 * margin) / steps
            py_top = margin + bw / 2 + amp * math.sin(i * freq * 2 * math.pi / steps + phase)
            py_bot = h - margin - bw / 2 + amp * math.sin(i * freq * 2 * math.pi / steps + phase)
            pts_top.append((px, py_top))
            pts_bot.append((px, py_bot))

        draw.line(pts_top, fill=alpha_color, width=1)
        draw.line(pts_bot, fill=alpha_color, width=1)

    steps_v = 240
    for layer in range(12):
        freq = 18 + (layer % 4) * 2
        amp = 14 + (layer % 3) * 4
        phase = layer * 0.45
        alpha_color = "#1D70B8" if layer % 2 == 0 else "#38BDF8"

        pts_l, pts_r = [], []
        for i in range(steps_v + 1):
            py = margin + i * (h - 2 * margin) / steps_v
            px_l = margin + bw / 2 + amp * math.sin(i * freq * 2 * math.pi / steps_v + phase)
            px_r = w - margin - bw / 2 + amp * math.sin(i * freq * 2 * math.pi / steps_v + phase)
            pts_l.append((px_l, py))
            pts_r.append((px_r, py))

        draw.line(pts_l, fill=alpha_color, width=1)
        draw.line(pts_r, fill=alpha_color, width=1)

    # Inner framing rectangle
    draw.rectangle([margin + bw + 10, margin + bw + 10, w - (margin + bw + 10), h - (margin + bw + 10)], outline="#BAE6FD", width=1)

    # Header Text
    f_title = get_font_safe("Georgia-Regular.ttf", 50)
    f_sub = get_font_safe("Georgia-Regular.ttf", 20)

    draw.text((w / 2, 140), "Two-Day Sustainability", fill="#1D4E89", font=f_title, anchor="mm")
    draw.text((w / 2, 200), "Certificate", fill="#1D4E89", font=f_title, anchor="mm")
    draw.text((w / 2, 255), "Presented in recognition of attendance", fill="#475569", font=f_sub, anchor="mm")

    # Horizontal divider rule
    draw.line([(w / 2 - 240, 395), (w / 2 + 240, 395)], fill="#0284C7", width=2)

    # Footer elements
    draw_footer_elements(img, text_color="#475569", sig_color="#1D4E89")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created: {output_path}")


# ==============================================================================
# 3. TEMPLATE: VINTAGE SLATE FILIGREE & GOLD (sustainability_slate.png)
# ==============================================================================
def create_slate_filigree_template(output_path: str):
    """Deep charcoal/slate background with rich Victorian filigree corner scrollwork and gold seal."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#181D26")
    draw = ImageDraw.Draw(img)

    # Subtle gradient
    for i in range(h):
        ratio = abs(i - h / 2) / (h / 2)
        v = int(24 - ratio * 7)
        draw.line([(0, i), (w, i)], fill=(v, v + 4, v + 12))

    # Inner decorative border frame
    draw.rectangle([55, 55, w - 55, h - 55], outline="#4A5568", width=1)
    draw.rectangle([72, 72, w - 72, h - 72], outline="#C5A059", width=2)
    draw.rectangle([82, 82, w - 82, h - 82], outline="#2D3748", width=1)

    # Ornate Victorian Corner Filigree Scrollwork Flourishes
    def draw_rich_corner_filigree(cx, cy, dir_x, dir_y):
        for base_r, lw, col in [(45, 2, '#CBD5E1'), (75, 2, '#D4AF37'), (105, 2, '#94A3B8'), (135, 2, '#E2E8F0'), (165, 2, '#C5A059')]:
            pts = []
            for deg in range(0, 92, 2):
                rad = math.radians(deg)
                r = base_r + 16 * math.sin(deg * 4 * math.pi / 180) * (deg / 90.0)
                px = cx + dir_x * (r * math.cos(rad))
                py = cy + dir_y * (r * math.sin(rad))
                pts.append((px, py))
            draw.line(pts, fill=col, width=lw)

        # Gold accent beads
        for dist in [65, 115, 160]:
            bx = cx + dir_x * dist
            by = cy + dir_y * dist
            draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill="#D4AF37", outline="#F7FAFC")
            draw.line([(cx + dir_x * 20, by), (bx, by)], fill="#4A5568", width=1)
            draw.line([(bx, cy + dir_y * 20), (bx, by)], fill="#4A5568", width=1)

    draw_rich_corner_filigree(82, 82, 1, 1)          # Top-Left
    draw_rich_corner_filigree(w - 82, 82, -1, 1)     # Top-Right
    draw_rich_corner_filigree(82, h - 82, 1, -1)     # Bottom-Left
    draw_rich_corner_filigree(w - 82, h - 82, -1, -1)# Bottom-Right

    # Header Text
    f_title = get_font_safe("Times-Bold.ttf", 46)
    f_sub = get_font_safe("Georgia-Regular.ttf", 20)

    draw.text((w / 2, 145), "TWO-DAY SUSTAINABILITY", fill="#FFFFFF", font=f_title, anchor="mm")
    draw.text((w / 2, 205), "CERTIFICATE", fill="#FFFFFF", font=f_title, anchor="mm")
    draw.text((w / 2, 260), "Presented in recognition of attendance", fill="#A0AEC0", font=f_sub, anchor="mm")

    # Horizontal divider rule
    draw.line([(w / 2 - 280, 395), (w / 2 + 280, 395)], fill="#4A5568", width=1)
    draw.line([(w / 2 - 160, 395), (w / 2 + 160, 395)], fill="#C5A059", width=2)

    # Footer elements
    draw_footer_elements(img, text_color="#A0AEC0", sig_color="#FFFFFF")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created: {output_path}")


# ==============================================================================
# 4. TEMPLATE: MODERN CORPORATE GEOMETRIC (sustainability_modern.png)
# ==============================================================================
def create_modern_geometric_template(output_path: str):
    """Crisp modern white certificate with faceted translucent cyan/blue corner polygons and gold seal."""
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_over = ImageDraw.Draw(overlay)

    # Top-Right Translucent Faceted Polygons
    d_over.polygon([(w, 0), (w - 550, 0), (w, 360)], fill=(186, 230, 253, 90))
    d_over.polygon([(w, 0), (w - 360, 0), (w, 480)], fill=(125, 211, 252, 110))
    d_over.polygon([(w, 60), (w - 220, 0), (w, 240)], fill=(56, 189, 248, 130))
    d_over.polygon([(w - 420, 0), (w - 180, 220), (w, 140)], fill=(2, 132, 199, 50))

    # Top-Left Subtle Corner Accent
    d_over.polygon([(0, 0), (220, 0), (0, 180)], fill=(224, 242, 254, 100))
    d_over.polygon([(0, 0), (140, 0), (0, 110)], fill=(186, 230, 253, 80))

    # Bottom-Left Subtle Facet
    d_over.polygon([(0, h), (320, h), (0, h - 220)], fill=(224, 242, 254, 90))
    d_over.polygon([(0, h), (180, h), (0, h - 130)], fill=(186, 230, 253, 80))

    # Bottom-Right Translucent Facet
    d_over.polygon([(w, h), (w - 400, h), (w, h - 280)], fill=(186, 230, 253, 70))

    img = Image.alpha_composite(img, overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Clean framing line
    draw.rectangle([50, 50, w - 50, h - 50], outline="#E2E8F0", width=1)

    # Header Text
    f_title = get_font_safe("Times-Bold.ttf", 46)
    f_sub = get_font_safe("Georgia-Regular.ttf", 20)

    draw.text((w / 2, 145), "TWO-DAY SUSTAINABILITY", fill="#1E3A8A", font=f_title, anchor="mm")
    draw.text((w / 2, 205), "CERTIFICATE", fill="#1E3A8A", font=f_title, anchor="mm")
    draw.text((w / 2, 260), "Presented in recognition of attendance", fill="#64748B", font=f_sub, anchor="mm")

    # Hairline above recipient
    draw.line([(w / 2 - 300, 395), (w / 2 + 300, 395)], fill="#0284C7", width=2)

    # Footer elements
    draw_footer_elements(img, text_color="#64748B", sig_color="#1E3A8A")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created: {output_path}")


# ==============================================================================
# 5. TEMPLATE: ROYAL ACADEMIC NAVY & ROSETTE (sustainability_academic.png)
# ==============================================================================
def create_royal_academic_template(output_path: str):
    """Authoritative navy & gold double border with intricate radial rosette security watermark and gold seal."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#FCFDFD")
    draw = ImageDraw.Draw(img)

    # Radial guilloche rosette watermark centered behind text
    cx, cy = w / 2, h / 2 + 10
    num_petals = 20
    for k in range(54):
        phase = k * (2 * math.pi / 54)
        pts = []
        for a in range(0, 360, 3):
            rad = math.radians(a)
            r = 380 + 80 * math.sin(num_petals * rad + phase)
            pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
        draw.polygon(pts, outline="#F3EFE6", width=1)

    # Solid Royal Navy Blue Outer Border (20px width)
    bw = 20
    draw.rectangle([0, 0, w, bw], fill="#1B3B6F")
    draw.rectangle([0, h - bw, w, h], fill="#1B3B6F")
    draw.rectangle([0, 0, bw, h], fill="#1B3B6F")
    draw.rectangle([w - bw, 0, w, h], fill="#1B3B6F")

    # White space and Inner Royal Gold Border
    draw.rectangle([bw + 12, bw + 12, w - (bw + 12), h - (bw + 12)], outline="#C5A059", width=3)
    draw.rectangle([bw + 18, bw + 18, w - (bw + 18), h - (bw + 18)], outline="#E2C992", width=1)

    # Corner blocks connecting frames
    for px, py in [(bw + 12, bw + 12), (w - bw - 24, bw + 12), (bw + 12, h - bw - 24), (w - bw - 24, h - bw - 24)]:
        draw.rectangle([px, py, px + 12, py + 12], fill="#1B3B6F", outline="#C5A059")

    # Header Text
    f_title = get_font_safe("Times-Bold.ttf", 48)
    f_sub = get_font_safe("Georgia-Regular.ttf", 20)

    draw.text((w / 2, 145), "TWO-DAY SUSTAINABILITY", fill="#1E293B", font=f_title, anchor="mm")
    draw.text((w / 2, 205), "CERTIFICATE", fill="#1E293B", font=f_title, anchor="mm")
    draw.text((w / 2, 260), "Presented in recognition of attendance", fill="#475569", font=f_sub, anchor="mm")

    # Horizontal divider rule
    draw.line([(w / 2 - 280, 395), (w / 2 + 280, 395)], fill="#CBD5E1", width=1)
    draw.line([(w / 2 - 160, 395), (w / 2 + 160, 395)], fill="#1B3B6F", width=2)

    # Footer elements
    draw_footer_elements(img, text_color="#475569", sig_color="#1B3B6F")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created: {output_path}")


# ==============================================================================
# 6. TEMPLATE: TRADITIONAL SECURITY LACE GUILLOCHE (sustainability_lace.png)
# ==============================================================================
def create_traditional_lace_template(output_path: str):
    """Traditional security banknote lace frame, faint wavy security background, and gold seal."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Faint central continuous security waves
    for y in range(120, h - 120, 18):
        pts = []
        for x in range(120, w - 120, 10):
            dy = 5 * math.sin(x * 0.03 + y * 0.02)
            pts.append((x, y + dy))
        draw.line(pts, fill="#F0F4F8", width=1)

    # Intricate Banknote Lace Border
    margin = 45
    lace_w = 28
    
    draw.rectangle([margin, margin, w - margin, h - margin], outline="#1D70B8", width=2)
    draw.rectangle([margin + lace_w, margin + lace_w, w - (margin + lace_w), h - (margin + lace_w)], outline="#1D70B8", width=2)

    # Scalloped lace loops
    loop_step = 20
    for x in range(margin, w - margin - loop_step, loop_step):
        draw.arc([x, margin, x + loop_step * 2, margin + lace_w * 2], 180, 360, fill="#2563EB", width=1)
        draw.arc([x + 4, margin + 4, x + loop_step * 2 - 4, margin + lace_w * 2 - 4], 180, 360, fill="#60A5FA", width=1)
        draw.arc([x, h - margin - lace_w * 2, x + loop_step * 2, h - margin], 0, 180, fill="#2563EB", width=1)
        draw.arc([x + 4, h - margin - lace_w * 2 + 4, x + loop_step * 2 - 4, h - margin - 4], 0, 180, fill="#60A5FA", width=1)

    for y in range(margin, h - margin - loop_step, loop_step):
        draw.arc([margin, y, margin + lace_w * 2, y + loop_step * 2], 90, 270, fill="#2563EB", width=1)
        draw.arc([w - margin - lace_w * 2, y, w - margin, y + loop_step * 2], 270, 90, fill="#2563EB", width=1)

    # Header Text
    f_title = get_font_safe("Times-Bold.ttf", 46)
    f_sub = get_font_safe("Georgia-Regular.ttf", 20)

    draw.text((w / 2, 145), "TWO-DAY SUSTAINABILITY", fill="#1E293B", font=f_title, anchor="mm")
    draw.text((w / 2, 205), "CERTIFICATE", fill="#1E293B", font=f_title, anchor="mm")
    draw.text((w / 2, 260), "Presented in recognition of attendance", fill="#64748B", font=f_sub, anchor="mm")

    # Divider rule
    draw.line([(w / 2 - 260, 395), (w / 2 + 260, 395)], fill="#2563EB", width=2)

    # Footer elements
    draw_footer_elements(img, text_color="#64748B", sig_color="#1E293B")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Created: {output_path}")


def generate_all_sustainability_templates():
    """Generate all 6 sustainability certificates in static/sample_templates."""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    
    generators = {
        "sustainability_midnight.png": create_midnight_navy_template,
        "sustainability_cyan.png": create_cyan_guilloche_template,
        "sustainability_slate.png": create_slate_filigree_template,
        "sustainability_modern.png": create_modern_geometric_template,
        "sustainability_academic.png": create_royal_academic_template,
        "sustainability_lace.png": create_traditional_lace_template
    }
    
    for filename, gen_fn in generators.items():
        out_p = os.path.join(TEMPLATES_DIR, filename)
        gen_fn(out_p)


if __name__ == "__main__":
    generate_all_sustainability_templates()
