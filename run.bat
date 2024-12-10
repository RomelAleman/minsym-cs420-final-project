@echo off

REM Get the location of the .bat file
set "batch_dir=%~dp0"

REM Construct the path to the Python script
set "python_script=%batch_dir%src\minsym.py"

REM Run the Python script
python "%python_script%"

REM Keep the command prompt window open
pause
