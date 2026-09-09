
from __future__ import annotations
import math
from typing import List, Dict, Optional
from PySide6 import QtCore, QtWidgets

def median(vals: List[float]) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    n = len(s)
    m = n // 2
    if n % 2 == 1:
        return s[m]
    return 0.5 * (s[m-1] + s[m])

def pairwise_max_distance(points: List[QtCore.QPointF]) -> float:
    m = 0.0
    n = len(points)
    for i in range(n):
        pi = points[i]
        for j in range(i+1, n):
            pj = points[j]
            d = math.hypot(pi.x()-pj.x(), pi.y()-pj.y())
            if d > m:
                m = d
    return m

def compute_metrics(
    shots_scene: List[QtCore.QPointF],
    origin: Optional[QtCore.QPointF],
    upp: float,
    unit_name: str,
    fallback_rect: Optional[QtCore.QRectF] = None
) -> Dict[str, float]:
    """
    Compute statistics in real units given scene points and scale (units per pixel).
    Matches MATLAB implementation for CEP analysis.
    """
    if not shots_scene:
        return {}
    
    # Validate units per pixel
    if upp <= 0:
        raise ValueError("Units per pixel must be positive")
    
    if origin is None:
        if fallback_rect is not None:
            origin = fallback_rect.center()
        else:
            # fallback to first point to avoid crash
            origin = shots_scene[0]

    # Convert to real units with y up (matching MATLAB coordinate system)
    real_pts: List[QtCore.QPointF] = []
    for p in shots_scene:
        dx = (p.x() - origin.x()) * upp
        dy = -(p.y() - origin.y()) * upp  # Flip Y axis
        real_pts.append(QtCore.QPointF(dx, dy))

    # Calculate mean position (napam in MATLAB)
    mean_x = sum(p.x() for p in real_pts) / len(real_pts)
    mean_y = sum(p.y() for p in real_pts) / len(real_pts)

    # Standard deviation calculation (matching MATLAB std function)
    def stddev(values: List[float]) -> float:
        n = len(values)
        if n <= 1:
            return 0.0
        mu = sum(values) / n
        var = sum((v - mu)**2 for v in values) / (n-1)  # Sample std (n-1)
        return math.sqrt(var)

    # Calculate standard deviations
    sigma_x = stddev([p.x() for p in real_pts])
    sigma_y = stddev([p.y() for p in real_pts])
    
    # Calculate radii from mean (distances from mean to each point)
    radii = [math.hypot(p.x()-mean_x, p.y()-mean_y) for p in real_pts]
    
    # CEP50 - median radius (50% circular error probable)
    cep50 = median(radii)
    
    # Extreme Spread (ES) - maximum pairwise distance (calc_es in MATLAB)
    extreme_spread = pairwise_max_distance(real_pts)
    
    # Blocking Radius (r) - furthest point from mean (calc_blocking_radii in MATLAB)
    blocking_radius = max(radii) if radii else 0.0
    
    # Distance from mean to origin (dist_napam_napar in MATLAB)
    mean_to_origin = math.hypot(mean_x, mean_y)
    
    # Combined standard deviation (overall spread)
    combined_std = math.sqrt(sigma_x**2 + sigma_y**2)
    
    # Number of points
    num_points = len(real_pts)

    return {
        "num_points": num_points,
        "mean_x": mean_x,
        "mean_y": mean_y,
        "sigma_x": sigma_x,
        "sigma_y": sigma_y,
        "combined_std": combined_std,
        "cep50": cep50,
        "blocking_radius": blocking_radius,
        "extreme_spread": extreme_spread,
        "mean_to_origin": mean_to_origin,
        "furthest_from_mean": blocking_radius,  # Alias for compatibility
        "unit": unit_name,
        "real_points": real_pts,
    }

def export_csv(
    shots_scene: List[QtCore.QPointF],
    origin: Optional[QtCore.QPointF],
    upp: float,
    unit_name: str,
    metrics: Dict[str, float],
    path: str,
    distance_m: float = 100.0,
    fallback_rect: Optional[QtCore.QRectF] = None
) -> None:
    if not shots_scene:
        raise ValueError("No points to export.")
    
    # Validate units per pixel
    if upp <= 0:
        raise ValueError("Units per pixel must be positive")
    
    # Validate path
    if not path:
        raise ValueError("Export path cannot be empty")
    
    if origin is None:
        if fallback_rect is not None:
            origin = fallback_rect.center()
        else:
            origin = shots_scene[0]
    unit = unit_name or "px"
    lines = [f"index,x({unit}),y({unit})"]
    for i, p in enumerate(shots_scene, start=1):
        dx = (p.x() - origin.x()) * upp
        dy = -(p.y() - origin.y()) * upp
        lines.append(f"{i},{dx:.6f},{dy:.6f}")
    lines.append("")
    lines.append("metric,value,units")
    
    # Convert all values to cm for consistency (2 decimal places)
    def to_cm(value: float, from_unit: str) -> float:
        if from_unit == "mm":
            return value / 10.0
        elif from_unit == "cm":
            return value
        elif from_unit == "in":
            return value * 2.54
        else:
            return value  # Assume already in cm
    
    # Add mean position first
    if "mean_x" in metrics and "mean_y" in metrics:
        mean_x_cm = to_cm(metrics["mean_x"], unit)
        mean_y_cm = to_cm(metrics["mean_y"], unit)
        lines.append(f"mean_x,{mean_x_cm:.2f},cm")
        lines.append(f"mean_y,{mean_y_cm:.2f},cm")
    
    # Add other metrics (renamed furthest_from_mean to blocking_radius)
    for key in ["sigma_x","sigma_y","cep50","extreme_spread","blocking_radius","mean_to_origin"]:
        if key in metrics:
            value_cm = to_cm(metrics[key], unit)
            lines.append(f"{key},{value_cm:.2f},cm")
    
    # Add milliradian calculations
    lines.append("")
    lines.append(f"distance_to_target,{distance_m:.1f},m")
    
    # Calculate mrad from sigma values (convert to meters first)
    if "sigma_x" in metrics and "sigma_y" in metrics:
        sigma_x_cm = to_cm(metrics["sigma_x"], unit)
        sigma_y_cm = to_cm(metrics["sigma_y"], unit)
        sigma_x_m = sigma_x_cm / 100.0  # cm to meters
        sigma_y_m = sigma_y_cm / 100.0
        
        # Validate distance to prevent division by zero
        if distance_m <= 0:
            distance_m = 100.0  # Default to 100m if invalid
        mrad_x = (sigma_x_m / distance_m) * 1000.0
        mrad_y = (sigma_y_m / distance_m) * 1000.0
        
        lines.append(f"sigma_x_mrad,{mrad_x:.2f},mrad")
        lines.append(f"sigma_y_mrad,{mrad_y:.2f},mrad")
    
    try:
        # Ensure directory exists
        import os
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except PermissionError:
        raise ValueError(f"Permission denied: Cannot write to {path}")
    except OSError as e:
        raise ValueError(f"Failed to write file: {str(e)}")
