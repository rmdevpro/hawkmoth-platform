@echo off
echo NUCLEAR OPTION - Complete Fresh Start
cd /d "G:\Claud\HAWKMOTH-Project"

REM Completely remove git history
if exist .git rmdir /s /q .git

REM Remove ALL the batch files with tokens completely
del PUSH_TO_GIT.bat 2>nul
del SIMPLE_RECOVERY.bat 2>nul  
del WORKING_RECOVERY.bat 2>nul
del FINAL_RECOVERY.bat 2>nul
del CLEAN_START.bat 2>nul
del DIRECT_RECOVERY.py 2>nul
del VERIFIED_RECOVERY.py 2>nul
del git-recovery\complete_recovery.bat 2>nul
del git-recovery\push_to_github.bat 2>nul

REM Fresh git init
git init
git config user.name "rmdevpro"
git config user.email "hawkmoth@platform.dev"

REM Add only the important files
git add *.py
git add *.md
git add *.html
git add *.txt
git add *.json
git add UPLOAD_TO_HF\
git add working\
git add src\

REM Create clean commit
git commit -m "HAWKMOTH Project - Clean version without any tokens"
git branch -M main

echo Ready to add remote manually with your token
echo Next: git remote add origin https://YOUR_TOKEN@github.com/rmdevpro/hawkmoth-platform.git
echo Then: git push -u origin main
pause
