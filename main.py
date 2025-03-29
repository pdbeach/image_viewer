#!/usr/bin/env python3
import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
import io
import qdarkstyle

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Image Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create horizontal splitter for main areas
        self.h_splitter = QSplitter(Qt.Horizontal)
        
        # Create file browser (left panel)
        self.setup_file_browser()
        
        # Create middle section (image viewer and console)
        self.middle_section = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_section)
        
        # Create image viewer
        self.setup_image_viewer()
        
        # Create console
        self.setup_console()
        
        # Add middle section to splitter
        self.h_splitter.addWidget(self.middle_section)
        
        # Create statistics panel (right panel)
        self.setup_statistics_panel()
        
        # Add the horizontal splitter to the main layout
        self.main_layout.addWidget(self.h_splitter)
        
        # Set initial splitter sizes
        self.h_splitter.setSizes([250, 700, 250])  # Left, Middle, Right
        
        # Current image path
        self.current_image_path = None

    def setup_file_browser(self):
        # Create file browser widget
        self.file_browser = QWidget()
        self.file_browser_layout = QVBoxLayout(self.file_browser)
        
        # Create label
        self.file_browser_label = QLabel("File Browser")
        self.file_browser_label.setAlignment(Qt.AlignCenter)
        self.file_browser_layout.addWidget(self.file_browser_label)
        
        # Create file system model
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.homePath())
        self.file_model.setNameFilters(["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"])
        self.file_model.setNameFilterDisables(False)
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.homePath()))
        self.tree_view.setAnimated(False)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setColumnWidth(0, 200)
        self.tree_view.clicked.connect(self.on_file_selected)
        
        # Add tree view to layout
        self.file_browser_layout.addWidget(self.tree_view)
        
        # Add file browser to splitter
        self.h_splitter.addWidget(self.file_browser)

    def setup_image_viewer(self):
        # Create image viewer widget
        self.image_frame = QFrame()
        self.image_frame.setFrameShape(QFrame.StyledPanel)
        self.image_frame.setFrameShadow(QFrame.Sunken)
        self.image_frame.setLineWidth(1)
        self.image_frame.setMinimumSize(400, 400)
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No image selected")
        
        # Create layout for image frame
        self.image_layout = QVBoxLayout(self.image_frame)
        self.image_layout.addWidget(self.image_label)
        
        # Add image frame to middle layout
        self.middle_layout.addWidget(self.image_frame, 7)  # 70% of middle section

    def setup_console(self):
        # Create console widget
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        
        # Add console to middle layout
        self.middle_layout.addWidget(self.console, 3)  # 30% of middle section
        
        # Initial console message
        self.log_message("Image Viewer started. Select an image from the file browser.")

    def setup_statistics_panel(self):
        # Create statistics panel widget
        self.stats_panel = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_panel)
        
        # Create label
        self.stats_label = QLabel("Image Statistics")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_layout.addWidget(self.stats_label)
        
        # Create grid for statistics
        self.stats_grid = QGridLayout()
        
        # Create labels for statistics
        self.filename_label = QLabel("Filename:")
        self.filename_value = QLabel("-")
        self.stats_grid.addWidget(self.filename_label, 0, 0)
        self.stats_grid.addWidget(self.filename_value, 0, 1)
        
        self.dimensions_label = QLabel("Dimensions:")
        self.dimensions_value = QLabel("-")
        self.stats_grid.addWidget(self.dimensions_label, 1, 0)
        self.stats_grid.addWidget(self.dimensions_value, 1, 1)
        
        self.format_label = QLabel("Format:")
        self.format_value = QLabel("-")
        self.stats_grid.addWidget(self.format_label, 2, 0)
        self.stats_grid.addWidget(self.format_value, 2, 1)
        
        self.size_label = QLabel("File Size:")
        self.size_value = QLabel("-")
        self.stats_grid.addWidget(self.size_label, 3, 0)
        self.stats_grid.addWidget(self.size_value, 3, 1)
        
        self.mode_label = QLabel("Color Mode:")
        self.mode_value = QLabel("-")
        self.stats_grid.addWidget(self.mode_label, 4, 0)
        self.stats_grid.addWidget(self.mode_value, 4, 1)
        
        # Add grid to layout
        self.stats_layout.addLayout(self.stats_grid)
        
        # Add spacer
        self.stats_layout.addStretch()
        
        # Add statistics panel to splitter
        self.h_splitter.addWidget(self.stats_panel)

    def on_file_selected(self, index):
        # Get file path
        file_path = self.file_model.filePath(index)
        
        # Check if it's a file
        if os.path.isfile(file_path):
            # Check if it's an image
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                self.load_image(file_path)
            else:
                self.log_message(f"Selected file is not a supported image: {file_path}")
        else:
            self.log_message(f"Selected directory: {file_path}")

    def load_image(self, file_path):
        try:
            # Load image with PIL for statistics
            pil_image = Image.open(file_path)
            
            # Load image with Qt for display
            pixmap = QPixmap(file_path)
            
            # Scale pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # Set pixmap to label
            self.image_label.setPixmap(scaled_pixmap)
            
            # Update current image path
            self.current_image_path = file_path
            
            # Update statistics
            self.update_statistics(file_path, pil_image)
            
            # Log message
            self.log_message(f"Loaded image: {os.path.basename(file_path)}")
            
        except Exception as e:
            self.log_message(f"Error loading image: {str(e)}")

    def update_statistics(self, file_path, pil_image):
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
        self.format_value.setText(pil_image.format)
        self.size_value.setText(size_str)
        self.mode_value.setText(pil_image.mode)

    def log_message(self, message):
        # Add message to console
        self.console.append(message)
        
        # Scroll to bottom
        self.console.verticalScrollBar().setValue(
            self.console.verticalScrollBar().maximum()
        )

    def resizeEvent(self, event):
        # Call parent resize event
        super().resizeEvent(event)
        
        # If an image is loaded, resize it
        if self.current_image_path and os.path.exists(self.current_image_path):
            pixmap = QPixmap(self.current_image_path)
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
