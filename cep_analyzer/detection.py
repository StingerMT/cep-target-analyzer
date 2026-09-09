
from __future__ import annotations
from typing import List, Optional, Dict
from PySide6 import QtCore, QtGui
try:
    import cv2
    import numpy as np
    HAVE_CV = True
except Exception:
    HAVE_CV = False

def qimage_to_bgr(qimg: QtGui.QImage):
    import numpy as np
    qimg = qimg.convertToFormat(QtGui.QImage.Format.Format_BGR888)
    width, height = qimg.width(), qimg.height()
    stride = qimg.bytesPerLine()
    buf = qimg.bits().tobytes()
    arr = np.frombuffer(buf, dtype=np.uint8).reshape((height, stride))
    arr = arr[:, : width*3]
    arr = arr.reshape((height, width, 3))
    return arr

def detect_circles(
    qimg: QtGui.QImage,
    min_diam: float,
    max_diam: float,
    dp: float,
    edge_thresh: int,
    accum_thresh: int,
    use_units: bool,
    units_per_pixel: Optional[float],
    bounds: Optional[QtCore.QRectF] = None
) -> List[QtCore.QPointF]:
    """Return candidate centers in scene (image) coordinates."""
    if not HAVE_CV:
        return []
    
    # Validate input parameters
    if min_diam <= 0 or max_diam <= 0:
        return []
    if min_diam > max_diam:
        min_diam, max_diam = max_diam, min_diam
    if dp <= 0:
        dp = 1.0
    
    try:
        bgr = qimage_to_bgr(qimg)
        import cv2, numpy as np
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
    except Exception:
        return []

    if use_units and units_per_pixel:
        px_per_unit = 1.0 / float(units_per_pixel)
        min_r = max(2.0, (min_diam * px_per_unit) / 2.0)
        max_r = max(min_r+1.0, (max_diam * px_per_unit) / 2.0)
        min_dist = max(4.0, min_diam * px_per_unit * 0.6)
    else:
        min_r = max(2.0, min_diam / 2.0)
        max_r = max(min_r+1.0, max_diam / 2.0)
        min_dist = max(4.0, min_diam * 0.6)

    try:
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=dp,
            minDist=min_dist,
            param1=edge_thresh,
            param2=accum_thresh,
            minRadius=int(round(min_r)),
            maxRadius=int(round(max_r)),
        )
    except Exception:
        return []
    
    candidates: List[QtCore.QPointF] = []
    if circles is not None:
        try:
            circles = np.uint16(np.around(circles))
            for c in circles[0, :]:
                x, y, r = int(c[0]), int(c[1]), int(c[2])
                pt = QtCore.QPointF(float(x), float(y))
                if bounds is None or bounds.contains(pt):
                    candidates.append(pt)
        except Exception:
            pass
    return candidates
