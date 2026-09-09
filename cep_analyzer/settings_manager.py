"""
Settings Manager for CEP Target Analyzer
Handles persistent application settings including window geometry, theme, and language.
"""

from __future__ import annotations
from typing import Optional, Tuple
from PySide6 import QtCore, QtWidgets

APP_ORG = "BenjiSoft"
APP_NAME = "CEPTargetAnalyzer"


class SettingsManager:
    """Manages application settings with QSettings backend."""
    
    def __init__(self):
        self.settings = QtCore.QSettings(APP_ORG, APP_NAME)
    
    # Language settings
    def get_language(self) -> str:
        """Get saved language preference. Defaults to 'en'."""
        return self.settings.value("language", "en", type=str)
    
    def set_language(self, lang: str):
        """Save language preference."""
        self.settings.setValue("language", lang)
        self.settings.sync()
    
    # Theme settings
    def get_theme(self) -> str:
        """Get saved theme preference. Defaults to 'light'."""
        return self.settings.value("theme", "light", type=str)
    
    def set_theme(self, theme: str):
        """Save theme preference."""
        self.settings.setValue("theme", theme)
        self.settings.sync()
    
    # Window geometry
    def get_window_geometry(self) -> Optional[QtCore.QByteArray]:
        """Get saved window geometry."""
        geo = self.settings.value("geometry")
        return geo if geo else None
    
    def set_window_geometry(self, geometry: QtCore.QByteArray):
        """Save window geometry."""
        self.settings.setValue("geometry", geometry)
        self.settings.sync()
    
    def get_window_state(self) -> Optional[QtCore.QByteArray]:
        """Get saved window state (toolbars, docks, etc.)."""
        state = self.settings.value("windowState")
        return state if state else None
    
    def set_window_state(self, state: QtCore.QByteArray):
        """Save window state."""
        self.settings.setValue("windowState", state)
        self.settings.sync()
    
    # Window position and size
    def get_window_position(self) -> Optional[Tuple[int, int]]:
        """Get saved window position as (x, y) tuple."""
        x = self.settings.value("window/x", type=int)
        y = self.settings.value("window/y", type=int)
        if x is not None and y is not None:
            return (x, y)
        return None
    
    def set_window_position(self, x: int, y: int):
        """Save window position."""
        self.settings.setValue("window/x", x)
        self.settings.setValue("window/y", y)
        self.settings.sync()
    
    def get_window_size(self) -> Optional[Tuple[int, int]]:
        """Get saved window size as (width, height) tuple."""
        width = self.settings.value("window/width", type=int)
        height = self.settings.value("window/height", type=int)
        if width is not None and height is not None:
            return (width, height)
        return None
    
    def set_window_size(self, width: int, height: int):
        """Save window size."""
        self.settings.setValue("window/width", width)
        self.settings.setValue("window/height", height)
        self.settings.sync()
    
    # Splitter state
    def get_splitter_state(self) -> Optional[QtCore.QByteArray]:
        """Get saved splitter state."""
        state = self.settings.value("splitter/state")
        return state if state else None
    
    def set_splitter_state(self, state: QtCore.QByteArray):
        """Save splitter state."""
        self.settings.setValue("splitter/state", state)
        self.settings.sync()
    
    # Last opened file
    def get_last_file_path(self) -> Optional[str]:
        """Get last opened file path."""
        path = self.settings.value("lastFile/path", type=str)
        return path if path else None
    
    def set_last_file_path(self, path: str):
        """Save last opened file path."""
        self.settings.setValue("lastFile/path", path)
        self.settings.sync()
    
    # Recent files
    def get_recent_files(self, max_count: int = 10) -> list[str]:
        """Get list of recent file paths."""
        size = self.settings.beginReadArray("recentFiles")
        files = []
        for i in range(min(size, max_count)):
            self.settings.setArrayIndex(i)
            path = self.settings.value("path", type=str)
            if path:
                files.append(path)
        self.settings.endArray()
        return files
    
    def add_recent_file(self, path: str, max_count: int = 10):
        """Add a file to recent files list."""
        recent = self.get_recent_files(max_count)
        
        # Remove if already exists
        if path in recent:
            recent.remove(path)
        
        # Add to front
        recent.insert(0, path)
        
        # Limit to max_count
        recent = recent[:max_count]
        
        # Save
        self.settings.beginWriteArray("recentFiles")
        for i, file_path in enumerate(recent):
            self.settings.setArrayIndex(i)
            self.settings.setValue("path", file_path)
        self.settings.endArray()
        self.settings.sync()
    
    def clear_recent_files(self):
        """Clear recent files list."""
        self.settings.remove("recentFiles")
        self.settings.sync()
    
    # Marker color preferences
    def get_point_color(self) -> str:
        """Get shot point marker color. Defaults to red (#ff5555)."""
        return self.settings.value("markers/pointColor", "#ff5555", type=str)
    
    def set_point_color(self, color: str):
        """Save shot point marker color."""
        self.settings.setValue("markers/pointColor", color)
        self.settings.sync()
    
    def get_origin_color(self) -> str:
        """Get origin marker color. Defaults to green (#50be78)."""
        return self.settings.value("markers/originColor", "#50be78", type=str)
    
    def set_origin_color(self, color: str):
        """Save origin marker color."""
        self.settings.setValue("markers/originColor", color)
        self.settings.sync()
    
    def get_scale_color(self) -> str:
        """Get scale line color. Defaults to blue (#82aaff)."""
        return self.settings.value("markers/scaleColor", "#82aaff", type=str)
    
    def set_scale_color(self, color: str):
        """Save scale line color."""
        self.settings.setValue("markers/scaleColor", color)
        self.settings.sync()
    
    # Utility methods
    def sync(self):
        """Force sync settings to disk."""
        self.settings.sync()
    
    def clear_all(self):
        """Clear all settings (use with caution)."""
        self.settings.clear()
        self.settings.sync()

    # Shortcuts panel visibility
    def get_shortcuts_expanded(self) -> bool:
        """Get shortcuts panel expanded state. Defaults to True (expanded on first launch)."""
        return self.settings.value("shortcuts_expanded", True, type=bool)
    
    def set_shortcuts_expanded(self, expanded: bool):
        """Save shortcuts panel expanded state."""
        self.settings.setValue("shortcuts_expanded", expanded)
        self.settings.sync()
