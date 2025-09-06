@echo off
cd /d "G:\Claud\HAWKMOTH-Project"

REM Remove the problematic files from Git tracking (but keep them locally)
git rm --cached PUSH_TO_GIT.bat
git rm --cached SIMPLE_RECOVERY.bat
git rm --cached WORKING_RECOVERY.bat
git rm --cached DIRECT_RECOVERY.py
git rm --cached VERIFIED_RECOVERY.py
git rm --cached PROJECT_CONTINUATION.md
git rm --cached git-recovery/complete_recovery.bat

REM Commit the removal
git commit -m "Remove files with tokens from Git tracking"

REM Now push
git push origin main

echo Done - sensitive files removed from Git but kept locally
pause
