import io
import os
import torch
import traceback

from PIL import Image
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import Qt, QSize, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont, QImage

class ImageDisplayWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("Initializing ImageDisplayWidget...")
        self.original_pixmap = None # Store the original loaded pixmap
        self.current_pixmap = None  # Store the pixmap currently being displayed (original or analyzed)
        self.analyze_button = None  # Placeholder for the button

        self.model_path = r'C:\Users\pbeac\Repos\image_viewer\AIModel\experiment1_gpu\weights\best.pt'
        self.model = self._load_yolo_model()

        self.initUI()

    def _load_yolo_model(self):
        print(f"Attempting to load YOLOv5 model from: {self.model_path}")
        model = None
        if not os.path.exists(self.model_path):
            print(f"Error: Model weights not found at {self.model_path}")
            return None
        try:
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=self.model_path, force_reload=False, trust_repo=True)
            model.conf = 0.35
            print("YOLOv5 model loaded successfully.")
        except Exception as e:
            print(f"Error loading YOLOv5 model: {e}")
            print("Ensure PyTorch, YOLOv5 dependencies are installed and the path is correct.")
            traceback.print_exc()
        return model

    def initUI(self):
        print("Initializing UI components.")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(1)
        self.setMinimumSize(400, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Image Label (Takes up most space)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No image selected")
        self.image_label.setMinimumSize(300, 300)
        layout.addWidget(self.image_label, 1) # Give it stretch factor 1

        # Analyze Button (Fixed height below image)
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setFixedHeight(40)
        self.analyze_button.setEnabled(False) # Initially disabled
        self.analyze_button.clicked.connect(self.analyze_image) # Connect signal
        layout.addWidget(self.analyze_button, 0) # Give it stretch factor 0

        self.setLayout(layout)
        print("UI Initialized with Image Label and Analyze Button.")

    def loadImage(self, file_path):
        print(f"Attempting to load image: {file_path}")
        self.clearImage() # Clear previous state first

        if not file_path or not os.path.exists(file_path):
            print(f"loadImage: Invalid or non-existent file path: {file_path}")
            return False

        try:
            print("Loading QPixmap from file.")
            loaded_pixmap = QPixmap(file_path)
            if loaded_pixmap.isNull():
                print(f"Error: Failed to load image file: {os.path.basename(file_path)}")
                self.image_label.setText(f"Error loading:\n{os.path.basename(file_path)}")
                return False

            print("QPixmap loaded successfully.")
            self.original_pixmap = loaded_pixmap
            self.current_pixmap = self.original_pixmap.copy()

            print("Updating display with original image.")
            self._update_display()

            if self.model:
                print("Model available, enabling Analyze button.")
                self.analyze_button.setEnabled(True)
            else:
                print("Model not available, Analyze button remains disabled.")
                self.analyze_button.setEnabled(False)

            print(f"Successfully loaded image: {os.path.basename(file_path)}")
            return True

        except Exception as e:
            print(f"Error loading image {os.path.basename(file_path)}: {e}")
            traceback.print_exc()
            self.clearImage()
            self.image_label.setText(f"Error loading:\n{os.path.basename(file_path)}")
            return False

    def analyze_image(self):
        """Runs AI inference on the loaded original image and updates display."""
        print("Analyze button clicked.")
        if not self.original_pixmap or self.original_pixmap.isNull():
            print("Analysis skipped: No original image loaded.")
            return
        if not self.model:
            print("Analysis skipped: Model not available.")
            return

        print("Starting AI analysis...")
        try:
            print("Converting QPixmap to PIL Image for model.")
            pil_image = self._qpixmap_to_pil(self.original_pixmap)

            if pil_image:
                print("Running AI model inference...")
                results = self.model(pil_image)
                print(f"AI Model analysis complete.")

                print("Drawing bounding boxes (if any) on pixmap.")
                pixmap_with_boxes = self._draw_boxes_on_pixmap(self.original_pixmap.copy(), results)
                self.current_pixmap = pixmap_with_boxes

                print("Updating display with analyzed image.")
                self._update_display()
            else:
                print("Error: Could not convert QPixmap to PIL format for analysis.")

        except Exception as e:
            print(f"Error during image analysis: {e}")
            traceback.print_exc()
            self.image_label.setText(f"Analysis Error:\n{str(e)}")


    def _qpixmap_to_pil(self, qpixmap):
        print("Attempting QPixmap to PIL conversion.")
        try:
            qimage = qpixmap.toImage()
            buffer = QBuffer()
            buffer.open(QIODevice.ReadWrite)
            qimage.save(buffer, "PNG")
            buffer.seek(0)
            image_data = buffer.data()
            image_stream = io.BytesIO(image_data)
            pil_img = Image.open(image_stream).convert('RGB')
            buffer.close()
            print("QPixmap to PIL conversion successful.")
            return pil_img
        except Exception as e:
            print(f"Error converting QPixmap to PIL: {e}")
            traceback.print_exc()
            return None

    def _draw_boxes_on_pixmap(self, pixmap_to_draw_on, yolo_results):
        painter = QPainter(pixmap_to_draw_on)
        painter.setRenderHint(QPainter.Antialiasing)

        detections = yolo_results.pandas().xyxy[0]
        num_detections = len(detections)
        print(f"Detected {num_detections} objects.")

        if num_detections > 0:
            print("Drawing bounding boxes...")
            for index, row in detections.iterrows():
                xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                confidence = row['confidence']
                name = row['name']
                label = f"{name} {confidence:.2f}"

                pen = QPen(QColor(0, 255, 0, 200), 2)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawRect(xmin, ymin, xmax - xmin, ymax - ymin)

                font = QFont()
                font_size = max(8, int(pixmap_to_draw_on.width() / 80))
                font.setPointSize(font_size)
                painter.setFont(font)
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(label) + 4
                text_height = metrics.height()

                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 255, 0, 180))
                bg_y = ymin - text_height if ymin - text_height > 0 else ymin
                painter.drawRect(xmin, bg_y, text_width, text_height)

                painter.setPen(QColor(0, 0, 0))
                painter.drawText(xmin + 2, bg_y + metrics.ascent(), label)

        painter.end()
        print("Finished drawing bounding boxes (if any).")
        return pixmap_to_draw_on

    def clearImage(self):
        print("Clearing image display.")
        self.original_pixmap = None
        self.current_pixmap = None
        self.image_label.clear()
        self.image_label.setText("No image selected")
        if self.analyze_button:
             self.analyze_button.setEnabled(False)

    def _update_display(self):
        """Scales and sets the current pixmap on the label."""
        if not self.current_pixmap or self.current_pixmap.isNull():
            print("Update display skipped: current pixmap is invalid.")
            if self.image_label.text() != "No image selected" and "Error" not in self.image_label.text():
                 self.image_label.clear()
                 self.image_label.setText("No image selected")
            return

        try:
             target_size = self.image_label.size()
             scaled_pixmap = self.current_pixmap.scaled(
                 target_size,
                 Qt.KeepAspectRatio,
                 Qt.SmoothTransformation
             )
             self.image_label.setPixmap(scaled_pixmap)
        except Exception as e:
             print(f"Error during _update_display: {e}")
             traceback.print_exc()
             self.image_label.setText("Error updating display")


    def resizeEvent(self, event):
        """Handles widget resize events to rescale the displayed image."""
        super().resizeEvent(event)
        if self.current_pixmap:
             self._update_display()