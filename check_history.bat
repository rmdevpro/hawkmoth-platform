@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
echo Checking current commit history...
"C:\Program Files\Git\bin\git.exe" log --oneline -5 > git_history_check.txt 2>&1
echo Current status...
"C:\Program Files\Git\bin\git.exe" status >> git_history_check.txt 2>&1
exit /b 0
