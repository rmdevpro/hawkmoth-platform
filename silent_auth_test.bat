@echo off
REM === SILENT HAWKMOTH Git Authentication Setup ===
cd /d "G:\Claud\HAWKMOTH-Project"

REM Clean up any remaining test files
del /f /q git_silent_test.* clean_recovery.bat recovery_status.txt 2>nul

REM Test current Git authentication
"C:\Program Files\Git\cmd\git.exe" push origin main --dry-run > auth_test_result.txt 2>&1

REM Capture authentication status
echo. >> auth_test_result.txt
echo === Authentication Test Completed === >> auth_test_result.txt
"C:\Program Files\Git\cmd\git.exe" status >> auth_test_result.txt 2>&1

REM Exit silently
exit /b 0
