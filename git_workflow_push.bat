@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
"C:\Program Files\Git\bin\git.exe" push origin main > git_push_result.txt 2>&1
echo Git push exit code: %ERRORLEVEL% >> git_push_result.txt
exit /b 0
