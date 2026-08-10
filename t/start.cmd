@echo off
:: t/start.cmd - Windows (PowerShell or Command Prompt)
::
:: Finds Python, then hands over to t/start.py, which does the real work.
::
:: Kept deliberately flat - no ( ) blocks, since %ERRORLEVEL% inside a block is
:: expanded when the block is parsed rather than when it runs.
setlocal EnableExtensions

:: `py` (the official launcher) first: plain `python` may be the Microsoft Store
:: placeholder, which sits on PATH but does nothing. Probing with a trivial
:: program is what rejects it - and probing separately from the real run means a
:: genuine failure inside start.py is never mistaken for "wrong interpreter".
py -3 -c "pass" >nul 2>&1
if "%ERRORLEVEL%"=="0" set "PY=py -3"
if defined PY goto run

python -c "pass" >nul 2>&1
if "%ERRORLEVEL%"=="0" set "PY=python"
if defined PY goto run

echo Could not find a working Python 3 on your PATH.>&2
echo Install it from https://python.org/downloads, ticking "Add python.exe to PATH",>&2
echo then open a new terminal.>&2
exit /b 1

:run
%PY% "%~dp0start.py" %*
exit /b %ERRORLEVEL%
