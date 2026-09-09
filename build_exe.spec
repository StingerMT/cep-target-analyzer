# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CEP Target Analyzer
Builds a standalone Windows executable with all dependencies bundled.
"""

block_cipher = None

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

# Find PySide6 location
try:
    import PySide6
    pyside6_path = os.path.dirname(PySide6.__file__)
    qt_plugins_path = os.path.join(pyside6_path, 'plugins')
    
    # Only add plugins if they exist
    datas_list = []
    if os.path.exists(os.path.join(qt_plugins_path, 'platforms')):
        datas_list.append((os.path.join(qt_plugins_path, 'platforms'), 'PySide6/plugins/platforms'))
    if os.path.exists(os.path.join(qt_plugins_path, 'styles')):
        datas_list.append((os.path.join(qt_plugins_path, 'styles'), 'PySide6/plugins/styles'))
    
    # Add qdarktheme data
    try:
        datas_list.extend(collect_data_files('qdarktheme'))
    except:
        pass
except:
    datas_list = []

# Add assets folder (icons for shortcuts)
assets_path = os.path.join(os.path.dirname(os.path.abspath('.')), 'assets')
if os.path.exists('assets'):
    datas_list.append(('assets', 'assets'))

a = Analysis(
    ['cep_analyzer/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas_list,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtPrintSupport',
        'matplotlib',
        'matplotlib.backends.backend_qtagg',
        'matplotlib.backends.backend_qt5agg',
        'numpy',
        'PIL',
        'PIL.Image',
        'qdarktheme',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',  # Exclude unused GUI frameworks
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CEP_Target_Analyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: 'icon.ico'
)
