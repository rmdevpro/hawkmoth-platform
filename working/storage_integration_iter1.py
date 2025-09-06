# HAWKMOTH Storage Integration - Connect Persistent Storage with Main Application
import os
import json
import time
from typing import Dict, Any, Optional
from fastapi import HTTPException
from .persistent_storage_iter1 import HAWKMOTHPersistentStorage

class HAWKMOTHStorageManager:
    """
    Storage Manager for HAWKMOTH Application
    Integrates persistent storage with the main HAWKMOTH platform
    """
    
    def __init__(self, hf_token: str = None):
        self.storage = HAWKMOTHPersistentStorage(hf_token)
        self.current_workspace = None
        self.initialized = True
        
        # Auto-create default workspace if none exists
        self._ensure_default_workspace()
    
    def _ensure_default_workspace(self):
        """Ensure there's always a default workspace available"""
        try:
            # Check if default workspace exists
            default_workspace = self.storage.get_workspace("hawkmoth-default")
            
            if not default_workspace:
                # Create default workspace
                result = self.storage.create_workspace(
                    "hawkmoth-default", 
                    "Default HAWKMOTH development workspace"
                )
                if result["success"]:
                    self.current_workspace = result["workspace_id"]
                    print("✅ Default HAWKMOTH workspace created")
                else:
                    print(f"⚠️ Could not create default workspace: {result.get('error')}")
            else:
                self.current_workspace = self.storage.active_workspaces["hawkmoth-default"]
                print("✅ Default HAWKMOTH workspace loaded")
                
        except Exception as e:
            print(f"⚠️ Workspace initialization warning: {e}")
    
    # === WORKSPACE OPERATIONS FOR HAWKMOTH ===
    
    def create_project_workspace(self, project_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new project workspace via HAWKMOTH"""
        try:
            # Validate project name
            if not project_name or not project_name.replace("-", "").replace("_", "").isalnum():
                return {
                    "success": False,
                    "error": "Project name must contain only letters, numbers, hyphens, and underscores"
                }
            
            result = self.storage.create_workspace(project_name, description)
            
            if result["success"]:
                # Switch to new workspace
                self.current_workspace = result["workspace_id"]
                
                # Create initial project structure
                self._create_initial_project_files(result["workspace_id"], project_name)
                
                return {
                    "success": True,
                    "workspace_id": result["workspace_id"],
                    "project_name": project_name,
                    "message": f"Project workspace '{project_name}' created and activated"
                }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create project workspace: {str(e)}"
            }
    
    def switch_workspace(self, project_name: str) -> Dict[str, Any]:
        """Switch to a different project workspace"""
        try:
            workspace = self.storage.get_workspace(project_name)
            
            if workspace:
                self.current_workspace = workspace["workspace_id"]
                return {
                    "success": True,
                    "workspace_id": workspace["workspace_id"],
                    "project_name": project_name,
                    "message": f"Switched to workspace '{project_name}'"
                }
            else:
                return {
                    "success": False,
                    "error": f"Workspace '{project_name}' not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to switch workspace: {str(e)}"
            }
    
    def get_current_workspace_info(self) -> Dict[str, Any]:
        """Get information about current active workspace"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace"
                }
            
            # Find workspace metadata
            workspace_metadata = None
            for ws_id, metadata in self.storage.local_memory.items():
                if ws_id == self.current_workspace:
                    workspace_metadata = metadata
                    break
            
            if workspace_metadata:
                files = self.storage.list_files(self.current_workspace)
                
                return {
                    "success": True,
                    "workspace_id": self.current_workspace,
                    "project_name": workspace_metadata.get("project_name", "Unknown"),
                    "description": workspace_metadata.get("description", ""),
                    "created_at": workspace_metadata.get("created_at", 0),
                    "file_count": len(workspace_metadata.get("files", {})),
                    "files": files.get("files", []) if files["success"] else [],
                    "storage_stats": self.storage.get_storage_stats()
                }
            else:
                return {
                    "success": False,
                    "error": "Current workspace metadata not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get workspace info: {str(e)}"
            }
    
    # === FILE OPERATIONS FOR HAWKMOTH ===
    
    def save_project_file(self, file_path: str, content: str, 
                         storage_layer: str = "auto") -> Dict[str, Any]:
        """Save file in current project workspace"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace - create or switch to a project first"
                }
            
            result = self.storage.save_file(
                self.current_workspace, 
                file_path, 
                content, 
                storage_layer
            )
            
            if result["success"]:
                result["workspace_id"] = self.current_workspace
                result["message"] = f"File '{file_path}' saved successfully"
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save file: {str(e)}"
            }
    
    def load_project_file(self, file_path: str) -> Dict[str, Any]:
        """Load file from current project workspace"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace"
                }
            
            result = self.storage.load_file(self.current_workspace, file_path)
            
            if result["success"]:
                result["workspace_id"] = self.current_workspace
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load file: {str(e)}"
            }
    
    def list_project_files(self, directory: str = "") -> Dict[str, Any]:
        """List files in current project workspace"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace"
                }
            
            result = self.storage.list_files(self.current_workspace, directory)
            
            if result["success"]:
                # Add workspace context
                result["workspace_id"] = self.current_workspace
                
                # Get workspace info
                workspace_info = self.get_current_workspace_info()
                if workspace_info["success"]:
                    result["project_name"] = workspace_info["project_name"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }
    
    def delete_project_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file from current project workspace"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace"
                }
            
            result = self.storage.delete_file(self.current_workspace, file_path)
            
            if result["success"]:
                result["workspace_id"] = self.current_workspace
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    # === GIT INTEGRATION FOR HAWKMOTH ===
    
    def create_project_repo(self, repo_name: str = None, description: str = "") -> Dict[str, Any]:
        """Create Git repository for current project"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace"
                }
            
            # Get current project name if repo_name not specified
            workspace_info = self.get_current_workspace_info()
            if not workspace_info["success"]:
                return workspace_info
            
            if not repo_name:
                repo_name = f"hawkmoth-{workspace_info['project_name']}"
            
            if not description:
                description = f"HAWKMOTH project: {workspace_info['project_name']}"
            
            result = self.storage.create_git_repo(self.current_workspace, repo_name, description)
            
            if result["success"]:
                result["workspace_id"] = self.current_workspace
                result["project_name"] = workspace_info["project_name"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create project repository: {str(e)}"
            }
    
    def sync_project_to_git(self, repo_name: str = None, 
                          commit_message: str = None) -> Dict[str, Any]:
        """Sync current project to Git repository"""
        try:
            if not self.current_workspace:
                return {
                    "success": False,
                    "error": "No active workspace"
                }
            
            workspace_info = self.get_current_workspace_info()
            if not workspace_info["success"]:
                return workspace_info
            
            if not repo_name:
                # Use default repo name based on project
                repo_name = f"hawkmoth-{workspace_info['project_name']}"
            
            if not commit_message:
                commit_message = f"HAWKMOTH sync: {workspace_info['project_name']} updates"
            
            result = self.storage.sync_with_git(self.current_workspace, repo_name, commit_message)
            
            if result["success"]:
                result["workspace_id"] = self.current_workspace
                result["project_name"] = workspace_info["project_name"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to sync project to Git: {str(e)}"
            }
    
    # === HAWKMOTH-SPECIFIC OPERATIONS ===
    
    def _create_initial_project_files(self, workspace_id: str, project_name: str):
        """Create initial project structure for new workspace"""
        try:
            # Create README.md
            readme_content = f"""# {project_name}

HAWKMOTH project created on {time.strftime('%Y-%m-%d %H:%M:%S')}

## Project Structure
- `src/` - Source code
- `docs/` - Documentation  
- `tests/` - Test files
- `config/` - Configuration files

## Development
This project was created and is being developed using the HAWKMOTH platform.

### HAWKMOTH Features Used:
- ✅ Persistent Storage (Git + HF Datasets + Local)
- ✅ LLM Teaming with Auto-Escalation
- ✅ Green/Blue Deployment
- ✅ Intelligent Model Routing

---
*Generated by HAWKMOTH v0.1.0-dev*
"""
            
            self.storage.save_file(workspace_id, "README.md", readme_content)
            
            # Create project configuration
            project_config = {
                "project_name": project_name,
                "hawkmoth_version": "0.1.0-dev",
                "created_at": time.time(),
                "storage_strategy": "hybrid",
                "features": {
                    "llm_teaming": True,
                    "auto_escalation": True,
                    "persistent_storage": True,
                    "green_blue_deployment": True
                }
            }
            
            self.storage.save_file(
                workspace_id, 
                "hawkmoth.json", 
                json.dumps(project_config, indent=2)
            )
            
            # Create basic directory structure
            self.storage.save_file(workspace_id, "src/.gitkeep", "# Source code directory")
            self.storage.save_file(workspace_id, "docs/.gitkeep", "# Documentation directory")
            self.storage.save_file(workspace_id, "tests/.gitkeep", "# Tests directory")
            self.storage.save_file(workspace_id, "config/.gitkeep", "# Configuration directory")
            
            print(f"✅ Initial project structure created for '{project_name}'")
            
        except Exception as e:
            print(f"⚠️ Could not create initial project files: {e}")
    
    def get_hawkmoth_status(self) -> Dict[str, Any]:
        """Get comprehensive HAWKMOTH storage system status"""
        try:
            storage_stats = self.storage.get_storage_stats()
            workspace_info = self.get_current_workspace_info()
            
            return {
                "success": True,
                "persistent_storage": {
                    "initialized": self.initialized,
                    "hf_available": storage_stats["hf_available"],
                    "storage_layers": ["Git Repositories", "HF Datasets", "Local Memory"]
                },
                "current_workspace": workspace_info if workspace_info["success"] else None,
                "storage_statistics": storage_stats,
                "available_workspaces": self.storage.list_workspaces()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get HAWKMOTH status: {str(e)}"
            }
    
    def cleanup(self):
        """Clean up storage resources"""
        self.storage.cleanup()

