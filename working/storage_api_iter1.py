# HAWKMOTH Storage API Endpoints - FastAPI routes for persistent storage
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os

# Import storage components (these will be relative imports in the actual app)
from .storage_integration_iter1 import get_hawkmoth_storage, initialize_hawkmoth_storage

# Pydantic models for API requests
class CreateWorkspaceRequest(BaseModel):
    project_name: str
    description: str = ""

class SaveFileRequest(BaseModel):
    file_path: str
    content: str
    storage_layer: str = "auto"

class LoadFileRequest(BaseModel):
    file_path: str

class DeleteFileRequest(BaseModel):
    file_path: str

class CreateRepoRequest(BaseModel):
    repo_name: Optional[str] = None
    description: str = ""

class SyncGitRequest(BaseModel):
    repo_name: Optional[str] = None
    commit_message: Optional[str] = None

class SwitchWorkspaceRequest(BaseModel):
    project_name: str

# Create router for storage endpoints
storage_router = APIRouter(prefix="/storage", tags=["storage"])

# === WORKSPACE MANAGEMENT ENDPOINTS ===

@storage_router.get("/status")
async def get_storage_status():
    """Get comprehensive HAWKMOTH storage system status"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            # Initialize if not already done
            storage_manager = initialize_hawkmoth_storage()
        
        status = storage_manager.get_hawkmoth_status()
        return JSONResponse(status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage status error: {str(e)}")

@storage_router.post("/workspace/create")
async def create_workspace(request: CreateWorkspaceRequest):
    """Create a new project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.create_project_workspace(
            request.project_name, 
            request.description
        )
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace creation error: {str(e)}")

@storage_router.post("/workspace/switch")
async def switch_workspace(request: SwitchWorkspaceRequest):
    """Switch to a different project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.switch_workspace(request.project_name)
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace switch error: {str(e)}")

@storage_router.get("/workspace/current")
async def get_current_workspace():
    """Get information about current active workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.get_current_workspace_info()
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace info error: {str(e)}")

@storage_router.get("/workspaces")
async def list_workspaces():
    """List all available workspaces"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        workspaces = storage_manager.storage.list_workspaces()
        
        return JSONResponse({
            "success": True,
            "workspaces": workspaces
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace listing error: {str(e)}")

# === FILE MANAGEMENT ENDPOINTS ===

@storage_router.post("/file/save")
async def save_file(request: SaveFileRequest):
    """Save file to current project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.save_project_file(
            request.file_path,
            request.content,
            request.storage_layer
        )
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")

@storage_router.post("/file/load")
async def load_file(request: LoadFileRequest):
    """Load file from current project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.load_project_file(request.file_path)
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File load error: {str(e)}")

@storage_router.get("/files")
async def list_files(directory: str = ""):
    """List files in current project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.list_project_files(directory)
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File listing error: {str(e)}")

@storage_router.delete("/file/delete")
async def delete_file(request: DeleteFileRequest):
    """Delete file from current project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.delete_project_file(request.file_path)
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion error: {str(e)}")

@storage_router.post("/file/upload")
async def upload_file(file: UploadFile = File(...), file_path: str = None):
    """Upload file to current project workspace"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8') if isinstance(content, bytes) else content
        
        # Use provided path or file's filename
        target_path = file_path or file.filename
        
        result = storage_manager.save_project_file(target_path, content_str)
        
        if result["success"]:
            result["uploaded_file"] = file.filename
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

# === GIT INTEGRATION ENDPOINTS ===

@storage_router.post("/git/create-repo")
async def create_git_repo(request: CreateRepoRequest):
    """Create Git repository for current project"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.create_project_repo(
            request.repo_name,
            request.description
        )
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git repo creation error: {str(e)}")

@storage_router.post("/git/sync")
async def sync_to_git(request: SyncGitRequest):
    """Sync current project to Git repository"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.sync_project_to_git(
            request.repo_name,
            request.commit_message
        )
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git sync error: {str(e)}")

# === STORAGE STATISTICS AND MANAGEMENT ===

@storage_router.get("/stats")
async def get_storage_stats():
    """Get detailed storage statistics"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        stats = storage_manager.storage.get_storage_stats()
        
        return JSONResponse({
            "success": True,
            "storage_statistics": stats,
            "timestamp": time.time()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage stats error: {str(e)}")

@storage_router.post("/cleanup")
async def cleanup_storage():
    """Clean up storage resources"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        storage_manager.cleanup()
        
        return JSONResponse({
            "success": True,
            "message": "Storage cleanup completed"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage cleanup error: {str(e)}")

# === DEVELOPMENT HELPER ENDPOINTS ===

@storage_router.get("/workspace/{workspace_id}/files")
async def get_workspace_files(workspace_id: str, directory: str = ""):
    """Get files for a specific workspace (development helper)"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.storage.list_files(workspace_id, directory)
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace files error: {str(e)}")

@storage_router.post("/workspace/{workspace_id}/file/save")
async def save_workspace_file(workspace_id: str, request: SaveFileRequest):
    """Save file to specific workspace (development helper)"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=500, detail="Storage system not initialized")
        
        result = storage_manager.storage.save_file(
            workspace_id,
            request.file_path,
            request.content,
            request.storage_layer
        )
        
        if result["success"]:
            return JSONResponse(result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace file save error: {str(e)}")

# Function to add these routes to main app
def add_storage_routes(app):
    """Add storage routes to main FastAPI app"""
    app.include_router(storage_router)
    print("✅ HAWKMOTH Storage API endpoints added")

# Usage example for main app.py:
"""
from .storage_api_iter1 import add_storage_routes
from .storage_integration_iter1 import initialize_hawkmoth_storage

# In main app initialization:
app = FastAPI()

# Initialize storage system
hf_token = os.getenv('HF_TOKEN')
initialize_hawkmoth_storage(hf_token)

# Add storage API routes
add_storage_routes(app)
"""
