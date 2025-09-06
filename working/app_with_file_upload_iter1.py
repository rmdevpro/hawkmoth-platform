# HAWKMOTH v0.1.0-dev - Component 2: File Upload Handling System
import os
import subprocess
import sys
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import time

# Add working directory to path for all imports
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Import storage system components
try:
    from storage_integration_iter1 import HAWKMOTHStorageManager, get_hawkmoth_storage, initialize_hawkmoth_storage
    from storage_api_iter1 import add_storage_routes
    STORAGE_AVAILABLE = True
    print("✅ HAWKMOTH Storage System imported successfully")
except ImportError as e:
    print(f"⚠️ Storage system not available: {e}")
    STORAGE_AVAILABLE = False

# Import enhanced conversation components
try:
    from enhanced_conversation_final import HAWKMOTHEnhancedConversationManager
    ENHANCED_CONVERSATION_AVAILABLE = True
    print("✅ Enhanced Conversation Manager (LLM Teaming + Auto-Escalation) imported successfully")
except ImportError as e:
    print(f"⚠️ Enhanced conversation not available: {e}")
    ENHANCED_CONVERSATION_AVAILABLE = False
    # Fallback to basic conversation
    from conversation import ConversationManager

# Import additional components
from analyzer import GitHubAnalyzer

# Initialize Git configuration immediately on startup
def initialize_git_config():
    """Configure Git for HAWKMOTH operations"""
    try:
        subprocess.run(['git', 'config', '--global', 'user.name', 'HAWKMOTH-Bot'], 
                     capture_output=True, timeout=3)
        subprocess.run(['git', 'config', '--global', 'user.email', 'hawkmoth@huggingface.co'], 
                     capture_output=True, timeout=3)
        print("✅ HAWKMOTH Git configuration applied")
    except Exception as e:
        print(f"⚠️ Git config warning: {e}")

# Initialize Git on startup
initialize_git_config()

# Create FastAPI app with CORS for file uploads
app = FastAPI(title="HAWKMOTH v0.1.0-dev - LLM Teaming + File Upload Platform")

# Add CORS middleware to handle file uploads from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
HF_TOKEN = os.getenv('HF_TOKEN', '')
analyzer = GitHubAnalyzer(GITHUB_TOKEN)

# Initialize Storage System
if STORAGE_AVAILABLE:
    try:
        storage_manager = initialize_hawkmoth_storage(HF_TOKEN)
        if storage_manager:
            add_storage_routes(app)
            print("🦅 HAWKMOTH Storage System initialized with API routes")
        else:
            print("⚠️ Storage system initialization failed")
            STORAGE_AVAILABLE = False
    except Exception as e:
        print(f"⚠️ Storage system initialization error: {e}")
        STORAGE_AVAILABLE = False

# Initialize Enhanced Conversation or fallback to basic conversation
if ENHANCED_CONVERSATION_AVAILABLE:
    enhanced_conversation_manager = HAWKMOTHEnhancedConversationManager(analyzer)
    print("🦅 HAWKMOTH Enhanced Conversation Manager initialized (LLM Teaming + Auto-Escalation)")
else:
    conversation_manager = ConversationManager(analyzer)
    print("📝 Basic conversation manager initialized (fallback)")

# === PYDANTIC MODELS ===

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"
    session_id: Optional[str] = None

class FileOperationRequest(BaseModel):
    operation: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    workspace_name: Optional[str] = None

