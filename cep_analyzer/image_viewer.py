
from __future__ import annotations
import math
from typing import List, Optional, Tuple, Any
from PySide6 import QtCore, QtGui, QtWidgets
from .dialogs import ScaleDialog
from .i18n import Translator

class ImageView(QtWidgets.QGraphicsView):
    scaleSet = QtCore.Signal(float, str)
    originSet = QtCore.Signal(QtCore.QPointF)
    originCleared = QtCore.Signal()
    pointsChanged = QtCore.Signal()

    def __init__(self, parent=None, translator: Optional[Translator] = None):
        super().__init__(parent)
        self.translator = translator or Translator()
        self.setRenderHints(
            QtGui.QPainter.Antialiasing
            | QtGui.QPainter.SmoothPixmapTransform
            | QtGui.QPainter.TextAntialiasing
        )
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setMouseTracking(True)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        
        # Enable touch support for tablet mode
        self.setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        self.viewport().setAttribute(QtCore.Qt.WA_AcceptTouchEvents, True)
        
        # Pinch-to-zoom tracking
        self._pinch_scale_factor = 1.0
        self._pinch_center = None

        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

        self.pixmap_item: Optional[QtWidgets.QGraphicsPixmapItem] = None
        self.shots: List[QtCore.QPointF] = []
        self.origin: Optional[QtCore.QPointF] = None
        self.units_per_pixel: Optional[float] = None
        self.unit_name: str = "cm"
        
        # Rotation tracking
        self._original_pixmap: Optional[QtGui.QPixmap] = None
        self._rotation_angle: int = 0  # Total rotation in degrees

        self.mode: str = "idle"
        self._scale_temp_points: List[QtCore.QPointF] = []
        self._last_scale_pts: Optional[Tuple[QtCore.QPointF, QtCore.QPointF]] = None
        self._space_down: bool = False

        self._panning: bool = False
        self._pan_anchor: Optional[QtCore.QPointF] = None
        self._last_mouse_scene_pos: Optional[QtCore.QPointF] = None  # Track mouse for scale line

        self._review_active: bool = False
        self._review_candidates: List[dict] = []
        self._review_dialog: Optional[Any] = None

        # Base marker sizes (will be scaled based on viewport)
        self.point_radius_base = 8  # Base size for 1080p reference
        
        # Initialize with default colors (will be updated from settings)
        self._init_marker_pens("#ff5555", "#50be78", "#82aaff")
        
        self.candidate_pen = QtGui.QPen(QtGui.QColor(255, 170, 60), 3)
        self.candidate_brush_ok = QtGui.QBrush(QtGui.QColor(80, 200, 120, 180))
        self.candidate_brush_reject = QtGui.QBrush(QtGui.QColor(200, 60, 60, 120))

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
    
    def _init_marker_pens(self, point_color: str, origin_color: str, scale_color: str):
        """Initialize marker pens with given colors (base sizes, will be scaled)."""
        # Store colors for dynamic pen creation
        self._point_color = point_color
        self._origin_color = origin_color
        self._scale_color = scale_color
        
        # Create base pens (will be recreated with scaled widths in drawForeground)
        point_qcolor = QtGui.QColor(point_color)
        self.point_pen = QtGui.QPen(point_qcolor, 7)
        point_qcolor.setAlpha(180)
        self.point_brush = QtGui.QBrush(point_qcolor)
        
        self.origin_pen = QtGui.QPen(QtGui.QColor(origin_color), 4)
        
        scale_qcolor = QtGui.QColor(scale_color)
        self.scale_pen = QtGui.QPen(scale_qcolor, 3, QtCore.Qt.DashLine)
        self.scale_endpoint_pen = QtGui.QPen(scale_qcolor, 3)
        scale_qcolor.setAlpha(140)
        self.scale_endpoint_brush = QtGui.QBrush(scale_qcolor)
        self.last_scale_pen = QtGui.QPen(QtGui.QColor(scale_color), 11, QtCore.Qt.DashLine)
    
    def update_marker_colors(self, colors: dict):
        """Update marker colors from preferences."""
        self._init_marker_pens(colors["point"], colors["origin"], colors["scale"])
    
    def _get_view_scale_factor(self) -> float:
        """Calculate view-based scale factor for consistent marker sizes across monitors."""
        viewport_rect = self.viewport().rect()
        viewport_diagonal = math.sqrt(viewport_rect.width()**2 + viewport_rect.height()**2)
        
        # Reference diagonal for 1080p at 70% window size
        reference_width = 1920 * 0.7
        reference_height = 1080 * 0.7
        reference_diagonal = math.sqrt(reference_width**2 + reference_height**2)
        
        view_scale_factor = viewport_diagonal / reference_diagonal
        
        # Detect monitor resolution and scale accordingly
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            screen_height = screen.geometry().height()
            monitor_scale = screen_height / 1080.0
            view_scale_factor *= monitor_scale
        
        # CRITICAL: Account for current zoom level
        # Get the current transform scale (how zoomed in/out we are)
        transform = self.transform()
        current_scale = transform.m11()  # Horizontal scale factor
        
        # Adjust marker size inversely to zoom level
        # When zoomed in (scale > 1), markers should be smaller in scene coordinates
        # When zoomed out (scale < 1), markers should be larger in scene coordinates
        # This keeps them visually consistent on screen
        if current_scale > 0:
            view_scale_factor /= current_scale
        
        return view_scale_factor

    # Loading & view
    def load_image(self, path: str):
        img = QtGui.QImage(path)
        if img.isNull():
            QtWidgets.QMessageBox.warning(self, self.translator.t("dialog.load.title"), self.translator.t("dialog.load.failed"))
            return
        pm = QtGui.QPixmap.fromImage(img)
        
        # Store original pixmap for rotation
        self._original_pixmap = pm
        self._rotation_angle = 0
        
        self._scene.clear()
        self.pixmap_item = self._scene.addPixmap(pm)
        rect = QtCore.QRectF(pm.rect())
        margin = max(rect.width(), rect.height()) * 0.25
        expanded = rect.adjusted(-margin, -margin, margin, margin)
        self._scene.setSceneRect(expanded)
        self.resetTransform()
        self.fit_to_image()
        self.shots.clear()
        self.origin = None
        self.units_per_pixel = None
        self._scale_temp_points.clear()
        self._last_scale_pts = None
        self._review_active = False
        self._review_candidates.clear()
        self.mode = "idle"
        self.pointsChanged.emit()

    def fit_to_image(self):
        if self.pixmap_item is not None:
            self.fitInView(self.pixmap_item.boundingRect(), QtCore.Qt.KeepAspectRatio)
        else:
            self.fitInView(self._scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
    
    def rotate_image_to_angle(self, angle: float):
        """
        Rotate the image to a specific angle (fine-tuned rotation).
        Only allowed before scale is set to avoid coordinate confusion.
        
        Args:
            angle: Target rotation angle in degrees (-180 to 180)
        """
        if self._original_pixmap is None or self.pixmap_item is None:
            return
        
        # Don't allow rotation after scale is set
        if self.units_per_pixel is not None:
            return
        
        # Update rotation angle
        self._rotation_angle = angle
        
        # Create transform for rotation
        transform = QtGui.QTransform()
        transform.rotate(angle)
        
        # Apply rotation to original pixmap
        rotated_pm = self._original_pixmap.transformed(transform, QtCore.Qt.SmoothTransformation)
        
        # Update the pixmap item
        self.pixmap_item.setPixmap(rotated_pm)
        
        # Update scene rect
        rect = QtCore.QRectF(rotated_pm.rect())
        margin = max(rect.width(), rect.height()) * 0.25
        expanded = rect.adjusted(-margin, -margin, margin, margin)
        self._scene.setSceneRect(expanded)
        
        # Clear any temporary points
        self._scale_temp_points.clear()
        self._last_scale_pts = None
        
        # Fit to view
        self.fit_to_image()
        self.viewport().update()

    def set_mode(self, mode: str):
        self.mode = mode
        if mode != "set_scale":
            self._scale_temp_points.clear()
        self.viewport().update()

    # Keyboard
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_F:
            self.fit_to_image(); event.accept(); return
        if event.key() == QtCore.Qt.Key_Space and not self._space_down:
            self._space_down = True
            self.viewport().setCursor(QtCore.Qt.OpenHandCursor)
            event.accept(); return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space and self._space_down:
            self._space_down = False
            self.viewport().unsetCursor(); event.accept(); return
        super().keyReleaseEvent(event)

    # Review API
    def start_review_candidates(self, pts: List[QtCore.QPointF], dialog_ref=None):
        self._review_candidates = [{'pt': p, 'accepted': True, 'idx': i} for i, p in enumerate(pts)]
        self._review_active = True
        self._review_dialog = dialog_ref
        self.viewport().update()

    def _set_candidate_accepted(self, idx: int, accepted: bool):
        if 0 <= idx < len(self._review_candidates):
            self._review_candidates[idx]['accepted'] = bool(accepted)
            self.viewport().update()

    def _toggle_candidate_near(self, scene_pos: QtCore.QPointF, tol_px: Optional[float] = None):
        if not self._review_active:
            return False
        if tol_px is None:
            view_scale_factor = self._get_view_scale_factor()
            tol_px = max(8, self.point_radius_base * 2 * view_scale_factor)
        for cand in self._review_candidates:
            p = cand['pt']
            d = math.hypot(p.x()-scene_pos.x(), p.y()-scene_pos.y())
            if d <= tol_px:
                cand['accepted'] = not cand['accepted']
                if self._review_dialog:
                    try:
                        self._review_dialog.update_row(cand['idx'], cand['accepted'])
                    except Exception:
                        pass
                self.viewport().update()
                return True
        return False

    def commit_review_candidates(self):
        if not self._review_active:
            return 0
        added = 0
        # Calculate view-scaled tolerance
        view_scale_factor = self._get_view_scale_factor()
        tol_px = max(4, int(self.point_radius_base/1.5 * view_scale_factor))
        
        for cand in self._review_candidates:
            if cand.get('accepted', False):
                pt = cand['pt']
                if self._find_nearby_index(pt, tol_px=tol_px) is None:
                    self.shots.append(pt); added += 1
        self._review_candidates.clear()
        self._review_active = False
        self._review_dialog = None
        self.pointsChanged.emit()
        self.viewport().update()
        return added

    def abort_review_candidates(self):
        self._review_candidates.clear()
        self._review_active = False
        self._review_dialog = None
        self.viewport().update()

    # Mouse
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if self.pixmap_item is None:
            return super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.position().toPoint())

        # Always-on panning (middle or Space+Left)
        if event.button() == QtCore.Qt.MiddleButton or (event.button() == QtCore.Qt.LeftButton and self._space_down):
            self._panning = True
            self._pan_anchor = event.position()
            self.viewport().setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept(); return

        if self._review_active and event.button() == QtCore.Qt.LeftButton:
            if self._toggle_candidate_near(scene_pos):
                return

        if self.mode == "set_scale":
            if event.button() == QtCore.Qt.LeftButton:
                self._scale_temp_points.append(scene_pos)
                if len(self._scale_temp_points) == 2:
                    p1, p2 = self._scale_temp_points
                    self._last_scale_pts = (p1, p2)
                    pixel_dist = math.hypot(p1.x()-p2.x(), p1.y()-p2.y())
                    if pixel_dist < 1e-6:
                        QtWidgets.QMessageBox.warning(self, self.translator.t("dialog.scale.title"), self.translator.t("dialog.scale.too_close"))
                        self._scale_temp_points.clear(); self._last_scale_pts = None
                    else:
                        self._ask_real_distance(pixel_dist)
                        self._scale_temp_points.clear()
                        self.set_mode("idle")
                self.viewport().update()
            elif event.button() == QtCore.Qt.RightButton:
                if self._scale_temp_points:
                    self._scale_temp_points.pop(); self.viewport().update()
            return

        if self.mode == "set_origin":
            if event.button() == QtCore.Qt.LeftButton:
                self.origin = scene_pos
                self.originSet.emit(scene_pos)
                self.set_mode("idle")
                self.viewport().update()
            elif event.button() == QtCore.Qt.RightButton:
                # Right-click to clear origin
                if self.origin is not None:
                    self.origin = None
                    self.originCleared.emit()
                    self.viewport().update()
            return

        if self.mode == "add_points":
            if event.button() == QtCore.Qt.LeftButton:
                if self.pixmap_item.boundingRect().contains(scene_pos):
                    dup = self._find_nearby_index(scene_pos)
                    if dup is not None:
                        msg_box = QtWidgets.QMessageBox(self)
                        msg_box.setWindowTitle(self.translator.t("dialog.overlap.title"))
                        msg_box.setText(self.translator.t("dialog.overlap.message"))
                        msg_box.setIcon(QtWidgets.QMessageBox.Question)
                        yes_btn = msg_box.addButton(self.translator.t("btn.yes"), QtWidgets.QMessageBox.YesRole)
                        no_btn = msg_box.addButton(self.translator.t("btn.no"), QtWidgets.QMessageBox.NoRole)
                        msg_box.setDefaultButton(no_btn)
                        msg_box.exec()
                        if msg_box.clickedButton() != yes_btn:
                            return
                    self.shots.append(scene_pos)
                    self.pointsChanged.emit()
                    self.viewport().update()
            elif event.button() == QtCore.Qt.RightButton:
                if self.shots:
                    nearest_idx = min(range(len(self.shots)), key=lambda i: (self.shots[i] - scene_pos).manhattanLength())
                    del self.shots[nearest_idx]
                    self.pointsChanged.emit()
                    self.viewport().update()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        # Track mouse position in scene coordinates for accurate drawing
        self._last_mouse_scene_pos = self.mapToScene(event.position().toPoint())
        
        if self.mode == "set_scale" and self._scale_temp_points:
            self.viewport().update()
        if self._panning and self._pan_anchor is not None:
            new_pos = event.position()
            dx = int(new_pos.x() - self._pan_anchor.x())
            dy = int(new_pos.y() - self._pan_anchor.y())
            h = self.horizontalScrollBar(); v = self.verticalScrollBar()
            # Fix RTL panning: invert dx if layout is RTL
            if self.layoutDirection() == QtCore.Qt.RightToLeft:
                dx = -dx
            h.setValue(h.value() - dx); v.setValue(v.value() - dy)
            self._pan_anchor = new_pos; event.accept(); return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if self._panning:
            self._panning = False; self._pan_anchor = None
            self.viewport().unsetCursor(); event.accept(); return
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        if event.modifiers() & QtCore.Qt.ControlModifier:
            angle = event.angleDelta().y()
            factor = 1.0015 ** angle
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)
    
    def event(self, event: QtCore.QEvent) -> bool:
        """Handle touch events for pinch-to-zoom on tablets."""
        if event.type() == QtCore.QEvent.TouchBegin:
            event.accept()
            return True
        elif event.type() == QtCore.QEvent.TouchUpdate:
            touch_event = event
            if len(touch_event.points()) == 2:
                # Pinch gesture with two fingers
                point1 = touch_event.points()[0]
                point2 = touch_event.points()[1]
                
                # Calculate current distance between touch points
                current_dist = QtCore.QLineF(
                    point1.position(),
                    point2.position()
                ).length()
                
                # Calculate previous distance
                prev_dist = QtCore.QLineF(
                    point1.lastPosition(),
                    point2.lastPosition()
                ).length()
                
                if prev_dist > 0:
                    # Calculate scale factor
                    scale_factor = current_dist / prev_dist
                    
                    # Apply zoom centered on pinch center
                    center = (point1.position() + point2.position()) / 2
                    self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
                    
                    # Map to scene coordinates
                    scene_pos = self.mapToScene(center.toPoint())
                    
                    # Apply scale
                    self.scale(scale_factor, scale_factor)
                    
                    # Re-center on pinch point
                    self.centerOn(scene_pos)
                
                event.accept()
                return True
        elif event.type() == QtCore.QEvent.TouchEnd:
            event.accept()
            return True
        
        return super().event(event)
    
    def paintEvent(self, event: QtGui.QPaintEvent):
        """Override paint event to add copyright watermark."""
        # Call parent to draw everything normally
        super().paintEvent(event)
        
        # Add subtle copyright watermark
        painter = QtGui.QPainter(self.viewport())
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.TextAntialiasing)
        
        # Set elegant font
        font = QtGui.QFont("Segoe UI", 9)  # or "Arial", "Helvetica"
        font.setWeight(QtGui.QFont.Light)
        painter.setFont(font)
        
        # Very subtle color - barely visible
        painter.setPen(QtGui.QColor(80, 80, 80, 120))  # Dark gray with transparency
        
        # Copyright text
        copyright_text = "© Benji Abramovitz, 2025"
        
        # Position in corner based on language direction
        viewport_rect = self.viewport().rect()
        text_rect = painter.fontMetrics().boundingRect(copyright_text)
        
        if self.translator.is_rtl():
            # Bottom-left for RTL (Hebrew)
            x = 10
            y = viewport_rect.height() - 10
        else:
            # Bottom-right for LTR (English)
            x = viewport_rect.width() - text_rect.width() - 10
            y = viewport_rect.height() - 10
        
        painter.drawText(x, y, copyright_text)
        painter.end()

    # Drawing
    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawForeground(painter, rect)
        if self.pixmap_item is None:
            return
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        
        # Calculate view-based scaling for consistent visual size across monitors
        view_scale_factor = self._get_view_scale_factor()
        
        # Apply scaling to marker sizes
        scaled_radius = self.point_radius_base * view_scale_factor
        scaled_line_size = 45 * view_scale_factor
        resolution_scale = view_scale_factor
        
        # Create scaled pens dynamically
        point_qcolor = QtGui.QColor(self._point_color)
        point_pen = QtGui.QPen(point_qcolor, max(1, int(7 * view_scale_factor)))
        point_qcolor.setAlpha(180)
        point_brush = QtGui.QBrush(point_qcolor)
        
        origin_pen = QtGui.QPen(QtGui.QColor(self._origin_color), max(1, int(4 * view_scale_factor)))
        
        scale_qcolor = QtGui.QColor(self._scale_color)
        scale_pen = QtGui.QPen(scale_qcolor, max(1, int(3 * view_scale_factor)), QtCore.Qt.DashLine)
        scale_endpoint_pen = QtGui.QPen(scale_qcolor, max(1, int(3 * view_scale_factor)))
        scale_qcolor.setAlpha(140)
        scale_endpoint_brush = QtGui.QBrush(scale_qcolor)
        last_scale_pen = QtGui.QPen(QtGui.QColor(self._scale_color), max(1, int(11 * view_scale_factor)), QtCore.Qt.DashLine)
        
        # Draw shot points
        painter.setPen(point_pen); painter.setBrush(point_brush)
        for p in self.shots:
            painter.drawEllipse(p, scaled_radius, scaled_radius)

        # Draw origin
        if self.origin is not None:
            painter.setPen(origin_pen)
            s = scaled_line_size
            painter.drawLine(self.origin + QtCore.QPointF(-s,0), self.origin + QtCore.QPointF(s,0))
            painter.drawLine(self.origin + QtCore.QPointF(0,-s), self.origin + QtCore.QPointF(0,s))

        # Draw last scale line
        if self._last_scale_pts is not None:
            p1, p2 = self._last_scale_pts
            painter.setPen(last_scale_pen)
            painter.drawLine(p1, p2)

        # Draw review candidates
        if self._review_active and self._review_candidates:
            candidate_radius = scaled_radius * 1.4
            candidate_pen = QtGui.QPen(QtGui.QColor(255, 170, 60), max(1, int(3 * view_scale_factor)))
            for cand in self._review_candidates:
                p = cand['pt']; accepted = cand.get('accepted', True)
                painter.setPen(candidate_pen)
                painter.setBrush(self.candidate_brush_ok if accepted else self.candidate_brush_reject)
                painter.drawEllipse(p, candidate_radius, candidate_radius)
                painter.setPen(QtGui.QPen(QtCore.Qt.white))
                text_offset = 6 * resolution_scale
                painter.drawText(p + QtCore.QPointF(-text_offset, text_offset*0.67), str(cand['idx']+1))

        # Draw scale temp points
        if self.mode == "set_scale" and self._scale_temp_points:
            endpoint_radius = 4 * resolution_scale
            painter.setPen(scale_pen); painter.setBrush(scale_endpoint_brush)
            if len(self._scale_temp_points) == 1:
                p1 = self._scale_temp_points[0]
                # Use tracked mouse position for accurate alignment when zoomed
                p2 = self._last_mouse_scene_pos if self._last_mouse_scene_pos else p1
                painter.drawLine(p1, p2)
                painter.setPen(scale_endpoint_pen)
                painter.drawEllipse(p1, endpoint_radius, endpoint_radius)
                painter.drawEllipse(p2, endpoint_radius, endpoint_radius)
                dist_px = math.hypot(p1.x()-p2.x(), p1.y()-p2.y())
                self._draw_label(painter, (p1+p2)*0.5, f"{dist_px:.1f} px", resolution_scale)
            else:
                p1, p2 = self._scale_temp_points[:2]
                painter.drawLine(p1, p2)
                painter.setPen(scale_endpoint_pen)
                painter.drawEllipse(p1, endpoint_radius, endpoint_radius)
                painter.drawEllipse(p2, endpoint_radius, endpoint_radius)
                dist_px = math.hypot(p1.x()-p2.x(), p1.y()-p2.y())
                if self.units_per_pixel:
                    dist_real = dist_px * float(self.units_per_pixel)
                    self._draw_label(painter, (p1+p2)*0.5, f"{dist_real:.2f} {self.unit_name}", resolution_scale)
                else:
                    self._draw_label(painter, (p1+p2)*0.5, f"{dist_px:.1f} px", resolution_scale)

    def _draw_label(self, painter: QtGui.QPainter, pos: QtCore.QPointF, text: str, resolution_scale: float = 1.0):
        # Resolution-based label sizing with scaled font
        # Cap the scale factor to prevent labels from becoming too large when zoomed out
        # Use square root to dampen the scaling effect
        capped_scale = min(resolution_scale, 3.0)  # Cap at 3x
        font_scale = math.sqrt(capped_scale)  # Dampen scaling with square root
        
        font = painter.font()
        base_font_size = 10  # Base font size in points
        font.setPointSizeF(base_font_size * font_scale)
        painter.setFont(font)
        
        metrics = painter.fontMetrics()
        pad = 4 * font_scale
        w = metrics.horizontalAdvance(text) + pad*2
        h = metrics.height() + pad
        offset = 8 * font_scale
        rect = QtCore.QRectF(pos.x()-w/2, pos.y()-h-offset, w, h)
        painter.setPen(QtCore.Qt.NoPen); painter.setBrush(QtGui.QColor(0,0,0,160))
        corner_radius = 6 * font_scale
        painter.drawRoundedRect(rect, corner_radius, corner_radius)
        painter.setPen(QtGui.QPen(QtGui.QColor(255,255,255)))
        painter.drawText(rect.adjusted(pad,0,-pad,0), QtCore.Qt.AlignCenter, text)

    # Helpers
    def _find_nearby_index(self, scene_pos: QtCore.QPointF, tol_px: Optional[float] = None) -> Optional[int]:
        # Use view-scaled tolerance if not specified
        if tol_px is None:
            view_scale_factor = self._get_view_scale_factor()
            tol_px = self.point_radius_base * view_scale_factor
        
        for i, p in enumerate(self.shots):
            d = math.hypot(p.x()-scene_pos.x(), p.y()-scene_pos.y())
            if d <= tol_px:
                return i
        return None

    def _ask_real_distance(self, pixel_dist: float):
        dialog = ScaleDialog(pixel_dist, parent=self, translator=self.translator)
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            upp, unit = dialog.result_values()
            self.units_per_pixel = upp; self.unit_name = unit
            self.scaleSet.emit(upp, unit)
        else:
            # User cancelled - clear the scale line
            self._last_scale_pts = None
            self.viewport().update()
