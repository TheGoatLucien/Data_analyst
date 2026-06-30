@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo  Detecteur de somnolence (mode OpenCV) - lancement
echo ============================================================

set "PY="
py -3.12 -c "print(1)" >nul 2>&1 && set "PY=py -3.12"
if not defined PY if exist "C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe" set "PY=C:\Users\User\AppData\Local\Programs\Python\Python312\python.exe"
if not defined PY set "PY=python"

echo Python utilise :
%PY% --version
echo.
echo Verification d'OpenCV et NumPy...
%PY% -m pip install --quiet --disable-pip-version-check opencv-python numpy

echo.
echo Lancement du detecteur (fenetre webcam). Touche Q pour quitter.
%PY% "detecteur_somnolence.py"

echo.
echo Programme termine.
pause
