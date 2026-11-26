@echo off
cd /d "%~dp0"
title LeafGuard 132-class demo
echo ============================================
echo  LeafGuard 132-class demo
echo  Keep this window OPEN.  Browser: http://127.0.0.1:8011/
echo ============================================
start "" cmd /c "timeout /t 20 >nul & start http://127.0.0.1:8011/"
".venv\Scripts\python.exe" scripts\serve_demo.py --checkpoint results\combined132\seed42\e3\checkpoints\resnet18_best.pt --port 8011
pause
