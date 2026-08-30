@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --pip-r requirements.txt --import yaml --import PIL
if errorlevel 1 exit /b 1
python scripts\icoon_toevoegen.py %*
exit /b %ERRORLEVEL%
