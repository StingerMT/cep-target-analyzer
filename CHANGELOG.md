# Changelog - CEP Target Analyzer

## Version 1.1.0 - "Polish & Precision" Release (2025-01-24)

### 🎨 Major UI Enhancements

#### Collapsible Shortcuts Panel
- **Smart Shortcuts Guide**: Professional keyboard shortcut reference with styled badges and icons
- **Collapsible Design**: Click title to expand/collapse, remembers state across sessions
- **Auto-Fade**: Fades to 35% opacity after 5 seconds of inactivity, returns on hover
- **Icon-Based**: Mouse icons (scroll, left-click, middle-click, right-click) replace text
- **Keyboard Badges**: Styled Ctrl, Space, F keys with consistent height and monospace font
- **RTL Support**: Proper right-to-left layout in Hebrew with correct arrow directions (◀/▼)
- **Default Open**: Expanded on first launch for discoverability

#### View-Based Marker Scaling
- **Resolution-Independent**: Marker sizes now based on viewport dimensions, not image resolution
- **Monitor Adaptive**: Automatically scales for 1080p, 1440p, 4K displays
- **Window-Responsive**: Markers scale proportionally when window is resized
- **Zoom-Aware**: Markers maintain consistent visual size at all zoom levels
- **Consistent Appearance**: Same visual marker size across different image resolutions

#### Visual Polish
- **Copyright Watermark**: Subtle "© Benji Abramovitz, 2025" in bottom corner (left for Hebrew, right for English)
- **Elegant Typography**: Segoe UI Light font with transparency for unobtrusive branding
- **Improved Badge Styling**: Larger padding (4px 8px), min-height 20px, font size 11px
- **Better Alignment**: Fixed RTL/LTR alignment issues in shortcuts panel

### 🔧 Bug Fixes & Improvements

#### Translation & Localization
- **Complete Translation Coverage**: All hardcoded English strings now properly translated
- **Status Messages**: "Image rotated", error messages, dialog titles all localized
- **Consistent Terminology**: Standardized "blocking_radius" terminology in CSV exports

#### CSV Export Enhancements
- **Mean Position Values**: Added mean_x and mean_y to CSV export
- **Renamed Column**: "furthest_from_mean" → "blocking_radius" for clarity
- **Better Data Completeness**: All calculated metrics now included in export

