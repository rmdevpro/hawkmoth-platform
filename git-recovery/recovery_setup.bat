@echo off
echo Starting HAWKMOTH Git Recovery...
cd /d "G:\Claud\HAWKMOTH-Project"

echo Step 1: Initialize Git Repository
git init

echo Step 2: Configure Git User
git config user.name "JmDrumsGarrison"
git config user.email "user@example.com"

echo Step 3: Add all files
git add .

echo Step 4: Create recovery commit with Components 1-3
git commit -m "v0.0.3 - HAWKMOTH Components 1-3 Recovery

Components Recovery Commit:
✅ Component 1: Persistent Storage (3-Layer Hybrid System)
✅ Component 2: File Upload Handling (Multipart Pipeline)  
✅ Component 3: Claude File Integration (Live Image Analysis)

Features Complete:
- LLM Teaming Engine with cost optimization
- Auto-escalation system with web search
- Claude Files API integration (50+ file types)
- Production deployment pipeline
- Comprehensive documentation

Ready for Component 4: Communication Control UI
Repository recovered from lost remote - all work preserved"

echo Step 5: Create retroactive component tags
git tag v0.0.1 -m "Component 1: Persistent Storage - 3-Layer Hybrid System"
git tag v0.0.2 -m "Component 2: File Upload Handling - Multipart Pipeline"
git tag v0.0.3 -m "Component 3: Claude File Integration - Live Image Analysis"

echo Step 6: Show status
git status
git log --oneline -5
git tag

echo.
echo ✅ Local Git Recovery Complete!
echo.
echo Next: Create GitHub repository 'hawkmoth-platform' then run recovery_push.bat
pause
