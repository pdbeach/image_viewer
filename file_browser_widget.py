# file_browser_widget.py
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QFileSystemModel, QTreeView)
from PyQt5.QtCore import Qt, QDir, pyqtSignal, QModelIndex

class FileBrowserWidget(QWidget):
    # Signal emitted when a valid file is selected
    fileSelected = pyqtSignal(str) 
    # Signal emitted when any item (file or dir) is clicked
    itemSelected = pyqtSignal(str) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("File Browser")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Create file system model
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.homePath())
        # Filter for image files - applied visually but we re-check in main window
        self.file_model.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"])
        self.file_model.setNameFilterDisables(False) # Show files that don't match filter
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setColumnWidth(0, 200)
        
        # Connect the click signal
        self.tree_view.clicked.connect(self._on_tree_clicked)
        
        layout.addWidget(self.tree_view)
        self.setLayout(layout)

    def _on_tree_clicked(self, index: QModelIndex):
        file_path = self.file_model.filePath(index)
        self.itemSelected.emit(file_path) # Emit path regardless of type initially
        
        if os.path.isfile(file_path):
             # Only emit fileSelected for actual files
            self.fileSelected.emit(file_path) 