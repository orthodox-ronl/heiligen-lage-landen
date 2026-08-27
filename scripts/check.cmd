@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo --pip-r requirements.txt --import yaml --import jsonschema --import pytest
if errorlevel 1 exit /b 1

python -m pytest -q
if errorlevel 1 exit /b 1
python scripts\validate.py
if errorlevel 1 exit /b 1
python scripts\generate.py --clean
if errorlevel 1 exit /b 1
python scripts\write_build_stamp.py
if errorlevel 1 exit /b 1
hugo --source site --destination generated\site --minify --baseURL /
exit /b %ERRORLEVEL%
