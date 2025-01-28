@echo off
pip install PyQt5
start /B pythonw SudokuSolver.py
taskkill /IM cmd.exe /F