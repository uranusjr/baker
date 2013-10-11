@echo off
setlocal

:: Syntax: bake <sub-command> <arguments ...>
python %~dp0\bake.py %*

endlocal
exit /b
