# HAWKMOTH Git Operations - Real HuggingFace API Integration
import subprocess
import os
import tempfile
import time
from typing import Dict, Any, Optional
from huggingface_hub import HfApi, upload_file, upload_folder

class HAWKMOTHGitHandler:
    def __init__(self):
        self.git_available = self._check_git_availability()
        self.hf_token = os.getenv('HF_TOKEN', '')
        self.hf_api = HfApi(token=self.hf_token) if self.hf_token else None
        self.space_repo_id = "JmDrumsGarrison/HAWKMOTH"
        
    def _check_git_availability(self) -> bool:
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def deploy_repository(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy external repo using temp directory cloning"""
        try:
            temp_dir = self._clone_repo(analysis['repo_url'])
            self._add_hf_config(temp_dir, analysis)
            
            # Create actual HuggingFace Space if API available
            if self.hf_api:
                space_name = f"{analysis['name'].lower().replace(' ', '-')}-{int(time.time())}"
                space_repo_id = f"JmDrumsGarrison/{space_name}"
                
                try:
                    # Create the Space
                    self.hf_api.create_repo(
                        repo_id=space_repo_id,
                        repo_type="space",
                        space_sdk="docker",
                        private=False,
                        exist_ok=True
                    )
                    
                    # Upload the prepared repository
                    upload_folder(
                        folder_path=temp_dir,
                        repo_id=space_repo_id,
                        repo_type="space",
                        token=self.hf_token
                    )
                    
                    space_url = f"https://huggingface.co/spaces/{space_repo_id}"
                    return {
                        'success': True,
                        'space_url': space_url,
                        'message': f'Real Space created: {space_name}',
                        'space_id': space_repo_id
                    }
                except Exception as api_error:
                    return {
                        'success': False,
                        'error': f'Space creation failed: {str(api_error)}'
                    }
            else:
                # Fallback: Prepare files but can't create Space
                space_name = f"{analysis['name'].lower()}-{int(time.time())}"
                space_url = f"https://huggingface.co/spaces/JmDrumsGarrison/{space_name}"
                
                return {
                    'success': True,
                    'space_url': space_url,
                    'message': 'Repository prepared (set HF_TOKEN for real deployment)',
                    'needs_token': True
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _clone_repo(self, repo_url: str) -> str:
        """Clone external repo to temp directory (this works fine)"""
        temp_dir = tempfile.mkdtemp()
        result = subprocess.run(['git', 'clone', '--depth=1', repo_url, temp_dir], 
                               capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return temp_dir
        else:
            raise Exception(f"Clone failed: {result.stderr}")
    
    def _add_hf_config(self, repo_path: str, analysis: Dict):
        """Add HuggingFace Space configuration"""
        sdk = 'streamlit' if 'Streamlit' in analysis['tech_stack'] else 'docker'
        readme_content = f"""---
title: {analysis['name']}
emoji: 🦅  
sdk: {sdk}
app_port: 7860
colorFrom: blue
colorTo: purple
---
# {analysis['name']}

{analysis['description']}

**Deployed via HAWKMOTH v0.0.0**

## Tech Stack
{', '.join(analysis['tech_stack'])}

## Deployment Details
- **Type**: {analysis['deployment_type']}
- **Complexity**: {analysis['complexity']}
- **Stars**: {analysis['stars']:,}

*Automatically deployed from GitHub repository*
"""
        with open(os.path.join(repo_path, 'README.md'), 'w') as f:
            f.write(readme_content)
    
    def commit_to_hawkmoth_repo(self, message: str) -> Dict[str, str]:
        """Real HuggingFace API-based self-management"""
        try:
            if not self.hf_token:
                return {
                    "success": False, 
                    "error": "🔑 HF_TOKEN required for self-management. Add it in Space Settings → Variables/Secrets."
                }
            
            if not self.hf_api:
                return {
                    "success": False,
                    "error": "❌ HuggingFace API initialization failed."
                }
            
            # Get current files to update
            current_files = self._get_current_files()
            if not current_files:
                return {
                    "success": False,
                    "error": "❌ No files found to manage."
                }
            
            # Actually upload files via HuggingFace API
            return self._real_api_update(message, current_files)
                
        except Exception as e:
            return {"success": False, "error": f"API update failed: {str(e)}"}
    
    def _real_api_update(self, message: str, files: list) -> Dict[str, str]:
        """Actually update HAWKMOTH files via HuggingFace API"""
        try:
            updated_count = 0
            
            for file_path in files:
                if os.path.exists(file_path):
                    try:
                        # Upload each file individually
                        upload_file(
                            path_or_fileobj=file_path,
                            path_in_repo=file_path,
                            repo_id=self.space_repo_id,
                            repo_type="space",
                            token=self.hf_token,
                            commit_message=f"{message} - Updated {file_path}"
                        )
                        updated_count += 1
                    except Exception as file_error:
                        print(f"Failed to upload {file_path}: {file_error}")
                        continue
            
            if updated_count > 0:
                return {
                    "success": True, 
                    "message": f"🚀 Real API update: {updated_count}/{len(files)} files updated via HuggingFace API"
                }
            else:
                return {
                    "success": False,
                    "error": "❌ No files were successfully updated"
                }
            
        except Exception as e:
            return {"success": False, "error": f"API operation failed: {str(e)}"}
    
    def _get_current_files(self) -> list:
        """Get list of HAWKMOTH files to manage"""
        try:
            files = []
            hawkmoth_files = [
                'app.py', 'git_handler.py', 'frontend.html', 'README.md', 
                'requirements.txt', 'Dockerfile', 'conversation.py', 'analyzer.py'
            ]
            
            for file in hawkmoth_files:
                if os.path.exists(file):
                    files.append(file)
            return files
        except:
            return []
    
    def get_git_status(self) -> str:
        """Return comprehensive HAWKMOTH status"""
        if not self.git_available:
            return "❌ Git unavailable for external repos"
        
        try:
            files = self._get_current_files()
            
            if self.hf_api:
                return f"🚀 API mode active - Managing {len(files)} files via HuggingFace API"
            elif self.hf_token:
                return f"⚠️ API token available but connection failed - {len(files)} files ready"
            else:
                return f"🔑 Set HF_TOKEN for API-based self-management - {len(files)} files detected"
                
        except Exception as e:
            return f"❌ Status check failed: {str(e)}"
    
    def create_new_space(self, space_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new HuggingFace Space"""
        if not self.hf_api:
            return {"success": False, "error": "HF_TOKEN required for Space creation"}
        
        try:
            space_repo_id = f"JmDrumsGarrison/{space_name}"
            
            # Create the Space
            self.hf_api.create_repo(
                repo_id=space_repo_id,
                repo_type="space",
                space_sdk="docker",
                private=False,
                exist_ok=True
            )
            
            # Create basic files
            readme_content = f"""---
title: {space_name}
emoji: 🦅
sdk: docker
app_port: 7860
---
# {space_name}

{description}

Created via HAWKMOTH API
"""
            
            # Upload README
            upload_file(
                path_or_fileobj=readme_content.encode(),
                path_in_repo="README.md",
                repo_id=space_repo_id,
                repo_type="space",
                token=self.hf_token,
                commit_message="Initial Space creation via HAWKMOTH API"
            )
            
            return {
                "success": True,
                "space_url": f"https://huggingface.co/spaces/{space_repo_id}",
                "space_id": space_repo_id,
                "message": f"Space '{space_name}' created successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Space creation failed: {str(e)}"}

# Alias the class for backward compatibility during transition
GitHandler = HAWKMOTHGitHandler

def deploy_with_real_git(analysis: Dict[str, Any]) -> Dict[str, Any]:
    handler = HAWKMOTHGitHandler()
    return handler.deploy_repository(analysis)

def hawkmoth_self_commit(message: str = "HAWKMOTH auto-update") -> Dict[str, str]:
    """Real API-based self-management"""
    handler = HAWKMOTHGitHandler()
    return handler.commit_to_hawkmoth_repo(message)

def create_space_via_api(space_name: str, description: str = "") -> Dict[str, Any]:
    """Create new Space via API"""
    handler = HAWKMOTHGitHandler()
    return handler.create_new_space(space_name, description)
