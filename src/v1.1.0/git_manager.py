# Git Manager for ACNE - Handles repository operations
import os
import subprocess
import json
import requests
from typing import Dict, List
from datetime import datetime

class GitManager:
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.git_exe = self._find_git()
        
    def _find_git(self) -> str:
        """Locate Git executable"""
        paths = [
            "git",
            "C:\\Program Files\\Git\\cmd\\git.exe",
            "C:\\Program Files\\Git\\bin\\git.exe"
        ]
        
        for path in paths:
            try:
                result = subprocess.run([path, "--version"], 
                                     capture_output=True, timeout=5)
                if result.returncode == 0:
                    return path
            except:
                continue
        raise Exception("Git not found")
    
    def run_git(self, args: List[str]) -> Dict:
        """Execute Git command"""
        try:
            cmd = [self.git_exe] + args
            result = subprocess.run(cmd, capture_output=True, 
                                 text=True, timeout=30)
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_github_repo(self, name: str, description: str) -> Dict:
        """Create GitHub repository"""
        if not self.github_token:
            return {"success": False, "error": "No GitHub token"}
            
        try:
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            data = {
                'name': name,
                'description': description,
                'private': False,
                'auto_init': False
            }
            
            response = requests.post('https://api.github.com/user/repos',
                                   headers=headers, json=data)
            
            if response.status_code == 201:
                repo = response.json()
                return {
                    "success": True,
                    "repo_url": repo['html_url'],
                    "clone_url": repo['clone_url']
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_acne_repo(self) -> Dict:
        """Complete ACNE repository setup"""
        results = []
        
        # Initialize if needed
        if not os.path.exists('.git'):
            init = self.run_git(['init'])
            results.append(f"Init: {init.get('error', 'Success')}")
        
        # Add all files
        add = self.run_git(['add', '.'])
        results.append(f"Add: {add.get('error', 'Success')}")
        
        # Commit
        commit = self.run_git(['commit', '-m', 'ACNE project update'])
        results.append(f"Commit: {commit.get('error', 'Success')}")
        
        return {"results": results}
