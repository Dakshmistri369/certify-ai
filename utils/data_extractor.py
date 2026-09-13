"""
data_extractor.py
Multi-Format Data Extraction Engine for Certificates:
- Spreadsheets: Excel (.xlsx, .xls, .xlsm), CSV (.csv), TSV (.tsv), TXT (.txt)
- Structured Data: JSON (.json)
- Documents: PDF (.pdf) via table extraction, multi-page stitching, and profile parsing
- Direct Paste: Clipboard / Raw TSV / CSV / JSON text parser
"""

import os
import re
import io
import json
import datetime
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None


# Normalized column alias regex patterns
FIELD_PATTERNS = {
    "SR_NO": r"^(?:sr|sl|s)\s*[\.\_\-]?\s*no\b|^\s*#\s*$|^\s*no\b|^\s*index\b|^\s*seq\b",
    "NAME": r"full\s*name|student\s*name|candidate\s*name|participant\s*name|learner\s*name|recipient\s*name|name\s*of\s*student|\bname\b",
    "COURSE": r"course\s*name|course\s*title|subject|program|workshop|training|topic|degree|stream|branch|department|specialization|module|\bcourse\b",
    "DATE": r"issue\s*date|completion\s*date|awarded\s*date|date\s*of\s*issue|issued\s*on|event\s*date|\bdate\b",
    "GRADE": r"graduation\s*marks|cgpa|gpa|score|percentage|marks|division|result|performance|achievement|\bgrade\b",
    "CERT_ID": r"roll\s*(?:no|num|number)|reg\s*(?:no|num|number)|enrollment|credential\s*id|cert(?:ificate)?\s*(?:id|no|number)|student\s*id|uid|\bid\b",
    "EMAIL": r"email|e-mail|mail",
    "PHONE": r"phone|mobile|contact|whatsapp|watsapp",
    "INSTITUTE": r"institute|institution|university|college|school|academy|organization|company",
    "INSTRUCTOR": r"instructor|trainer|teacher|professor|mentor|signatory|director|principal",
    "BACKLOG": r"backlog"
}


def clean_header(header: Any) -> str:
    """Clean whitespace and special line breaks from header string."""
    if header is None:
        return ""
    return ' '.join(str(header).replace('\r', ' ').replace('\n', ' ').split()).strip()


def normalize_header(header: str) -> Optional[str]:
    """Map raw column header to standard field key."""
    if not header:
        return None
    clean = re.sub(r'[^a-z0-9]', ' ', clean_header(header).lower())
    clean_s = ' '.join(clean.split())
    if not clean_s:
        return None

    # Check SR_NO first to avoid false 'name' matches
    if re.search(FIELD_PATTERNS["SR_NO"], clean_s):
        return "SR_NO"

    for field, pattern in FIELD_PATTERNS.items():
        if field == "SR_NO":
            continue
        if re.search(pattern, clean_s):
            # Guard against course name / institute name being tagged as student NAME
            if field == "NAME" and any(k in clean_s for k in ["course", "institute", "college", "school", "univ", "company", "file", "folder"]):
                continue
            return field
    return None


def format_date_value(val: Any) -> str:
    """Format various date inputs into standard 'Month DD, YYYY' format."""
    if pd.isna(val) or val is None or str(val).strip() == "":
        return datetime.date.today().strftime("%B %d, %Y")
    if isinstance(val, (datetime.date, datetime.datetime, pd.Timestamp)):
        return val.strftime("%B %d, %Y")
    val_str = str(val).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y", "%B %d, %Y", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(val_str, fmt).strftime("%B %d, %Y")
        except ValueError:
            continue
    return val_str


def score_name_col(series: pd.Series) -> float:
    """Score how likely a column contains person names."""
    valid, score = 0, 0.0
    for v in series.dropna():
        s = str(v).strip()
        if not s:
            continue
        valid += 1
        if "@" in s or re.match(r'^\+?\d[\d\s\-]{8,}$', s) or s.isdigit():
            return -100.0
        words = s.split()
        if 1 <= len(words) <= 5 and sum(c.isalpha() or c in " .'-" for c in s) / len(s) > 0.85:
            score += (2.5 if len(words) >= 2 else 1.0)
    return score / max(1, valid)


