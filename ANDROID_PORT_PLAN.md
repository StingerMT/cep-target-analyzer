# CEP Target Analyzer - Android Port Project Plan

## Project Overview
**Goal**: Port the desktop CEP Target Analyzer to Android (phones & tablets) with native mobile UX and camera integration.

**Version**: 2.0.0 - "Mobile Edition"
**Target Platforms**: Android 8.0+ (API 26+)
**Primary Devices**: Samsung tablets, Android phones

---

## Current Desktop Application Analysis

### Core Architecture (Desktop)
```
cep_analyzer/
├── __main__.py          # Entry point
├── ui_mainwindow.py     # Main window (340px left panel + image viewer)
├── image_viewer.py      # QGraphicsView with zoom/pan/drawing
├── dialogs.py           # Scale, Rotation, Results, Preferences dialogs
├── analysis.py          # Metrics computation (CEP50, ES, blocking radius)
├── i18n.py             # English/Hebrew translations
├── settings_manager.py  # QSettings persistence
└── detection.py         # (Optional) Auto-detection
```

### Key Features to Port
1. **Image Loading**: File picker → Camera + Gallery
2. **Scale Setting**: Two-point calibration with presets
3. **Origin Setting**: Tap to set (0,0)
4. **Shot Marking**: Tap to add, long-press to remove
5. **Rotation**: Fine-tune with slider
6. **Metrics Calculation**: CEP50, ES, σx, σy, mrad
7. **Results Display**: Floating dialog with metrics
8. **Export**: CSV + PNG → Share intent
9. **Bilingual**: English + Hebrew (RTL)
10. **Zoom/Pan**: Pinch-to-zoom, drag to pan

### Current UI Layout (Desktop)
- **Left Panel (340px)**: Vertical button stack
  - Open Image
  - Rotate Image
  - Set Scale (step 1)
  - Set Origin (step 2)
  - Add Points (step 3)
  - Undo/Clear/Fit controls
  - Distance input
  - Compute Metrics
  - Show Plot
  - Export CSV
  - Collapsible Shortcuts
- **Right Panel**: Image viewer with overlays
- **Status Bar**: Context messages (bottom)

---

## Android Port Strategy

### Technology Stack Options

#### Option 1: PySide6 + Buildozer (Recommended for MVP)
**Pros:**
- Reuse 90% of existing Python code
- Qt for Android supports touch gestures
- Buildozer packages Python apps for Android
- Maintain single codebase

**Cons:**
- Larger APK size (~50-80MB)
- Not native performance
- Camera integration requires platform-specific code

#### Option 2: Kivy + Buildozer
**Pros:**
- Designed for mobile from ground up
- Better touch support
- Smaller APK than PySide6

**Cons:**
- Complete UI rewrite
- Different widget system
- Less polished than Qt

#### Option 3: Native Kotlin/Java
**Pros:**
- Best performance
- Native camera integration
- Smallest APK

**Cons:**
- Complete rewrite from scratch
- Separate codebase to maintain
- Longer development time

**DECISION**: Start with **PySide6 + Buildozer** for fastest time-to-market, can rewrite native later if needed.

---

## Mobile UI/UX Design

### Layout Strategy: Adaptive Single-Screen

#### Portrait Mode (Phones)
```
┌─────────────────────┐
│  [≡] CEP Analyzer   │ ← Top bar with hamburger menu
├─────────────────────┤
│                     │
│   Image Viewer      │ ← Full screen image area
│   (with overlays)   │
│                     │
│                     │
├─────────────────────┤
│ [📷] [⚙️] [📊] [⤴️] │ ← Bottom action bar (4 icons)
└─────────────────────┘
```

#### Landscape Mode (Tablets)
```
┌──────────────────────────────────────┐
│ [≡] CEP Analyzer    [📷] [⚙️] [📊] [⤴️] │ ← Top bar
├──────────────────────────────────────┤
│                                      │
│        Image Viewer (full width)     │
│        (with overlays)               │
│                                      │
└──────────────────────────────────────┘
```

### Navigation: Hamburger Menu (Slide-out Drawer)

