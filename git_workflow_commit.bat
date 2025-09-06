@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
if "%1"=="" (
    echo Usage: git_workflow_commit.bat "commit message"
    exit /b 1
)
"C:\Program Files\Git\bin\git.exe" commit -m %1 > git_commit_result.txt 2>&1
echo Git commit exit code: %ERRORLEVEL% >> git_commit_result.txt
exit /b 0