def process_dataframe(df: pd.DataFrame, source_type: str = "spreadsheet") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process DataFrame into normalized records while preserving all custom columns."""
    df.columns = [clean_header(c) for c in df.columns]
    raw_columns = list(df.columns)
    column_mapping: Dict[str, str] = {}

    for col in df.columns:
        matched = normalize_header(str(col))
        if matched and matched not in column_mapping.values():
            column_mapping[col] = matched

    if "NAME" not in column_mapping.values():
        best_col, best_score = None, 0.5
        for col in df.columns:
            if col in column_mapping and column_mapping[col] in ["SR_NO", "EMAIL", "PHONE", "DATE"]:
                continue
            sc = score_name_col(df[col])
            if sc > best_score:
                best_score, best_col = sc, col
        if best_col:
            column_mapping[best_col] = "NAME"
        elif len(df.columns) > 0:
            column_mapping[df.columns[0]] = "NAME"

    records: List[Dict[str, Any]] = []
    errors: List[str] = []
    skipped = 0

    for idx, row in df.iterrows():
        rec: Dict[str, Any] = {
            "NAME": "",
            "COURSE": "Certificate of Completion",
            "DATE": datetime.date.today().strftime("%B %d, %Y"),
            "GRADE": "A",
            "CERT_ID": f"CERT-{datetime.date.today().strftime('%Y')}-{len(records) + 1:04d}"
        }

        # 1. Preserve all raw and slugified columns
        for col in df.columns:
            val = row.get(col)
            if pd.notna(val) and str(val).strip() != "":
                c_val = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val).strip()
                slug = re.sub(r'_+', '_', re.sub(r'[^a-zA-Z0-9_]', '_', str(col).strip()).upper()).strip('_')
                if slug:
                    rec[slug] = c_val
                rec[str(col).strip()] = c_val

        # 2. Populate mapped standard fields
        for orig_col, std_field in column_mapping.items():
            val = row.get(orig_col)
            if pd.notna(val) and str(val).strip() != "":
                c_val = str(int(val)) if isinstance(val, float) and val.is_integer() else str(val).strip()
                if std_field == "DATE":
                    rec["DATE"] = format_date_value(val)
                elif std_field in rec:
                    rec[std_field] = c_val
                elif std_field in ["EMAIL", "PHONE", "INSTITUTE", "INSTRUCTOR"]:
                    rec[std_field] = c_val

        # 3. Fallbacks for name
        if not rec["NAME"]:
            for k in ["FULL_NAME", "FULLNAME", "STUDENT_NAME", "CANDIDATE_NAME", "STUDENT", "PARTICIPANT"]:
                if rec.get(k):
                    rec["NAME"] = rec[k]
                    break

        if not rec["NAME"] or rec["NAME"].lower() in ["name", "student name", "full name", "null", "nan"]:
            skipped += 1
            errors.append(f"Row {idx + 2}: Skipped because student name was empty or invalid.")
            continue

        # Clean sequential CERT_ID fallback
        if not rec.get("CERT_ID") or rec["CERT_ID"].startswith("CERT-"):
            roll = rec.get("ROLL_NUMBER") or rec.get("ROLL_NO") or rec.get("REG_NO")
            rec["CERT_ID"] = f"CERT-{datetime.date.today().strftime('%Y')}-{str(roll).zfill(4)}" if roll else f"CERT-{datetime.date.today().strftime('%Y')}-{len(records) + 1:04d}"

        records.append({k: (v.strip() if isinstance(v, str) else v) for k, v in rec.items()})

    all_keys = list(set(k for r in records for k in r.keys())) if records else []
    stats = {
        "total_rows": len(df),
        "valid_rows": len(records),
        "skipped_rows": skipped,
        "errors": errors,
        "source_type": source_type,
        "raw_columns": raw_columns,
        "columns_found": list(column_mapping.values()),
        "all_fields": all_keys
    }
    return records, stats


def extract_from_excel_or_csv(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract student records from spreadsheet files."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.xlsx', '.xls', '.xlsm']:
        df = pd.read_excel(file_path)
        source = "excel"
    elif ext == '.tsv':
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep='\t', encoding='latin-1')
        source = "tsv"
    else:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
        if len(df.columns) == 1:
            for sep in ['\t', ';', '|']:
                try:
                    df_alt = pd.read_csv(file_path, sep=sep, encoding='latin-1')
                    if len(df_alt.columns) > 1:
                        df = df_alt
                        break
                except Exception:
                    pass
        source = "csv"
    return process_dataframe(df, source_type=source)


def extract_from_json(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract records from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    raw_list = data if isinstance(data, list) else (
        next((data[k] for k in ["students", "data", "records", "participants", "candidates", "roster", "items"] if k in data and isinstance(data[k], list)), 
        list(data.values()) if all(isinstance(v, dict) for v in data.values()) else [data])
    )
    return process_dataframe(pd.DataFrame(raw_list), source_type="json")


def extract_from_raw_text(raw_text: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract student records from arbitrary raw/clipboard text (JSON, TSV, CSV, or lines)."""
    text = raw_text.strip()
    if not text:
        return [], {"total_rows": 0, "valid_rows": 0, "skipped_rows": 0, "errors": ["Empty text"], "source_type": "raw_paste"}

    # 1. JSON parse
    if text.startswith(('[', '{')):
        try:
            parsed = json.loads(text)
            data = parsed if isinstance(parsed, list) else (
                next((parsed[k] for k in ["students", "data", "records", "items"] if k in parsed and isinstance(parsed[k], list)), [parsed])
            )
            return process_dataframe(pd.DataFrame(data), source_type="pasted_json")
        except Exception:
            pass

    # 2. Delimited table parse
    for sep in ['\t', ',', ';', '|']:
        try:
            df = pd.read_csv(io.StringIO(text), sep=sep)
            if len(df.columns) > 1 and len(df) > 0:
                return process_dataframe(df, source_type="pasted_table")
        except Exception:
            continue

    # 3. Line by line fallback
    records = []
    for idx, line in enumerate(text.split('\n')):
        parts = [p.strip() for p in re.split(r'[\t,|;]', line) if p.strip()]
        if parts:
            records.append({
                "NAME": parts[0],
                "COURSE": parts[1] if len(parts) > 1 else "Certificate Course",
                "DATE": format_date_value(parts[2]) if len(parts) > 2 else datetime.date.today().strftime("%B %d, %Y"),
                "GRADE": parts[3] if len(parts) > 3 else "A",
                "CERT_ID": parts[4] if len(parts) > 4 else f"CERT-{datetime.date.today().strftime('%Y')}-{idx + 1:04d}"
            })
    return process_dataframe(pd.DataFrame(records), source_type="pasted_lines")


