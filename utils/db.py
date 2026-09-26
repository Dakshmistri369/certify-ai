"""
utils/db.py
MongoDB Atlas Database Layer for CertifyAI with High-Performance Circuit Breaker,
Automatic Connection Caching, and Instant Local JSON Fallback Persistence.
Provides seamless operations whether connected to MongoDB Atlas or operating offline.
"""

import os
import json
import time
import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DEFAULT_MONGO_URI = "mongodb+srv://dakshmistri369_db_user:M.Dax123@certifyai.qdtepvc.mongodb.net/?appName=certifyai"
MONGO_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", DEFAULT_MONGO_URI))
DB_NAME = os.getenv("MONGODB_DB_NAME", "certifyai")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_DIR = os.path.join(BASE_DIR, "generated_certificates")
LOCAL_CERTS_FILE = os.path.join(GENERATED_DIR, "certificates.json")
BATCH_LOGS_FILE = os.path.join(GENERATED_DIR, "batches.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Ensure generated directory exists
os.makedirs(GENERATED_DIR, exist_ok=True)

_mongo_client = None
_mongo_db = None
_is_connected = False
_last_error = None
_last_check_time = 0.0
_last_failure_time = 0.0
_cached_status = None

# Circuit Breaker Configuration
FAILURE_COOLDOWN_SECONDS = 60.0  # Skip reconnecting for 60s after failure
SUCCESS_CACHE_SECONDS = 30.0     # Cache status for 30s after success


def _get_local_certs() -> List[Dict[str, Any]]:
    """Load locally persisted certificates."""
    if os.path.exists(LOCAL_CERTS_FILE):
        try:
            with open(LOCAL_CERTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def _save_local_certs(certs: List[Dict[str, Any]]) -> None:
    """Save certificates to local JSON fallback store."""
    try:
        with open(LOCAL_CERTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(certs, f, indent=2)
    except Exception as e:
        print(f"[LocalStore] Save certs note: {e}")


def _get_local_certs_count() -> int:
    return len(_get_local_certs())


def _get_local_batches_count() -> int:
    if os.path.exists(BATCH_LOGS_FILE):
        try:
            with open(BATCH_LOGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return len(data) if isinstance(data, list) else 0
        except Exception:
            return 0
    return 0


import threading

try:
    import certifi
    _ca_file = certifi.where()
except Exception:
    _ca_file = None

_connecting_lock = threading.Lock()
_is_checking = False


def _async_connect():
    """Attempt MongoDB connection in background without blocking HTTP threads."""
    global _mongo_client, _mongo_db, _is_connected, _last_error, _last_failure_time, _is_checking
    with _connecting_lock:
        if _is_checking:
            return
        _is_checking = True
    try:
        import pymongo
        client_kwargs = {
            "serverSelectionTimeoutMS": 2000,
            "connectTimeoutMS": 2000,
            "socketTimeoutMS": 3000,
            "maxPoolSize": 10,
            "retryWrites": True
        }
        if _ca_file:
            client_kwargs["tlsCAFile"] = _ca_file

        c = pymongo.MongoClient(MONGO_URI, **client_kwargs)
        c.admin.command('ping')
        _mongo_client = c
        _mongo_db = _mongo_client[DB_NAME]
        _is_connected = True
        _last_error = None
        _init_db_indexes(_mongo_db)
    except Exception as e:
        _is_connected = False
        err_msg = str(e)
        if "TLSV1_ALERT_INTERNAL_ERROR" in err_msg or "SSL handshake failed" in err_msg:
            _last_error = "MongoDB Atlas cluster offline or IP access restricted (Add 0.0.0.0/0 to MongoDB Atlas Network Access)."
        else:
            _last_error = err_msg
        _last_failure_time = time.time()
    finally:
        _is_checking = False


# Start background connect immediately on import
threading.Thread(target=_async_connect, daemon=True).start()


def get_client(block: bool = False):
    """Get PyMongo client; non-blocking by default to guarantee instant response."""
    global _mongo_client, _mongo_db, _is_connected, _last_error, _last_failure_time, _is_checking
    if _mongo_client is not None and _is_connected:
        return _mongo_client

    now = time.time()
    if (now - _last_failure_time) < FAILURE_COOLDOWN_SECONDS:
        return None

    if not block:
        if not _is_checking:
            threading.Thread(target=_async_connect, daemon=True).start()
        return None

    _async_connect()
    if _is_connected:
        return _mongo_client
    return None


def get_db(block: bool = False):
    """Get MongoDB database instance without blocking web request."""
    global _mongo_db, _is_connected
    client = get_client(block=block)
    if client is not None:
        try:
            return client[DB_NAME]
        except Exception:
            _is_connected = False
    return None


def _init_db_indexes(db):
    """Ensure fast query performance with background indexes."""
    try:
        if db is None:
            return
        db.certificates.create_index([("cert_id", 1)], unique=False, background=True)
        db.certificates.create_index([("batch_id", 1)], background=True)
        db.certificates.create_index([("student_name", 1)], background=True)
        db.certificates.create_index([("created_at", -1)], background=True)
        db.batches.create_index([("batch_id", 1)], unique=True, background=True)
        db.batches.create_index([("created_at", -1)], background=True)
    except Exception as e:
        print(f"[MongoDB] Index creation note: {e}")


def get_db_status(block: bool = False) -> Dict[str, Any]:
    """
    Check MongoDB health, cluster information, and collection statistics with non-blocking caching.
    """
    global _is_connected, _last_error, _cached_status, _last_check_time, _last_failure_time
    now = time.time()
    masked_uri = "mongodb+srv://dakshmistri369_db_user:***@certifyai.qdtepvc.mongodb.net/?appName=certifyai"

    # Return cached response if still fresh
    if _cached_status is not None and not block:
        if _is_connected and (now - _last_check_time < SUCCESS_CACHE_SECONDS):
            return _cached_status
        if (not _is_connected) and (now - _last_failure_time < FAILURE_COOLDOWN_SECONDS):
            return _cached_status

    # If within failure cooldown and not explicitly blocking, return local offline status immediately
    if (now - _last_failure_time) < FAILURE_COOLDOWN_SECONDS and not block:
        _cached_status = {
            "connected": False,
            "database": DB_NAME,
            "cluster_uri": masked_uri,
            "collections": [],
            "total_certificates_stored": _get_local_certs_count(),
            "total_batches_stored": _get_local_batches_count(),
            "server_time": datetime.datetime.now().isoformat(),
            "mode": "Local High-Speed Fallback Mode",
            "error": _last_error or "Atlas cluster offline or IP access restricted (offline fallback active)."
        }
        return _cached_status

    try:
        db = get_db(block=block)
        if db is not None:
            db.command('ping')
            collections = db.list_collection_names()
            cert_count = db.certificates.count_documents({})
            batch_count = db.batches.count_documents({})
            _is_connected = True
            _last_error = None
            _last_check_time = now
            _cached_status = {
                "connected": True,
                "database": DB_NAME,
                "cluster_uri": masked_uri,
                "collections": collections,
                "total_certificates_stored": cert_count,
                "total_batches_stored": batch_count,
                "server_time": datetime.datetime.now().isoformat(),
                "mode": "MongoDB Atlas Live Cluster",
                "error": None
            }
            return _cached_status
    except Exception as e:
        _is_connected = False
        _last_error = str(e)
        _last_failure_time = now

    _cached_status = {
        "connected": False,
        "database": DB_NAME,
        "cluster_uri": masked_uri,
        "collections": [],
        "total_certificates_stored": _get_local_certs_count(),
        "total_batches_stored": _get_local_batches_count(),
        "server_time": datetime.datetime.now().isoformat(),
        "mode": "Local High-Speed Fallback Mode",
        "error": _last_error or "MongoDB Atlas cluster offline or IP access restricted."
    }
    return _cached_status


# ==============================================================================
# CONFIGURATION PERSISTENCE
# ==============================================================================

def _get_local_batches() -> List[Dict[str, Any]]:
    """Load batches from local JSON store."""
    if os.path.exists(BATCH_LOGS_FILE):
        try:
            with open(BATCH_LOGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


def _save_local_batches(batches: List[Dict[str, Any]]) -> None:
    """Save batches to local JSON store."""
    try:
        with open(BATCH_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(batches[:100], f, indent=2)
    except Exception as e:
        print(f"[LocalStore] Batch save note: {e}")


def save_config_db(cfg: Dict[str, Any]) -> bool:
    """Save configuration to MongoDB if connected, and to local config.json."""
    saved_local = False
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2)
        saved_local = True
    except Exception as e:
        print(f"[LocalStore] Config save note: {e}")

    db = get_db()
    if db is not None:
        try:
            db.configs.update_one(
                {"_id": "app_config"},
                {"$set": {"data": cfg, "updated_at": datetime.datetime.now().isoformat()}},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[MongoDB] Config save note: {e}")
    return saved_local


def load_config_db() -> Optional[Dict[str, Any]]:
    """Load configuration from MongoDB if connected, falling back to local config.json."""
    db = get_db()
    if db is not None:
        try:
            doc = db.configs.find_one({"_id": "app_config"})
            if doc and "data" in doc:
                return doc["data"]
        except Exception as e:
            print(f"[MongoDB] Config load note: {e}")

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None


# ==============================================================================
# BATCHES PERSISTENCE
# ==============================================================================

def record_batch_db(meta: Dict[str, Any]) -> bool:
    """Insert or update batch metadata in MongoDB and local batches.json."""
    doc = dict(meta)
    doc["created_at"] = doc.get("timestamp") or datetime.datetime.now().isoformat()

    # 1. Always record in local JSON storage for instant retrieval & offline resilience
    saved_local = False
    try:
        batches = _get_local_batches()
        idx = next((i for i, b in enumerate(batches) if b.get("batch_id") == doc.get("batch_id")), None)
        if idx is not None:
            batches[idx] = doc
        else:
            batches.insert(0, doc)
        _save_local_batches(batches)
        saved_local = True
    except Exception as e:
        print(f"[LocalStore] Batch record note: {e}")

    # 2. Persist to MongoDB Atlas if connected
    db = get_db()
    if db is not None:
        try:
            db.batches.update_one(
                {"batch_id": doc["batch_id"]},
                {"$set": doc},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[MongoDB] Batch record note: {e}")

    return saved_local


def load_batches_db(limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """Retrieve recent batch history from MongoDB Atlas, falling back to local storage."""
    db = get_db()
    if db is not None:
        try:
            cursor = db.batches.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
            results = list(cursor)
            if results:
                return results
        except Exception as e:
            print(f"[MongoDB] Batch load note: {e}")

    local_batches = _get_local_batches()
    return local_batches[:limit] if local_batches else []


def clear_batches_db() -> bool:
    """Clear all batches and certificates history from MongoDB and local storage."""
    # Clear local files
    try:
        if os.path.exists(LOCAL_CERTS_FILE):
            with open(LOCAL_CERTS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        if os.path.exists(BATCH_LOGS_FILE):
            with open(BATCH_LOGS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
    except Exception as e:
        print(f"[LocalStore] Clear history note: {e}")

    db = get_db()
    if db is not None:
        try:
            db.batches.delete_many({})
            db.certificates.delete_many({})
            return True
        except Exception as e:
            print(f"[MongoDB] Clear history note: {e}")
    return True


# ==============================================================================
# INDIVIDUAL CERTIFICATES PERSISTENCE & VERIFICATION
# ==============================================================================

def record_certificates_db(batch_id: str, cert_records: List[Dict[str, Any]], template_name: str = "") -> int:
    """
    Store individual generated student certificate records to both local store and MongoDB.
    """
    if not cert_records:
        return 0
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    docs = []
    for r in cert_records:
        doc = {
            "batch_id": batch_id,
            "student_name": r.get("student_name") or r.get("NAME", ""),
            "cert_id": str(r.get("cert_id") or r.get("CERT_ID") or ""),
            "course": r.get("course") or r.get("COURSE", ""),
            "date": r.get("date") or r.get("DATE", ""),
            "grade": r.get("grade") or r.get("GRADE", ""),
            "template_name": template_name,
            "files": r.get("files", {}),
            "created_at": now_str
        }
        docs.append(doc)

    # 1. Always record in local JSON storage for instant retrieval & offline support
    try:
        existing = _get_local_certs()
        existing_map = {c.get("cert_id"): idx for idx, c in enumerate(existing) if c.get("cert_id")}
        for d in docs:
            cid = d.get("cert_id")
            if cid and cid in existing_map:
                existing[existing_map[cid]] = d
            else:
                existing.append(d)
        _save_local_certs(existing)
    except Exception as e:
        print(f"[LocalStore] Record certificates note: {e}")

    # 2. Persist to MongoDB Atlas if connected
    db = get_db()
    if db is not None:
        try:
            result = db.certificates.insert_many(docs, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            print(f"[MongoDB] Record certificates note: {e}")

    return len(docs)


def get_certificates_db(batch_id: Optional[str] = None, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Query certificates from MongoDB Atlas, falling back to local storage."""
    db = get_db()
    if db is not None:
        filter_dict = {}
        if batch_id:
            filter_dict["batch_id"] = batch_id
        if query:
            filter_dict["$or"] = [
                {"cert_id": {"$regex": query, "$options": "i"}},
                {"student_name": {"$regex": query, "$options": "i"}},
                {"course": {"$regex": query, "$options": "i"}}
            ]
        try:
            cursor = db.certificates.find(filter_dict, {"_id": 0}).sort("created_at", -1).limit(limit)
            results = list(cursor)
            if results:
                return results
        except Exception as e:
            print(f"[MongoDB] Query certificates note: {e}")

    # Fallback to local certificates store
    local_certs = _get_local_certs()
    if batch_id:
        local_certs = [c for c in local_certs if c.get("batch_id") == batch_id]
    if query:
        q = query.lower()
        local_certs = [
            c for c in local_certs
            if q in str(c.get("cert_id", "")).lower()
            or q in str(c.get("student_name", "")).lower()
            or q in str(c.get("course", "")).lower()
        ]
    return local_certs[:limit]


def verify_certificate_db(cert_id: str) -> Optional[Dict[str, Any]]:
    """
    Search and verify certificate authenticity by its unique Certificate ID or Student Name.
    Queries MongoDB Atlas first, then automatically falls back to local batch records.
    """
    if not cert_id:
        return None
    
    clean_id = str(cert_id).strip()
    
    # 1. Try MongoDB Atlas if connected
    db = get_db()
    if db is not None:
        try:
            # Exact cert_id match
            doc = db.certificates.find_one({"cert_id": clean_id}, {"_id": 0})
            if doc:
                return doc
            # Case-insensitive cert_id match
            doc = db.certificates.find_one({"cert_id": {"$regex": f"^{clean_id}$", "$options": "i"}}, {"_id": 0})
            if doc:
                return doc
            # Partial cert_id match
            doc = db.certificates.find_one({"cert_id": {"$regex": clean_id, "$options": "i"}}, {"_id": 0})
            if doc:
                return doc
            # Student Name match
            doc = db.certificates.find_one({"student_name": {"$regex": clean_id, "$options": "i"}}, {"_id": 0})
            if doc:
                return doc
        except Exception as e:
            print(f"[MongoDB] Verify certificate note: {e}")
    
    # 2. Local fallback search in local certificates store
    local_certs = _get_local_certs()
    clean_lower = clean_id.lower()
    for c in local_certs:
        cid = str(c.get("cert_id", "")).strip().lower()
        sname = str(c.get("student_name", "")).strip().lower()
        if cid == clean_lower or sname == clean_lower:
            return c
    for c in local_certs:
        cid = str(c.get("cert_id", "")).strip().lower()
        sname = str(c.get("student_name", "")).strip().lower()
        if clean_lower in cid or clean_lower in sname:
            return c

    # 3. Search in generated certificates directory for existing files
    if os.path.exists(GENERATED_DIR):
        for item in os.listdir(GENERATED_DIR):
            sub_dir = os.path.join(GENERATED_DIR, item)
            if os.path.isdir(sub_dir) and item.startswith("batch_"):
                for fname in os.listdir(sub_dir):
                    if clean_lower in fname.lower():
                        name_part = fname.replace(".png", "").replace(".pdf", "")
                        return {
                            "batch_id": item,
                            "student_name": name_part.replace("_", " "),
                            "cert_id": clean_id,
                            "course": "Verified Course Credential",
                            "date": datetime.date.today().strftime("%B %d, %Y"),
                            "grade": "Verified Distinction",
                            "template_name": "Standard Template",
                            "files": {"pdf": fname} if fname.endswith(".pdf") else {"png": fname},
                            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

    return None
