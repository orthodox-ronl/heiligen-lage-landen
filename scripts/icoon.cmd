@echo off
setlocal
cd /d "%~dp0.."
call "%~dp0_ensure.cmd" --pip-r requirements.txt --import yaml --import PIL
if errorlevel 1 exit /b 1
python "%~dp0icoon.py" %*
exit /b %ERRORLEVEL%
