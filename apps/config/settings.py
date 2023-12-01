from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = True
DEBUG_PRINT_FILEINPUT = False

DB_NAME = "FEWT.sqlite3"
WATCHING_INTERVAL_MS = 5