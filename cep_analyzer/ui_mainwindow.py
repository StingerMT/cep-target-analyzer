
from __future__ import annotations
from typing import Optional, List
import sys
import os
from PySide6 import QtCore, QtGui, QtWidgets

try:
    import qdarktheme
    HAVE_QDARK = True
except Exception:
    HAVE_QDARK = False

from .image_viewer import ImageView
from .dialogs import HoleDetectDialog, PointReviewDialog, ResultsDialog, RotationDialog
from . import detection
from .analysis import compute_metrics, export_csv
from .i18n import Translator
from .settings_manager import SettingsManager

APP_ORG = "BenjiSoft"
APP_NAME = "CEPTargetAnalyzer"

class MainWindow(QtWidgets.QMainWindow):
    COMPLETED_QSS = (
        "QPushButton{background-color:#2e7d32;color:white;border-radius:6px;padding:6px;}"
        "QPushButton:hover{background-color:#388e3c;}"
    )
    ACTIVE_QSS = (
        "QPushButton{background-color:#1976d2;color:white;border-radius:6px;padding:6px;}"
        "QPushButton:hover{background-color:#1e88e5;}"
    )

    def __init__(self):
        super().__init__()
        self._skip_exit_confirmation = False  # Flag to skip exit confirmation during restart
        
        # Force dark mode
        if HAVE_QDARK:
            qdarktheme.setup_theme("dark")
        
        # Initialize settings manager
        self.settings_mgr = SettingsManager()
        
        # Initialize translator
        saved_lang = self.settings_mgr.get_language()
        self.translator = Translator(saved_lang)
        
        self.setWindowTitle(self.translator.t("app.title"))
        
        # Fixed window size (Discord-style) - 70% of screen
        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()  # Use availableGeometry to account for taskbar
        width = int(screen.width() * 0.7)
        height = int(screen.height() * 0.7)
        self.resize(width, height)
        
        # Center window on screen (accounting for taskbar position)
        self.move(
            screen.x() + (screen.width() - width) // 2,
            screen.y() + (screen.height() - height) // 2
        )
        
        # Set layout direction based on language
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)

        self._build_menu()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.setCentralWidget(splitter)

        # Create scroll area for left panel to handle any screen size
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setFixedWidth(340)  # Increased from 320 to prevent shortcuts overlap
        
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)  # Reduced from 12 for compactness

        self.title = QtWidgets.QLabel(f"<h2>{self.translator.t('title.main')}</h2>")
        self.subtitle = QtWidgets.QLabel(self.translator.t("subtitle.workflow"))
        self.subtitle.setWordWrap(True)

        # Removed mode_banner - using status bar instead

        self.btn_open = QtWidgets.QPushButton(self.translator.t("btn.open"))
        self.btn_open.clicked.connect(self.on_open)

        self.btn_set_scale = QtWidgets.QPushButton(self.translator.t("btn.setscale"))
        self.btn_set_scale.clicked.connect(self._enter_set_scale)

        self.btn_set_origin = QtWidgets.QPushButton(self.translator.t("btn.setorigin"))
        self.btn_set_origin.clicked.connect(self._enter_set_origin)

        self.btn_add_points = QtWidgets.QPushButton(self.translator.t("btn.addpoints"))
        self.btn_add_points.setCheckable(True)
        self.btn_add_points.toggled.connect(self.on_add_points_toggle)

        # Rotation control
        self.btn_rotate = QtWidgets.QPushButton(self.translator.t("btn.rotate"))
        self.btn_rotate.clicked.connect(self.on_rotate_image)
        
        controls_row = QtWidgets.QHBoxLayout()
        self.btn_undo = QtWidgets.QPushButton(self.translator.t("btn.undo"))
        self.btn_clear = QtWidgets.QPushButton(self.translator.t("btn.clear"))
        self.btn_fit = QtWidgets.QPushButton(self.translator.t("btn.fit"))
        self.btn_fit.clicked.connect(self._fit_action)
        self.btn_undo.clicked.connect(self.on_undo)
        self.btn_clear.clicked.connect(self.on_clear)
        controls_row.addWidget(self.btn_undo); controls_row.addWidget(self.btn_clear); controls_row.addWidget(self.btn_fit)

        # Distance input for mrad calculations (before compute)
        distance_group = QtWidgets.QGroupBox(self.translator.t("group.distance"))
        distance_layout = QtWidgets.QHBoxLayout()
        distance_layout.setContentsMargins(8, 10, 8, 10)  # Compact padding
        distance_layout.setSpacing(8)  # Compact spacing
        distance_label = QtWidgets.QLabel(self.translator.t("label.distance"))
        self.distance_input = QtWidgets.QDoubleSpinBox()
        self.distance_input.setRange(1.0, 10000.0)
        self.distance_input.setValue(100.0)  # Default 100m
        self.distance_input.setDecimals(1)
        self.distance_input.setSuffix(" m")
        distance_layout.addWidget(distance_label)
        distance_layout.addWidget(self.distance_input)
        distance_layout.addStretch()
        distance_group.setLayout(distance_layout)

        self.btn_compute = QtWidgets.QPushButton(self.translator.t("btn.compute"))
        self.btn_compute.clicked.connect(self.compute_metrics_action)

        self.detect_group = QtWidgets.QGroupBox(self.translator.t("group.detection"))
        detect_layout = QtWidgets.QVBoxLayout()
        self.btn_detect = QtWidgets.QPushButton(self.translator.t("btn.detect"))
        self.btn_detect.clicked.connect(self.detect_holes)
        detect_layout.addWidget(self.btn_detect)
        self.detect_group.setLayout(detect_layout)

        # Plot and Export buttons
        self.btn_plot = QtWidgets.QPushButton(self.translator.t("btn.plot"))
        self.btn_plot.setEnabled(False)
        self.btn_plot.clicked.connect(self.show_result_plot_action)
        
        export_row = QtWidgets.QHBoxLayout()
        self.btn_export_csv = QtWidgets.QPushButton(self.translator.t("btn.export"))
        self.btn_export_csv.clicked.connect(self.export_csv_action)
        export_row.addStretch(1); export_row.addWidget(self.btn_export_csv)

        # Progress indicator (minimal, bottom of left panel)
        self.progress_label = QtWidgets.QLabel("")
        self.progress_label.setStyleSheet("color: palette(mid); font-size: 10px; font-style: italic;")
        self.progress_label.setAlignment(QtCore.Qt.AlignLeft if not self.translator.is_rtl() else QtCore.Qt.AlignRight)
        self.progress_label.setVisible(False)

        # Build left panel layout
        left_layout.addWidget(self.title)
        left_layout.addWidget(self.subtitle)
        left_layout.addWidget(self.btn_open)
        left_layout.addWidget(self.btn_rotate)
        left_layout.addWidget(self.btn_set_scale)
        left_layout.addWidget(self.btn_set_origin)
        left_layout.addWidget(self.btn_add_points)
        left_layout.addLayout(controls_row)
        #left_layout.addWidget(self.detect_group)
        left_layout.addSpacing(5)  # Compact space before distance group
        left_layout.addWidget(distance_group)  # Distance input before compute
        left_layout.addSpacing(5)  # Compact space after distance group
        left_layout.addWidget(self.btn_compute)
        left_layout.addWidget(self.btn_plot)  # Plot button
        left_layout.addLayout(export_row)
        
        # Shortcuts guide - simple, unobtrusive text
        shortcuts_container = QtWidgets.QWidget()
        self._shortcuts_container = shortcuts_container  # Store reference for opacity control
        shortcuts_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        shortcuts_layout = QtWidgets.QVBoxLayout(shortcuts_container)
        shortcuts_layout.setSpacing(6)  # More spacing between lines
        shortcuts_layout.setContentsMargins(10, 8, 10, 8)  # Equal margins, no extra right padding
        
        # Collapsible title - clickable to show/hide shortcuts
        # Get saved state (default to True = expanded on first launch)
        self._shortcuts_expanded = self.settings_mgr.get_shortcuts_expanded()
        
        # Create title button with proper sizing
        title_button = QtWidgets.QPushButton()
        title_button.setFlat(True)
        title_button.setCursor(QtCore.Qt.PointingHandCursor)
        title_button.clicked.connect(self._toggle_shortcuts)
        title_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
        # Create horizontal layout for arrow and title
        title_hlayout = QtWidgets.QHBoxLayout(title_button)
        title_hlayout.setContentsMargins(4, 4, 4, 4)
        title_hlayout.setSpacing(6)
        
        # Arrow indicator - different for RTL
        if self.translator.is_rtl():
            arrow_expanded = "▼"
            arrow_collapsed = "◀"  # Points left in RTL
        else:
            arrow_expanded = "▼"
            arrow_collapsed = "▶"  # Points right in LTR
        
        self._shortcuts_arrow = QtWidgets.QLabel(arrow_expanded if self._shortcuts_expanded else arrow_collapsed)
        self._shortcuts_arrow.setStyleSheet("QLabel { color: #cccccc; font-size: 10px; }")
        
        title_label = QtWidgets.QLabel(self.translator.t("shortcuts.title"))
        title_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        
        # Build title layout - right-aligned for RTL, left-aligned for LTR
        if self.translator.is_rtl():
            title_hlayout.addWidget(self._shortcuts_arrow)
            title_hlayout.addWidget(title_label)
            title_hlayout.addStretch()
        else:
            title_hlayout.addWidget(self._shortcuts_arrow)
            title_hlayout.addWidget(title_label)
            title_hlayout.addStretch()
        
        # Store arrow symbols for toggle
        self._arrow_expanded = arrow_expanded
        self._arrow_collapsed = arrow_collapsed
        
        # Style the button
        title_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                text-align: left;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 3px;
            }
        """)
        
        shortcuts_layout.addWidget(title_button)
        
        # Helper function to create keyboard badge
        def create_kbd_label(text):
            """Create a styled keyboard key badge as a QLabel."""
            label = QtWidgets.QLabel(text)
            label.setStyleSheet("""
                QLabel {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-family: monospace;
                    font-size: 11px;
                    border: 1px solid #555;
                    min-height: 20px;
                }
            """)
            label.setAlignment(QtCore.Qt.AlignCenter)
            return label
        
        # Helper function to load icon from assets folder
        def load_icon(filename, size=16):
            """Load an icon from the assets folder."""
            # Handle PyInstaller bundled environment
            if getattr(sys, 'frozen', False):
                # Running in PyInstaller bundle
                base_path = sys._MEIPASS
            else:
                # Running in normal Python environment
                base_path = os.path.dirname(os.path.dirname(__file__))
            
            assets_path = os.path.join(base_path, "assets", filename)
            if os.path.exists(assets_path):
                pixmap = QtGui.QPixmap(assets_path)
                if not pixmap.isNull():
                    return pixmap.scaled(size, size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            return None
        
        # Create shortcuts with styled badges and icons using grid layout
        # For RTL, reverse the order so they read right-to-left
        if self.translator.is_rtl():
            shortcuts_items = [
                # (description, [widgets]) - RTL order (reversed)
                (self.translator.t("shortcuts.zoom"), 
                 ["scroll_icon", QtWidgets.QLabel("+"), create_kbd_label("Ctrl")]),
                
                (self.translator.t("shortcuts.pan"),
                 ["mmb_icon", QtWidgets.QLabel("/"), "leftclick_icon", QtWidgets.QLabel("+"), create_kbd_label("Space")]),
                
                (self.translator.t("shortcuts.fit"),
                 [create_kbd_label("F"), QtWidgets.QLabel("+"), create_kbd_label("Ctrl")]),
                
                (self.translator.t("shortcuts.undo"),
                 ["rightclick_icon"])
            ]
        else:
            shortcuts_items = [
                # (description, [widgets]) - LTR order (normal)
                (self.translator.t("shortcuts.zoom"), 
                 [create_kbd_label("Ctrl"), QtWidgets.QLabel("+"), "scroll_icon"]),
                
                (self.translator.t("shortcuts.pan"),
                 [create_kbd_label("Space"), QtWidgets.QLabel("+"), "leftclick_icon", QtWidgets.QLabel("/"), "mmb_icon"]),
                
                (self.translator.t("shortcuts.fit"),
                 [create_kbd_label("Ctrl"), QtWidgets.QLabel("+"), create_kbd_label("F")]),
                
                (self.translator.t("shortcuts.undo"),
                 ["rightclick_icon"])
            ]
        
        # Use grid layout for table-like alignment
        grid_container = QtWidgets.QWidget()
        # CRITICAL: Force LTR layout so columns work in natural order (0=left, 2=right)
        grid_container.setLayoutDirection(QtCore.Qt.LeftToRight)
        grid_layout = QtWidgets.QGridLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(6)
        
        is_rtl = self.translator.is_rtl()
        
        if is_rtl:
            # RTL: 3 columns - [stretch][keys][description]
            grid_layout.setColumnStretch(0, 1)  # Stretch column on left
            grid_layout.setColumnStretch(1, 0)  # Keys column - no stretch
            grid_layout.setColumnStretch(2, 0)  # Description column - no stretch
        else:
            # LTR: 3 columns - [description][keys][stretch]
            grid_layout.setColumnStretch(0, 0)  # Description column - no stretch
            grid_layout.setColumnStretch(1, 0)  # Keys column - no stretch
            grid_layout.setColumnStretch(2, 1)  # Stretch column on right
        
        for row, (description, widgets_spec) in enumerate(shortcuts_items):
            # Description label
            desc_label = QtWidgets.QLabel(description)
            desc_label.setStyleSheet("QLabel { color: #aaaaaa; font-size: 11px; }")
            desc_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            
            # Keys container - right-aligned
            keys_container = QtWidgets.QWidget()
            keys_layout = QtWidgets.QHBoxLayout(keys_container)
            keys_layout.setContentsMargins(0, 0, 0, 0)
            keys_layout.setSpacing(4)
            if self.translator.is_rtl():
                keys_layout.addStretch()  # Push keys to the right
            
            # Build keys widgets
            for item in widgets_spec:
                if isinstance(item, str):
                    if item == "scroll_icon":
                        # Try to load scroll icon (try 48x48 first, then 96x96)
                        icon_pixmap = load_icon("scroll icon 48x48.png", 24) or load_icon("scroll icon 96x96.png", 16)
                        if icon_pixmap:
                            icon_label = QtWidgets.QLabel()
                            keys_layout.addWidget(icon_label)
                            icon_label.setPixmap(icon_pixmap)
                            
                        else:
                            keys_layout.addWidget(QtWidgets.QLabel("🖱"))
                    elif item == "leftclick_icon":
                        # Try to load left-click icon (try 50x50 first, then 100x100)
                        icon_pixmap = load_icon("left click 50x50.png", 24) or load_icon("left click 100x100.png", 16)
                        if icon_pixmap:
                            icon_label = QtWidgets.QLabel()
                            icon_label.setPixmap(icon_pixmap)
                            keys_layout.addWidget(icon_label)
                        else:
                            # Fallback to text
                            keys_layout.addWidget(QtWidgets.QLabel("🖱️"))
                    elif item == "mmb_icon":
                        # Try to load middle mouse button icon
                        icon_pixmap = load_icon("mmb icon.png", 24)
                        if icon_pixmap:
                            icon_label = QtWidgets.QLabel()
                            icon_label.setPixmap(icon_pixmap)
                            keys_layout.addWidget(icon_label)
                        else:
                            keys_layout.addWidget(create_kbd_label("MMB"))
                    elif item == "rightclick_icon":
                        # Try to load right-click icon (try 48x48 first, then 96x96)
                        icon_pixmap = load_icon("right click 48x48.png", 24) or load_icon("right click 96x96.png", 16)
                        if icon_pixmap:
                            icon_label = QtWidgets.QLabel()
                            icon_label.setPixmap(icon_pixmap)
                            keys_layout.addWidget(icon_label)
                        else:
                            text = "לחיצה ימנית" if self.translator.is_rtl() else "Right-click"
                            keys_layout.addWidget(QtWidgets.QLabel(text))
                    else:
                        # Regular text
                        label = QtWidgets.QLabel(item)
                        label.setStyleSheet("QLabel { color: #999999; }")
                        keys_layout.addWidget(label)
                elif isinstance(item, QtWidgets.QWidget):
                    keys_layout.addWidget(item)
            
            # Add to grid layout
            if is_rtl:
                # RTL: [stretch:col0][keys:col1][description:col2]
                # Description on the right (column 2), keys on the left (column 1)
                grid_layout.addWidget(keys_container, row, 1, QtCore.Qt.AlignRight)
                grid_layout.addWidget(desc_label, row, 2, QtCore.Qt.AlignRight)
            else:
                # LTR: [description:col0][keys:col1][stretch:col2]
                # Description on the left (column 0), keys on the left too (column 1)
                grid_layout.addWidget(desc_label, row, 0, QtCore.Qt.AlignLeft)
                grid_layout.addWidget(keys_container, row, 1, QtCore.Qt.AlignLeft)
        
        # Store grid container for collapse/expand
        self._shortcuts_grid = grid_container
        self._shortcuts_grid.setVisible(self._shortcuts_expanded)
        shortcuts_layout.addWidget(grid_container)
        
        # Enable mouse tracking for hover detection
        shortcuts_container.setMouseTracking(True)
        shortcuts_container.enterEvent = lambda e: self._reset_shortcuts_fade_timer()
        
        left_layout.addWidget(shortcuts_container)
        left_layout.addStretch(1)  # Push everything to top
        left_layout.addWidget(self.progress_label)  # Progress at bottom
        
        # Start initial fade timer
        QtCore.QTimer.singleShot(100, self._reset_shortcuts_fade_timer)

        # Set the left widget into the scroll area
        scroll_area.setWidget(left)
        
        self.image_viewer = ImageView(translator=self.translator)
        self.image_viewer.setMinimumWidth(200)  # Allow image viewer to shrink
        
        # Apply saved marker colors
        saved_colors = {
            "point": self.settings_mgr.get_point_color(),
            "origin": self.settings_mgr.get_origin_color(),
            "scale": self.settings_mgr.get_scale_color()
        }
        self.image_viewer.update_marker_colors(saved_colors)
        
        splitter.addWidget(scroll_area); splitter.addWidget(self.image_viewer)
        splitter.setStretchFactor(0, 0); splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)  # Don't allow left panel to collapse
        splitter.setCollapsible(1, True)  # Allow image viewer to shrink

        self.image_viewer.scaleSet.connect(self.on_scale_set)
        self.image_viewer.originSet.connect(self.on_origin_set)
        self.image_viewer.originCleared.connect(self.on_origin_cleared)
        self.image_viewer.pointsChanged.connect(self.on_points_changed)

        # Apply polished styling
        self._apply_polish_styling()
        
        # Fade-in animation
        self._setup_fade_in_animation()

        # No window state restoration - always use fixed size/position
        # Dark mode is forced in __init__
        
        # Configure status bar with custom label for proper RTL support
        self.statusBar().setSizeGripEnabled(False)
        
        # Create custom label for status messages
        self._status_label = QtWidgets.QLabel()
        
        # Add to status bar FIRST
        self.statusBar().addWidget(self._status_label, 1)
        
        # CRITICAL FIX: In RTL layout mode, the alignment is LOGICAL not VISUAL
        # So AlignLeft in RTL mode actually appears on the visual RIGHT side!
        if self.translator.is_rtl():
            # For RTL layout, use AlignLeft (which appears on visual right)
            self._status_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self._status_label.setContentsMargins(10, 0, 0, 0)
        else:
            # For LTR, use AlignLeft (which appears on visual left)
            self._status_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self._status_label.setContentsMargins(10, 0, 0, 0)
        
        # Add tooltips to buttons
        self._add_tooltips()
        
        self.update_ui_state()

    def _toggle_shortcuts(self):
        """Toggle shortcuts panel visibility."""
        self._shortcuts_expanded = not self._shortcuts_expanded
        self._shortcuts_grid.setVisible(self._shortcuts_expanded)
        self._shortcuts_arrow.setText(self._arrow_expanded if self._shortcuts_expanded else self._arrow_collapsed)
        # Save state
        self.settings_mgr.set_shortcuts_expanded(self._shortcuts_expanded)
        # Reset fade timer
        self._reset_shortcuts_fade_timer()
    
    def _reset_shortcuts_fade_timer(self):
        """Reset the auto-fade timer for shortcuts panel."""
        # Cancel existing timer if any
        if hasattr(self, '_shortcuts_fade_timer'):
            self._shortcuts_fade_timer.stop()
        
        # Stop any ongoing fade animation
        if hasattr(self, '_shortcuts_fade_animation'):
            self._shortcuts_fade_animation.stop()
        
        # Make shortcuts fully visible
        self._set_shortcuts_opacity(1.0)
        
        # Start new timer (5 seconds is standard for non-critical UI)
        self._shortcuts_fade_timer = QtCore.QTimer(self)
        self._shortcuts_fade_timer.setSingleShot(True)
        self._shortcuts_fade_timer.timeout.connect(self._fade_shortcuts)
        self._shortcuts_fade_timer.start(5000)  # 5 seconds
    
    def _fade_shortcuts(self):
        """Fade shortcuts panel to be less obtrusive."""
        # Animate opacity change smoothly
        if hasattr(self, '_shortcuts_opacity_effect'):
            self._shortcuts_fade_animation = QtCore.QPropertyAnimation(self._shortcuts_opacity_effect, b"opacity")
            self._shortcuts_fade_animation.setDuration(1000)  # 500ms smooth fade
            self._shortcuts_fade_animation.setStartValue(1.0)
            self._shortcuts_fade_animation.setEndValue(0.45)  # 35% opacity
            self._shortcuts_fade_animation.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
            self._shortcuts_fade_animation.start()
    
    def _set_shortcuts_opacity(self, opacity: float):
        """Set opacity of shortcuts container."""
        if hasattr(self, '_shortcuts_container'):
            if not hasattr(self, '_shortcuts_opacity_effect'):
                self._shortcuts_opacity_effect = QtWidgets.QGraphicsOpacityEffect()
                self._shortcuts_container.setGraphicsEffect(self._shortcuts_opacity_effect)
            self._shortcuts_opacity_effect.setOpacity(opacity)
    
    # Menu
    def _build_menu(self):
        # Settings menu with Language and Preferences
        self.settings_menu = self.menuBar().addMenu(self.translator.t("menu.settings"))
        
        # Language submenu
        self.lang_menu = self.settings_menu.addMenu(self.translator.t("menu.language"))
        lang_group = QtGui.QActionGroup(self)
        lang_group.setExclusive(True)
        
        self.act_lang_en = QtGui.QAction(self.translator.t("lang.en"), self, checkable=True)
        self.act_lang_he = QtGui.QAction(self.translator.t("lang.he"), self, checkable=True)
        
        # Set checked state based on current language
        if self.translator.lang == "he":
            self.act_lang_he.setChecked(True)
        else:
            self.act_lang_en.setChecked(True)
        
        lang_group.addAction(self.act_lang_en)
        lang_group.addAction(self.act_lang_he)
        
        self.act_lang_en.triggered.connect(lambda: self.change_language("en"))
        self.act_lang_he.triggered.connect(lambda: self.change_language("he"))
        
        self.lang_menu.addActions(lang_group.actions())
        
        # Preferences action
        self.settings_menu.addSeparator()
        self.act_preferences = QtGui.QAction(self.translator.t("menu.preferences"), self)
        self.act_preferences.triggered.connect(self.open_preferences)
        self.settings_menu.addAction(self.act_preferences)

    def change_language(self, lang: str):
        """Change language and prompt for restart."""
        if lang == self.translator.lang:
            return
        
        # Save the new theme preference
        self.settings_mgr.set_theme(mode)
        
        # Apply theme immediately
        self.apply_theme(mode)
        
        # Show restart dialog
        theme_names = {
            "system": self.translator.t("action.theme.system"),
            "light": self.translator.t("action.theme.light"),
            "dark": self.translator.t("action.theme.dark")
        }
        theme_name = theme_names.get(mode, mode)
        
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(self.translator.t("dialog.restart.title"))
        msg_box.setText(self.translator.t("dialog.restart.message"))
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        
        restart_btn = msg_box.addButton(
            self.translator.t("dialog.restart.restart"),
            QtWidgets.QMessageBox.AcceptRole
        )
        later_btn = msg_box.addButton(
            self.translator.t("dialog.restart.later"),
            QtWidgets.QMessageBox.RejectRole
        )
        
        msg_box.exec()
        
        if msg_box.clickedButton() == restart_btn:
            self.restart_application()

    # UI helpers
    def change_language(self, lang: str):
        """Change the application language."""
        if lang == self.translator.lang:
            return
        
        # Save the new language preference
        self.settings_mgr.set_language(lang)
        
        # Show close application dialog
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(self.translator.t("dialog.restart.title"))
        msg_box.setText(self.translator.t("dialog.restart.message"))
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        
        close_btn = msg_box.addButton(
            self.translator.t("dialog.restart.close"),
            QtWidgets.QMessageBox.AcceptRole
        )
        
        msg_box.exec()
        
        # Close the application
        QtWidgets.QApplication.instance().quit()
    
    def open_preferences(self):
        """Open preferences dialog."""
        from .dialogs import PreferencesDialog
        dlg = PreferencesDialog(self, self.translator, self.settings_mgr)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            colors = dlg.get_colors()
            # Save colors
            self.settings_mgr.set_point_color(colors["point"])
            self.settings_mgr.set_origin_color(colors["origin"])
            self.settings_mgr.set_scale_color(colors["scale"])
            # Apply to image viewer
            self.image_viewer.update_marker_colors(colors)
            self.image_viewer.viewport().update()
    
    def _add_tooltips(self):
        """Add helpful tooltips to all buttons."""
        self.btn_open.setToolTip(self.translator.t("tooltip.open"))
        self.btn_rotate.setToolTip(self.translator.t("tooltip.rotate"))
        self.btn_set_scale.setToolTip(self.translator.t("tooltip.setscale"))
        self.btn_set_origin.setToolTip(self.translator.t("tooltip.setorigin"))
        self.btn_add_points.setToolTip(self.translator.t("tooltip.addpoints"))
        self.btn_undo.setToolTip(self.translator.t("tooltip.undo"))
        self.btn_clear.setToolTip(self.translator.t("tooltip.clear"))
        self.btn_fit.setToolTip(self.translator.t("tooltip.fit"))
        self.btn_compute.setToolTip(self.translator.t("tooltip.compute"))
        self.btn_plot.setToolTip(self.translator.t("tooltip.plot"))
        self.btn_export_csv.setToolTip(self.translator.t("tooltip.export"))
        self.distance_input.setToolTip(self.translator.t("tooltip.distance"))
    
    def _show_status_message(self, message: str, timeout: int = 0):
        """Show status message with proper RTL/LTR alignment."""
        if self._status_label is not None:
            self._status_label.setText(message)
            if timeout > 0:
                QtCore.QTimer.singleShot(timeout, lambda: self._status_label.setText(""))
        else:
            self.statusBar().showMessage(message, timeout)
    
    def _enter_set_scale(self):
        self.image_viewer.set_mode("set_scale")
        self._highlight_active(self.btn_set_scale)
        self._set_mode_banner(self.translator.t("banner.setscale"))
        self._show_status_message(self.translator.t("status.setscale"), 5000)

    def _enter_set_origin(self):
        self.image_viewer.set_mode("set_origin")
        self._highlight_active(self.btn_set_origin)
        self._set_mode_banner(self.translator.t("banner.setorigin"))
        self._show_status_message(self.translator.t("status.setorigin"), 5000)

    def _fit_action(self):
        self.image_viewer.fit_to_image()
    
    def on_rotate_image(self):
        """Open rotation dialog for fine-tuned angle adjustment."""
        if self.image_viewer.pixmap_item is None:
            return
        
        # Check if scale is already set
        if self.image_viewer.units_per_pixel is not None:
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.t("dialog.rotation.locked.title"),
                self.translator.t("dialog.rotation.locked.message")
            )
            return
        
        from .dialogs import RotationDialog
        current_angle = self.image_viewer._rotation_angle
        
        dlg = RotationDialog(current_angle, self, self.translator)
        
        # Connect for live preview
        dlg.angleChanged.connect(lambda angle: self.image_viewer.rotate_image_to_angle(angle))
        
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            # Angle already applied via live preview
            final_angle = dlg.get_angle()
            self._show_status_message(self.translator.t("status.image.rotated", final_angle), 2000)
        else:
            # User cancelled - restore original angle
            self.image_viewer.rotate_image_to_angle(current_angle)

    def _set_mode_banner(self, text: str):
        # Show mode in status bar instead of banner
        self._show_status_message(text)

    def _highlight_active(self, btn: QtWidgets.QPushButton):
        for b in (self.btn_set_scale, self.btn_set_origin, self.btn_add_points):
            b.setStyleSheet("")
        btn.setStyleSheet(self.ACTIVE_QSS)

    def _mark_completed(self, btn: QtWidgets.QPushButton):
        text = btn.text()
        if not text.endswith("✅"):
            btn.setText(text + " ✅")
        btn.setStyleSheet(self.COMPLETED_QSS)

    def _apply_polish_styling(self):
        """Apply polished styling with drop shadows - dark mode only."""
        # Always use dark mode styling
        button_style = """
            QPushButton {
                background-color: #424242;
                color: white;
                border: 1px solid #616161;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666666;
            }
        """
        
        # Group box styling - dark mode
        group_style = """
            QGroupBox {
                border: 2px solid #616161;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """
        
        # Apply to all buttons
        for btn in self.findChildren(QtWidgets.QPushButton):
            btn.setStyleSheet(button_style)
            # Add drop shadow effect
            shadow = QtWidgets.QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QtGui.QColor(0, 0, 0, 120))
            shadow.setOffset(0, 2)
            btn.setGraphicsEffect(shadow)
        
        # Apply to group boxes
        for group in self.findChildren(QtWidgets.QGroupBox):
            group.setStyleSheet(group_style)
    
    def _setup_fade_in_animation(self):
        """Setup fade-in animation for window."""
        self.setWindowOpacity(0.0)
        self.fade_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1500)  # 800ms - longer, more pronounced
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        QtCore.QTimer.singleShot(50, self.fade_animation.start)
    
    def _show_progress(self, message: str):
        """Show progress indicator with message."""
        self.progress_label.setText(message)
        self.progress_label.setVisible(True)
        QtWidgets.QApplication.processEvents()  # Force UI update
    
    def _hide_progress(self):
        """Hide progress indicator."""
        self.progress_label.setVisible(False)
    
    def update_ui_state(self):
        has_img = self.image_viewer.pixmap_item is not None
        has_scale = self.image_viewer.units_per_pixel is not None
        has_metrics = hasattr(self, '_last_metrics') and self._last_metrics is not None
        
        # Rotation button: enabled only when image loaded but scale not yet set
        self.btn_rotate.setEnabled(has_img and not has_scale)
        
        self.btn_set_scale.setEnabled(has_img)
        self.btn_set_origin.setEnabled(has_img)
        self.btn_add_points.setEnabled(has_img)
        self.btn_compute.setEnabled(has_img and has_scale and len(self.image_viewer.shots) >= 2)
        self.btn_plot.setEnabled(has_metrics)  # Enable plot after compute
        self.btn_export_csv.setEnabled(len(self.image_viewer.shots) >= 1)
        self.btn_detect.setEnabled(has_img)

        if not has_img:
            self._set_mode_banner(self.translator.t("banner.idle.noimage"))

    # Slots
    def on_add_points_toggle(self, checked: bool):
        self.image_viewer.set_mode("add_points" if checked else "idle")
        if checked:
            self._highlight_active(self.btn_add_points)
            self._set_mode_banner(self.translator.t("banner.addpoints"))
        else:
            self._set_mode_banner(self.translator.t("banner.idle"))
        self._show_status_message(self.translator.t("status.addpoints"), 4000)

    def _reset_all_state(self):
        """Reset all application state when loading new image."""
        # Clear metrics and calculations
        if hasattr(self, '_last_metrics'):
            self._last_metrics = None
        
        # Reset button states (remove green checkmarks)
        for btn in [self.btn_set_scale, self.btn_set_origin, self.btn_add_points, self.btn_compute]:
            text = btn.text()
            if text.endswith(" ✅"):
                btn.setText(text[:-2])  # Remove checkmark
            btn.setStyleSheet("")  # Reset to default style
        
        # Close any open result dialogs/plots
        # Find and close any MetricsDialog or ResultsDialog windows
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget != self and isinstance(widget, QtWidgets.QDialog):
                widget.close()
        
        # Reset image viewer state
        self.image_viewer.shots.clear()
        self.image_viewer.origin = None
        self.image_viewer.units_per_pixel = None
        self.image_viewer._last_scale_pts = None
        self.image_viewer._scale_temp_points.clear()
        
        # Reset mode
        self.image_viewer.set_mode("idle")
        self.image_viewer.viewport().update()
    
    def on_open(self):
        # Get last directory from settings
        last_path = self.settings_mgr.get_last_file_path()
        start_dir = os.path.dirname(last_path) if last_path else ""
        
        dlg = QtWidgets.QFileDialog(self, self.translator.t("btn.open"), start_dir, "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dlg.exec():
            path = dlg.selectedFiles()[0]
            
            # Reset everything before loading new image
            self._reset_all_state()
            
            self.image_viewer.load_image(path)
            self._current_image_path = path  # Store for output folder creation
            
            # Save to recent files
            self.settings_mgr.set_last_file_path(path)
            self.settings_mgr.add_recent_file(path)
            
            self._set_mode_banner(self.translator.t("banner.image.loaded"))
            self._show_status_message(self.translator.t("status.image.loaded"), 5000)
            self.update_ui_state()

    def on_scale_set(self, upp: float, unit: str):
        # Scale has been set successfully
        self._mark_completed(self.btn_set_scale)
        self.update_ui_state()
        self._set_mode_banner(self.translator.t("banner.scale.done"))
        self._show_status_message(self.translator.t("status.scale.set", upp, unit), 5000)
        self.update_ui_state()

    def on_origin_set(self, pt: QtCore.QPointF):
        self._mark_completed(self.btn_set_origin)
        self._set_mode_banner(self.translator.t("banner.origin.done"))
        self._show_status_message(self.translator.t("status.origin.set", pt.x(), pt.y()), 4000)
        self.update_ui_state()
    
    def on_origin_cleared(self):
        """Handle origin being cleared (right-click or undo)."""
        # Remove green checkmark from origin button
        text = self.btn_set_origin.text()
        if text.endswith(" ✅"):
            self.btn_set_origin.setText(text[:-2])
        self.btn_set_origin.setStyleSheet("")
        self._set_mode_banner(self.translator.t("banner.origin.cleared"))
        self._show_status_message(self.translator.t("status.origin.cleared"), 4000)
        self.update_ui_state()

    def on_points_changed(self):
        if len(self.image_viewer.shots) >= 2:
            self._mark_completed(self.btn_add_points)
        self.update_ui_state()

    def on_undo(self):
        # Undo last action - either remove last point or clear origin
        if self.image_viewer.shots:
            self.image_viewer.shots.pop()
            self.image_viewer.pointsChanged.emit()
            self.image_viewer.viewport().update()
        elif self.image_viewer.origin is not None:
            # If no points but origin exists, clear origin
            self.image_viewer.origin = None
            self.image_viewer.originCleared.emit()
            self.image_viewer.viewport().update()

    def on_clear(self):
        if self.image_viewer.shots:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle(self.translator.t("dialog.clear.title"))
            msg_box.setText(self.translator.t("dialog.clear.message"))
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            
            yes_btn = msg_box.addButton(
                self.translator.t("btn.yes"),
                QtWidgets.QMessageBox.YesRole
            )
            no_btn = msg_box.addButton(
                self.translator.t("btn.no"),
                QtWidgets.QMessageBox.NoRole
            )
            
            msg_box.exec()
            
            if msg_box.clickedButton() == yes_btn:
                self.image_viewer.shots.clear()
                self.image_viewer.pointsChanged.emit()
                self.image_viewer.viewport().update()

    def compute_metrics_action(self):
        # Check all prerequisites
        if self.image_viewer.units_per_pixel is None:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.compute.title"),
                self.translator.t("dialog.compute.need_scale")
            )
            return
        
        if not self.image_viewer.shots:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.compute.title"),
                self.translator.t("dialog.compute.need_points")
            )
            return
        
        if self.image_viewer.origin is None:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.compute.title"),
                self.translator.t("dialog.compute.need_origin")
            )
            return
        
        # Show progress
        self._show_progress(self.translator.t("progress.computing"))
        
        try:
            upp = float(self.image_viewer.units_per_pixel)
            unit = self.image_viewer.unit_name
            origin = self.image_viewer.origin
            rect = self.image_viewer.pixmap_item.boundingRect() if self.image_viewer.pixmap_item else None
            m = compute_metrics(self.image_viewer.shots, origin, upp, unit, rect)
            if not m:
                self._hide_progress()
                return
        except Exception as e:
            self._hide_progress()
            QtWidgets.QMessageBox.warning(self, self.translator.t("dialog.error.title"), self.translator.t("dialog.error.computation", str(e)))
            return
        
        # Convert all values to cm for display (matching MATLAB output)
        def to_cm(value: float, from_unit: str) -> float:
            """Convert value to centimeters."""
            if from_unit == "mm":
                return value / 10.0
            elif from_unit == "in":
                return value * 2.54
            else:  # cm or unknown
                return value
        
        # Convert all metrics to cm
        napam_x_cm = to_cm(m['mean_x'], unit)
        napam_y_cm = to_cm(m['mean_y'], unit)
        sigma_x_cm = to_cm(m['sigma_x'], unit)
        sigma_y_cm = to_cm(m['sigma_y'], unit)
        blocking_radius_cm = to_cm(m['blocking_radius'], unit)
        es_cm = to_cm(m['extreme_spread'], unit)
        dist_napam_napar_cm = to_cm(m['mean_to_origin'], unit)
        
        # Calculate milliradian (mrad) values
        # mrad = (size_in_meters / distance_in_meters) * 1000
        # Convert cm to meters: cm / 100
        distance_m = self.distance_input.value()  # Distance in meters
        
        # Validate distance to prevent division by zero
        if distance_m <= 0:
            distance_m = 100.0  # Default to 100m if invalid
            self.distance_input.setValue(distance_m)
        
        # Sigma in mrad (אלפיות)
        sigma_x_m = sigma_x_cm / 100.0  # Convert cm to meters
        sigma_y_m = sigma_y_cm / 100.0
        mrad_x = (sigma_x_m / distance_m) * 1000.0
        mrad_y = (sigma_y_m / distance_m) * 1000.0
        
        # Prepare metrics for display (removed "units" line - unnecessary)
        display_unit = "cm"
        unit_cm = self.translator.unit_display("cm")
        unit_mrad = self.translator.unit_display("mrad")
        
        # Helper to format numbers correctly for RTL (minus sign after number)
        def format_value(value: float, unit: str) -> str:
            if self.translator.is_rtl():
                # For Hebrew RTL: put minus sign AFTER the number
                if value < 0:
                    return f"{abs(value):.2f}- {unit}"
                else:
                    return f"{value:.2f} {unit}"
            else:
                return f"{value:.2f} {unit}"
        
        metrics = {
            self.translator.t("label.num_points"): f"\u200F{m['num_points']}" if self.translator.is_rtl() else str(m['num_points']),
            self.translator.t("label.napam_x"): format_value(napam_x_cm, unit_cm),
            self.translator.t("label.napam_y"): format_value(napam_y_cm, unit_cm),
            self.translator.t("label.sigma_x"): format_value(sigma_x_cm, unit_cm),
            self.translator.t("label.sigma_y"): format_value(sigma_y_cm, unit_cm),
            self.translator.t("label.blocking_radius"): format_value(blocking_radius_cm, unit_cm),
            self.translator.t("label.es"): format_value(es_cm, unit_cm),
            self.translator.t("label.dist_napam_napar"): format_value(dist_napam_napar_cm, unit_cm),
            self.translator.t("label.mrad_x"): format_value(mrad_x, unit_mrad),
            self.translator.t("label.mrad_y"): format_value(mrad_y, unit_mrad),
        }
        
        # Store metrics for CSV export
        self._last_metrics = {
            'napam_x_cm': napam_x_cm,
            'napam_y_cm': napam_y_cm,
            'sigma_x_cm': sigma_x_cm,
            'sigma_y_cm': sigma_y_cm,
            'blocking_radius_cm': blocking_radius_cm,
            'es_cm': es_cm,
            'dist_napam_napar_cm': dist_napam_napar_cm,
            'mrad_x': mrad_x,
            'mrad_y': mrad_y,
            'num_points': m['num_points'],
            'unit': display_unit
        }
        
        # Store metrics for later use (e.g., plot save with results)
        self._last_metrics = metrics
        
        # Show floating metrics dialog
        from .dialogs import MetricsDialog
        dialog = MetricsDialog(metrics, self, self.translator)
        # Position near the main window
        dialog.move(self.x() + self.width() - dialog.width() - 20, self.y() + 100)
        dialog.show()
        
        # Hide progress and update UI
        self._hide_progress()
        self.update_ui_state()  # This will enable the plot button
        self._show_status_message(self.translator.t("status.metrics.computed"), 3000)

    def _get_output_folder(self):
        """Get or create output folder based on loaded image name."""
        if hasattr(self, '_current_image_path') and self._current_image_path:
            try:
                import os
                image_dir = os.path.dirname(self._current_image_path)
                image_name = os.path.splitext(os.path.basename(self._current_image_path))[0]
                output_folder = os.path.join(image_dir, image_name)
                os.makedirs(output_folder, exist_ok=True)
                return output_folder
            except (OSError, PermissionError, ValueError):
                # If folder creation fails, return None (will use current directory)
                return None
        return None
    
    def export_csv_action(self):
        if not self.image_viewer.shots:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.export.title"),
                self.translator.t("dialog.export.nopoints")
            )
            return
        
        # Get output folder
        output_folder = self._get_output_folder()
        default_name = "results.csv"
        if output_folder:
            default_name = os.path.join(output_folder, "results.csv")
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.translator.t("btn.export"),
            default_name,
            "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            upp = float(self.image_viewer.units_per_pixel or 1.0)
            unit = self.image_viewer.unit_name or "px"
            origin = self.image_viewer.origin
            rect = self.image_viewer.pixmap_item.boundingRect() if self.image_viewer.pixmap_item else None
            # Compute metrics on demand if labels are not filled yet
            m = compute_metrics(self.image_viewer.shots, origin, upp, unit, rect)
            distance_m = self.distance_input.value()
            export_csv(self.image_viewer.shots, origin, upp, unit, m, path, distance_m, rect)
            self._show_status_message(self.translator.t("status.exported", path), 4000)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.t("dialog.export.title"),
                self.translator.t("dialog.export.failed", str(e))
            )

    def detect_holes(self):
        if self.image_viewer.pixmap_item is None:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.detect.title"),
                self.translator.t("dialog.detect.noimage")
            )
            return
        # ask config
        dlg = HoleDetectDialog(self.image_viewer.units_per_pixel, self.image_viewer.unit_name, self, self.translator)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        cfg = dlg.get_config()

        qimg = self.image_viewer.pixmap_item.pixmap().toImage()
        bounds = self.image_viewer.pixmap_item.boundingRect()

        # candidates in pixel (scene) coords
        cands = detection.detect_circles(
            qimg,
            min_diam=cfg['min_diam'],
            max_diam=cfg['max_diam'],
            dp=cfg['dp'],
            edge_thresh=cfg['edge_thresh'],
            accum_thresh=cfg['accum_thresh'],
            use_units=cfg['use_units'],
            units_per_pixel=self.image_viewer.units_per_pixel,
            bounds=bounds
        )

        # Filter out near-duplicates wrt existing shots
        filtered: List[QtCore.QPointF] = []
        for pt in cands:
            if self._find_near(self.image_viewer.shots, pt, tol_px=6.0) is None:
                filtered.append(pt)

        if not filtered:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.detect.title"),
                self.translator.t("dialog.detect.nocandidates")
            )
            return

        review = PointReviewDialog(self.image_viewer, filtered, parent=self, translator=self.translator)
        review.show()
        self._show_status_message(self.translator.t("review.status"), 8000)

    def _find_near(self, points: List[QtCore.QPointF], scene_pos: QtCore.QPointF, tol_px: float = 6.0):
        for i, p in enumerate(points):
            d = ((p.x()-scene_pos.x())**2 + (p.y()-scene_pos.y())**2)**0.5
            if d <= tol_px:
                return i
        return None

    def show_result_plot_action(self):
        if self.image_viewer.units_per_pixel is None or not self.image_viewer.shots:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.plot.title"),
                self.translator.t("dialog.plot.nodata")
            )
            return
        upp = float(self.image_viewer.units_per_pixel)
        unit = self.image_viewer.unit_name
        origin = self.image_viewer.origin
        rect = self.image_viewer.pixmap_item.boundingRect() if self.image_viewer.pixmap_item else None
        m = compute_metrics(self.image_viewer.shots, origin, upp, unit, rect)
        if not m:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.t("dialog.plot.title"),
                self.translator.t("dialog.plot.insufficient")
            )
            return

        real_pts = m.get("real_points", [])
        mean_x = m.get("mean_x", 0.0)
        mean_y = m.get("mean_y", 0.0)
        radius = m.get("furthest_from_mean", 0.0)
        image_path = self._current_image_path if hasattr(self, '_current_image_path') else None
        dlg = ResultsDialog(real_pts, mean_x, mean_y, radius, unit, self, self.translator, image_path)
        dlg.exec()
    def keyPressEvent(self, event):
        """Handle ESC key to show exit confirmation."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        # Show exit confirmation dialog (unless restarting)
        if not self._skip_exit_confirmation:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle(self.translator.t("dialog.exit.title"))
            msg_box.setText(self.translator.t("dialog.exit.message"))
            msg_box.setIcon(QtWidgets.QMessageBox.Question)
            yes_btn = msg_box.addButton(self.translator.t("btn.yes"), QtWidgets.QMessageBox.YesRole)
            no_btn = msg_box.addButton(self.translator.t("btn.no"), QtWidgets.QMessageBox.NoRole)
            msg_box.setDefaultButton(no_btn)
            msg_box.exec()
            
            if msg_box.clickedButton() != yes_btn:
                event.ignore()
                return
        
        try:
            # Save window geometry and state
            self.settings_mgr.set_window_geometry(self.saveGeometry())
            self.settings_mgr.set_window_state(self.saveState())
            
            # Save window position and size explicitly
            pos = self.pos()
            size = self.size()
            self.settings_mgr.set_window_position(pos.x(), pos.y())
            self.settings_mgr.set_window_size(size.width(), size.height())
            
            # Save splitter state
            splitter = self.centralWidget()
            if isinstance(splitter, QtWidgets.QSplitter):
                self.settings_mgr.set_splitter_state(splitter.saveState())
            
            # Ensure settings are written
            self.settings_mgr.sync()
        except Exception:
            pass
        super().closeEvent(event)
