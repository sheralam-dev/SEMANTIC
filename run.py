import argparse
from app.storage import db
from app.ui.window import SearchApp

def parse_arguments():
    """Handles Command Line Interface (CLI) configuration flags flags."""
    parser = argparse.ArgumentParser(description="Scrollable Table Engine")
    parser.add_argument("--reindex", action="store_true", help="Force clear and rebuild database index.")
    parser.add_argument("--no-watch", action="store_true", help="Disable the background live directory watcher service.")
    parser.add_argument("--debug", action="store_true", help="Run application framework in verbose mode.")
    return parser.parse_args()

if __name__ == "__main__":
    # 1. Initialize Runtime Arguments & Configuration
    args = parse_arguments()
    
    # 2. Initialize Database Layer
    # Clear the schema instantly if --reindex flag is passed down by CLI user
    db.init_db(drop_tables=args.reindex, vector_len=768)
    
    # Default runtime configurations
    default_paths = ["D:\Videos\AI Development"]
    default_extensions = {'mp4', 'pdf'}
    
    # 3. Boot Application Lifecycle Thread Loop
    # Blocks executing process internally until user dismisses native window 
    SearchApp.start_class_app(
        paths=default_paths, 
        extensions=default_extensions,
        enable_watcher=not args.no_watch

    )
