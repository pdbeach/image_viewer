#!/usr/bin/env python3
# main.py
import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle
import PIL

# Import the main window class
from main_window import ImageViewer

def main():
    app = QApplication(sys.argv)
    
    # Apply dark style (optional)
    try:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    except Exception as e:
        print(f"Could not load dark style: {e}. Using default.")

    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()