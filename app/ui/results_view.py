import os
import subprocess

from PySide6.QtGui import QDesktopServices, Qt, QStandardItemModel, QStandardItem
from PySide6.QtCore import QFileInfo, QUrl, Qt, QSize
from PySide6.QtWidgets import (
    QHeaderView, QTableView, QFileIconProvider, QListWidget, 
    QListWidgetItem, QGraphicsOpacityEffect
)

from app.storage.models import File
from app.ui.custom_elements import ThumbnailWidget


class DetailView(QTableView):
    def __init__(self):
        super().__init__()
        self.header_labels = ["", "Name", "Size", "Date Created", "Date Modified", "Path"]
        self.verticalHeader().hide()
        self.doubleClicked.connect(self.on_table_cell_double_clicked)
        self.table_model = QStandardItemModel()
        self.setModel(self.table_model)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

    def update(self, files):
        self.table_model.clear()
        self.table_model.setHorizontalHeaderLabels(self.header_labels)
        for row in range(len(files)):
            row_items = []
            file: File = files[row]
            for col in range(len(self.header_labels)):
                item = QStandardItem()
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                item.setFlags(Qt.ItemIsEnabled)
                item.setToolTip(file.path)
                match self.header_labels[col]:
                    case '':
                        item.setIcon(self._get_memitype_icon(file.path))
                    case 'Name':
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        item.setText(file.name)
                    case 'Size': 
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        item.setText(f'{round(file.file_size / 1024):,} KB')
                    case 'Score':
                        item.setText(f'{file.score}')
                    case 'Path':
                        item.setText(file.path_parent)
                    case 'Date Created':
                        item.setText(file.date_created)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    case 'Date Modified':
                        item.setText(file.date_modified)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                row_items.append(item)
            self.table_model.appendRow(row_items) 
            header = self.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            self.setColumnWidth(1, int(self.width() * 0.45))
            header.setSectionResizeMode(0, QHeaderView.Fixed)
            header.setSectionResizeMode(3, QHeaderView.Fixed)
            header.setSectionResizeMode(4, QHeaderView.Fixed)
            header.setSectionResizeMode(5, QHeaderView.Stretch)

    def _get_memitype_icon(self, file_path: str):
        provider = QFileIconProvider()
        icon = provider.icon(QFileInfo(file_path))
        pixmap = icon.pixmap(8, 8)
        return pixmap
    
    def on_table_cell_double_clicked(self, index):
        match self.header_labels[index.column()]:
            case '' | 'Name':
                file_path = index.data(Qt.ToolTipRole)
                file_url = QUrl.fromLocalFile(file_path)
                QDesktopServices.openUrl(file_url)
            case 'Path':
                file_path = index.data(Qt.ToolTipRole)
                subprocess.run(f'explorer /select,"{os.path.normpath(file_path)}"')


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