# === MAIN ROUTES ===

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("frontend_with_file_upload_iter1.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Enhanced chat endpoint with LLM Teaming + Auto-Escalation + Storage Integration"""
    try:
        # Check for storage commands first
        if STORAGE_AVAILABLE and _is_storage_command(chat_message.message):
            return await process_storage_command(chat_message)
        
        # Process through enhanced conversation manager
        if ENHANCED_CONVERSATION_AVAILABLE:
            return await enhanced_chat(chat_message)
        else:
            return await basic_chat(chat_message)
    except Exception as e:
        return JSONResponse({
            "success": False, 
            "response": f"🔄 HAWKMOTH Error: {str(e)}", 
            "status": "error",
            "fallback_used": True
        })

async def enhanced_chat(chat_message: ChatMessage):
    """Process chat using Enhanced Conversation Manager (LLM Teaming + Auto-Escalation)"""
    try:
        session_id = chat_message.session_id or f"{chat_message.user_id}_session"
        
        # Process message through enhanced conversation manager
        result = enhanced_conversation_manager.process_message(
            chat_message.user_id, 
            chat_message.message, 
            session_id
        )
        
        # Enhanced response format
        response_data = {
            "success": result['success'],
            "response": result['response'],
            "status": "enhanced",
            "session_id": session_id
        }
        
        # Add escalation information if used
        if result.get('escalation_used'):
            response_data["escalation_info"] = result.get('escalation_info', {})
            response_data["auto_approved"] = result.get('auto_approved', False)
        
        # Add LLM information if available
        if result.get('llm_info'):
            response_data["llm_teaming"] = result['llm_info']
        
        # Add command type if this was a platform command
        if result.get('command_type'):
            response_data["command_type"] = result['command_type']
        
        # Add storage information if available
        if STORAGE_AVAILABLE:
            storage_manager = get_hawkmoth_storage()
            if storage_manager:
                current_workspace = storage_manager.get_current_workspace_info()
                if current_workspace.get('success'):
                    response_data["current_workspace"] = current_workspace["workspace"]
        
        return JSONResponse(response_data)
        
    except Exception as e:
        # Fallback to basic response on error
        basic_response = f"🦅 HAWKMOTH (Local): {chat_message.message} processed. Enhanced error: {str(e)}"
        return JSONResponse({
            "success": True,
            "response": basic_response,
            "status": "fallback",
            "enhanced_features": {
                "available": False,
                "error": str(e)
            }
        })

async def basic_chat(chat_message: ChatMessage):
    """Fallback basic chat processing"""
    response = conversation_manager.process_message(
        chat_message.user_id, 
        chat_message.message
    )
    return JSONResponse({
        "success": True, 
        "response": response, 
        "status": "basic",
        "llm_teaming": None
    })

# === STORAGE COMMAND PROCESSING ===

def _is_storage_command(message: str) -> bool:
    """Check if message is a storage-related command"""
    storage_keywords = [
        'create project', 'new project', 'switch project', 'current project',
        'list projects', 'list files', 'save file', 'load file', 'delete file',
        'upload file', 'download file', 'storage status', 'create repo',
        'sync git', 'workspace'
    ]
    return any(keyword in message.lower() for keyword in storage_keywords)

async def process_storage_command(chat_message: ChatMessage):
    """Process storage-related commands through chat interface"""
    try:
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            return JSONResponse({
                "success": False,
                "response": "❌ Storage system not available",
                "status": "error"
            })
        
        message = chat_message.message.lower()
        
        # Parse and execute storage commands
        if 'create project' in message or 'new project' in message:
            # Extract project name from message
            parts = message.replace('create project', '').replace('new project', '').strip().split()
            project_name = parts[0] if parts else f"project_{int(time.time())}"
            
            result = storage_manager.create_project_workspace(project_name, "Created via chat")
            response = f"✅ Project '{project_name}' created successfully!" if result['success'] else f"❌ Failed to create project: {result['error']}"
            
        elif 'switch project' in message or 'switch to' in message:
            parts = message.replace('switch project', '').replace('switch to', '').strip().split()
            project_name = parts[0] if parts else None
            
            if project_name:
                result = storage_manager.switch_workspace(project_name)
                response = f"✅ Switched to project '{project_name}'" if result['success'] else f"❌ Failed to switch: {result['error']}"
            else:
                response = "❌ Please specify project name: switch to PROJECT_NAME"
                
        elif 'current project' in message:
            result = storage_manager.get_current_workspace_info()
            if result['success']:
                workspace = result['workspace']
                response = f"📁 Current project: {workspace['project_name']}\n💾 Files: {len(workspace.get('files', {}))}\n🕒 Created: {time.ctime(workspace.get('created_at', 0))}"
            else:
                response = "❌ No active project"
                
        elif 'list projects' in message:
            workspaces = storage_manager.storage.list_workspaces()
            if workspaces:
                response = "📁 Available projects:\n" + "\n".join([f"• {w['project_name']} ({w['file_count']} files)" for w in workspaces])
            else:
                response = "📁 No projects found. Use 'create project NAME' to start."
                
        elif 'list files' in message:
            result = storage_manager.list_project_files()
            if result['success']:
                files = result['files']
                if files:
                    response = "📄 Project files:\n" + "\n".join([f"• {f['path']} ({f['storage_layer']}, {f['size']} bytes)" for f in files])
                else:
                    response = "📄 No files in current project"
            else:
                response = f"❌ Failed to list files: {result['error']}"
                
        elif 'storage status' in message:
            status = storage_manager.get_hawkmoth_status()
            stats = status['storage_statistics']
            response = f"💾 HAWKMOTH Storage Status:\n• Workspaces: {stats['workspaces']}\n• Total Files: {stats['total_files']}\n• Storage Layers: Git({stats['storage_layers']['git']}), HF({stats['storage_layers']['dataset']}), Local({stats['storage_layers']['local']})\n• HF Available: {stats['hf_available']}"
            
        else:
            response = "🤔 Storage command not recognized. Try: create project, list files, storage status"
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command",
            "command_type": "storage",
            "storage_available": True
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "response": f"❌ Storage command error: {str(e)}",
            "status": "error"
        })

