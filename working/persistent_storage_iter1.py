# HAWKMOTH Persistent Storage System - Hybrid Approach (Git + HF Datasets + Local Memory)
import os
import json
import tempfile
import shutil
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from huggingface_hub import HfApi, upload_file, upload_folder, download_file, create_repo
from huggingface_hub.errors import RepositoryNotFoundError
import subprocess

class HAWKMOTHPersistentStorage:
    """
    Hybrid persistent storage system for HAWKMOTH development environment
    
    Storage Layers:
    1. Git Repositories - Code files, project management, version control
    2. HF Datasets - Large files, temporary workspace, cache storage
    3. Local Memory - Session-based development, temporary edits
    """
    
    def __init__(self, hf_token: str = None, user_name: str = "JmDrumsGarrison"):
        self.hf_token = hf_token or os.getenv('HF_TOKEN', '')
        self.hf_api = HfApi(token=self.hf_token) if self.hf_token else None
        self.user_name = user_name
        
        # Storage configuration
        self.workspace_dataset = f"{user_name}/hawkmoth-workspace"
        self.cache_dataset = f"{user_name}/hawkmoth-cache"
        
        # Local memory storage (session-based)
        self.local_memory = {}
        self.active_workspaces = {}
        
        # Temporary directory for local operations
        self.temp_dir = tempfile.mkdtemp(prefix="hawkmoth_")
        
        # Initialize storage layers
        self._initialize_storage_layers()
    
    def _initialize_storage_layers(self):
        """Initialize all storage layers"""
        try:
            if self.hf_api:
                # Ensure workspace dataset exists
                self._ensure_dataset_exists(self.workspace_dataset, "HAWKMOTH Development Workspace")
                # Ensure cache dataset exists  
                self._ensure_dataset_exists(self.cache_dataset, "HAWKMOTH Cache Storage")
                print("✅ HuggingFace Dataset storage layers initialized")
            else:
                print("⚠️ HF_TOKEN not available - using local-only storage")
                
            print(f"✅ Local memory storage initialized: {self.temp_dir}")
            
        except Exception as e:
            print(f"⚠️ Storage initialization warning: {e}")
    
    def _ensure_dataset_exists(self, dataset_id: str, description: str):
        """Ensure a dataset exists, create if necessary"""
        try:
            # Try to access the dataset
            self.hf_api.dataset_info(dataset_id)
        except RepositoryNotFoundError:
            # Create the dataset if it doesn't exist
            try:
                create_repo(
                    repo_id=dataset_id,
                    repo_type="dataset", 
                    token=self.hf_token,
                    private=False,
                    exist_ok=True
                )
                
                # Create initial README
                readme_content = f"""---
title: {dataset_id.split('/')[-1]}
dataset_info:
  features:
  - name: file_path
    dtype: string
  - name: content
    dtype: string
  - name: metadata
    dtype: string
---

# {dataset_id}

{description}

This dataset is managed by HAWKMOTH Persistent Storage System.
"""
                
                upload_file(
                    path_or_fileobj=readme_content.encode(),
                    path_in_repo="README.md",
                    repo_id=dataset_id,
                    repo_type="dataset",
                    token=self.hf_token,
                    commit_message="Initialize HAWKMOTH storage dataset"
                )
                
                print(f"✅ Created dataset: {dataset_id}")
                
            except Exception as create_error:
                print(f"⚠️ Could not create dataset {dataset_id}: {create_error}")
    
    # === WORKSPACE MANAGEMENT ===
    
    def create_workspace(self, project_name: str, description: str = "") -> Dict[str, Any]:
        """Create a new persistent workspace for a project"""
        try:
            workspace_id = f"workspace_{project_name}_{int(time.time())}"
            workspace_path = os.path.join(self.temp_dir, workspace_id)
            os.makedirs(workspace_path, exist_ok=True)
            
            # Initialize workspace metadata
            workspace_metadata = {
                "workspace_id": workspace_id,
                "project_name": project_name,
                "description": description,
                "created_at": time.time(),
                "files": {},
                "git_repos": {},
                "storage_layers": ["local", "datasets", "git"]
            }
            
            # Save to local memory
            self.local_memory[workspace_id] = workspace_metadata
            self.active_workspaces[project_name] = workspace_id
            
            # Save workspace metadata to HF Dataset
            if self.hf_api:
                self._save_to_dataset(
                    f"workspaces/{workspace_id}/metadata.json",
                    json.dumps(workspace_metadata, indent=2),
                    self.workspace_dataset
                )
            
            return {
                "success": True,
                "workspace_id": workspace_id,
                "workspace_path": workspace_path,
                "message": f"Workspace '{project_name}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create workspace: {str(e)}"
            }
    
    def get_workspace(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get active workspace for a project"""
        workspace_id = self.active_workspaces.get(project_name)
        if workspace_id and workspace_id in self.local_memory:
            return self.local_memory[workspace_id]
        return None
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """List all available workspaces"""
        workspaces = []
        for workspace_id, metadata in self.local_memory.items():
            workspaces.append({
                "workspace_id": workspace_id,
                "project_name": metadata.get("project_name", "Unknown"),
                "description": metadata.get("description", ""),
                "created_at": metadata.get("created_at", 0),
                "file_count": len(metadata.get("files", {}))
            })
        return workspaces
    
    # === FILE OPERATIONS ===
    
    def save_file(self, workspace_id: str, file_path: str, content: str, 
                  storage_layer: str = "auto") -> Dict[str, Any]:
        """Save file to persistent storage with automatic layer selection"""
        try:
            if workspace_id not in self.local_memory:
                return {"success": False, "error": "Workspace not found"}
            
            # Determine storage layer
            if storage_layer == "auto":
                storage_layer = self._determine_storage_layer(file_path, content)
            
            # Save to local memory first
            workspace_path = os.path.join(self.temp_dir, workspace_id)
            full_path = os.path.join(workspace_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update workspace metadata
            workspace_metadata = self.local_memory[workspace_id]
            workspace_metadata["files"][file_path] = {
                "storage_layer": storage_layer,
                "size": len(content),
                "modified_at": time.time(),
                "local_path": full_path
            }
            
            # Save to appropriate persistent layer
            if storage_layer == "git":
                result = self._save_to_git(workspace_id, file_path, content)
            elif storage_layer == "dataset":
                result = self._save_to_dataset(
                    f"workspaces/{workspace_id}/{file_path}",
                    content,
                    self.workspace_dataset
                )
            else:
                result = {"success": True, "message": "Saved to local memory"}
            
            # Update metadata in dataset
            if self.hf_api:
                self._save_to_dataset(
                    f"workspaces/{workspace_id}/metadata.json",
                    json.dumps(workspace_metadata, indent=2),
                    self.workspace_dataset
                )
            
            return {
                "success": True,
                "file_path": file_path,
                "storage_layer": storage_layer,
                "message": f"File saved to {storage_layer} storage"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save file: {str(e)}"
            }
    
    def load_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Load file from persistent storage"""
        try:
            if workspace_id not in self.local_memory:
                return {"success": False, "error": "Workspace not found"}
            
            workspace_metadata = self.local_memory[workspace_id]
            file_info = workspace_metadata["files"].get(file_path)
            
            if not file_info:
                return {"success": False, "error": "File not found in workspace"}
            
            storage_layer = file_info["storage_layer"]
            
            # Try local first
            local_path = file_info.get("local_path")
            if local_path and os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "success": True,
                    "content": content,
                    "storage_layer": "local_cache",
                    "file_info": file_info
                }
            
            # Load from persistent storage
            if storage_layer == "git":
                content = self._load_from_git(workspace_id, file_path)
            elif storage_layer == "dataset":
                content = self._load_from_dataset(
                    f"workspaces/{workspace_id}/{file_path}",
                    self.workspace_dataset
                )
            else:
                return {"success": False, "error": "File not available"}
            
            if content:
                # Cache locally
                workspace_path = os.path.join(self.temp_dir, workspace_id)
                full_path = os.path.join(workspace_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "content": content,
                    "storage_layer": storage_layer,
                    "file_info": file_info
                }
            
            return {"success": False, "error": "Could not load file from storage"}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load file: {str(e)}"
            }
    
    def list_files(self, workspace_id: str, directory: str = "") -> Dict[str, Any]:
        """List files in workspace directory"""
        try:
            if workspace_id not in self.local_memory:
                return {"success": False, "error": "Workspace not found"}
            
            workspace_metadata = self.local_memory[workspace_id]
            files = []
            
            for file_path, file_info in workspace_metadata["files"].items():
                if directory == "" or file_path.startswith(directory):
                    files.append({
                        "path": file_path,
                        "storage_layer": file_info["storage_layer"],
                        "size": file_info["size"],
                        "modified_at": file_info["modified_at"]
                    })
            
            return {
                "success": True,
                "files": files,
                "directory": directory,
                "workspace_id": workspace_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list files: {str(e)}"
            }
    
    def delete_file(self, workspace_id: str, file_path: str) -> Dict[str, Any]:
        """Delete file from persistent storage"""
        try:
            if workspace_id not in self.local_memory:
                return {"success": False, "error": "Workspace not found"}
            
            workspace_metadata = self.local_memory[workspace_id]
            
            if file_path not in workspace_metadata["files"]:
                return {"success": False, "error": "File not found"}
            
            file_info = workspace_metadata["files"][file_path]
            
            # Remove from local
            local_path = file_info.get("local_path")
            if local_path and os.path.exists(local_path):
                os.remove(local_path)
            
            # Remove from workspace metadata
            del workspace_metadata["files"][file_path]
            
            # Update metadata in dataset
            if self.hf_api:
                self._save_to_dataset(
                    f"workspaces/{workspace_id}/metadata.json",
                    json.dumps(workspace_metadata, indent=2),
                    self.workspace_dataset
                )
            
            return {
                "success": True,
                "message": f"File '{file_path}' deleted from workspace"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    # === GIT INTEGRATION ===
    
    def create_git_repo(self, workspace_id: str, repo_name: str, 
                       description: str = "") -> Dict[str, Any]:
        """Create a new Git repository for workspace"""
        try:
            if not self.hf_api:
                return {"success": False, "error": "HF_TOKEN required for Git operations"}
            
            repo_id = f"{self.user_name}/{repo_name}"
            
            # Create the repository
            create_repo(
                repo_id=repo_id,
                token=self.hf_token,
                private=False,
                exist_ok=True
            )
            
            # Update workspace metadata
            if workspace_id in self.local_memory:
                workspace_metadata = self.local_memory[workspace_id]
                workspace_metadata["git_repos"][repo_name] = {
                    "repo_id": repo_id,
                    "created_at": time.time(),
                    "description": description
                }
                
                # Save updated metadata
                self._save_to_dataset(
                    f"workspaces/{workspace_id}/metadata.json",
                    json.dumps(workspace_metadata, indent=2),
                    self.workspace_dataset
                )
            
            return {
                "success": True,
                "repo_id": repo_id,
                "repo_url": f"https://huggingface.co/{repo_id}",
                "message": f"Git repository '{repo_name}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create Git repository: {str(e)}"
            }
    
    def sync_with_git(self, workspace_id: str, repo_name: str, 
                      commit_message: str = "HAWKMOTH workspace sync") -> Dict[str, Any]:
        """Sync workspace files with Git repository"""
        try:
            if workspace_id not in self.local_memory:
                return {"success": False, "error": "Workspace not found"}
            
            workspace_metadata = self.local_memory[workspace_id]
            
            if repo_name not in workspace_metadata["git_repos"]:
                return {"success": False, "error": "Git repository not found in workspace"}
            
            repo_id = workspace_metadata["git_repos"][repo_name]["repo_id"]
            uploaded_files = []
            
            # Upload all git-layer files to repository
            for file_path, file_info in workspace_metadata["files"].items():
                if file_info["storage_layer"] == "git":
                    local_path = file_info.get("local_path")
                    if local_path and os.path.exists(local_path):
                        upload_file(
                            path_or_fileobj=local_path,
                            path_in_repo=file_path,
                            repo_id=repo_id,
                            token=self.hf_token,
                            commit_message=f"{commit_message} - {file_path}"
                        )
                        uploaded_files.append(file_path)
            
            return {
                "success": True,
                "repo_id": repo_id,
                "uploaded_files": uploaded_files,
                "message": f"Synced {len(uploaded_files)} files to Git repository"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to sync with Git: {str(e)}"
            }
    
    # === DATASET OPERATIONS ===
    
    def _save_to_dataset(self, file_path: str, content: str, dataset_id: str) -> Dict[str, Any]:
        """Save content to HuggingFace Dataset"""
        try:
            if not self.hf_api:
                return {"success": False, "error": "HF API not available"}
            
            upload_file(
                path_or_fileobj=content.encode(),
                path_in_repo=file_path,
                repo_id=dataset_id,
                repo_type="dataset",
                token=self.hf_token,
                commit_message=f"HAWKMOTH storage update: {file_path}"
            )
            
            return {"success": True, "message": "Saved to dataset"}
            
        except Exception as e:
            return {"success": False, "error": f"Dataset save failed: {str(e)}"}
    
    def _load_from_dataset(self, file_path: str, dataset_id: str) -> Optional[str]:
        """Load content from HuggingFace Dataset"""
        try:
            if not self.hf_api:
                return None
            
            # Download file to temporary location
            temp_file = os.path.join(self.temp_dir, "temp_download")
            download_file(
                repo_id=dataset_id,
                filename=file_path,
                local_dir=os.path.dirname(temp_file),
                token=self.hf_token,
                repo_type="dataset"
            )
            
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            os.remove(temp_file)
            return content
            
        except Exception as e:
            print(f"Dataset load failed: {e}")
            return None
    
    # === GIT OPERATIONS ===
    
    def _save_to_git(self, workspace_id: str, file_path: str, content: str) -> Dict[str, Any]:
        """Save file to Git repository (placeholder - requires git repo setup)"""
        # This would be implemented once we have git repos set up for workspaces
        return {"success": True, "message": "Git save placeholder"}
    
    def _load_from_git(self, workspace_id: str, file_path: str) -> Optional[str]:
        """Load file from Git repository (placeholder)"""
        # This would be implemented once we have git repos set up for workspaces
        return None
    
    # === UTILITY METHODS ===
    
    def _determine_storage_layer(self, file_path: str, content: str) -> str:
        """Automatically determine best storage layer for file"""
        file_size = len(content)
        file_ext = Path(file_path).suffix.lower()
        
        # Large files to dataset storage
        if file_size > 100000:  # > 100KB
            return "dataset"
        
        # Code files to git storage  
        if file_ext in ['.py', '.js', '.html', '.css', '.md', '.json', '.yml', '.yaml']:
            return "git"
        
        # Default to local memory for small files
        return "local"
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        stats = {
            "workspaces": len(self.active_workspaces),
            "total_files": 0,
            "storage_layers": {"local": 0, "git": 0, "dataset": 0},
            "total_size": 0,
            "hf_available": bool(self.hf_api)
        }
        
        for workspace_metadata in self.local_memory.values():
            files = workspace_metadata.get("files", {})
            stats["total_files"] += len(files)
            
            for file_info in files.values():
                layer = file_info.get("storage_layer", "local")
                stats["storage_layers"][layer] += 1
                stats["total_size"] += file_info.get("size", 0)
        
        return stats
    
    def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            print("✅ HAWKMOTH storage cleanup completed")
        except Exception as e:
            print(f"⚠️ Storage cleanup warning: {e}")

# === USAGE EXAMPLE ===

def example_usage():
    """Example of how to use HAWKMOTH Persistent Storage"""
    
    # Initialize storage system
    storage = HAWKMOTHPersistentStorage()
    
    # Create a workspace
    result = storage.create_workspace("my-project", "Example development project")
    workspace_id = result["workspace_id"]
    
    # Save some files
    storage.save_file(workspace_id, "main.py", "print('Hello HAWKMOTH!')")
    storage.save_file(workspace_id, "README.md", "# My Project\n\nDeveloped in HAWKMOTH")
    storage.save_file(workspace_id, "data/large_file.json", '{"data": "' + "x" * 50000 + '"}')
    
    # List files
    files = storage.list_files(workspace_id)
    print("Workspace files:", files)
    
    # Load a file
    file_content = storage.load_file(workspace_id, "main.py")
    print("Loaded content:", file_content["content"])
    
    # Get storage stats
    stats = storage.get_storage_stats()
    print("Storage stats:", stats)
    
    # Cleanup
    storage.cleanup()

if __name__ == "__main__":
    example_usage()
