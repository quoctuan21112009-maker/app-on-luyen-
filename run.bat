@echo off
if "%1"=="-d" (
    python main.py --debug
) else (
    if "%1"=="--debug" (
        python main.py --debug
    ) else (
        python main.py %*
    )
)
