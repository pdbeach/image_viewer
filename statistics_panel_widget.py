# statistics_panel_widget.py
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtCore import Qt
from PIL import Image 

class StatisticsPanelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Image Statistics")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        grid = QGridLayout()
        
        self.filename_label = QLabel("Filename:")
        self.filename_value = QLabel("-")
        grid.addWidget(self.filename_label, 0, 0)
        grid.addWidget(self.filename_value, 0, 1)
        
        self.dimensions_label = QLabel("Dimensions:")
        self.dimensions_value = QLabel("-")
        grid.addWidget(self.dimensions_label, 1, 0)
        grid.addWidget(self.dimensions_value, 1, 1)
        
        self.format_label = QLabel("Format:")
        self.format_value = QLabel("-")
        grid.addWidget(self.format_label, 2, 0)
        grid.addWidget(self.format_value, 2, 1)
        
        self.size_label = QLabel("File Size:")
        self.size_value = QLabel("-")
        grid.addWidget(self.size_label, 3, 0)
        grid.addWidget(self.size_value, 3, 1)
        
        self.mode_label = QLabel("Color Mode:")
        self.mode_value = QLabel("-")
        grid.addWidget(self.mode_label, 4, 0)
        grid.addWidget(self.mode_value, 4, 1)
        
        layout.addLayout(grid)
        layout.addStretch() # Add spacer
        self.setLayout(layout)

    def updateStats(self, file_path, pil_image):
        try:
            # Get file info
            file_info = os.stat(file_path)
            file_size = file_info.st_size
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Update statistics labels
            self.filename_value.setText(os.path.basename(file_path))
            self.dimensions_value.setText(f"{pil_image.width} x {pil_image.height}")
            self.format_value.setText(pil_image.format or "N/A")
            self.size_value.setText(size_str)
            self.mode_value.setText(pil_image.mode or "N/A")
        except Exception as e:
            print(f"Error updating stats: {e}") # Or log to console
            self.clearStats()
            self.filename_value.setText(f"Error reading stats")

    def clearStats(self):
        self.filename_value.setText("-")
        self.dimensions_value.setText("-")
        self.format_value.setText("-")
        self.size_value.setText("-")
        self.mode_value.setText("-")