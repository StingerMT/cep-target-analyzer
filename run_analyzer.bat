
@echo off
setlocal

if not exist .venv (
  py -3 -m venv .venv
)

call .venv\Scripts\activate

python -m pip show PySide6 >nul 2>&1
if errorlevel 1 (
  python -m pip install --upgrade pip
  python -m pip install PySide6 pyqtdarktheme pymupdf matplotlib
)

python -m cep_analyzer.main

pause
