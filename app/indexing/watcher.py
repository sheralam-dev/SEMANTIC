
from pathlib import Path
from queue import Queue
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler

from app.storage.models import File
import app.storage.repository as repo


# 1. The Worker: This runs in the background and processes the queue
def process_events(event_queue: Queue):
    while True:
        # Get the next event from the queue (waits if empty)
        event: FileSystemEvent = event_queue.get()
        if event is None: 
            break  # Stop signal
        
        src_path = Path(event.src_path)
        match event.event_type:
            case 'created': 
                file: File = File(src_path)
                repo.insert_file(file)
                print(f'record inserted: {file.name}')
            case 'deleted': 
                repo.delete_file(str(src_path)) 
                print(f'file deleted: {src_path.name}') 
            case 'moved': 
                dest_path = Path(event.dest_path)
                repo.update_file_path(src_path, dest_path)
                print(f'File renamed: {src_path.name} -> {dest_path.name}')
        event_queue.task_done()


# 2. File Event Listner. 
class FastEventHandler(PatternMatchingEventHandler):
    def __init__(self, event_queue: Queue, patterns = ["*.txt"]):
        super().__init__(
            patterns=patterns, 
            ignore_directories=True,
            case_sensitive=False,
        )
        self.event_queue = event_queue
    def on_any_event(self, event):
        if event.event_type == 'modified': 
            return
        self.event_queue.put(event)


# 3. Setting it up
def start_watching_async(params: dict):
    print(f'[watcher.py] {params = }')
    event_queue = Queue()
    # Start the worker thread
    worker = Thread(target=process_events, args=(event_queue,), daemon=True)
    worker.start()
    # Start the watcher
    extensions = [f"*.{ext}" for ext in params['extensions']]
    handler = FastEventHandler(event_queue, extensions)
    observer = Observer()
    observer.schedule(handler, params['paths'][0], recursive=True)
    observer.start()
    return observer