# === GLOBAL STORAGE MANAGER INSTANCE ===

# Global instance that can be imported by other modules
hawkmoth_storage = None

def initialize_hawkmoth_storage(hf_token: str = None) -> HAWKMOTHStorageManager:
    """Initialize global HAWKMOTH storage manager"""
    global hawkmoth_storage
    hawkmoth_storage = HAWKMOTHStorageManager(hf_token)
    return hawkmoth_storage

def get_hawkmoth_storage() -> Optional[HAWKMOTHStorageManager]:
    """Get global HAWKMOTH storage manager instance"""
    return hawkmoth_storage

# === CONVENIENCE FUNCTIONS ===

def save_file(file_path: str, content: str) -> Dict[str, Any]:
    """Convenience function to save file using global storage manager"""
    if hawkmoth_storage:
        return hawkmoth_storage.save_project_file(file_path, content)
    else:
        return {"success": False, "error": "HAWKMOTH storage not initialized"}

def load_file(file_path: str) -> Dict[str, Any]:
    """Convenience function to load file using global storage manager"""
    if hawkmoth_storage:
        return hawkmoth_storage.load_project_file(file_path)
    else:
        return {"success": False, "error": "HAWKMOTH storage not initialized"}

def list_files(directory: str = "") -> Dict[str, Any]:
    """Convenience function to list files using global storage manager"""
    if hawkmoth_storage:
        return hawkmoth_storage.list_project_files(directory)
    else:
        return {"success": False, "error": "HAWKMOTH storage not initialized"}
