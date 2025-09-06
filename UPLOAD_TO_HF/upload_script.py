#!/usr/bin/env python3
"""Upload HAWKMOTH to HuggingFace Space"""

import os
import sys

def main():
    try:
        # Install requirements if needed
        try:
            from huggingface_hub import HfApi, upload_folder
        except ImportError:
            print("Installing huggingface_hub...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub>=0.20.0"])
            from huggingface_hub import HfApi, upload_folder
        
        # Initialize API
        api = HfApi()
        space_id = "JmDrumsGarrison/HAWKMOTH"
        
        print(f"📤 Uploading to {space_id}...")
        
        # Upload files
        api.upload_folder(
            folder_path=".",
            repo_id=space_id,
            repo_type="space",
            ignore_patterns=[".git", "__pycache__", "*.pyc", ".env", "upload_script.py"],
            commit_message="Fix auto-escalation - restore weather query functionality"
        )
        
        print("✅ Upload successful!")
        print(f"🌐 Space: https://huggingface.co/spaces/{space_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
