# image_display_widget.py
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap

class ImageDisplayWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_pixmap = None
        self.initUI()

    def initUI(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.setMinimumSize(400, 400)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No image selected")
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def loadImage(self, file_path):
        if not file_path or not os.path.exists(file_path):
            self.clearImage()
            return False
            
        try:
            self.current_pixmap = QPixmap(file_path)
            if self.current_pixmap.isNull():
                self.clearImage()
                self.image_label.setText(f"Error loading:\n{os.path.basename(file_path)}")
                return False
            self._update_display()
            return True
        except Exception:
            self.clearImage()
            self.image_label.setText(f"Error loading:\n{os.path.basename(file_path)}")
            return False

    def clearImage(self):
        self.current_pixmap = None
        self.image_label.clear()
        self.image_label.setText("No image selected")

    def _update_display(self):
        if not self.current_pixmap or self.current_pixmap.isNull():
            return
            
        # Scale pixmap to fit the label while maintaining aspect ratio
        scaled_pixmap = self.current_pixmap.scaled(
            self.image_label.size(), # Use label size for scaling target
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        # Call parent resize event
        super().resizeEvent(event)
        # Rescale the image when the widget is resized
        self._update_display()