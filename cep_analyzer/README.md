
# CEP Target Analyzer (Modular)

This is a modular refactor of your single-file PySide6 app. It includes:

- **Auto-detect review UI** (accept/reject detected holes, live markers on image).
- **Scale presets** (A2/A3/A4/A5, US Letter).
- **Always-on panning** with middle mouse or Space+Left during selection modes.
- **New metric**: "Furthest from Mean" (max distance from group mean).

## How to run

```bash
cd cep_analyzer
python -m cep_analyzer.main
# or
python main.py
```

## Install

```bash
pip install PySide6 opencv-python numpy qdarktheme
```

qdarktheme is optional; the app works without it.

## Layout

- `main.py` – App entry.
- `ui_mainwindow.py` – MainWindow and UI wiring.
- `image_viewer.py` – Panning/zoom, selection, drawing, review overlay.
- `dialogs.py` – ScaleDialog, HoleDetectDialog, PointReviewDialog.
- `detection.py` – OpenCV HoughCircles-based hole detection.
- `analysis.py` – Metric calculations and CSV export.


## Results Plot
- Click **Show Result Plot…** to see a scatter of shots (in real units) with a circle centered at the mean.
- The circle radius equals **Furthest from Mean**.
- You can save the plot as a PNG from the dialog.
