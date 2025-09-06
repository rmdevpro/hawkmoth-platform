@echo off
cd /d "G:\Claud\HAWKMOTH-Project"
git add UPLOAD_TO_HF/
git commit -m "HAWKMOTH v0.1.0-dev - LLM Teaming test deployment

- Added Together AI integration with flexible API key detection
- Enhanced conversation manager with routing capabilities
- LLM router with rule-based and AI-based routing
- Test commands: 'test together', 'routing status'
- Updated app.py with routing endpoints
- Ready for Together AI testing with TOGETHERAI_KEY"
git push
echo Done!