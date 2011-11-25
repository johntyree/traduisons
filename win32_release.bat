@echo off
for /f "delims=" %%a in ('python setup.py --version') do @set VER=%%a
python setup.py py2exe
mkdir dist\data
copy /V traduisons\data dist\data
makensis traduisons_installer.nsi
@echo on
copy traduisons_installer.exe Z:\traduisons-%VER%-win32.exe
@echo off
del /f /s /q build dist traduisons.pyc
rmdir /s /q build dist
echo "Copied: .\traduisons_installer.exe -> Z:\traduisons-%VER%-win32.exe"
