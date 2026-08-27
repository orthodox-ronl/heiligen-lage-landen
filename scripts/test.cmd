@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --pip-r requirements.txt --import yaml --import jsonschema --import pytest
if errorlevel 1 exit /b 1
python -m pytest %*
exit /b %ERRORLEVEL%
