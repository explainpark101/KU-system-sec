from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

USER_HOME = Path(os.path.expanduser("~"))

DEBUG = False
DEBUG_PRINT_FILEINPUT = False

DB_NAME = "FEWT.sqlite3"
WATCHING_INTERVAL_MS = 5

TRACKING_IGNORE_LIST = [
    USER_HOME / "DIR" / "NOT_FOR" / "Tracking",
    # USER_HOME / "AppData",
    # USER_HOME / "scoop",
]