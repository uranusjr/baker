@echo off

setlocal
:: TODO: Automatically elevate ourself.

:: TODO: Make this some config file
set PYTHON=C:\Python33\python.exe

:: Syntax: bake <sub-command> <arguments ...>
utils\elevate -c -w %PYTHON% %~dp0\bake.py %*

endlocal
exit /b