def extract_resume_candidate(text: str, file_path: str = "") -> Dict[str, Any]:
    """Extract single candidate details from a resume/CV document."""
    email_m = re.search(r'[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}', text)
    phone_m = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    name_m = re.search(r'(?:Candidate\s*Name|Student\s*Name|Full\s*Name|Name)\s*[:=\-]\s*([A-Za-z\s\.\'\-]+)', text, re.I)
    
    name = ""
    if name_m and 1 <= len(name_m.group(1).split()) <= 6:
        name = " ".join(w.capitalize() for w in name_m.group(1).split())
    if not name:
        for line in text.split('\n')[:8]:
            l = line.strip()
            if l and not any(k in l.lower() for k in ["resume", "cv", "profile", "contact", "@", "http"]) and re.match(r'^[A-Za-z\s\.\'\-]+$', l) and 3 <= len(l) <= 40:
                name = " ".join(w.capitalize() for w in l.split())
                break
    if not name and file_path:
        base = re.sub(r'^[0-9a-fA-F]{8}_|\.[a-zA-Z0-9]+$|\b(resume|cv|biodata|profile|s)\b', '', os.path.basename(file_path), flags=re.I)
        name = " ".join(w.capitalize() for w in re.sub(r'[_.\-]+', ' ', base).split()) or "Participant"

    course_m = re.search(r'(?:Course(?:\s*Name|\s*Title)?|Subject|Program|Track|Specialization)\s*[:=\-]\s*([A-Za-z0-9\s&,.\-\/\+]+)', text, re.I)
    course = course_m.group(1).strip().title() if course_m else "Certificate of Achievement"

    date_m = re.search(r'(?:Date|Issued\s*On|Completion\s*Date|Awarded)\s*[:=\-]\s*([A-Za-z0-9,\s\-\/]+)', text, re.I)
    date_val = format_date_value(date_m.group(1).strip().split('\n')[0]) if date_m else datetime.date.today().strftime("%B %d, %Y")

    grade_m = re.search(r'(?:Grade|Score|Marks|Performance)\s*[:=\-]\s*([A-Za-z0-9\+\-\s%]+)', text, re.I)
    grade_val = grade_m.group(1).strip().split('\n')[0] if grade_m else "A+ Distinction"

    id_m = re.search(r'(?:Certificate\s*ID|Cert\s*ID|Credential\s*ID|ID|Reg\s*No|Roll\s*No)\s*[:=\-]\s*([A-Za-z0-9\-_#]+)', text, re.I)
    cert_id = id_m.group(1).strip().split('\n')[0] if id_m else f"CERT-{datetime.date.today().strftime('%Y%m')}-0001"

    return {
        "NAME": name or "Student Participant",
        "COURSE": course,
        "EMAIL": email_m.group(0) if email_m else "",
        "PHONE": phone_m.group(0) if phone_m else "",
        "DATE": date_val,
        "GRADE": grade_val,
        "CERT_ID": cert_id,
        "SOURCE_TYPE": "PDF Resume/Profile"
    }


