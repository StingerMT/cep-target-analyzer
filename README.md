# CEP Target Analyzer v1.1.0

**Professional ballistic target analysis tool with bilingual support (English/Hebrew)**

**Version 1.1.0** — Production Ready ✅

Analyzes shooting target photos to calculate precision and dispersion metrics used in ballistic evaluation.

---

## 🎯 What It Does

Load a photo of a shooting target, mark your shot holes, set the scale and origin — the app calculates all standard precision metrics in real units (cm, mm, or inches):

| Metric | Description |
|--------|-------------|
| **Napam X, Y** | Mean hit point coordinates |
| **Sigma X, Y** | Horizontal/vertical standard deviation |
| **CEP50** | Median radius — 50% circular error probable |
| **Blocking Radius** | Furthest point from mean |
| **Extreme Spread** | Maximum distance between any two points |
| **Dist. Napam→Napar** | Mean hit point to origin distance |
| **mrad** | Milliradian equivalents based on target distance |

---

## ✨ Key Features

- **Bilingual** — Full English (LTR) and Hebrew (RTL) support with automatic layout mirroring
- **Image rotation** — Fine-tune image angle with 0.1° precision before analysis
- **Scale presets** — A4, A5, Letter paper sizes or custom two-point scale
- **Interactive plot** — Scatter plot with radius circles, extreme spread lines, draggable legend; exportable as PNG
- **CSV export** — All coordinates and metrics exported with milliradian conversions
- **Dark theme** — Modern dark UI, adapts to 1080p/1440p/4K displays
- **Persistent settings** — Window position, language, colors, and recent files remembered between sessions

---

## 🚀 Quick Start

### Download (Windows — recommended)

Go to the **[Releases page](https://github.com/StingerMT/cep-target-analyzer/releases)** and download the `.exe` — no installation required, just run it.

> ⚠️ **Windows SmartScreen notice**: Windows may show a "Windows protected your PC" warning the first time you run the app. This is normal for unsigned source-available software. Click **"More info"** → **"Run anyway"** to proceed. The full source code is available in this repository for inspection.

### Run from source

```bash
# Clone the repo
git clone https://github.com/StingerMT/cep-target-analyzer.git
cd cep-target-analyzer

# Create and activate a virtual environment (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install PySide6 numpy opencv-python matplotlib

# Run the application
python -m cep_analyzer.main
```

Or use the included batch file which handles setup automatically:
```bash
run_analyzer.bat
```

---

## 📖 Usage

1. **Load Image** — Open your target photo
2. **Rotate** *(optional)* — Use "Rotate Image…" to straighten the image before analysis
3. **Set Scale** — Click two known points on the image, enter their real-world distance
4. **Set Origin** — Right-click the aiming point (target center)
5. **Mark Shots** — Left-click each shot hole
6. **Compute** — Calculate all metrics
7. **View Plot** — Inspect the scatter plot visualization
8. **Export** — Save results to CSV

---

## 🔧 Requirements

- Windows 10 / 11
- Python 3.8+ *(only needed if running from source)*
- PySide6, NumPy, OpenCV, Matplotlib *(auto-installed by `run_analyzer.bat`)*

---

## 🌍 Languages

- **English** — Full support
- **Hebrew (עברית)** — Full RTL support

---

## 🔮 Roadmap

- Additional language support (Arabic, Russian, French)
- PDF report generation
- Batch processing for multiple images
- Advanced statistics (R95, R99)
- Shot hole auto-detection (planned)

---

## 📝 License

[PolyForm Noncommercial 1.0.0](LICENSE) — Free for non-commercial use. Attribution required.
Commercial use requires explicit written permission from the author.
© 2025 Benji Abramovitz | [GitHub](https://github.com/StingerMT)

---

**Version**: 1.1.0 | **Last Updated**: 2025 | **Status**: Production Ready ✅
