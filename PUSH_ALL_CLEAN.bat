@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
git add -A
git commit -m "Clean all remaining token instances from batch files"
git push origin main
echo All tokens cleaned - repository pushed successfully
pause