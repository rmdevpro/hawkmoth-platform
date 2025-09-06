@echo off
REM === SILENT SSH CONNECTION TEST & GIT PUSH ===
cd /d "G:\Claud\HAWKMOTH-Project"

REM Test SSH connection to GitHub
echo === Testing SSH Connection === > ssh_push_test.txt
"C:\Program Files\Git\usr\bin\ssh.exe" -o StrictHostKeyChecking=no -T git@github.com >> ssh_push_test.txt 2>&1

REM Show current Git remote configuration
echo. >> ssh_push_test.txt
echo === Git Remote Configuration === >> ssh_push_test.txt
"C:\Program Files\Git\cmd\git.exe" remote -v >> ssh_push_test.txt 2>&1

REM Check current Git status
echo. >> ssh_push_test.txt
echo === Current Git Status === >> ssh_push_test.txt
"C:\Program Files\Git\cmd\git.exe" status >> ssh_push_test.txt 2>&1

REM Attempt to push to GitHub using SSH
echo. >> ssh_push_test.txt
echo === Pushing to GitHub via SSH === >> ssh_push_test.txt
"C:\Program Files\Git\cmd\git.exe" push origin main >> ssh_push_test.txt 2>&1

REM Final status check
echo. >> ssh_push_test.txt
echo === Final Status Check === >> ssh_push_test.txt
"C:\Program Files\Git\cmd\git.exe" status >> ssh_push_test.txt 2>&1

REM Exit silently
exit /b 0
