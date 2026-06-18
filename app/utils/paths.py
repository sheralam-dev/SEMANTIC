import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    # Path to the folder containing the .exe
    EXE_LOCATION = Path(sys.executable).parent
    # In 'onedir' mode, PyInstaller puts data in the '_internal' folder
    # We check if '_internal' exists to support different PyInstaller versions
    INTERNAL_DIR = EXE_LOCATION / "_internal"
    if INTERNAL_DIR.exists():
        BASE_DIR = INTERNAL_DIR
    else:
        BASE_DIR = EXE_LOCATION
    # Store DB in AppData (as established before)
    DATA_DIR = Path(os.environ["LOCALAPPDATA"]) / "SearchApp"
else:
    # Development mode
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"

MODEL_PATH = BASE_DIR / "models"
DB_PATH = DATA_DIR / "files.db"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = DATA_DIR /"config.json"
ICON_PATH = BASE_DIR / "app.ico"