# Build Checklist - v1.1.0

## Pre-Build Verification

### Files Present
- [ ] `assets/scroll icon 48x48.png` exists
- [ ] `assets/scroll icon 96x96.png` exists
- [ ] `assets/mmb icon.png` exists
- [ ] `assets/left click 50x50.png` exists
- [ ] `assets/left click 100x100.png` exists
- [ ] `assets/right click 48x48.png` exists
- [ ] `assets/right click 96x96.png` exists

### Configuration Updated
- [x] `build_exe.spec` includes assets folder
- [x] `CHANGELOG.md` updated to v1.1.0
- [x] `RELEASE_GUIDE.md` updated with v1.1 notes

### Code Ready
- [x] All diagnostics passing
- [x] No syntax errors
- [x] All translations complete
- [x] PyInstaller path handling for assets (sys._MEIPASS)

## Build Process

### Step 1: Clean Previous Builds
```bash
# Delete old build artifacts
rmdir /s /q build
rmdir /s /q dist
```

### Step 2: Run Build
```bash
# Run the build script
build_exe.bat
```

### Step 3: Verify Build Output
Check that `dist/CEP_Target_Analyzer.exe` exists and is ~150-200 MB

## Post-Build Testing

### Quick Smoke Test
1. [ ] Run the EXE (should start without errors)
2. [ ] Check shortcuts panel shows icons (not gray boxes or text)
3. [ ] Click shortcuts title to collapse/expand
4. [ ] Wait 5 seconds - shortcuts should fade to 35% opacity
5. [ ] Hover over shortcuts - should return to 100% opacity
6. [ ] Load an image
7. [ ] Check copyright watermark in bottom corner
8. [ ] Set scale (markers should be consistent size)
9. [ ] Add points
10. [ ] Compute metrics
11. [ ] Export CSV - check mean_x, mean_y, blocking_radius columns
12. [ ] Switch to Hebrew - verify RTL layout
13. [ ] Check shortcuts in Hebrew (icons on left, descriptions on right)

### Full Feature Test
- [ ] Open image
- [ ] Rotate image
- [ ] Set scale with presets
- [ ] Set origin
- [ ] Add multiple points
- [ ] Undo point
- [ ] Clear points
- [ ] Compute metrics
- [ ] View results dialog
- [ ] Show plot
- [ ] Save plot with results
- [ ] Export CSV
- [ ] Open preferences
- [ ] Change marker colors
- [ ] Switch language
- [ ] Close and reopen (settings persist)

## Known Issues to Check

### Assets Not Loading
**Symptom**: Gray boxes instead of icons in shortcuts
**Cause**: Assets folder not included in build
**Fix**: Verify `build_exe.spec` has `datas_list.append(('assets', 'assets'))`

### Shortcuts Not Collapsing
**Symptom**: Clicking title doesn't hide shortcuts
**Cause**: Settings not persisting
**Fix**: Check QSettings is working

### Fade Not Working
**Symptom**: Shortcuts don't fade after 5 seconds
**Cause**: Timer or opacity effect not initialized
**Fix**: Check console for errors

### Markers Wrong Size
**Symptom**: Markers too small or too large
**Cause**: View scale factor calculation issue
**Fix**: Test on different resolution monitors

## Distribution Package

### What to Include
```
CEP_Target_Analyzer_v1.1.0/
├── CEP_Target_Analyzer.exe    # Main executable
├── README.txt                  # Quick start guide
└── CHANGELOG.txt              # What's new in v1.1
```

### Optional Files
- Sample target images
- User manual PDF
- Video tutorial link

## Release Notes Template

```
CEP Target Analyzer v1.1.0 - "Polish & Precision"
Released: 2025-01-24

What's New:
✨ Collapsible shortcuts panel with icons
✨ View-based marker scaling (consistent across monitors)
✨ Auto-fade shortcuts after 5 seconds
✨ Copyright watermark
✨ Complete Hebrew translations
✨ CSV export includes mean_x, mean_y
✨ Renamed "furthest_from_mean" to "blocking_radius"

Bug Fixes:
🐛 Fixed shortcuts alignment in RTL
🐛 Fixed all untranslated strings
🐛 Fixed status bar messages in Hebrew
🐛 Fixed marker sizes on high-resolution images

Download: [Link to EXE]
Size: ~150-200 MB
Requirements: Windows 7+
```

---

**Checklist Complete**: Ready to build v1.1.0! 🚀
