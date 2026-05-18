import sys
sys.path.insert(0, '.')

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def run() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("GUI Language Processor Editor")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