# === FILE UPLOAD ENDPOINTS ===

@app.post("/upload")
async def upload_file_endpoint(
    file: UploadFile = File(...),
    workspace_name: Optional[str] = Form(None),
    file_path: Optional[str] = Form(None)
):
    """Enhanced file upload endpoint with workspace integration"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        # Switch to specified workspace if provided
        if workspace_name:
            switch_result = storage_manager.switch_workspace(workspace_name)
            if not switch_result['success']:
                # Create workspace if it doesn't exist
                create_result = storage_manager.create_project_workspace(workspace_name, "Created during file upload")
                if not create_result['success']:
                    raise HTTPException(status_code=400, detail=f"Failed to create/switch workspace: {create_result['error']}")
        
        # Read file content
        content = await file.read()
        
        # Handle binary files by converting to base64
        try:
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            import base64
            content_str = base64.b64encode(content).decode('utf-8')
            file_path = file_path or file.filename
            if file_path and not file_path.endswith('.b64'):
                file_path += '.b64'
        
        # Use provided path or file's filename
        target_path = file_path or file.filename
        
        # Save file to storage
        result = storage_manager.save_project_file(target_path, content_str)
        
        if result['success']:
            return JSONResponse({
                "success": True,
                "message": f"File '{file.filename}' uploaded successfully",
                "file_path": target_path,
                "storage_layer": result['storage_layer'],
                "size": len(content),
                "workspace": workspace_name or "current"
            })
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.post("/upload-multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    workspace_name: Optional[str] = Form(None)
):
    """Upload multiple files to workspace"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        # Switch to specified workspace if provided
        if workspace_name:
            switch_result = storage_manager.switch_workspace(workspace_name)
            if not switch_result['success']:
                create_result = storage_manager.create_project_workspace(workspace_name, "Created during multiple file upload")
                if not create_result['success']:
                    raise HTTPException(status_code=400, detail=f"Failed to create/switch workspace: {create_result['error']}")
        
        results = []
        total_size = 0
        
        for file in files:
            try:
                content = await file.read()
                
                # Handle binary files
                try:
                    content_str = content.decode('utf-8')
                    file_path = file.filename
                except UnicodeDecodeError:
                    import base64
                    content_str = base64.b64encode(content).decode('utf-8')
                    file_path = file.filename + '.b64'
                
                # Save file
                result = storage_manager.save_project_file(file_path, content_str)
                
                if result['success']:
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "storage_layer": result['storage_layer'],
                        "size": len(content)
                    })
                    total_size += len(content)
                else:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": result['error']
                    })
                    
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        successful_uploads = sum(1 for r in results if r['success'])
        
        return JSONResponse({
            "success": True,
            "message": f"Uploaded {successful_uploads}/{len(files)} files successfully",
            "results": results,
            "total_size": total_size,
            "workspace": workspace_name or "current"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multiple upload error: {str(e)}")

@app.get("/download/{file_path:path}")
async def download_file_endpoint(file_path: str, workspace_name: Optional[str] = None):
    """Download file from workspace"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        # Switch to specified workspace if provided
        if workspace_name:
            switch_result = storage_manager.switch_workspace(workspace_name)
            if not switch_result['success']:
                raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Load file from storage
        result = storage_manager.load_project_file(file_path)
        
        if result['success']:
            content = result['content']
            
            # Handle base64 encoded files
            if file_path.endswith('.b64'):
                import base64
                content = base64.b64decode(content)
                original_filename = file_path[:-4]  # Remove .b64 extension
                return FileResponse(
                    path=None,
                    filename=original_filename,
                    content=content,
                    media_type='application/octet-stream'
                )
            else:
                # Text file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                    f.write(content)
                    temp_path = f.name
                
                return FileResponse(
                    path=temp_path,
                    filename=os.path.basename(file_path),
                    media_type='text/plain'
                )
        else:
            raise HTTPException(status_code=404, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download error: {str(e)}")

# === FILE MANAGEMENT ENDPOINTS ===

@app.get("/files")
async def list_files_endpoint(workspace_name: Optional[str] = None):
    """List all files in workspace with enhanced metadata"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        # Switch to specified workspace if provided
        if workspace_name:
            switch_result = storage_manager.switch_workspace(workspace_name)
            if not switch_result['success']:
                raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Get current workspace info
        workspace_info = storage_manager.get_current_workspace_info()
        if not workspace_info['success']:
            raise HTTPException(status_code=404, detail="No active workspace")
        
        # List files with enhanced metadata
        result = storage_manager.list_project_files()
        
        if result['success']:
            files = result['files']
            
            # Add file type and preview for each file
            enhanced_files = []
            for file_info in files:
                enhanced_file = file_info.copy()
                
                # Determine file type
                file_extension = os.path.splitext(file_info['path'])[1].lower()
                if file_extension in ['.py', '.js', '.html', '.css', '.md', '.json', '.txt']:
                    enhanced_file['type'] = 'text'
                    enhanced_file['category'] = 'code' if file_extension in ['.py', '.js', '.html', '.css'] else 'document'
                elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
                    enhanced_file['type'] = 'image'
                    enhanced_file['category'] = 'media'
                elif file_extension == '.b64':
                    enhanced_file['type'] = 'binary'
                    enhanced_file['category'] = 'binary'
                else:
                    enhanced_file['type'] = 'unknown'
                    enhanced_file['category'] = 'other'
                
                # Add human-readable size
                size = file_info['size']
                if size < 1024:
                    enhanced_file['human_size'] = f"{size} B"
                elif size < 1024 * 1024:
                    enhanced_file['human_size'] = f"{size / 1024:.1f} KB"
                else:
                    enhanced_file['human_size'] = f"{size / (1024 * 1024):.1f} MB"
                
                # Add human-readable time
                enhanced_file['human_time'] = time.ctime(file_info['modified_at'])
                
                enhanced_files.append(enhanced_file)
            
            return JSONResponse({
                "success": True,
                "files": enhanced_files,
                "workspace": workspace_info['workspace'],
                "total_files": len(enhanced_files),
                "total_size": sum(f['size'] for f in enhanced_files)
            })
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File listing error: {str(e)}")

@app.delete("/files/{file_path:path}")
async def delete_file_endpoint(file_path: str, workspace_name: Optional[str] = None):
    """Delete file from workspace"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        # Switch to specified workspace if provided
        if workspace_name:
            switch_result = storage_manager.switch_workspace(workspace_name)
            if not switch_result['success']:
                raise HTTPException(status_code=404, detail="Workspace not found")
        
        # Delete file
        result = storage_manager.delete_project_file(file_path)
        
        if result['success']:
            return JSONResponse({
                "success": True,
                "message": f"File '{file_path}' deleted successfully"
            })
        else:
            raise HTTPException(status_code=404, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion error: {str(e)}")

# === STATUS AND ENHANCED ENDPOINTS ===

@app.get("/enhanced-status")
async def enhanced_status():
    """Get Enhanced Conversation Manager + Storage status"""
    status_response = {
        "enhanced_features_available": ENHANCED_CONVERSATION_AVAILABLE,
        "storage_available": STORAGE_AVAILABLE,
        "file_upload_available": STORAGE_AVAILABLE
    }
    
    # Add enhanced conversation status
    if ENHANCED_CONVERSATION_AVAILABLE:
        session_stats = enhanced_conversation_manager.get_session_stats()
        status_response.update({
            "llm_teaming_available": session_stats.get('enhanced_mode', False),
            "auto_escalation_available": session_stats.get('enhanced_mode', False),
            "session_statistics": {
                "total_queries": session_stats['total_queries'],
                "escalations_triggered": session_stats['escalations_triggered'],
                "escalations_successful": session_stats['escalations_successful'],
                "real_time_queries": session_stats['real_time_queries'],
                "model_failures": session_stats['model_failures'],
                "total_cost": session_stats['total_cost']
            }
        })
    
    # Add storage status
    if STORAGE_AVAILABLE:
        storage_manager = get_hawkmoth_storage()
        if storage_manager:
            storage_status = storage_manager.get_hawkmoth_status()
            status_response["storage_status"] = storage_status['storage_statistics']
            
            # Get current workspace info
            workspace_info = storage_manager.get_current_workspace_info()
            if workspace_info['success']:
                status_response["current_workspace"] = workspace_info['workspace']
    
    return JSONResponse(status_response)

@app.get("/health")
async def health_check():
    """Enhanced health check with all features"""
    base_health = {
        "status": "healthy", 
        "service": "HAWKMOTH v0.1.0-dev", 
        "git_available": True,
        "platform_ready": True,
        "storage_available": STORAGE_AVAILABLE,
        "file_upload_available": STORAGE_AVAILABLE
    }
    
    if ENHANCED_CONVERSATION_AVAILABLE:
        session_stats = enhanced_conversation_manager.get_session_stats()
        base_health.update({
            "enhanced_features": True,
            "llm_teaming": session_stats.get('enhanced_mode', False),
            "auto_escalation": session_stats.get('enhanced_mode', False),
            "total_queries": session_stats['total_queries'],
            "escalations_triggered": session_stats['escalations_triggered']
        })
    
    if STORAGE_AVAILABLE:
        storage_manager = get_hawkmoth_storage()
        if storage_manager:
            storage_stats = storage_manager.storage.get_storage_stats()
            base_health.update({
                "storage_workspaces": storage_stats['workspaces'],
                "storage_files": storage_stats['total_files'],
                "storage_layers": storage_stats['storage_layers']
            })
    
    return base_health

@app.get("/version")
async def version():
    """Enhanced version info with all features"""
    features = ["Basic Chat"]
    if ENHANCED_CONVERSATION_AVAILABLE:
        features.extend(["LLM Teaming", "Auto-Escalation", "Sticky Sessions", "Cost Optimization"])
    if STORAGE_AVAILABLE:
        features.extend(["Persistent Storage", "File Upload", "Workspace Management", "Git Integration"])
    
    version_info = {
        "version": "0.1.0-dev", 
        "platform": "HAWKMOTH",
        "component": "Component 2: File Upload Handling",
        "features": features,
        "storage_available": STORAGE_AVAILABLE,
        "file_upload_available": STORAGE_AVAILABLE,
        "git_available": True,
        "deployment_system": "HuggingFace Spaces"
    }
    
    return version_info

# === ADDITIONAL FILE OPERATIONS ===

@app.post("/create-file")
async def create_file_endpoint(request: FileOperationRequest):
    """Create new file in workspace"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        if not request.file_path or not request.content:
            raise HTTPException(status_code=400, detail="file_path and content required")
        
        # Switch workspace if specified
        if request.workspace_name:
            switch_result = storage_manager.switch_workspace(request.workspace_name)
            if not switch_result['success']:
                create_result = storage_manager.create_project_workspace(request.workspace_name, "Created during file creation")
                if not create_result['success']:
                    raise HTTPException(status_code=400, detail=f"Failed to create/switch workspace: {create_result['error']}")
        
        # Save file
        result = storage_manager.save_project_file(request.file_path, request.content)
        
        if result['success']:
            return JSONResponse({
                "success": True,
                "message": f"File '{request.file_path}' created successfully",
                "storage_layer": result['storage_layer']
            })
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File creation error: {str(e)}")

@app.get("/workspaces")
async def list_workspaces_endpoint():
    """List all available workspaces"""
    try:
        if not STORAGE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Storage system not available")
        
        storage_manager = get_hawkmoth_storage()
        if not storage_manager:
            raise HTTPException(status_code=503, detail="Storage manager not initialized")
        
        workspaces = storage_manager.storage.list_workspaces()
        
        return JSONResponse({
            "success": True,
            "workspaces": workspaces
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workspace listing error: {str(e)}")

if __name__ == "__main__":
    # Ensure Git config is set before starting server
    initialize_git_config()
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
