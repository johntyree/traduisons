set /p VER=<LATEST-IS
python setup.py py2exe
makensis traduisons_installer.nsi
copy traduisons_installer.exe Z:\traduisons_%VER%_win32.exe
del /f /s /q traduisons_installer.exe build dist traduisons.pyc
rmdir /s /q build dist