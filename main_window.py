import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QSplitter)
from PyQt5.QtCore import Qt
from PIL import Image

from file_browser_widget import FileBrowserWidget
from image_display_widget import ImageDisplayWidget
from statistics_panel_widget import StatisticsPanelWidget
from console_widget import ConsoleWidget

class ImageViewer(QMainWindow):
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Image Viewer (Refactored)")
        self.setGeometry(100, 100, 1200, 800)
        
        self.current_image_path = None
        self.initUI()

    def initUI(self):
        try:
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget) 
            
            self.h_splitter = QSplitter(Qt.Horizontal)
            
            self.file_browser = FileBrowserWidget()
            self.console = ConsoleWidget()
            self.image_display = ImageDisplayWidget()
            self.statistics_panel = StatisticsPanelWidget()
            
            self.middle_splitter = QSplitter(Qt.Vertical)
            self.middle_splitter.addWidget(self.image_display)
            self.middle_splitter.addWidget(self.console)
            self.middle_splitter.setSizes([550, 150])

            self.h_splitter.addWidget(self.file_browser)
            self.h_splitter.addWidget(self.middle_splitter)
            self.h_splitter.addWidget(self.statistics_panel)
            
            self.main_layout.addWidget(self.h_splitter)
            
            self.h_splitter.setSizes([250, 700, 250])  
            
            self.file_browser.fileSelected.connect(self.handle_file_selected)
            self.file_browser.itemSelected.connect(self.handle_item_selected)

            self.console.logMessage("Image Viewer started. Select an image from the file browser.")
        except Exception as e:
            print(f"Error in initUI: {e}")

    def handle_item_selected(self, path):
        try:
            if not os.path.isdir(path) and not path.lower().endswith(self.SUPPORTED_FORMATS):
                 self.console.logMessage(f"Selected non-image file: {os.path.basename(path)}")
            elif os.path.isdir(path):
                 self.console.logMessage(f"Selected directory: {os.path.basename(path)}")
        except Exception as e:
            print(f"Error in handle_item_selected: {e}")


    def handle_file_selected(self, file_path):
        try:
            if file_path.lower().endswith(self.SUPPORTED_FORMATS):
                self.load_image(file_path)
        except Exception as e:
            print(f"Error in handle_file_selected: {e}")

    def load_image(self, file_path):
        try:
            pil_image = Image.open(file_path)
            pil_image.verify()
            pil_image = Image.open(file_path) 
            
            if self.image_display.loadImage(file_path):
                self.current_image_path = file_path
                self.statistics_panel.updateStats(file_path, pil_image)
                self.console.logMessage(f"Loaded image: {os.path.basename(file_path)}")
            else:
                self.console.logMessage(f"Failed to display image: {os.path.basename(file_path)}")
                self.current_image_path = None
                self.statistics_panel.clearStats()

        except FileNotFoundError:
             self.console.logMessage(f"Error: File not found - {file_path}")
             self.image_display.clearImage()
             self.statistics_panel.clearStats()
             self.current_image_path = None
        except (Image.UnidentifiedImageError, IOError) as e:
            self.console.logMessage(f"Error reading image file ({type(e).__name__}): {os.path.basename(file_path)}")
            self.image_display.clearImage()
            self.image_display.image_label.setText(f"Cannot read file:\n{os.path.basename(file_path)}")
            self.statistics_panel.clearStats()
            self.current_image_path = None
        except Exception as e:
            self.console.logMessage(f"Error loading image '{os.path.basename(file_path)}': {str(e)}")
            self.image_display.clearImage()
            self.statistics_panel.clearStats()
            self.current_image_path = None