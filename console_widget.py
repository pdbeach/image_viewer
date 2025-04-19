# console_widget.py
from PyQt5.QtWidgets import QTextEdit

class ConsoleWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(150) # Keep height restriction

    def logMessage(self, message):
        self.append(message)
        # Scroll to bottom
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )