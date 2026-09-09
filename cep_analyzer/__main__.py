"""
Entry point for CEP Target Analyzer when run as a module or packaged as EXE.
This allows running with: python -m cep_analyzer
"""

import sys
from PySide6 import QtWidgets, QtGui, QtCore

# When frozen as EXE, use absolute imports
if getattr(sys, 'frozen', False):
    from cep_analyzer.ui_mainwindow import MainWindow
else:
    from .ui_mainwindow import MainWindow

def setup_dark_palette():
    """Set up Windows 11-style dark palette for the entire application."""
    palette = QtGui.QPalette()
    
    # Windows 11 dark theme colors
    dark_bg = QtGui.QColor(32, 32, 32)          # #202020 - Main background
    darker_bg = QtGui.QColor(24, 24, 24)        # #181818 - Darker areas
    light_bg = QtGui.QColor(45, 45, 45)         # #2d2d2d - Lighter areas (hover)
    text_color = QtGui.QColor(255, 255, 255)    # #ffffff - Primary text
    disabled_text = QtGui.QColor(128, 128, 128) # #808080 - Disabled text
    highlight = QtGui.QColor(0, 120, 215)       # #0078d7 - Windows 11 accent blue
    highlight_text = QtGui.QColor(255, 255, 255)
    
    # Set all palette colors
    palette.setColor(QtGui.QPalette.Window, dark_bg)
    palette.setColor(QtGui.QPalette.WindowText, text_color)
    palette.setColor(QtGui.QPalette.Base, darker_bg)
    palette.setColor(QtGui.QPalette.AlternateBase, dark_bg)
    palette.setColor(QtGui.QPalette.ToolTipBase, light_bg)
    palette.setColor(QtGui.QPalette.ToolTipText, text_color)
    palette.setColor(QtGui.QPalette.Text, text_color)
    palette.setColor(QtGui.QPalette.Button, dark_bg)
    palette.setColor(QtGui.QPalette.ButtonText, text_color)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, highlight)
    palette.setColor(QtGui.QPalette.Highlight, highlight)
    palette.setColor(QtGui.QPalette.HighlightedText, highlight_text)
    
    # Disabled colors
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, disabled_text)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, disabled_text)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, disabled_text)
    
    return palette

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("CEP Target Analyzer")
    
    # Set Fusion style for better dark theme support
    QtWidgets.QApplication.setStyle("Fusion")
    
    # Apply Windows 11-style dark palette to entire application
    app.setPalette(setup_dark_palette())
    
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