**Menu Structure:**
```
┌─────────────────────┐
│ CEP Target Analyzer │
├─────────────────────┤
│ 📷 Capture/Load     │ ← Camera or gallery
│ 🔄 Rotate Image     │
│ 📏 Set Scale        │
│ 🎯 Set Origin       │
│ 📍 Add Points       │
│ ↩️  Undo            │
│ 🗑️  Clear Points    │
│ 📐 Distance (100m)  │ ← Expandable
│ 🧮 Compute          │
│ 📊 Show Results     │
│ 💾 Export & Share   │
├─────────────────────┤
│ ⚙️  Settings        │
│ 🌐 Language         │
│ ℹ️  About           │
└─────────────────────┘
```

### Bottom Action Bar (Quick Access)
1. **📷 Camera**: Capture or load image
2. **⚙️ Mode**: Toggle between Scale/Origin/Points modes
3. **📊 Results**: Show metrics (disabled until computed)
4. **⤴️ Share**: Export and share (disabled until computed)

### Gesture Controls
- **Single Tap**: Add point (in add points mode)
- **Long Press**: Remove nearest point
- **Pinch**: Zoom in/out
- **Two-Finger Drag**: Pan image
- **Double Tap**: Fit to screen
- **Swipe from Left**: Open menu drawer

---

## Feature Mapping: Desktop → Mobile

| Desktop Feature | Mobile Implementation | Notes |
|----------------|----------------------|-------|
| File Open Dialog | Camera + Gallery picker | Use Android intents |
| Left Panel Buttons | Hamburger menu | Slide-out drawer |
| Rotation Dialog | Bottom sheet slider | 0-360° with live preview |
| Scale Dialog | Bottom sheet with presets | Same logic, mobile UI |
| Origin Setting | Tap mode | Visual feedback |
| Point Adding | Tap mode | Long-press to remove |
| Undo/Clear | Menu items | Confirmation dialog |
| Distance Input | Bottom sheet spinner | Quick presets (25m, 50m, 100m, 200m) |
| Compute Button | Menu item | Shows progress |
| Results Dialog | Bottom sheet | Scrollable metrics |
| Plot Display | Full-screen dialog | Pinch to zoom |
| CSV Export | Share intent | Multiple apps |
| Shortcuts Panel | Remove | Not needed on mobile |
| Status Bar | Snackbar messages | Android standard |
| Preferences | Settings screen | Standard Android |

---

## Camera Integration

### Workflow
1. User taps **📷 Camera** button
2. Options appear:
   - **Take Photo** → Opens camera
   - **Choose from Gallery** → Opens file picker
3. Photo captured/selected
4. Image loaded into viewer
5. Proceed with analysis

### Implementation
```python
# Android-specific camera code (via Pyjnius)
from jnius import autoclass

# Camera intent
Intent = autoclass('android.content.Intent')
MediaStore = autoclass('android.provider.MediaStore')

def capture_photo():
    intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
    # Handle result in onActivityResult
```

### Permissions Required
- `CAMERA`: For taking photos
- `READ_EXTERNAL_STORAGE`: For gallery access
- `WRITE_EXTERNAL_STORAGE`: For saving exports

---

## Share Functionality

### Android Share Intent
```python
from jnius import autoclass

def share_files(csv_path, png_path):
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    
    intent = Intent(Intent.ACTION_SEND_MULTIPLE)
    intent.setType("*/*")
    
    # Attach files
    files = ArrayList()
    files.add(Uri.fromFile(File(csv_path)))
    files.add(Uri.fromFile(File(png_path)))
    
    intent.putParcelableArrayListExtra(Intent.EXTRA_STREAM, files)
    intent.putExtra(Intent.EXTRA_SUBJECT, "CEP Analysis Results")
    
    # Show chooser
    chooser = Intent.createChooser(intent, "Share Results")
    activity.startActivity(chooser)
```

### Share Options
- **CSV Only**: Share just the data
- **PNG Only**: Share just the plot
- **Both**: Share CSV + PNG together
- **Target Apps**: WhatsApp, Drive, Email, etc.

---

## Code Reuse Strategy

### Keep As-Is (90% reuse)
- ✅ `analysis.py` - All calculation logic
- ✅ `i18n.py` - Translation system
- ✅ Core logic in `image_viewer.py` (coordinate math)
- ✅ Settings persistence (adapt QSettings)

