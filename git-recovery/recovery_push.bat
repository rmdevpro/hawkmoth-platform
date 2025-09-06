@echo off
echo Adding remote and pushing to GitHub...
cd /d "G:\Claud\HAWKMOTH-Project"

echo Step 1: Add GitHub remote
git remote add origin https://github.com/JmDrumsGarrison/hawkmoth-platform.git

echo Step 2: Push main branch
git push -u origin main

echo Step 3: Push all tags
git push --tags

echo Step 4: Verify remote connection
git remote -v
git branch -a

echo.
echo ✅ HAWKMOTH Recovery Complete!
echo Repository: https://github.com/JmDrumsGarrison/hawkmoth-platform
echo.
pause
