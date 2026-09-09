
from __future__ import annotations
from typing import List, Optional, Any
from PySide6 import QtCore, QtWidgets, QtGui
from .i18n import Translator

class MetricsDialog(QtWidgets.QDialog):
    """Floating borderless dialog to display computed metrics."""
    
    def __init__(self, metrics: dict, parent=None, translator: Optional[Translator] = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setWindowTitle(self.translator.t("group.results"))
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        
        # Set layout direction
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)
        
        # Main layout with border
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        
        # Content widget with background - uses application palette (dark theme)
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: palette(window);
                color: palette(window-text);
                border: 2px solid palette(mid);
                border-radius: 8px;
            }
        """)
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title bar with close button
        title_bar = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(self.translator.t("group.results"))
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        # Make close button visible in both light and dark modes
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f44336;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffebee;
                color: #d32f2f;
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        title_bar.addWidget(close_btn)
        content_layout.addLayout(title_bar)
        
        # Metrics grid (using grid instead of form for better RTL control)
        grid = QtWidgets.QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(15)
        
        # Add metrics (keys already have ":" from translation)
        row = 0
        for key, value in metrics.items():
            label = QtWidgets.QLabel(key)
            value_label = QtWidgets.QLabel(value)
            value_label.setStyleSheet("font-weight: bold;")
            
            # Labels center-aligned, values left-aligned (Qt will flip to right in RTL)
            label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            value_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            
            # Always add in same order - Qt's RTL layout will flip them automatically
            # Label always in col 0, value always in col 1
            grid.addWidget(label, row, 0)
            grid.addWidget(value_label, row, 1)
            row += 1
        
        # Value column always stretches
        grid.setColumnStretch(0, 0)  # Label column doesn't stretch
        grid.setColumnStretch(1, 1)  # Value column stretches
        
        content_layout.addLayout(grid)
        
        # Action buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        copy_btn = QtWidgets.QPushButton(self.translator.t("btn.copy") if hasattr(self.translator, "t") else "Copy")
        copy_btn.clicked.connect(lambda: self._copy_to_clipboard(metrics))
        button_layout.addWidget(copy_btn)
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_widget)
        
        # Make draggable
        self._drag_position = None
        
        # Size
        self.setMinimumWidth(350)
        self.adjustSize()
    
    def _copy_to_clipboard(self, metrics: dict):
        """Copy metrics to clipboard."""
        text = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
        QtWidgets.QApplication.clipboard().setText(text)
    
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() == QtCore.Qt.LeftButton and self._drag_position is not None:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()


class RotationDialog(QtWidgets.QDialog):
    """Dialog for fine-tuning image rotation angle."""
    
    angleChanged = QtCore.Signal(float)  # Emits angle changes for live preview
    
    def __init__(self, current_angle: float = 0.0, parent=None, translator: Optional[Translator] = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setWindowTitle("Rotate Image" if not self.translator.is_rtl() else "סובב תמונה")
        self.setModal(True)
        self.resize(400, 200)
        
        # Set layout direction
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info label
        info = QtWidgets.QLabel("Adjust the rotation angle to straighten the image:" if not self.translator.is_rtl() 
                               else "התאם את זווית הסיבוב ליישור התמונה:")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Angle display
        angle_layout = QtWidgets.QHBoxLayout()
        angle_layout.addWidget(QtWidgets.QLabel("Angle:" if not self.translator.is_rtl() else ":זווית"))
        self.angle_spinbox = QtWidgets.QDoubleSpinBox()
        self.angle_spinbox.setRange(-180.0, 180.0)
        self.angle_spinbox.setDecimals(1)
        self.angle_spinbox.setSingleStep(0.1)
        self.angle_spinbox.setValue(current_angle)
        self.angle_spinbox.setSuffix("°")
        angle_layout.addWidget(self.angle_spinbox)
        angle_layout.addStretch()
        layout.addLayout(angle_layout)
        
        # Slider for fine control
        slider_layout = QtWidgets.QVBoxLayout()
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(-1800, 1800)  # -180.0 to 180.0 degrees (x10 for precision)
        self.slider.setValue(int(current_angle * 10))
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setTickInterval(450)  # Tick every 45 degrees
        slider_layout.addWidget(self.slider)
        
        # Quick angle buttons
        quick_buttons = QtWidgets.QHBoxLayout()
        btn_minus_90 = QtWidgets.QPushButton("-90°")
        btn_minus_45 = QtWidgets.QPushButton("-45°")
        btn_reset = QtWidgets.QPushButton("0°")
        btn_plus_45 = QtWidgets.QPushButton("+45°")
        btn_plus_90 = QtWidgets.QPushButton("+90°")
        
        btn_minus_90.clicked.connect(lambda: self.set_angle(-90))
        btn_minus_45.clicked.connect(lambda: self.set_angle(-45))
        btn_reset.clicked.connect(lambda: self.set_angle(0))
        btn_plus_45.clicked.connect(lambda: self.set_angle(45))
        btn_plus_90.clicked.connect(lambda: self.set_angle(90))
        
        quick_buttons.addWidget(btn_minus_90)
        quick_buttons.addWidget(btn_minus_45)
        quick_buttons.addWidget(btn_reset)
        quick_buttons.addWidget(btn_plus_45)
        quick_buttons.addWidget(btn_plus_90)
        slider_layout.addLayout(quick_buttons)
        
        layout.addLayout(slider_layout)
        
        # Dialog buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        # Translate buttons
        buttons.button(QtWidgets.QDialogButtonBox.Ok).setText(self.translator.t("btn.ok"))
        buttons.button(QtWidgets.QDialogButtonBox.Cancel).setText(self.translator.t("btn.cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Connect signals
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.angle_spinbox.valueChanged.connect(self._on_spinbox_changed)
    
    def _on_slider_changed(self, value: int):
        angle = value / 10.0
        self.angle_spinbox.blockSignals(True)
        self.angle_spinbox.setValue(angle)
        self.angle_spinbox.blockSignals(False)
        self.angleChanged.emit(angle)
    
    def _on_spinbox_changed(self, value: float):
        self.slider.blockSignals(True)
        self.slider.setValue(int(value * 10))
        self.slider.blockSignals(False)
        self.angleChanged.emit(value)
    
    def set_angle(self, angle: float):
        self.angle_spinbox.setValue(angle)
    
    def get_angle(self) -> float:
        return self.angle_spinbox.value()


class ScaleDialog(QtWidgets.QDialog):
    def __init__(self, pixel_dist: float, parent=None, translator: Optional[Translator] = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setWindowTitle(self.translator.t("scale.title"))
        self.setModal(True)
        self.pixel_dist = pixel_dist
        
        # Set layout direction based on language
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)

        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.input_distance = QtWidgets.QDoubleSpinBox()
        self.input_distance.setRange(0.001, 1e6)
        self.input_distance.setDecimals(2)
        self.input_distance.setValue(10.0)
        self.combo_units = QtWidgets.QComboBox()
        # Translate units
        if self.translator.is_rtl():
            self.combo_units.addItems(['ס"מ', "מ\"מ", 'אינצ'])
            self._unit_map = {'ס"מ': "cm", "מ\"מ": "mm", 'אינצ': "in"}
            self._unit_reverse_map = {"cm": 'ס"מ', "mm": "מ\"מ", "in": 'אינצ'}
        else:
            self.combo_units.addItems(["cm", "mm", "in"])
            self._unit_map = {"cm": "cm", "mm": "mm", "in": "in"}
            self._unit_reverse_map = {"cm": "cm", "mm": "mm", "in": "in"}
        self.combo_units.setCurrentText(self._unit_reverse_map["cm"])

        # Presets in cm with 2 decimals
        if self.translator.is_rtl():
            self.presets = {
                "ללא": None,
                'A5 רוחב (14.80 ס"מ)': (14.80, "cm"),
                'A5 אורך (21.00 ס"מ)': (21.00, "cm"),
                'A4 רוחב (21.00 ס"מ)': (21.00, "cm"),
                'A4 אורך (29.70 ס"מ)': (29.70, "cm"),
                'A3 רוחב (29.70 ס"מ)': (29.70, "cm"),
                'A3 אורך (42.00 ס"מ)': (42.00, "cm"),
                'A2 רוחב (42.00 ס"מ)': (42.00, "cm"),
                'A2 אורך (59.40 ס"מ)': (59.40, "cm"),
                'US Letter רוחב (21.59 ס"מ)': (21.59, "cm"),
                'US Letter אורך (27.94 ס"מ)': (27.94, "cm"),
            }
        else:
            self.presets = {
                "None": None,
                "A5 short (14.80 cm)": (14.80, "cm"),
                "A5 long  (21.00 cm)": (21.00, "cm"),
                "A4 short (21.00 cm)": (21.00, "cm"),
                "A4 long  (29.70 cm)": (29.70, "cm"),
                "A3 short (29.70 cm)": (29.70, "cm"),
                "A3 long  (42.00 cm)": (42.00, "cm"),
                "A2 short (42.00 cm)": (42.00, "cm"),
                "A2 long  (59.40 cm)": (59.40, "cm"),
                "US Letter short (21.59 cm)": (21.59, "cm"),
                "US Letter long  (27.94 cm)": (27.94, "cm"),
            }
        self.combo_presets = QtWidgets.QComboBox()
        self.combo_presets.addItems(list(self.presets.keys()))
        # Set default to A4 width (short side)
        default_key = 'A4 רוחב (21.00 ס"מ)' if self.translator.is_rtl() else "A4 short (21.00 cm)"
        self.combo_presets.setCurrentText(default_key)
        self.combo_presets.currentTextChanged.connect(self._apply_preset)
        # Apply default preset
        self._apply_preset(default_key)

        form.addRow(self.translator.t("scale.preset"), self.combo_presets)
        form.addRow(self.translator.t("scale.distance"), self.input_distance)
        form.addRow(self.translator.t("scale.unit"), self.combo_units)

        info = QtWidgets.QLabel(self.translator.t("scale.measured", pixel_dist))
        info.setWordWrap(True)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        # Translate buttons
        btns.button(QtWidgets.QDialogButtonBox.Ok).setText(self.translator.t("btn.ok"))
        btns.button(QtWidgets.QDialogButtonBox.Cancel).setText(self.translator.t("btn.cancel"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        layout.addWidget(info)
        layout.addLayout(form)
        layout.addWidget(btns)

    def _apply_preset(self, text: str):
        val = self.presets.get(text)
        if val is None:
            return
        dist, unit = val
        self.input_distance.setValue(dist)
        self.combo_units.setCurrentText(self._unit_reverse_map[unit])

    def result_values(self):
        dist = float(self.input_distance.value())
        unit_display = self.combo_units.currentText()
        unit = self._unit_map[unit_display]  # Convert to internal unit
        units_per_pixel = dist / self.pixel_dist
        return units_per_pixel, unit

class HoleDetectDialog(QtWidgets.QDialog):
    def __init__(self, units_per_pixel: Optional[float], unit_name: str, parent=None, translator: Optional[Translator] = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setWindowTitle(self.translator.t("detect.title"))
        self.setModal(True)
        self.units_per_pixel = units_per_pixel
        self.unit_name = unit_name
        
        # Set layout direction based on language
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)

        use_units = units_per_pixel is not None

        layout = QtWidgets.QFormLayout(self)
        self.chk_units = QtWidgets.QCheckBox(self.translator.t("detect.use_units", unit_name))
        self.chk_units.setChecked(use_units)
        self.chk_units.setEnabled(use_units)

        self.spin_min = QtWidgets.QDoubleSpinBox()
        self.spin_max = QtWidgets.QDoubleSpinBox()
        self.spin_min.setRange(0.5, 2000.0)
        self.spin_max.setRange(1.0, 4000.0)
        self.spin_min.setDecimals(2)
        self.spin_max.setDecimals(2)
        if use_units and unit_name in ("mm", "cm"):
            default_min = 5.0 if unit_name == "mm" else 0.5
            default_max = 20.0 if unit_name == "mm" else 2.0
        elif use_units and unit_name == "in":
            default_min, default_max = 0.2, 0.8
        else:
            default_min, default_max = 8.0, 40.0
        self.spin_min.setValue(default_min)
        self.spin_max.setValue(default_max)

        self.spin_dp = QtWidgets.QDoubleSpinBox()
        self.spin_dp.setRange(0.8, 3.0)
        self.spin_dp.setSingleStep(0.1)
        self.spin_dp.setValue(1.2)

        self.spin_edge = QtWidgets.QSpinBox()
        self.spin_edge.setRange(10, 300)
        self.spin_edge.setValue(120)

        self.spin_accum = QtWidgets.QSpinBox()
        self.spin_accum.setRange(5, 150)
        self.spin_accum.setValue(25)

        layout.addRow(self.chk_units)
        layout.addRow(self.translator.t("detect.min_diam"), self.spin_min)
        layout.addRow(self.translator.t("detect.max_diam"), self.spin_max)
        layout.addRow(self.translator.t("detect.dp"), self.spin_dp)
        layout.addRow(self.translator.t("detect.edge"), self.spin_edge)
        layout.addRow(self.translator.t("detect.accum"), self.spin_accum)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        layout.addRow(btns)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

    def get_config(self):
        return {
            'use_units': self.chk_units.isChecked(),
            'min_diam': float(self.spin_min.value()),
            'max_diam': float(self.spin_max.value()),
            'dp': float(self.spin_dp.value()),
            'edge_thresh': int(self.spin_edge.value()),
            'accum_thresh': int(self.spin_accum.value()),
        }

class PointReviewDialog(QtWidgets.QDialog):
    """Non-modal review dialog pairing with an ImageView-like object that supports
    start_review_candidates / commit_review_candidates / abort_review_candidates
    and _set_candidate_accepted(idx, accepted).
    """
    def __init__(self, image_viewer: Any, candidates: List[QtCore.QPointF], parent=None, translator: Optional[Translator] = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setWindowTitle(self.translator.t("review.title"))
        self.setModal(False)
        self.resize(420, 360)
        self.image_viewer = image_viewer
        
        # Set layout direction based on language
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)

        layout = QtWidgets.QVBoxLayout(self)
        self.info = QtWidgets.QLabel(self.translator.t("review.info"))
        layout.addWidget(self.info)

        self.table = QtWidgets.QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            self.translator.t("review.col.keep"),
            self.translator.t("review.col.num"),
            self.translator.t("review.col.x"),
            self.translator.t("review.col.y")
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        layout.addWidget(self.table)

        btn_row = QtWidgets.QHBoxLayout()
        self.btn_accept_all = QtWidgets.QPushButton(self.translator.t("review.accept_all"))
        self.btn_reject_all = QtWidgets.QPushButton(self.translator.t("review.reject_all"))
        btn_row.addWidget(self.btn_accept_all)
        btn_row.addWidget(self.btn_reject_all)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        action_row = QtWidgets.QHBoxLayout()
        self.btn_ok = QtWidgets.QPushButton(self.translator.t("review.ok"))
        self.btn_cancel = QtWidgets.QPushButton(self.translator.t("review.cancel"))
        action_row.addStretch(1)
        action_row.addWidget(self.btn_ok)
        action_row.addWidget(self.btn_cancel)
        layout.addLayout(action_row)

        self._populate_table(candidates)

        self.btn_accept_all.clicked.connect(self._accept_all)
        self.btn_reject_all.clicked.connect(self._reject_all)
        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancel.clicked.connect(self._on_cancel)

        self.image_viewer.start_review_candidates(candidates, dialog_ref=self)

    def _populate_table(self, candidates: List[QtCore.QPointF]):
        self.table.blockSignals(True)
        self.table.setRowCount(len(candidates))
        for i, p in enumerate(candidates):
            chk = QtWidgets.QCheckBox()
            chk.setChecked(True)
            chk.stateChanged.connect(lambda st, ix=i: self._on_checkbox_changed(ix, st))
            self.table.setCellWidget(i, 0, chk)

            item_idx = QtWidgets.QTableWidgetItem(str(i+1))
            item_idx.setFlags(item_idx.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table.setItem(i, 1, item_idx)

            item_x = QtWidgets.QTableWidgetItem(f"{p.x():.1f}")
            item_x.setFlags(item_x.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table.setItem(i, 2, item_x)

            item_y = QtWidgets.QTableWidgetItem(f"{p.y():.1f}")
            item_y.setFlags(item_y.flags() ^ QtCore.Qt.ItemIsEditable)
            self.table.setItem(i, 3, item_y)
        self.table.blockSignals(False)

    def _on_checkbox_changed(self, idx: int, state: int):
        accepted = (state == QtCore.Qt.Checked)
        self.image_viewer._set_candidate_accepted(idx, accepted)

    def update_row(self, idx: int, accepted: bool):
        if idx < 0 or idx >= self.table.rowCount():
            return
        w = self.table.cellWidget(idx, 0)
        if isinstance(w, QtWidgets.QCheckBox):
            w.blockSignals(True)
            w.setChecked(bool(accepted))
            w.blockSignals(False)

    def _accept_all(self):
        for i in range(self.table.rowCount()):
            w = self.table.cellWidget(i, 0)
            if isinstance(w, QtWidgets.QCheckBox):
                w.setChecked(True)
                self.image_viewer._set_candidate_accepted(i, True)

    def _reject_all(self):
        for i in range(self.table.rowCount()):
            w = self.table.cellWidget(i, 0)
            if isinstance(w, QtWidgets.QCheckBox):
                w.setChecked(False)
                self.image_viewer._set_candidate_accepted(i, False)

    def _on_ok(self):
        self.image_viewer.commit_review_candidates()
        self.close()

    def _on_cancel(self):
        self.image_viewer.abort_review_candidates()
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent):
        if getattr(self.image_viewer, "_review_active", False):
            self.image_viewer.abort_review_candidates()
        super().closeEvent(event)


class ResultsDialog(QtWidgets.QDialog):
    """Shows a scatter of shots in real units and a circle centered on the mean
    with radius = furthest-from-mean distance.
    """
    def __init__(self, real_points: list[QtCore.QPointF], mean_x: float, mean_y: float, radius: float, unit_name: str, parent=None, translator: Optional[Translator] = None, image_path: str = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.image_path = image_path
        self.setWindowTitle(self.translator.t("plot.title"))
        self.resize(720, 540)
        
        # Set layout direction based on language
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)

        try:
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        except Exception:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        layout = QtWidgets.QVBoxLayout(self)
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        btns = QtWidgets.QHBoxLayout()
        
        # Add checkbox for including results dialog - default to unchecked
        self.include_results_checkbox = QtWidgets.QCheckBox(
            "כולל תוצאות" if self.translator.is_rtl() else "Include Results"
        )
        self.include_results_checkbox.setChecked(False)  # Changed to False by default
        btns.addWidget(self.include_results_checkbox)
        
        btns.addStretch(1)
        self.btn_save = QtWidgets.QPushButton(self.translator.t("plot.save"))
        self.btn_close = QtWidgets.QPushButton(self.translator.t("plot.close"))
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_close)
        layout.addLayout(btns)

        self.btn_close.clicked.connect(self.close)
        self.btn_save.clicked.connect(self._save_png)

        # Build the scatter plot with enhanced features
        import numpy as np
        import matplotlib.pyplot as plt
        
        # Convert all values to cm for consistent display
        def to_cm(value: float, from_unit: str) -> float:
            if from_unit == "mm":
                return value / 10.0
            elif from_unit == "cm":
                return value
            elif from_unit == "in":
                return value * 2.54
            else:
                return value  # Assume already in cm
        
        # Convert all coordinates and radius to cm
        real_points_cm = [QtCore.QPointF(to_cm(p.x(), unit_name), to_cm(p.y(), unit_name)) for p in real_points]
        mean_x_cm = to_cm(mean_x, unit_name)
        mean_y_cm = to_cm(mean_y, unit_name)
        radius_cm = to_cm(radius, unit_name)
        unit_display = "cm"  # Always display in cm
        
        # Helper function to fix Hebrew text display in matplotlib
        def fix_hebrew_text(text):
            """Fix Hebrew text display - simple character reversal for Hebrew."""
            if not self.translator.is_rtl():
                return text
            
            # Simple approach: just reverse the entire Hebrew string
            # Matplotlib will display it correctly
            return text[::-1]
        
        # Configure matplotlib for RTL if needed
        if self.translator.is_rtl():
            plt.rcParams['axes.unicode_minus'] = False
        
        ax = self.fig.add_subplot(111)
        
        # Extract coordinates (now in cm)
        xs = [p.x() for p in real_points_cm]
        ys = [p.y() for p in real_points_cm]
        
        # Helper to fix parentheses in Hebrew
        def fix_parens(text):
            """Fix parentheses direction in Hebrew text."""
            if not self.translator.is_rtl():
                return text
            # For Hebrew, we need to actually swap the parentheses characters
            # Replace ( with a placeholder, ) with (, then placeholder with )
            text = text.replace('(', '\x00')  # Temp placeholder
            text = text.replace(')', '(')
            text = text.replace('\x00', ')')
            return text
        
        # Plot shot points
        ax.scatter(xs, ys, c='blue', s=30, alpha=0.6, 
                  label=fix_hebrew_text(self.translator.t("plot.shots")), zorder=3)

        # Plot origin (0,0)
        origin_label = fix_parens(fix_hebrew_text(self.translator.t("plot.origin")))
        ax.scatter([0], [0], marker='s', c='green', s=60, 
                  label=origin_label, zorder=4)

        # Plot mean point (Napam)
        mean_label = fix_parens(fix_hebrew_text(self.translator.t("plot.mean")))
        ax.scatter([mean_x_cm], [mean_y_cm], marker="x", c='red', s=80, linewidths=2, 
                  label=mean_label, zorder=5)

        # Circle around mean: blocking radius
        theta = np.linspace(0, 2*np.pi, 256)
        cx = mean_x_cm + radius_cm * np.cos(theta)
        cy = mean_y_cm + radius_cm * np.sin(theta)
        ax.plot(cx, cy, 'r--', linewidth=2, 
               label=fix_hebrew_text(self.translator.t('plot.blocking_radius')), zorder=2)
        
        # Add red line from mean to circle edge (radius visualization) - no text
        radius_angle = np.pi / 4  # 45 degrees
        radius_end_x = mean_x_cm + radius_cm * np.cos(radius_angle)
        radius_end_y = mean_y_cm + radius_cm * np.sin(radius_angle)
        ax.plot([mean_x_cm, radius_end_x], [mean_y_cm, radius_end_y], 'r-', linewidth=2, alpha=0.8, zorder=6)

        # Line from origin to mean (green line)
        ax.plot([0, mean_x_cm], [0, mean_y_cm], 'g-', linewidth=2, alpha=0.7,
               label=fix_hebrew_text(self.translator.t("plot.radius_line")), zorder=2)

        # Find and draw extreme spread line (between furthest two points)
        if len(real_points_cm) >= 2:
            max_dist = 0
            pt1_idx, pt2_idx = 0, 1
            for i in range(len(real_points_cm)):
                for j in range(i+1, len(real_points_cm)):
                    dist = np.hypot(real_points_cm[i].x() - real_points_cm[j].x(),
                                   real_points_cm[i].y() - real_points_cm[j].y())
                    if dist > max_dist:
                        max_dist = dist
                        pt1_idx, pt2_idx = i, j
            
            # Draw ES line - no text annotation
            ax.plot([real_points_cm[pt1_idx].x(), real_points_cm[pt2_idx].x()],
                   [real_points_cm[pt1_idx].y(), real_points_cm[pt2_idx].y()],
                   'orange', linewidth=2, linestyle=':', alpha=0.8,
                   label=fix_hebrew_text(self.translator.t('plot.extreme_spread')), zorder=2)

        # Axes setup
        ax.set_aspect("equal", adjustable="datalim")
        unit_text = self.translator.unit_display(unit_display)
        xlabel = fix_parens(fix_hebrew_text(f"{self.translator.t('plot.xlabel')} {unit_text}"))
        ylabel = fix_parens(fix_hebrew_text(f"{self.translator.t('plot.ylabel')} {unit_text}"))
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='k', linewidth=0.5, alpha=0.3)
        ax.axvline(x=0, color='k', linewidth=0.5, alpha=0.3)
        
        # Moveable legend (draggable) with proper RTL handling
        if self.translator.is_rtl():
            # For RTL, reverse the legend order and use right alignment
            handles, labels = ax.get_legend_handles_labels()
            legend = ax.legend(handles[::-1], labels[::-1], loc="upper right", 
                             fontsize=9, framealpha=0.9)
        else:
            legend = ax.legend(loc="upper right", fontsize=9, framealpha=0.9)
        
        legend.set_draggable(True)

        # Autoscale with a small margin
        try:
            allx = xs + [mean_x_cm, 0] + list(cx)
            ally = ys + [mean_y_cm, 0] + list(cy)
            if allx and ally:
                xmin, xmax = min(allx), max(allx)
                ymin, ymax = min(ally), max(ally)
                dx = (xmax - xmin) * 0.1 if xmax > xmin else 1.0
                dy = (ymax - ymin) * 0.1 if ymax > ymin else 1.0
                ax.set_xlim(xmin - dx, xmax + dx)
                ax.set_ylim(ymin - dy, ymax + dy)
        except Exception:
            pass

        self.canvas.draw_idle()

    def _save_png(self):
        # Get output folder based on image path
        import os
        default_name = "results_plot.png"
        if self.image_path:
            try:
                image_dir = os.path.dirname(self.image_path)
                image_name = os.path.splitext(os.path.basename(self.image_path))[0]
                output_folder = os.path.join(image_dir, image_name)
                os.makedirs(output_folder, exist_ok=True)
                default_name = os.path.join(output_folder, "results_plot.png")
            except (OSError, PermissionError):
                # If folder creation fails, use current directory
                default_name = "results_plot.png"
        
        # Track if we need to close a temporary metrics dialog
        metrics_dialog_to_close = None
        
        # If checkbox is checked, ensure metrics dialog is open (auto-open if needed)
        if self.include_results_checkbox.isChecked():
            # Find existing metrics dialog
            metrics_dialog = None
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if isinstance(widget, MetricsDialog) and widget.isVisible():
                    metrics_dialog = widget
                    break
            
            if not metrics_dialog:
                # Metrics dialog not open - we need to create it temporarily
                # Get the metrics from parent (MainWindow should have _last_metrics)
                parent = self.parent()
                if parent and hasattr(parent, '_last_metrics') and parent._last_metrics:
                    # Create temporary metrics dialog
                    try:
                        metrics_dialog = MetricsDialog(
                            parent._last_metrics,
                            parent,
                            parent.translator if hasattr(parent, 'translator') else None
                        )
                        
                        # Position in bottom-right corner of screen to not obstruct save dialog
                        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
                        dialog_width = metrics_dialog.width()
                        dialog_height = metrics_dialog.height()
                        # Position in bottom-right with 20px margin
                        metrics_dialog.move(
                            screen.x() + screen.width() - dialog_width - 20,
                            screen.y() + screen.height() - dialog_height - 20
                        )
                        
                        metrics_dialog.show()
                        # Process events to ensure dialog is rendered
                        QtWidgets.QApplication.processEvents()
                        # Give it a moment to render
                        import time
                        time.sleep(0.1)
                        QtWidgets.QApplication.processEvents()
                        # Mark for closing after save
                        metrics_dialog_to_close = metrics_dialog
                    except Exception as e:
                        print(f"Error creating metrics dialog: {e}")
                        # No metrics available - uncheck and continue with plot only
                        self.include_results_checkbox.setChecked(False)
                else:
                    # No metrics available - uncheck and continue with plot only
                    self.include_results_checkbox.setChecked(False)
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.translator.t("plot.save"),
            default_name,
            "PNG Image (*.png)"
        )
        if not path:
            return
        try:
            # Save plot
            self.fig.savefig(path, dpi=160, bbox_inches="tight")
            
            # If checkbox is checked, also save with results dialog
            if self.include_results_checkbox.isChecked():
                # Find MetricsDialog (we know it exists from check above)
                metrics_dialog = None
                for widget in QtWidgets.QApplication.topLevelWidgets():
                    if isinstance(widget, MetricsDialog) and widget.isVisible():
                        metrics_dialog = widget
                        break
                
                if metrics_dialog:
                    # Create combined image
                    from PIL import Image
                    
                    # Save plot to temp file
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        temp_plot_path = tmp.name
                    self.fig.savefig(temp_plot_path, dpi=160, bbox_inches="tight")
                    
                    # Capture metrics dialog
                    metrics_pixmap = metrics_dialog.grab()
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        temp_metrics_path = tmp.name
                    metrics_pixmap.save(temp_metrics_path)
                    
                    # Combine images side by side
                    plot_img = Image.open(temp_plot_path)
                    metrics_img = Image.open(temp_metrics_path)
                    
                    # Create combined image
                    total_width = plot_img.width + metrics_img.width + 20  # 20px gap
                    max_height = max(plot_img.height, metrics_img.height)
                    combined = Image.new('RGB', (total_width, max_height), 'white')
                    combined.paste(plot_img, (0, 0))
                    combined.paste(metrics_img, (plot_img.width + 20, 0))
                    
                    # Save combined image
                    base_path = os.path.splitext(path)[0]
                    combined_path = f"{base_path}_with_results.png"
                    combined.save(combined_path)
                    
                    # Clean up temp files (suppress errors)
                    try:
                        os.unlink(temp_plot_path)
                    except:
                        pass
                    try:
                        os.unlink(temp_metrics_path)
                    except:
                        pass
                    
                    QtWidgets.QMessageBox.information(
                        self,
                        self.translator.t("plot.title"),
                        f"Saved:\n{path}\n{combined_path}"
                    )
                    
                    # Close temporary metrics dialog if we created one
                    if metrics_dialog_to_close:
                        metrics_dialog_to_close.close()
                else:
                    QtWidgets.QMessageBox.information(
                        self,
                        self.translator.t("plot.title"),
                        self.translator.t("plot.saved", path)
                    )
            else:
                QtWidgets.QMessageBox.information(
                    self,
                    self.translator.t("plot.title"),
                    self.translator.t("plot.saved", path)
                )
        except Exception as e:
            # Close temporary metrics dialog on error too
            if metrics_dialog_to_close:
                metrics_dialog_to_close.close()
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.t("plot.title"),
                self.translator.t("plot.save_failed", str(e))
            )


class PreferencesDialog(QtWidgets.QDialog):
    """Preferences dialog for customizing marker colors and other settings."""
    
    def __init__(self, parent=None, translator: Optional[Translator] = None, settings_mgr=None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.settings_mgr = settings_mgr
        self.setWindowTitle(self.translator.t("prefs.title"))
        self.setModal(True)
        self.resize(450, 300)
        
        # Set layout direction
        if self.translator.is_rtl():
            self.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            self.setLayoutDirection(QtCore.Qt.LeftToRight)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Marker Colors Group
        colors_group = QtWidgets.QGroupBox(self.translator.t("prefs.colors"))
        colors_layout = QtWidgets.QFormLayout()
        
        # Shot points color
        self.point_color_btn = QtWidgets.QPushButton()
        self.point_color_btn.setFixedSize(100, 30)
        self.point_color = self.settings_mgr.get_point_color() if self.settings_mgr else "#ff5555"
        self.point_color_btn.setStyleSheet(f"background-color: {self.point_color};")
        self.point_color_btn.clicked.connect(lambda: self._choose_color("point"))
        colors_layout.addRow(self.translator.t("prefs.point_color"), self.point_color_btn)
        
        # Origin color
        self.origin_color_btn = QtWidgets.QPushButton()
        self.origin_color_btn.setFixedSize(100, 30)
        self.origin_color = self.settings_mgr.get_origin_color() if self.settings_mgr else "#50be78"
        self.origin_color_btn.setStyleSheet(f"background-color: {self.origin_color};")
        self.origin_color_btn.clicked.connect(lambda: self._choose_color("origin"))
        colors_layout.addRow(self.translator.t("prefs.origin_color"), self.origin_color_btn)
        
        # Scale line color
        self.scale_color_btn = QtWidgets.QPushButton()
        self.scale_color_btn.setFixedSize(100, 30)
        self.scale_color = self.settings_mgr.get_scale_color() if self.settings_mgr else "#82aaff"
        self.scale_color_btn.setStyleSheet(f"background-color: {self.scale_color};")
        self.scale_color_btn.clicked.connect(lambda: self._choose_color("scale"))
        colors_layout.addRow(self.translator.t("prefs.scale_color"), self.scale_color_btn)
        
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
        # Reset to defaults button
        reset_btn = QtWidgets.QPushButton(self.translator.t("prefs.reset_defaults"))
        reset_btn.clicked.connect(self._reset_defaults)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        
        # Dialog buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.button(QtWidgets.QDialogButtonBox.Ok).setText(self.translator.t("btn.ok"))
        buttons.button(QtWidgets.QDialogButtonBox.Cancel).setText(self.translator.t("btn.cancel"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _choose_color(self, color_type: str):
        """Open color picker dialog."""
        if color_type == "point":
            current_color = QtGui.QColor(self.point_color)
        elif color_type == "origin":
            current_color = QtGui.QColor(self.origin_color)
        else:  # scale
            current_color = QtGui.QColor(self.scale_color)
        
        color = QtWidgets.QColorDialog.getColor(current_color, self, self.translator.t("prefs.choose_color"))
        
        if color.isValid():
            color_hex = color.name()
            if color_type == "point":
                self.point_color = color_hex
                self.point_color_btn.setStyleSheet(f"background-color: {color_hex};")
            elif color_type == "origin":
                self.origin_color = color_hex
                self.origin_color_btn.setStyleSheet(f"background-color: {color_hex};")
            else:  # scale
                self.scale_color = color_hex
                self.scale_color_btn.setStyleSheet(f"background-color: {color_hex};")
    
    def _reset_defaults(self):
        """Reset all colors to defaults."""
        self.point_color = "#ff5555"
        self.origin_color = "#50be78"
        self.scale_color = "#82aaff"
        self.point_color_btn.setStyleSheet(f"background-color: {self.point_color};")
        self.origin_color_btn.setStyleSheet(f"background-color: {self.origin_color};")
        self.scale_color_btn.setStyleSheet(f"background-color: {self.scale_color};")
    
    def get_colors(self):
        """Return selected colors as dict."""
        return {
            "point": self.point_color,
            "origin": self.origin_color,
            "scale": self.scale_color
        }
