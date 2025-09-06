@echo off
echo Removing problematic commit from Git history
cd /d "G:\Claud\HAWKMOTH-Project"

REM Create a new orphan branch (no history)
git checkout --orphan clean-main

REM Add all current files (they're already clean)
git add .

REM Create a fresh commit without the problematic history
git commit -m "HAWKMOTH Components 1-3 - Clean repository without token history"

REM Delete the old main branch
git branch -D main

REM Rename clean branch to main
git branch -m main

REM Force push the new clean history
git push -f origin main

echo Clean history pushed without problematic commit
pause