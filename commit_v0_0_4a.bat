@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
"C:\Program Files\Git\bin\git.exe" add . > git_commit_result.txt 2>&1
echo Git add exit code: %ERRORLEVEL% >> git_commit_result.txt
"C:\Program Files\Git\bin\git.exe" commit -m "HAWKMOTH v0.0.4a - Complete platform backup + versioning standardization" >> git_commit_result.txt 2>&1
echo Git commit exit code: %ERRORLEVEL% >> git_commit_result.txt
exit /b 0
