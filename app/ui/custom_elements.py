import os
from PySide6.QtCore import QFileInfo, Qt, QEvent, Signal, QObject
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QFileIconProvider, QWidget, QVBoxLayout, QLabel, QDialog, QLineEdit, QPushButton, QHBoxLayout, QFileDialog)



class SetupDialog(QDialog):
    def __init__(self, config=None):
        super().__init__()
        self.setWindowTitle("SEMANTIC: Initial Setup")
        self.setFixedWidth(500)
        self.result_config = None
        layout = QVBoxLayout(self)
        # Path Input
        layout.addWidget(QLabel("Search Paths (comma separated):"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("e.g. C:/Users/Documents, D:/Videos")
        
        path_btn = QPushButton("Browse...")
        path_btn.clicked.connect(self.browse_folder)

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_input)
        path_row.addWidget(path_btn)
        layout.addLayout(path_row)
        # Extensions Input
        layout.addWidget(QLabel("Extensions (comma separated):"))
        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("e.g. mp4, pdf, docx")
        layout.addWidget(self.ext_input)
        # Submit
        self.submit_btn = QPushButton("Save and Start")
        self.submit_btn.clicked.connect(self.validate_and_submit)
        layout.addWidget(self.submit_btn)

        if config: 
            self.path_input.setText(', '.join(config['paths']))
            self.ext_input.setText(', '.join(config['extensions']))

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            current = self.path_input.text()
            self.path_input.setText(f"{current}, {folder}" if current else folder)

    def validate_and_submit(self):
        # Split and clean inputs
        paths = [p.strip() for p in self.path_input.text().split(",") if p.strip()]
        exts = [e.strip().replace(".", "") for e in self.ext_input.text().split(",") if e.strip()]
        # Validation: Check if paths exist and lists aren't empty
        valid_paths = [p for p in paths if os.path.isdir(p)]
        if not valid_paths:
            self.path_input.setStyleSheet("border: 1px solid red;")
            return
        if not exts:
            self.ext_input.setStyleSheet("border: 1px solid red;")
            return
        self.result_config = {"paths": valid_paths, "extensions": exts}
        self.accept()



# --- 1. Event Filter for Individual Elements ---
class DoubleClickFilter(QObject):
    double_clicked = Signal()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:
                self.double_clicked.emit()
                return True
        return super().eventFilter(obj, event)


# --- 2. Custom Grid Item View Component ---
class ThumbnailWidget(QWidget):
    # Signals passing the file path back to the parent application layout
    thumbnail_double_clicked = Signal(str)
    label_double_clicked = Signal(str)

    def __init__(self, file_path: str, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        filename = os.path.basename(file_path)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        # Explicit bounds sizing matching grid distribution engine bounds
        self.setFixedSize(130, 160)
        self.setStyleSheet("""
            ThumbnailWidget { border: none; background: transparent; }
            ThumbnailWidget:focus { background-color: rgba(0, 120, 212, 0.4); border-radius: 4px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Thumbnail setup
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(120, 110)
        self.thumbnail_label.setStyleSheet("border: 2px solid black;")
        
        # Determine asset configuration type
        pixmap = QPixmap(file_path) if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) else QPixmap()
        if pixmap.isNull():
            # icon = self.style().standardIcon(QStyle.SP_FileIcon)
            icon = self._get_memitype_icon(file_path)
            pixmap = icon.pixmap(80, 80)
        else:
            pixmap = pixmap.scaled(120, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        self.thumbnail_label.setPixmap(pixmap)
        layout.addWidget(self.thumbnail_label, alignment=Qt.AlignCenter)

        # Title Label setup
        label_text = filename[:30] + '...' if len(filename) > 30 else filename
        self.title_label = QLabel(label_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("border: 2px solid black;")
        # Prevent long labels from pushing the layout outward vertically
        self.title_label.setMaximumHeight(40)
        layout.addWidget(self.title_label)

        # Setup and attach event filters
        self.icon_filter = DoubleClickFilter(self)
        self.label_filter = DoubleClickFilter(self)
        self.thumbnail_label.installEventFilter(self.icon_filter)
        self.title_label.installEventFilter(self.label_filter)

        # Connect low-level actions to parent signal channels
        self.icon_filter.double_clicked.connect(lambda: self.thumbnail_double_clicked.emit(self.file_path))
        self.label_filter.double_clicked.connect(lambda: self.label_double_clicked.emit(self.file_path))

    def mousePressEvent(self, event):
        self.setFocus()
        super().mousePressEvent(event)


    def _get_memitype_icon(self, file_path: str):
        # db = QMimeDatabase()
        # mime = db.mimeTypeForFile(file_path)
        file_info = QFileInfo(file_path)
        provider = QFileIconProvider()
        icon = provider.icon(file_info)
        return icon
