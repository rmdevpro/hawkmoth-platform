@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
"C:\Program Files\Git\bin\git.exe" commit -m "Git SSH authentication and workflow setup complete" > git_clean_commit.txt 2>&1
echo Git commit exit code: %ERRORLEVEL% >> git_clean_commit.txt
exit /b 0
