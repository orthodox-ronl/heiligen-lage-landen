@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --pip-r requirements.txt --import yaml --import jsonschema
if errorlevel 1 exit /b 1
python scripts\validate.py %*
exit /b %ERRORLEVEL%
