@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
git add .gitignore
git commit -m "Update gitignore to exclude files with tokens"
git push origin main
echo Done - sensitive files now ignored
pause
