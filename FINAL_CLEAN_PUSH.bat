@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
git add -A
git commit -m "Clean all tokens from files"
git push origin main
echo Push complete - all tokens removed
pause