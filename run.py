import argparse
import json
import os
import sys
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QFileDialog)
from PySide6.QtCore import Qt
from app.storage import db
from app.ui.window import SearchApp
from app.ui.custom_elements import SetupDialog
from app.utils.paths import CONFIG_FILE


def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    app = QApplication.instance() or QApplication(sys.argv)
    dialog = SetupDialog()
    if dialog.exec() == QDialog.Accepted:
        config = dialog.result_config
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return config
    else:
        # Exit the entire script if they close the dialog without submitting
        sys.exit("Setup cancelled by user.")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrollable Table Engine")
    parser.add_argument("--reindex", action="store_true", help="Force rebuild index.")
    parser.add_argument("--no-watch", action="store_true", help="Disable live watcher.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    config = get_config()
    
    db.init_db(drop_tables=args.reindex, vector_len=384)
    
    SearchApp.start_class_app(
        paths=config["paths"], 
        extensions=set(config["extensions"]),
        enable_watcher=not args.no_watch
    )

