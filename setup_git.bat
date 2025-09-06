@echo off
cd /d "G:\Claud\ACNE-Project"
"C:\Program Files\Git\cmd\git.exe" init
"C:\Program Files\Git\cmd\git.exe" config user.name "JmDrumsGarrison"
"C:\Program Files\Git\cmd\git.exe" config user.email "user@example.com"
"C:\Program Files\Git\cmd\git.exe" add .
"C:\Program Files\Git\cmd\git.exe" commit -m "Initial ACNE project commit - working deployment system"
echo Git repository initialized successfully!
pause
