
from __future__ import annotations
import sys
from PySide6 import QtWidgets
from .ui_mainwindow import MainWindow

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("CEP Target Analyzer")
    QtWidgets.QApplication.setStyle("Fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
