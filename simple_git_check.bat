@echo off
REM === SIMPLE GIT STATUS CHECK ===
cd /d "G:\Claud\HAWKMOTH-Project"

REM Just check current status
"C:\Program Files\Git\cmd\git.exe" status > simple_git_status.txt 2>&1
"C:\Program Files\Git\cmd\git.exe" remote -v >> simple_git_status.txt 2>&1

REM Exit immediately
exit /b 0
