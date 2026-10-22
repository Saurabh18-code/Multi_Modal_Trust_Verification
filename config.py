# ============================================================
# PROJECT: TrustNet AI - Multi-Modal Digital Trust
#          Intelligence and Authentication Verification Platform
# COLLEGE: St. John College of Engineering and Management, Palghar
# DEPARTMENT: Computer Engineering
# YEAR: B.Tech Final Year (2026-2027)
#
# FILE: config.py
# DESCRIPTION: Central configuration file for all project settings,
#              constants, thresholds, and directory paths
#
# GUIDE: [Guide Name] | [Designation]
# DATE: August 2026
# ============================================================
 
import os
 
# ─────────────────────────────────────────
# PROJECT INFORMATION
# ─────────────────────────────────────────
PROJECT_NAME        = "TrustNet AI"
PROJECT_VERSION     = "1.0.0"
PROJECT_DESCRIPTION = "Multi-Modal Digital Trust Intelligence and Authentication Verification Platform"
COLLEGE_NAME        = "St. John College of Engineering and Management, Palghar"
DEPARTMENT          = "Department of Computer Engineering"
 
# ─────────────────────────────────────────
# DIRECTORY PATHS
# ─────────────────────────────────────────
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR     = os.path.join(BASE_DIR, "database")
DATA_DIR         = os.path.join(BASE_DIR, "data")
SAMPLE_FACES_DIR = os.path.join(DATA_DIR, "sample_faces")
SAMPLE_DOCS_DIR  = os.path.join(DATA_DIR, "sample_docs")
BASELINES_DIR    = os.path.join(BASE_DIR, "baselines")
UPLOAD_FOLDER    = os.path.join(BASE_DIR, "uploads")
LOGS_DIR         = os.path.join(BASE_DIR, "logs")
 
# ─────────────────────────────────────────
# DATABASE SETTINGS
# ─────────────────────────────────────────
DATABASE_NAME = "trustnet.db"
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)
 
# ─────────────────────────────────────────
# FLASK SERVER SETTINGS
# ─────────────────────────────────────────
FLASK_HOST          = "0.0.0.0"
FLASK_PORT          = 5000
FLASK_DEBUG         = True
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "local-development-only-change-before-deployment"
)
MAX_CONTENT_LENGTH  = 16 * 1024 * 1024       # 16 MB max upload
ALLOWED_EXTENSIONS  = {"png", "jpg", "jpeg", "gif", "pdf"}
 
# ─────────────────────────────────────────
# MODULE 1: FACE VERIFICATION SETTINGS
# ─────────────────────────────────────────
FACE_MODEL               = "VGG-Face"   # DeepFace pretrained model
FACE_DISTANCE_METRIC     = "cosine"     # Similarity metric
FACE_ENFORCE_DETECTION   = False        # Dont crash if face not found
FACE_SIMILARITY_THRESHOLD = 0.4        # Below this = faces match
FACE_RELIABILITY_WEIGHT  = 0.9         # Trust level of face module
 
# Distance to confidence mapping
FACE_CONFIDENCE_THRESHOLDS = {
    "very_high": 0.2,
    "high":      0.4,
    "medium":    0.6
}
FACE_CONFIDENCE_SCORES = {
    "very_high": 0.95,
    "high":      0.80,
    "medium":    0.60,
    "low":       0.30
}
 
# ─────────────────────────────────────────
# MODULE 2: DOCUMENT VERIFICATION SETTINGS
# ─────────────────────────────────────────
# Change this path based on your OS
TESSERACT_PATH = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
# Linux/Mac: TESSERACT_PATH = "/usr/bin/tesseract"
 
DOCUMENT_RELIABILITY_WEIGHT = 0.8    # Trust level of document module
DOCUMENT_MIN_TEXT_LENGTH    = 10     # Min characters from OCR
 
# Validation rules for Indian ID documents
DOCUMENT_RULES = {
    "aadhaar": {
        "length":      12,
        "pattern":     r"^\d{12}$",
        "description": "12 digit number"
    },
    "pan": {
        "length":      10,
        "pattern":     r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$",
        "description": "5 letters + 4 digits + 1 letter"
    },
    "passport": {
        "length":      8,
        "pattern":     r"^[A-Z]{1}[0-9]{7}$",
        "description": "1 letter + 7 digits"
    }
}
 