def extract_from_pdf(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Extract records from PDF via table stitching or resume/profile text extraction."""
    page_texts: List[str] = []
    page_tables: List[List[List[str]]] = []

    # 1. Extract text and tables with pdfplumber
    if pdfplumber is not None:
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text()
                    if txt and txt.strip():
                        page_texts.append(txt.strip())
                    tbls = page.extract_tables() or page.extract_tables(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
                    for t in tbls or []:
                        clean_t = [[str(c).strip() if c is not None else "" for c in row] for row in t if any(c is not None and str(c).strip() for c in row)]
                        if len(clean_t) > 1 and len(clean_t[0]) >= 2:
                            page_tables.append(clean_t)
        except Exception:
            pass

    # 2. PyPDF fallback for text
    if not page_texts and PdfReader is not None:
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                txt = page.extract_text()
                if txt and txt.strip():
                    page_texts.append(txt.strip())
        except Exception:
            pass

    # Method A: Process tables if extracted
    if page_tables:
        cleaned_tables = [([clean_header(c) for c in t[0]], [[str(c).strip() if c is not None else "" for c in row] for row in t[1:]]) for t in page_tables if len(t) > 1]
        if cleaned_tables:
            # Check horizontal vs vertical split
            if len(cleaned_tables) == 2 and len(cleaned_tables[0][1]) == len(cleaned_tables[1][1]) and not any(normalize_header(h) == "NAME" for h in cleaned_tables[1][0]):
                hdr = list(cleaned_tables[0][0]) + [h for h in cleaned_tables[1][0] if h not in cleaned_tables[0][0]]
                rows = [r0 + r1[:len(hdr) - len(r0)] for r0, r1 in zip(cleaned_tables[0][1], cleaned_tables[1][1])]
                return process_dataframe(pd.DataFrame(rows, columns=hdr), source_type="pdf_table")
            else:
                hdr = cleaned_tables[0][0]
                rows = [r + [""] * (len(hdr) - len(r)) if len(r) < len(hdr) else r[:len(hdr)] for _, t_rows in cleaned_tables for r in t_rows if [clean_header(c) for c in r] != hdr]
                return process_dataframe(pd.DataFrame(rows, columns=hdr), source_type="pdf_table")

    full_text = "\n".join(page_texts)

    # Method B: Parse multiple pages (1 candidate per page)
    if len(page_texts) >= 2:
        recs = [extract_resume_candidate(p_txt, file_path=f"Page_{i+1}") for i, p_txt in enumerate(page_texts)]
        valid_recs = [r for r in recs if r["NAME"] != "Student Participant"]
        if len(valid_recs) >= 2:
            return process_dataframe(pd.DataFrame(valid_recs), source_type="pdf_multipage")

    # Method C: Single candidate profile
    cand = extract_resume_candidate(full_text, file_path=file_path)
    return [cand], {
        "total_rows": 1,
        "valid_rows": 1,
        "skipped_rows": 0,
        "errors": [],
        "source_type": "pdf_document",
        "all_fields": list(cand.keys())
    }


def extract_student_data(file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Universal entry point to extract student records from any supported file format."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.xlsx', '.xls', '.xlsm', '.csv', '.tsv', '.txt']:
        return extract_from_excel_or_csv(file_path)
    elif ext == '.json':
        return extract_from_json(file_path)
    elif ext == '.pdf':
        return extract_from_pdf(file_path)
    raise ValueError(f"Unsupported file format: {ext}")
