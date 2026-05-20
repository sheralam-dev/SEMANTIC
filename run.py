import os
import json
import argparse
from app.storage import db
from app.ui.window import SearchApp
from app.utils.paths import CONFIG_FILE


def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None


def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrollable Table Engine")
    parser.add_argument("--reindex", action="store_true", help="Force rebuild index.")
    parser.add_argument("--no-watch", action="store_true", help="Disable live watcher.")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    config = get_config()
    db.init_db(drop_tables=True, vector_len=384)
    SearchApp.start_class_app(
        config=config,
        enable_watcher=not args.no_watch
    )

