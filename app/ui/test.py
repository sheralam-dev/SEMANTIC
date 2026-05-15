import os
import sys
import subprocess
from PySide6.QtCore import Qt, QEvent, Signal, QObject, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, 
    QStyle, QListWidget, QListWidgetItem
)

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
            ThumbnailWidget:focus { background-color: rgba(0, 120, 212, 0.15); border-radius: 4px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Thumbnail setup
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setFixedSize(120, 110)
        
        # Determine asset configuration type
        pixmap = QPixmap(file_path) if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) else QPixmap()
        if pixmap.isNull():
            icon = self.style().standardIcon(QStyle.SP_FileIcon)
            pixmap = icon.pixmap(80, 80)
        else:
            pixmap = pixmap.scaled(120, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
        self.thumbnail_label.setPixmap(pixmap)
        layout.addWidget(self.thumbnail_label, alignment=Qt.AlignCenter)

        # Title Label setup
        self.title_label = QLabel(filename)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
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


# --- 3. Grid View Implementation via List View Wrapper ---
class GridView(QListWidget):
    def __init__(self, on_cell_double_clicked, parent=None):
        super().__init__(parent)
        self.on_cell_double_clicked = on_cell_double_clicked
        
        # Configure layout engine to serve as a wrapping Grid component
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setSpacing(10)
        self.setWordWrap(True)
        self.setStyleSheet("QListWidget { border: none; background-color: #ffffff; }")

    def update(self, paths: list[str]):
        self.clear()
        for path in paths:
            item = QListWidgetItem(self)
            
            # Match the exact dimensions of your custom ThumbnailWidget (130x160)
            from PySide6.QtCore import QSize
            item.setSizeHint(QSize(130, 160)) 
            
            custom_widget = ThumbnailWidget(path)
            
            # Route signals straight to callback handler functions
            custom_widget.thumbnail_double_clicked.connect(lambda p: self.on_cell_double_clicked(p, "thumbnail"))
            custom_widget.label_double_clicked.connect(lambda p: self.on_cell_double_clicked(p, "label"))
            
            self.addItem(item)
            self.setItemWidget(item, custom_widget)


# --- 4. Main Application ---
class SearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.paths = [
            "D:/Desktop/Pydantic AI Crash Course: Agentic Framework For Production [pXktHVUpXUc].mp4",
            "D:/Desktop/training ouput.txt",
            "D:/Desktop/Embeddings.png",
            "D:/Desktop/Sher Alam.txt",
            "D:/Desktop/bonkheads - enemies.xlsx",
            "D:/Desktop/navigation-button.psd",
        ]
        self.setWindowTitle("Scrollable Table Tool")
        self.resize(500, 400)
        self.main_layout = QVBoxLayout(self)

        # Initialize GridView with standard uniform router callback method 
        self.table_view = GridView(on_cell_double_clicked=self.on_cell_double_clicked)
        self.main_layout.addWidget(self.table_view)
        self.table_view.update(self.paths)

    def on_cell_double_clicked(self, file_path: str, clicked_part: str):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        if clicked_part == "thumbnail":
            # Action: Open file with default application system layer handler
            file_url = QUrl.fromLocalFile(file_path)
            QDesktopServices.openUrl(file_url)
            
        elif clicked_part == "label":
            # Action: Target folder workspace directory layout highlight locator
            subprocess.run(f'explorer /select,"{os.path.normpath(file_path)}"')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SearchApp()
    window.show()
    sys.exit(app.exec())
