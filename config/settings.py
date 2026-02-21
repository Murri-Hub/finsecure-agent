config/settings.py

import os

BASE_DIR = os.getenv(
    "FINSECURE_BASE_DIR",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