DOCUMENT_CONFIDENCE_SCORES = {
    "high":     0.90,
    "medium":   0.65,
    "low":      0.30,
    "very_low": 0.10
}
 
# ─────────────────────────────────────────
# MODULE 3: BEHAVIORAL VERIFICATION SETTINGS
# ─────────────────────────────────────────
BEHAVIORAL_RELIABILITY_WEIGHT = 0.6   # Trust level of behavior module
BEHAVIORAL_BASELINE_SAMPLES   = 3     # Min samples for baseline
BEHAVIORAL_BASELINES_FILE     = os.path.join(BASELINES_DIR, "baselines.json")
 
BEHAVIORAL_THRESHOLDS = {
    "strong_match":   0.80,
    "moderate_match": 0.60,
    "weak_match":     0.40
}
 
BEHAVIORAL_HOUR_TOLERANCE_NORMAL   = 3
BEHAVIORAL_HOUR_TOLERANCE_MODERATE = 6
 
# ─────────────────────────────────────────
# DEMPSTER-SHAFER FUSION ENGINE SETTINGS
# ─────────────────────────────────────────
DS_RELIABILITY_WEIGHTS = {
    "face":     FACE_RELIABILITY_WEIGHT,
    "document": DOCUMENT_RELIABILITY_WEIGHT,
    "behavior": BEHAVIORAL_RELIABILITY_WEIGHT
}
 
TRUST_SCORE_THRESHOLDS = {
    "high_trust":   0.75,
    "medium_trust": 0.50
}
 
TRUST_LEVELS = {
    "verified": "VERIFIED",
    "flagged":  "FLAGGED - MANUAL REVIEW REQUIRED",
    "rejected": "REJECTED"
}
 
DS_HIGH_CONFLICT_THRESHOLD = 0.60
 
# ─────────────────────────────────────────
# CONFLICT TEST SCENARIO NAMES
# ─────────────────────────────────────────
CONFLICT_SCENARIOS = {
    "scenario_1": "All modules agree - genuine user",
    "scenario_2": "Face PASS, Document FAIL, Behavior PASS",
    "scenario_3": "Face FAIL, Document PASS, Behavior PASS",
    "scenario_4": "Face PASS, Document PASS, Behavior FAIL",
    "scenario_5": "All modules fail - impostor"
}
 
# ─────────────────────────────────────────
# LOGGING SETTINGS
# ─────────────────────────────────────────
LOG_FILE   = os.path.join(LOGS_DIR, "trustnet.log")
LOG_LEVEL  = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
 
# ─────────────────────────────────────────
# AUTO-CREATE REQUIRED DIRECTORIES
# ─────────────────────────────────────────
def create_directories():
    dirs = [
        DATABASE_DIR, DATA_DIR, SAMPLE_FACES_DIR,
        SAMPLE_DOCS_DIR, BASELINES_DIR, UPLOAD_FOLDER, LOGS_DIR
    ]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
 
create_directories()
 
# ─────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print(f"  {PROJECT_NAME} v{PROJECT_VERSION}")
    print(f"  {COLLEGE_NAME}")
    print(f"  {DEPARTMENT}")
    print("=" * 60)
    print(f"\n  Base Dir      : {BASE_DIR}")
    print(f"  Database      : {DATABASE_PATH}")
    print(f"  Baselines     : {BEHAVIORAL_BASELINES_FILE}")
    print(f"  Uploads       : {UPLOAD_FOLDER}")
    print(f"\n  Module Reliability Weights:")
    for module, weight in DS_RELIABILITY_WEIGHTS.items():
        print(f"    {module.capitalize():12}: {weight}")
    print(f"\n  Trust Thresholds:")
    print(f"    VERIFIED  : >= 75%")
    print(f"    FLAGGED   : 50% to 74%")
    print(f"    REJECTED  : < 50%")
    print("\n  All directories created successfully")
    print("  Config loaded OK")
 