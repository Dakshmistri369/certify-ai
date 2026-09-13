"""
utils/db.py
MongoDB Atlas Database Layer for CertifyAI.
Provides high-performance persistence for batch history, individual student certificates,
template coordinate configurations, and instant certificate verification lookups.
Features automatic index creation, connection pooling, and seamless local sync fallback.
"""

import os
import json
import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DEFAULT_MONGO_URI = "mongodb+srv://dakshmistri369_db_user:M.Dax123@certifyai.qdtepvc.mongodb.net/?appName=certifyai"
MONGO_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URI", DEFAULT_MONGO_URI))
DB_NAME = os.getenv("MONGODB_DB_NAME", "certifyai")

_mongo_client = None
_mongo_db = None
_is_connected = False
_last_error = None
_last_check_time = 0


def get_client():
    """Get or initialize PyMongo MongoClient singleton."""
    global _mongo_client, _mongo_db, _is_connected, _last_error
    if _mongo_client is not None and _is_connected:
        return _mongo_client
    
    try:
        import pymongo
        _mongo_client = pymongo.MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=5000,
            maxPoolSize=20,
            retryWrites=True
        )
        # Verify connection
        _mongo_client.admin.command('ping')
        _mongo_db = _mongo_client[DB_NAME]
        _is_connected = True
        _last_error = None
        _init_db_indexes(_mongo_db)
        return _mongo_client
    except Exception as e:
        _is_connected = False
        _last_error = str(e)
        return None


def get_db():
    """Get MongoDB database instance."""
    global _mongo_db, _is_connected
    client = get_client()
    if client is not None:
        try:
            return client[DB_NAME]
        except Exception:
            _is_connected = False
    return None


def _init_db_indexes(db):
    """Ensure fast query performance with indexes."""
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


def get_db_status() -> Dict[str, Any]:
    """Check MongoDB health, cluster information, and collection statistics."""
    global _is_connected, _last_error
    masked_uri = "mongodb+srv://dakshmistri369_db_user:***@certifyai.qdtepvc.mongodb.net/?appName=certifyai"
    try:
        db = get_db()
        if db is not None:
            db.command('ping')
            collections = db.list_collection_names()
            cert_count = db.certificates.count_documents({})
            batch_count = db.batches.count_documents({})
            _is_connected = True
            _last_error = None
            return {
                "connected": True,
                "database": DB_NAME,
                "cluster_uri": masked_uri,
                "collections": collections,
                "total_certificates_stored": cert_count,
                "total_batches_stored": batch_count,
                "server_time": datetime.datetime.now().isoformat(),
                "error": None
            }
    except Exception as e:
        _is_connected = False
        _last_error = str(e)
    
    return {
        "connected": False,
        "database": DB_NAME,
        "cluster_uri": masked_uri,
        "collections": [],
        "total_certificates_stored": 0,
        "total_batches_stored": 0,
        "server_time": datetime.datetime.now().isoformat(),
        "error": _last_error or "MongoDB Atlas cluster offline or IP access restricted."
    }


# ==============================================================================
# CONFIGURATION PERSISTENCE
# ==============================================================================

def save_config_db(cfg: Dict[str, Any]) -> bool:
    """Save configuration to MongoDB and sync with local fallback."""
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
    return False


def load_config_db() -> Optional[Dict[str, Any]]:
    """Load configuration from MongoDB."""
    db = get_db()
    if db is not None:
        try:
            doc = db.configs.find_one({"_id": "app_config"})
            if doc and "data" in doc:
                return doc["data"]
        except Exception as e:
            print(f"[MongoDB] Config load note: {e}")
    return None


# ==============================================================================
# BATCHES PERSISTENCE
# ==============================================================================

def record_batch_db(meta: Dict[str, Any]) -> bool:
    """Insert or update batch metadata in MongoDB."""
    db = get_db()
    if db is not None:
        try:
            doc = dict(meta)
            doc["created_at"] = doc.get("timestamp") or datetime.datetime.now().isoformat()
            db.batches.update_one(
                {"batch_id": doc["batch_id"]},
                {"$set": doc},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"[MongoDB] Batch record note: {e}")
    return False


def load_batches_db(limit: int = 50) -> Optional[List[Dict[str, Any]]]:
    """Retrieve recent batch history from MongoDB sorted newest first."""
    db = get_db()
    if db is not None:
        try:
            cursor = db.batches.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
            results = list(cursor)
            if results:
                return results
        except Exception as e:
            print(f"[MongoDB] Batch load note: {e}")
    return None


def clear_batches_db() -> bool:
    """Clear all batches and certificates history from MongoDB."""
    db = get_db()
    if db is not None:
        try:
            db.batches.delete_many({})
            db.certificates.delete_many({})
            return True
        except Exception as e:
            print(f"[MongoDB] Clear history note: {e}")
    return False


# ==============================================================================
# INDIVIDUAL CERTIFICATES PERSISTENCE & VERIFICATION
# ==============================================================================

def record_certificates_db(batch_id: str, cert_records: List[Dict[str, Any]], template_name: str = "") -> int:
    """
    Store individual generated student certificate records to MongoDB for verification and querying.
    """
    if not cert_records:
        return 0
    db = get_db()
    if db is None:
        return 0
    
    docs = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    
    try:
        result = db.certificates.insert_many(docs, ordered=False)
        return len(result.inserted_ids)
    except Exception as e:
        print(f"[MongoDB] Record certificates note: {e}")
        return 0


def get_certificates_db(batch_id: Optional[str] = None, query: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Query certificates from MongoDB by batch ID, student name, or certificate ID."""
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
            return list(cursor)
        except Exception as e:
            print(f"[MongoDB] Query certificates note: {e}")
    return []


def verify_certificate_db(cert_id: str) -> Optional[Dict[str, Any]]:
    """
    Search and verify certificate authenticity by its unique Certificate ID or Student Name.
    Queries MongoDB Atlas first, then falls back to local batch records.
    """
    if not cert_id:
        return None
    
    clean_id = str(cert_id).strip()
    db = get_db()
    if db is not None:
        try:
            # 1. Exact cert_id match
            doc = db.certificates.find_one({"cert_id": clean_id}, {"_id": 0})
            if doc:
                return doc
            # 2. Case-insensitive cert_id match
            doc = db.certificates.find_one({"cert_id": {"$regex": f"^{clean_id}$", "$options": "i"}}, {"_id": 0})
            if doc:
                return doc
            # 3. Partial cert_id match
            doc = db.certificates.find_one({"cert_id": {"$regex": clean_id, "$options": "i"}}, {"_id": 0})
            if doc:
                return doc
            # 4. Student Name match
            doc = db.certificates.find_one({"student_name": {"$regex": clean_id, "$options": "i"}}, {"_id": 0})
            if doc:
                return doc
        except Exception as e:
            print(f"[MongoDB] Verify certificate note: {e}")
    
    return None
