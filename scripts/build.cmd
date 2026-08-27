@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo --pip-r requirements.txt --import yaml --import jsonschema
if errorlevel 1 exit /b 1
python scripts\validate.py
if errorlevel 1 exit /b 1
python scripts\generate.py --clean
if errorlevel 1 exit /b 1
python scripts\inject_git_dates.py
python scripts\write_build_stamp.py
hugo --source site --destination generated\site --minify --baseURL /
if errorlevel 1 exit /b 1
echo Built generated\site
exit /b 0
