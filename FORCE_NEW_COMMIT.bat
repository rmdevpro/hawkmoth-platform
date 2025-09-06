@echo off
echo Force creating new commit with clean content
cd /d "G:\Claud\HAWKMOTH-Project"

REM Unstage everything
git reset

REM Remove all files from Git tracking but keep them locally  
git rm -r --cached .

REM Re-add all files (forces Git to read current file contents)
git add .

REM Create completely new commit
git commit -m "HAWKMOTH Project - Clean commit with current file contents"

REM Push new commit
git push origin main

echo New clean commit created and pushed
pause