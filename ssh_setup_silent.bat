@echo off
REM === SILENT SSH KEY GENERATION FOR HAWKMOTH ===
cd /d "G:\Claud\HAWKMOTH-Project"

REM Check if SSH directory exists
if not exist "%USERPROFILE%\.ssh" mkdir "%USERPROFILE%\.ssh"

REM Generate SSH key pair (silent, no passphrase for automation)
echo === Generating SSH Key Pair === > ssh_setup_log.txt
"C:\Program Files\Git\usr\bin\ssh-keygen.exe" -t ed25519 -C "hawkmoth@platform.dev" -f "%USERPROFILE%\.ssh\id_ed25519_hawkmoth" -N "" >> ssh_setup_log.txt 2>&1

REM Display the public key for GitHub
echo. >> ssh_setup_log.txt
echo === PUBLIC KEY (Add to GitHub) === >> ssh_setup_log.txt
type "%USERPROFILE%\.ssh\id_ed25519_hawkmoth.pub" >> ssh_setup_log.txt 2>&1

REM Configure Git to use SSH instead of HTTPS
echo. >> ssh_setup_log.txt
echo === Configuring Git for SSH === >> ssh_setup_log.txt
"C:\Program Files\Git\cmd\git.exe" remote set-url origin git@github.com:rmdevpro/hawkmoth-platform.git >> ssh_setup_log.txt 2>&1

REM Test SSH connection (will show fingerprint for first time)
echo. >> ssh_setup_log.txt
echo === Testing SSH Connection === >> ssh_setup_log.txt
"C:\Program Files\Git\usr\bin\ssh.exe" -T git@github.com >> ssh_setup_log.txt 2>&1

REM Show final status
echo. >> ssh_setup_log.txt
echo === Final Git Status === >> ssh_setup_log.txt
"C:\Program Files\Git\cmd\git.exe" remote -v >> ssh_setup_log.txt 2>&1

REM Exit silently
exit /b 0