### Adapt for Mobile
- 🔄 `ui_mainwindow.py` → `ui_mobile.py`
  - Replace left panel with drawer menu
  - Add bottom action bar
  - Responsive layout
- 🔄 `dialogs.py` → `mobile_dialogs.py`
  - Convert to bottom sheets
  - Touch-friendly controls
- 🔄 `image_viewer.py`
  - Already has touch support!
  - Add tap handlers for mobile
  - Optimize for smaller screens

### Add New (Mobile-specific)
- ➕ `camera_handler.py` - Camera integration
- ➕ `share_handler.py` - Android share intents
- ➕ `permissions.py` - Runtime permission requests
- ➕ `mobile_gestures.py` - Enhanced touch handling

---

## Development Phases

### Phase 1: Setup & Infrastructure (Week 1)
- [ ] Install Buildozer and dependencies
- [ ] Create `buildozer.spec` configuration
- [ ] Set up Android SDK/NDK
- [ ] Test basic "Hello World" APK build
- [ ] Configure permissions in manifest

### Phase 2: Core UI Migration (Week 2)
- [ ] Create `ui_mobile.py` with drawer menu
- [ ] Implement bottom action bar
- [ ] Port image viewer to mobile layout
- [ ] Add responsive sizing for phones/tablets
- [ ] Test on emulator

### Phase 3: Camera Integration (Week 3)
- [ ] Implement camera capture via Pyjnius
- [ ] Add gallery picker
- [ ] Handle image rotation (EXIF)
- [ ] Test on physical device
- [ ] Add permission requests

### Phase 4: Touch Interactions (Week 4)
- [ ] Adapt scale setting for touch
- [ ] Adapt origin setting for touch
- [ ] Adapt point adding for touch
- [ ] Implement long-press to remove
- [ ] Test gesture conflicts

### Phase 5: Dialogs & Sheets (Week 5)
- [ ] Convert rotation dialog to bottom sheet
- [ ] Convert scale dialog to bottom sheet
- [ ] Convert results to bottom sheet
- [ ] Convert preferences to settings screen
- [ ] Add distance picker

### Phase 6: Export & Share (Week 6)
- [ ] Implement file saving to app directory
- [ ] Add share intent for CSV
- [ ] Add share intent for PNG
- [ ] Add combined share option
- [ ] Test with WhatsApp, Drive, Email

### Phase 7: Polish & Testing (Week 7)
- [ ] Add loading indicators
- [ ] Add snackbar messages
- [ ] Optimize for different screen sizes
- [ ] Test on multiple devices
- [ ] Fix RTL layout issues
- [ ] Add app icon and splash screen

### Phase 8: Release (Week 8)
- [ ] Build signed APK
- [ ] Test on Samsung tablets
- [ ] Create Play Store listing
- [ ] Write user documentation
- [ ] Submit to Play Store

---

## Technical Challenges & Solutions

### Challenge 1: APK Size
**Problem**: PySide6 + Python creates large APKs (50-80MB)
**Solutions**:
- Use `--requirements` to include only needed modules
- Exclude unused Qt modules
- Use ProGuard for code shrinking
- Consider Kivy if size is critical

### Challenge 2: Camera Quality
**Problem**: Need high-resolution photos for accurate analysis
**Solutions**:
- Request full resolution in camera intent
- Handle large images efficiently (downsample for display, full-res for analysis)
- Add image quality settings

### Challenge 3: Performance
**Problem**: Matplotlib rendering may be slow on mobile
**Solutions**:
- Use lower DPI for mobile plots (96 instead of 160)
- Cache rendered plots
- Show progress indicator during computation
- Consider using Qt's native plotting instead

### Challenge 4: Screen Real Estate
**Problem**: Limited space for controls
**Solutions**:
- Hamburger menu for primary actions
- Bottom sheets for dialogs
- Floating action button for primary action
- Collapsible sections in results

### Challenge 5: File Management
**Problem**: Android scoped storage restrictions
**Solutions**:
- Save to app-specific directory (no permission needed)
- Use share intent instead of direct file access
- Use MediaStore API for gallery integration

