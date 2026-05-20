import json
import os
import subprocess
import sys
from typing import List
from PySide6.QtCore import QUrl, Qt, QThread, Signal, Slot
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QProgressDialog, QPushButton, QStackedWidget, QStyle, QWidget, QVBoxLayout, QLineEdit)
from app.search.embedding_model import load_model
from app.storage import db, repository
from app.storage.models import File
from app.ui.custom_elements import SetupDialog
from app.ui.results_view import DetailView, GridView
from app.utils.paths import CONFIG_FILE

# --- NEW: QT SAFE THREAD WORKER COMPONENT ---
class ScanWorker(QThread):
    """Executes background indexing operations safely without freezing the window."""
    scan_finished = Signal()

    def __init__(self, params, dialog: QProgressDialog):
        super().__init__()
        self.params = params
        self.dialog = dialog

    def run(self):
        from app.indexing import scanner
        print("[window] Loading embedding model...")
        self.dialog.setLabelText('Loading embedding model...')
        load_model()
        print("[window] Scanning file system...")
        self.dialog.setLabelText('Scanning file system...')
        scanner.batch_scan(**self.params)
        print("[window] Scan finished.")
        self.scan_finished.emit()


class SearchApp(QWidget):
    # --- MODIFIED: ACCEPT RUNTIME PARAMETERS FROM RUN.PY ---
    def __init__(self, config=None, enable_watcher=True):
        super().__init__()
        
        # New State Variables for Service Control
        self.enable_watcher = enable_watcher
        self.observer = None
        self.scan_thread = None
        self.params = {"paths": [], "extensions": [], "batch_size": 200}
        
        self.setWindowTitle("Semantic v_0.2")
        self.resize(850, 600)

        # 1. Main Vertical Layout
        self.main_layout = QVBoxLayout(self)

        # 2. Horizontal Header Layout for Search and Toggle Controls
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(6)

        # Setting Button Setup
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setMinimumHeight(38)
        self.settings_btn.setToolTip("Settings")
        # self.settings_btn.setIcon(settings_icon)
        self.header_layout.addWidget(self.settings_btn)
        self.settings_btn.clicked.connect(self.open_setup_dialog)

        # Search Box Setup
        self.search_box = QLineEdit()
        self.search_box.setStyleSheet("font-size: 18px;")
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.search_box.returnPressed.connect(self.update_result_view)
        self.header_layout.addWidget(self.search_box)

        # Toggle Button Setup
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(False)
        self.toggle_btn.setMinimumHeight(38) 
        self.toggle_btn.setToolTip("Toggle Grid / Detail View")
        self.toggle_btn.clicked.connect(self.toggle_view_mode)
        self.header_layout.addWidget(self.toggle_btn)

        self.main_layout.addLayout(self.header_layout)

        # 3. View Architecture Container Layer
        self.view_stack = QStackedWidget()
        self.main_layout.addWidget(self.view_stack)

        # Initialize DetailView
        self.detail_view = DetailView()
        self.view_stack.addWidget(self.detail_view)

        # Initialize GridView
        self.grid_view = GridView(on_cell_double_clicked=self.on_grid_cell_double_clicked)
        self.view_stack.addWidget(self.grid_view)

        self.detail_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        self.grid_icon = self.style().standardIcon(QStyle.SP_FileDialogListView)
        self.toggle_btn.setIcon(self.detail_icon)
        self.view_stack.setCurrentWidget(self.detail_view)

        if not config:
            config = self.open_setup_dialog()
        if config:
            self.params.update(config) 
            self.trigger_background_scan()

    @property
    def result_view(self):
        return self.view_stack.currentWidget()

    def toggle_view_mode(self):
        if self.view_stack.currentWidget() == self.grid_view:
            self.view_stack.setCurrentWidget(self.detail_view)
            self.toggle_btn.setIcon(self.detail_icon)
        else:
            self.view_stack.setCurrentWidget(self.grid_view)
            self.toggle_btn.setIcon(self.grid_icon)
        if self.search_box.text():
            self.update_result_view()

    def update_result_view(self):
        term = self.search_box.text()
        if not term: return
        files: List[File] = repository.search_similar_files(term, top_k=500, max_distance=0.45)
        # Populates whichever view is active via the dynamic property
        self.result_view.update(files)

    # --- NEW: BACKGROUND CONCURRENCY & WORKER LIFECYCLE MANAGERS ---
    def trigger_background_scan(self):
        """Asynchronously triggers directory file engine index scanning safely."""
        # 1. Create the blocking dialog
        self.dialog = QProgressDialog("", None, 0, 0, self)
        self.dialog.setFixedWidth(500)
        self.dialog.setWindowTitle("Please Wait")
        self.dialog.setWindowModality(Qt.WindowModality.WindowModal)
        
        # Remove close button and reset cancel configurations
        self.dialog.setWindowFlags(self.dialog.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.dialog.setCancelButton(None) 
        if self.scan_thread and self.scan_thread.isRunning():
            return
        self.scan_thread = ScanWorker(self.params, self.dialog)
        self.scan_thread.scan_finished.connect(self._on_scan_complete)
        self.scan_thread.start()
        self.dialog.show()

    @Slot()
    def _on_scan_complete(self):
        """Executes safely on Main UI thread once file engine scanner finishes operation."""
        print("[UI] Asynchronous indexing routine completed successfully.")
        self.dialog.close()
        # Proactively trigger UI render update if a query is already typed out 
        if self.search_box.text():
            self.update_result_view()
        # Start Live Observer Watcher tracking modifications 
        if self.enable_watcher and not self.observer:
            self.start_watcher()

    def start_watcher(self):
        from app.indexing.watcher import start_watching_async
        print('[UI] Starting background folder monitoring watcher system...')
        self.observer = start_watching_async(self.params)
    
    def open_setup_dialog(self):
        """Handles ONLY the UI and persistence of settings."""
        dialog = SetupDialog(self.params)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.result_config
            db.init_db(drop_tables=True, vector_len=384)
            try:
                with open(CONFIG_FILE, "w") as f:
                    json.dump(config, f, indent=4)
                self.update_settings(config)
            except IOError as e:
                print(f"Failed to save config: {e}")
                self.update_settings(config)

    def update_settings(self, config: dict):
        """The single point of truth for applying configuration changes."""
        self.params.update({
            'paths': config.get('paths', []),
            'extensions': config.get('extensions', []),
            'batch_size': 200
        })
        if self.observer:
            print('[UI] Halting watcher system for engine scope reset...')
            self.observer.stop()
            self.observer.join()
            self.observer = None
        self.trigger_background_scan()

    def closeEvent(self, event):
        """Hook executing automatically when window interface closes down."""
        print("[UI] Cleaning up resources before window destruction...")
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
            
        event.accept()

   
    @classmethod
    def start_class_app(cls, config, enable_watcher=True):
        """Class method acting as single blocking runtime launch engine hook."""
        app = QApplication.instance() or QApplication(sys.argv)
        window = cls(config, enable_watcher=enable_watcher)
        window.show()
        sys.exit(app.exec())


    def on_grid_cell_double_clicked(self, file_path: str, clicked_part: str):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        if clicked_part == "thumbnail":
            file_url = QUrl.fromLocalFile(file_path)
            QDesktopServices.openUrl(file_url)
        elif clicked_part == "label":
            subprocess.run(f'explorer /select,"{os.path.normpath(file_path)}"')