#### UI Fixes
- **Shortcuts Alignment**: Fixed text overflow and alignment issues in both RTL and LTR
- **Removed Padding**: Eliminated right-side padding for proper UI alignment
- **Title Color**: Changed from gray (#888) to light (#e0e0e0) for better visibility
- **Grid Layout**: Proper column alignment for description and icon columns

### 🎯 Technical Improvements

#### Marker Rendering System
- **Dynamic Pen Scaling**: Pen widths scale with viewport size (7px, 4px, 3px base sizes)
- **View Scale Factor**: Calculates based on viewport diagonal relative to 1080p reference
- **Monitor Detection**: Automatically detects screen resolution and adjusts scaling
- **Transform Compensation**: Accounts for current zoom level to maintain visual consistency

#### Settings Management
- **Shortcuts State**: Persists expanded/collapsed state of shortcuts panel
- **Opacity Effects**: Smooth QPropertyAnimation for fade transitions (500ms)
- **Hover Detection**: Mouse tracking for automatic fade reset on interaction

### 📝 Code Quality

#### Architecture
- **Helper Methods**: `_get_view_scale_factor()` for consistent scaling calculations
- **Opacity Management**: Persistent QGraphicsOpacityEffect with animation support
- **Event Handling**: Proper enterEvent override for hover detection
- **Timer Management**: Single-shot timers for fade delays with proper cleanup

#### Maintainability
- **Reduced Duplication**: Centralized view scaling logic
- **Better Comments**: Clear documentation of RTL/LTR layout decisions
- **Cleaner Code**: Removed unnecessary `.split()` logic from shortcuts

---

## Version 1.0.0 - Production Release

### Core Features
- **Image Analysis**: Load target images and analyze shot groupings
- **Scale Setting**: Set scale using two known points with preset options (A4, A5, Letter, etc.)
- **Origin Setting**: Define coordinate system origin (0,0) with right-click to clear
- **Shot Point Marking**: Add shot points with left-click, remove with right-click
- **Metrics Calculation**: Compute CEP50, extreme spread, standard deviations, and milliradian values
- **Visual Plot**: Interactive matplotlib plot with legend and measurements
- **CSV Export**: Export all metrics and coordinates to CSV format
- **Bilingual Support**: Full English and Hebrew (RTL) interface

### User Interface
- **Dark Theme**: Modern dark interface using qdarktheme
- **Floating Results Dialog**: Draggable, borderless metrics display
- **Status Bar Tooltips**: Context-sensitive help messages
- **Zoom & Pan**: Mouse wheel zoom, Space+drag or middle-click pan
- **Image Rotation**: Fine-tune image rotation with live preview
- **Fixed Window Size**: 70% of screen, respects taskbar position
- **Scrollable Left Panel**: Accommodates all controls at any screen size

### Measurements & Calculations
- **Units**: Support for mm, cm, and inches with Hebrew localization (ס"מ, אינצ)
- **Zoom-Independent**: All calculations use scene coordinates (not affected by zoom)
- **MATLAB-Compatible**: Standard deviation uses n-1 (sample std), Y-axis flipped
- **Milliradian Calculations**: Automatic mrad conversion based on target distance
- **CEP50**: Median radius from mean (50% circular error probable)
- **Extreme Spread**: Maximum distance between any two shots
- **Blocking Radius**: Furthest shot from mean point

### Plot Features
- **Clean Visualization**: Shot points, origin, mean, blocking radius circle, extreme spread line
- **RTL Support**: Proper Hebrew text rendering with correct parentheses direction
- **Legend**: Draggable legend with proper RTL ordering
- **Radius Line**: Visual red line from mean to circle edge
- **Export Options**: Save plot with or without results dialog side-by-side
- **Auto-Folder Creation**: Saves to folder named after image file

### Robustness & Safety
- **Input Validation**: All numeric inputs validated, prevents division by zero
- **Error Handling**: Graceful error messages, no crashes on invalid input
- **File System Protection**: Handles permission errors, creates directories safely
- **State Management**: Complete reset when loading new images
- **Undo Functionality**: Undo last point or clear origin
- **Cancel Protection**: Scale dialog cancel clears the line properly

### Localization
- **Hebrew (עברית)**: Full RTL support with proper text alignment
- **Unit Translation**: cm → ס"מ, mrad → אלפיות
- **Dialog Translation**: All buttons, labels, and messages translated
- **Number Formatting**: RTL mark for proper number alignment in Hebrew
- **Preset Translation**: Paper sizes in Hebrew (רוחב/אורך for width/length)

### Visual Improvements
- **Scale Line**: Thick (5px), high-contrast teal dashed line for visibility
- **Fade-in Animation**: 800ms smooth fade-in on startup
- **Green Checkmarks**: Visual confirmation when steps completed
- **Center-Aligned Values**: Clean, consistent metrics display
- **Fixed Width Panel**: 320px left panel prevents overlap

### File Management
- **Auto-Output Folders**: Creates folder named after image for organized exports
- **CSV Format**: Clean CSV with coordinates, metrics, and mrad calculations
- **PNG Export**: High-quality plot export (160 DPI)
- **Combined Export**: Optional plot + results dialog in single image
- **Recent Files**: Remembers last opened directory

### Settings & Persistence
- **Window Position**: Remembers window size and position
- **Language Preference**: Saves selected language
- **Last File Path**: Remembers last opened directory
- **Splitter State**: Remembers panel sizes
- **Distance Setting**: Remembers target distance for mrad calculations

### Exit & Restart
- **Exit Confirmation**: Prevents accidental closure (ESC key or close button)
- **Skip on Restart**: No confirmation when restarting for language change
- **State Saving**: All settings saved before exit

### Bug Fixes
- Mouse cursor alignment at all zoom levels
- Origin can be reset (right-click or undo)
- Scale dialog cancel clears the line
- Results dialog values properly aligned in Hebrew
- Plot parentheses correct direction in Hebrew
- First metric (number of shots) properly aligned in Hebrew
- Negative numbers display correctly in Hebrew (minus sign after number)
- Compute button requires scale, origin, AND points
- Image viewer can shrink properly (no overlap)

### Technical Details
- **Framework**: PySide6 (Qt6)
- **Plotting**: Matplotlib
- **Image Processing**: PIL/Pillow
- **Math**: NumPy for calculations
- **Coordinate System**: Scene coordinates for zoom independence
- **File Encoding**: UTF-8 for international character support

---

## Development Notes

### Architecture
- Modular design with separate files for UI, analysis, dialogs, i18n, settings
- Signal/slot pattern for component communication
- Translator class for centralized localization
- Settings manager for persistent configuration

### Code Quality
- Type hints throughout
- Comprehensive error handling
- Input validation on all user inputs
- No SQL injection risk (desktop app, no database)
- Protected against division by zero
- Graceful fallbacks for file system errors

### Future Enhancements (TODO)
- [ ] Executable packaging (PyInstaller)
- [ ] Auto-detection of shot holes
- [ ] Additional language support
- [ ] Batch processing multiple images
- [ ] Custom color schemes
- [ ] Export to additional formats (PDF, Excel)

---

**Release Date**: 2025
**License**: CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0)
**Author**: Benji Abramovitz
