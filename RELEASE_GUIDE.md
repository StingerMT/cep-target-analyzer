# Release Guide - CEP Target Analyzer v1.0

## Building the Executable

### Prerequisites
1. Python 3.8 or higher installed
2. All dependencies installed: `pip install -r requirements.txt`
3. PyInstaller: `pip install pyinstaller`

### Build Steps

**Option 1: Using the build script (Recommended)**
```bash
build_exe.bat
```

**Option 2: Manual build**
```bash
pyinstaller build_exe.spec --clean
```

### Build Output
- Executable: `dist/CEP_Target_Analyzer.exe`
- Size: ~150-200 MB (includes Python runtime and all libraries)
- Standalone: No installation required, runs on any Windows PC

## Distribution

### What to Distribute
You can distribute either:
1. **Single EXE**: Just `CEP_Target_Analyzer.exe` (if using --onefile mode)
2. **Folder**: The entire `dist` folder (faster startup, recommended)

### User Requirements
- Windows 7 or higher
- No Python installation needed
- No additional dependencies needed
- ~200 MB disk space

## Testing the Build

1. Copy the `dist` folder to a clean Windows machine (without Python)
2. Run `CEP_Target_Analyzer.exe`
3. Test all features:
   - Load image
   - Set scale
   - Set origin
   - Add points
   - Compute metrics
   - Export CSV
   - Save plot
   - Switch language

## Troubleshooting

### Build Fails
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Try cleaning: Delete `build` and `dist` folders, then rebuild
- Check Python version: `python --version` (should be 3.8+)

### EXE Won't Run
- Check Windows Defender/Antivirus (may flag unsigned EXE)
- Run from command line to see error messages
- Ensure all DLL files are in the same folder as EXE

### Missing Features
- Check `hiddenimports` in `build_exe.spec`
- Add any missing modules to the spec file

## Code Signing (Optional)

For production distribution, consider code signing:
1. Obtain a code signing certificate
2. Use `signtool` to sign the EXE
3. This prevents Windows SmartScreen warnings

## Version Updates

When releasing a new version:
1. Update version in `CHANGELOG.md`
2. Update version in `README.md`
3. Rebuild the executable
4. Test thoroughly
5. Create release notes
6. Tag the release in version control

## File Structure

```
dist/
├── CEP_Target_Analyzer.exe    # Main executable
├── _internal/                   # Supporting files (if not --onefile)
│   ├── Python DLLs
│   ├── Qt libraries
│   └── Other dependencies
```

## Performance Notes

- First launch may be slower (Windows scanning)
- Subsequent launches are faster
- Startup time: 2-5 seconds typical
- Memory usage: ~100-150 MB

## Known Issues

- Windows Defender may show warning on first run (unsigned EXE)
- Some antivirus software may quarantine the EXE
- Solution: Add exception or code sign the executable

## Version 1.1 Specific Notes

### Assets Folder
Version 1.1 includes icon assets for the shortcuts panel. Ensure these are bundled:
- `assets/scroll icon 48x48.png`
- `assets/scroll icon 96x96.png`
- `assets/mmb icon.png`
- `assets/left click 50x50.png`
- `assets/left click 100x100.png`
- `assets/right click 48x48.png`
- `assets/right click 96x96.png`

The `build_exe.spec` file should include:
```python
datas_list.append(('assets', 'assets'))
```

### CRITICAL: PyInstaller Path Handling
The code now properly handles PyInstaller's bundled environment using `sys._MEIPASS`:
```python
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in normal Python environment
    base_path = os.path.dirname(os.path.dirname(__file__))
```
This ensures assets load correctly in both development and bundled environments.

### Verification Checklist
After building v1.1, verify:
- ✅ Shortcuts panel shows icons (not gray boxes)
- ✅ Collapsible shortcuts work
- ✅ Auto-fade after 5 seconds
- ✅ Copyright watermark visible in image viewer
- ✅ All translations working
- ✅ View-based marker scaling working

---

**Build Date**: 2025-01-24
**Version**: 1.1.0 "Polish & Precision"
**Status**: Production Ready ✅
