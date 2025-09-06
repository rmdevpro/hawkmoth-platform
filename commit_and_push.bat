@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
"C:\Program Files\Git\bin\git.exe" commit -m "Update WAYS_OF_WORKING.md - Git SSH authentication fully functional" > final_commit.txt 2>&1
echo Git commit exit code: %ERRORLEVEL% >> final_commit.txt
"C:\Program Files\Git\bin\git.exe" push origin main >> final_commit.txt 2>&1
echo Git push exit code: %ERRORLEVEL% >> final_commit.txt
exit /b 0
