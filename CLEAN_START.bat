@echo off
echo HAWKMOTH Clean Start Recovery
cd /d "G:\Claud\HAWKMOTH-Project"
mkdir clean_repo
cd clean_repo
xcopy ..\*.py . /y
xcopy ..\*.md . /y /exclude:..\exclude_tokens.txt
xcopy ..\*.html . /y
xcopy ..\*.txt . /y
xcopy ..\*.json . /y
xcopy ..\UPLOAD_TO_HF\*.* UPLOAD_TO_HF\ /y /s
xcopy ..\working\*.* working\ /y /s
xcopy ..\src\*.* src\ /y /s
git init
git config user.name "rmdevpro"
git config user.email "hawkmoth@platform.dev"
git add .
git commit -m "HAWKMOTH Clean Repository - Components 1-3"
git branch -M main
git remote add origin https://YOUR_TOKEN_HERE@github.com/rmdevpro/hawkmoth-platform.git
git push -f origin main
echo Clean repository pushed
pause