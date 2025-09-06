@echo off
echo Start-Process test with admin at %DATE% %TIME% > start_process_test.txt
git --version >> start_process_test.txt 2>&1
exit /b 0
