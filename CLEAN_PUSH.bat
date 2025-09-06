@echo off
echo HAWKMOTH Git Push - Clean Repository
cd /d "G:\Claud\HAWKMOTH-Project"

echo Step 1: Add all changes
git add .

echo Step 2: Commit changes  
git commit -m "HAWKMOTH Components 1-3 - Complete project without tokens"

echo Step 3: Push to GitHub
git push origin main

echo Step 4: Verify push
git log --oneline -3

echo.
echo Push complete. Check: https://github.com/rmdevpro/hawkmoth-platform
pause