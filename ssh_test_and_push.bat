@echo off
REM === SILENT SSH CONNECTION TEST & GIT RECOVERY ===
cd /d "G:\Claud\HAWKMOTH-Project"

REM Test SSH connection to GitHub
echo === Testing SSH Connection to GitHub === > ssh_test_results.txt
"C:\Program Files\Git\usr\bin\ssh.exe" -T -o StrictHostKeyChecking=no git@github.com >> ssh_test_results.txt 2>&1

REM Check current Git remote configuration
echo. >> ssh_test_results.txt
echo === Current Git Remote Configuration === >> ssh_test_results.txt
"C:\Program Files\Git\cmd\git.exe" remote -v >> ssh_test_results.txt 2>&1

REM Check repository status
echo. >> ssh_test_results.txt
echo === Repository Status === >> ssh_test_results.txt
"C:\Program Files\Git\cmd\git.exe" status >> ssh_test_results.txt 2>&1

REM Attempt to push to GitHub via SSH
echo. >> ssh_test_results.txt
echo === Attempting Git Push via SSH === >> ssh_test_results.txt
"C:\Program Files\Git\cmd\git.exe" push origin main >> ssh_test_results.txt 2>&1

REM Final status check
echo. >> ssh_test_results.txt
echo === Final Status Check === >> ssh_test_results.txt
"C:\Program Files\Git\cmd\git.exe" status >> ssh_test_results.txt 2>&1

REM Exit silently
exit /b 0
