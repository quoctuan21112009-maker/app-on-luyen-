@echo off
REM Usage: run.bat [OPTIONS]
REM Options:
REM   -l, --logid <ID>     : Test ID to process (optional)
REM   -d, --debug          : Enable debug mode (optional)
REM
REM Examples:
REM   run.bat
REM   run.bat -l 69b7e0c2ea0e1ac3556961fc
REM   run.bat --logid 69b7e0c2ea0e1ac3556961fc --debug

if "%1"=="-d" (
    python main.py --debug
) else (
    if "%1"=="--debug" (
        python main.py --debug
    ) else (
        python main.py %*
    )
)
