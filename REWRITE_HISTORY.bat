@echo off
cd /d "G:\Claud\HAWKMOTH-Project"

REM Step 1: Reset to before the problematic commit
git reset --hard HEAD~1

REM Step 2: Remove the files with tokens from staging
git rm --cached PUSH_TO_GIT.bat 2>nul
git rm --cached SIMPLE_RECOVERY.bat 2>nul
git rm --cached WORKING_RECOVERY.bat 2>nul
git rm --cached DIRECT_RECOVERY.py 2>nul
git rm --cached VERIFIED_RECOVERY.py 2>nul
git rm --cached git-recovery/complete_recovery.bat 2>nul

REM Step 3: Create new clean commit
git add .
git commit -m "HAWKMOTH Components 1-3 - Clean version without tokens"

REM Step 4: Force push to overwrite history
git push -f origin main

echo Done - history rewritten without token commit
pause
