@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
"C:\Program Files\Git\bin\git.exe" status > git_status_result.txt 2>&1
"C:\Program Files\Git\bin\git.exe" log --oneline -3 >> git_status_result.txt 2>&1
exit /b 0
