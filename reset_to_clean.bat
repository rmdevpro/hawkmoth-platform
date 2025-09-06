@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
echo Step 1: Reset to clean commit a9cef3c (before token exposure)
"C:\Program Files\Git\bin\git.exe" reset --hard a9cef3c > git_clean_reset.txt 2>&1
echo Git reset exit code: %ERRORLEVEL% >> git_clean_reset.txt

echo Step 2: Check status after reset
"C:\Program Files\Git\bin\git.exe" status >> git_clean_reset.txt 2>&1

echo Step 3: Show current files
dir >> git_clean_reset.txt 2>&1

exit /b 0
