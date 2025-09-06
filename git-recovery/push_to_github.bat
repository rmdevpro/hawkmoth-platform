@echo off
echo ========================================
echo HAWKMOTH Git Setup and Push to GitHub
echo Repository: https://github.com/rmdevpro/hawkmoth-platform
echo ========================================

cd /d "G:\Claud\HAWKMOTH-Project"

echo Step 1: Initialize Git Repository
git init
if !ERRORLEVEL! neq 0 (
    echo ERROR: Git init failed
    pause
    exit /b 1
)

echo Step 2: Configure Git User
git config user.name "rmdevpro"
git config user.email "hawkmoth@platform.dev"

echo Step 3: Add all files
git add .
if !ERRORLEVEL! neq 0 (
    echo ERROR: Git add failed
    pause
    exit /b 1
)

echo Step 4: Create recovery commit with Components 1-3
git commit -m "v0.0.3 - HAWKMOTH Components 1-3 Recovery - Complete project with LLM Teaming Engine, Auto-escalation, and Claude File Integration"
if !ERRORLEVEL! neq 0 (
    echo ERROR: Git commit failed
    pause
    exit /b 1
)

echo Step 5: Create retroactive component tags
git tag v0.0.1 -m "Component 1: Persistent Storage - 3-Layer Hybrid System"
git tag v0.0.2 -m "Component 2: File Upload Handling - Multipart Pipeline"
git tag v0.0.3 -m "Component 3: Claude File Integration - Live Image Analysis"

echo Step 6: Add remote origin
git remote add origin https://YOUR_TOKEN_HERE@github.com/rmdevpro/hawkmoth-platform.git
if !ERRORLEVEL! neq 0 (
    echo ERROR: Remote add failed
    pause
    exit /b 1
)

echo Step 7: Push to GitHub
git push -u origin main
if !ERRORLEVEL! neq 0 (
    echo ERROR: Push main failed
    pause
    exit /b 1
)

echo Step 8: Push tags
git push --tags
if !ERRORLEVEL! neq 0 (
    echo ERROR: Push tags failed
    pause
    exit /b 1
)

echo Step 9: Verify
git remote -v
git log --oneline -3
git tag

echo.
echo SUCCESS! Repository: https://github.com/rmdevpro/hawkmoth-platform
echo All HAWKMOTH Components 1-3 have been pushed to GitHub
echo.
pause