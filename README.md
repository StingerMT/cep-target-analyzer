# CEP Target Analyzer v1.0

**Professional ballistic target analysis tool with bilingual support (English/Hebrew)**

**Version 1.0** - Production Ready ✅

A professional ballistic target analysis application with full bilingual support (English/Hebrew) and advanced image rotation capabilities.

---

## 🎯 What It Does

Analyzes shooting target images to calculate precision metrics:
- Mean Hit Point (Napam)
- Standard Deviation (Sigma X/Y)
- Blocking Radius
- Extreme Spread
- CEP50 (Circular Error Probable)
- Distance from Mean to Origin

---

## ✨ Key Features

### 🌍 True Bilingual Support
- **English** (LTR) and **Hebrew** (RTL) with automatic layout switching
- All UI elements, dialogs, and plots fully translated
- Hebrew text displays correctly in matplotlib plots

### 🔄 Advanced Rotation System
- **Quick rotations**: 90° increments
- **Fine-tuned rotation**: Custom angles with live preview
- Slider control with 0.1° precision
- Smart locking after scale to prevent errors

### 📊 Enhanced Visualization
- Professional scatter plots with multiple visual elements
- Draggable legend
- Radius lines, extreme spread indicators
- Save plots as PNG

### 💾 Persistent Settings
- Window position and size remembered
- Language and theme preferences saved
- Recent files tracking

### 🎨 Theme Support
- System, Light, and Dark themes
- Instant preview with optional restart

---

## 🚀 Quick Start

### Installation
```bash
# Clone or download the project
cd cep_analyzer_modular_with_plot1old

# Activate virtual environment (Windows)
.\.venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install PySide6 numpy opencv-python matplotlib

# Run the application
python -m cep_analyzer.main
```

### Or use the batch file:
```bash
run_analyzer.bat
```

---

## 📖 Usage

1. **Load Image** - Open your target image
2. **Rotate** (optional) - Use "Rotate Image…" for precise angle adjustment
3. **Set Scale** - Click two known points, enter real distance
4. **Set Origin** - Click the target center
5. **Add Points** - Click manually or use "Auto-Detect"
6. **Compute** - Calculate all metrics
7. **View Plot** - See visual analysis
8. **Export** - Save results to CSV

---

## 📚 Documentation

- **[README.md](README.md)** - This file — overview and quick start
- **[CHANGELOG.md](CHANGELOG.md)** - Full version history
- **[BUILD_CHECKLIST.md](BUILD_CHECKLIST.md)** - How to build the EXE yourself
- **[RELEASE_GUIDE.md](RELEASE_GUIDE.md)** - Release process notes

---

## 🔧 Requirements

- Python 3.8+
- PySide6
- NumPy
- OpenCV (cv2)
- Matplotlib

---

## 📊 Calculated Metrics

| Metric | Description |
|--------|-------------|
| **Napam X, Y** | Mean Hit Point coordinates |
| **Sigma X, Y** | Horizontal/Vertical standard deviation |
| **Blocking Radius** | Furthest point from mean |
| **Extreme Spread** | Maximum distance between any two points |
| **Distance Napam-Napar** | Mean to origin distance |
| **CEP50** | Median radius (50% circular error) |

All results displayed in **cm** with **2 decimal places**.

---

## 🌍 Languages

- **English** - Full support
- **Hebrew** - Full support with RTL layout

Want to add more? See [ADDING_LANGUAGES.md](cep_analyzer/README.md)

---

## 🎨 Screenshots

### English Interface (LTR)
- Clean, intuitive layout
- Professional appearance
- All controls clearly labeled

### Hebrew Interface (RTL)
- Proper right-to-left layout
- Hebrew text displays correctly
- All dialogs mirror appropriately

### Enhanced Plots
- Multiple visual elements
- Draggable legend
- Professional appearance
- Translated labels

---

## 🏆 Status

**✅ COMPLETE & PRODUCTION READY**

All planned features implemented, tested, and documented.

---

## 📝 License

[CC BY-NC 4.0](LICENSE) — Free for personal and non-commercial use. Attribution required.  
Commercial use requires explicit permission from the author.  
© 2025 Benji Abramovitz

---

## 👨‍💻 Developer Notes

- Clean architecture with separation of concerns
- Type hints throughout
- Comprehensive error handling
- Easy to extend and modify
- Well-documented code

---

## 🔮 Future Ideas

- Additional languages (Spanish, French, Arabic, Russian)
- Batch processing mode
- Milliradian spread calculation
- PDF report generation
- Advanced statistics (R95, R99)

---

**Last Updated**: November 13, 2025  
**Version**: 1.0  
**Status**: Production Ready ✅