---

## File Structure (Android Port)

```
cep_analyzer_mobile/
├── buildozer.spec           # Buildozer configuration
├── main.py                  # Android entry point
├── cep_analyzer/
│   ├── __init__.py
│   ├── ui_mobile.py         # Mobile main window
│   ├── mobile_dialogs.py    # Bottom sheets
│   ├── image_viewer.py      # Adapted for mobile
│   ├── camera_handler.py    # NEW: Camera integration
│   ├── share_handler.py     # NEW: Share intents
│   ├── permissions.py       # NEW: Permission handling
│   ├── analysis.py          # REUSED: Same as desktop
│   ├── i18n.py             # REUSED: Same as desktop
│   └── settings_manager.py  # ADAPTED: Android storage
├── assets/
│   ├── icon.png            # App icon
│   ├── splash.png          # Splash screen
│   └── icons/              # UI icons
└── README_ANDROID.md       # Android-specific docs
```

---

## Buildozer Configuration

```ini
[app]
title = CEP Target Analyzer
package.name = ceptargetanalyzer
package.domain = com.benjiabramovitz

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 2.0.0

requirements = python3,pyside6,numpy,matplotlib,pillow

permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

orientation = sensor
fullscreen = 0

android.api = 31
android.minapi = 26
android.ndk = 25b
android.sdk = 31

[buildozer]
log_level = 2
warn_on_root = 1
```

---

## Testing Strategy

### Emulator Testing
- Android Studio emulator
- Various screen sizes (phone, tablet)
- Different Android versions (8.0, 10, 12, 13)

### Physical Device Testing
- Samsung Galaxy Tab (primary target)
- Samsung Galaxy Phone
- Generic Android phone
- Test camera on real devices

### Test Cases
1. ✅ Camera capture and load
2. ✅ Gallery image selection
3. ✅ Pinch zoom and pan
4. ✅ Scale setting with touch
5. ✅ Origin setting with tap
6. ✅ Point adding with tap
7. ✅ Point removal with long-press
8. ✅ Metrics computation
9. ✅ Results display
10. ✅ CSV export and share
11. ✅ PNG export and share
12. ✅ Language switching (EN/HE)
13. ✅ RTL layout in Hebrew
14. ✅ Rotation across orientations
15. ✅ Settings persistence

---

## Success Criteria

### Must Have (MVP)
- ✅ Camera capture working
- ✅ Gallery selection working
- ✅ Touch-based scale/origin/points
- ✅ Metrics calculation accurate
- ✅ Share to WhatsApp/Drive
- ✅ English + Hebrew support
- ✅ Works on phones and tablets

### Should Have
- ✅ Smooth 60fps interactions
- ✅ Professional UI/UX
- ✅ Proper error handling
- ✅ Loading indicators
- ✅ Offline functionality

### Nice to Have
- ⭐ Auto-detection of shot holes
- ⭐ Cloud sync of results
- ⭐ History of past analyses
- ⭐ Comparison mode (multiple targets)
- ⭐ AR overlay for live shooting

---

## Timeline Estimate

**Total**: 8 weeks (2 months)
- Weeks 1-2: Setup + Core UI
- Weeks 3-4: Camera + Touch
- Weeks 5-6: Dialogs + Share
- Weeks 7-8: Polish + Release

**Accelerated**: 4 weeks (1 month) for MVP
- Focus on core features only
- Skip advanced polish
- Basic UI acceptable

---

## Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Set up environment** - Install Buildozer, Android SDK
3. **Create mobile branch** - `git checkout -b android-port`
4. **Start Phase 1** - Basic APK build test
5. **Iterate rapidly** - Test on device early and often

---

## Questions to Resolve

1. **Target Android version**: Minimum API 26 (Android 8.0) OK?
2. **APK size acceptable**: 50-80MB acceptable for initial release?
3. **Play Store**: Planning to publish on Google Play?
4. **Monetization**: Free app or paid? Ads?
5. **Priority devices**: Samsung tablets most important?
6. **Feature priority**: Which features are must-have for v1?

---

**Status**: 📋 Planning Complete - Ready for Implementation
**Next**: Environment setup and Phase 1 execution
