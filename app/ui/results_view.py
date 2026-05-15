from PySide6.QtGui import Qt, QStandardItemModel, QStandardItem, QColor, QBrush
from PySide6.QtCore import QFileInfo, QMimeDatabase, Qt, QSize
from PySide6.QtWidgets import (
    QHeaderView, QTableView, QFileIconProvider, QListWidget, 
    QListWidgetItem, QGraphicsOpacityEffect
)

from app.storage.models import File
from app.ui.elements import ThumbnailWidget


class DetailView(QTableView):
    def __init__(self, on_cell_double_clicked):
        super().__init__()
        self.verticalHeader().hide()
        self.doubleClicked.connect(on_cell_double_clicked)
        self.table_model = QStandardItemModel()
        self.setModel(self.table_model)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)


    def update(self, files):
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(["", "Name", "Score", "Path"])
        
        for row in range(len(files)):
            row_items = []
            file = files[row]
            
            
            for col in range(4):
                item = QStandardItem()
                item.setToolTip(file.path)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled)
                # item.setForeground(black_brush) # Apply strong 
                if col == 0:
                    item.setIcon(self._get_memitype_icon(file.path))
                elif col == 1:
                    item.setText(file.name)
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                elif col == 2:
                    item.setText(f'{file.score:.3}')
                elif col == 3:
                    item.setText(file.path) 
                row_items.append(item)
            self.table_model.appendRow(row_items)
            
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(2)
        self.setColumnWidth(1, int(self.width() * 0.6))
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)

    def _get_memitype_icon(self, file_path: str):
        db = QMimeDatabase()
        file_info = QFileInfo(file_path)
        provider = QFileIconProvider()
        icon = provider.icon(file_info)
        pixmap = icon.pixmap(8, 8)
        return pixmap



class GridView(QListWidget):
    def __init__(self, on_cell_double_clicked, parent=None):
        super().__init__(parent)
        self.on_cell_double_clicked = on_cell_double_clicked
        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setSpacing(10)
        self.setWordWrap(True)

    def update(self, files: list[File]):
        self.clear()
        for file in files:
            item = QListWidgetItem(self)
            item.setSizeHint(QSize(130, 160)) 
            
            custom_widget = ThumbnailWidget(file.path)
            
            # Map score (0.0 -> 1.0 opacity, 1.0 -> 0.2 opacity)
            opacity_val = 1.0 - (file.score * 0.8)
            opacity_effect = QGraphicsOpacityEffect(custom_widget)
            opacity_effect.setOpacity(opacity_val)
            custom_widget.setGraphicsEffect(opacity_effect)
            
            custom_widget.thumbnail_double_clicked.connect(lambda p: self.on_cell_double_clicked(p, "thumbnail"))
            custom_widget.label_double_clicked.connect(lambda p: self.on_cell_double_clicked(p, "label"))
            
            self.addItem(item)
            self.setItemWidget(item, custom_widget)
