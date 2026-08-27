@echo off
setlocal
cd /d "%~dp0.."
call scripts\_ensure.cmd --hugo --pip-r requirements.txt --import yaml --import jsonschema
if errorlevel 1 exit /b 1

REM Eerdere hugo-serve/build op :1313 houdt generated\site vast; een tweede
REM hugo blijft dan hangen op "Start building sites ...".
powershell -NoProfile -Command ^
  "$procs = Get-CimInstance Win32_Process -Filter \"Name='hugo.exe'\";" ^
  "$kill = $procs | Where-Object { $_.CommandLine -match '127\.0\.0\.1:1313|generated\\\\site' };" ^
  "$kill | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"

python scripts\validate.py || exit /b 1
python scripts\generate.py --clean || exit /b 1
python scripts\write_build_stamp.py
hugo serve --source site --destination generated\site --bind 127.0.0.1 --baseURL http://127.0.0.1:1313/ --disableFastRender
exit /b %ERRORLEVEL%
