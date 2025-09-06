# HAWKMOTH Storage Integration - Updated app.py with Persistent Storage
"""
This file shows how to integrate the HAWKMOTH Persistent Storage system
into the main application. Copy these changes to your main app.py file.
"""

import os
import sys
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

# Add current directory to path for enhanced features
sys.path.append(os.path.dirname(__file__))

# Import storage components
try:
    from storage_integration_iter1 import initialize_hawkmoth_storage, get_hawkmoth_storage
    from storage_api_iter1 import add_storage_routes
    STORAGE_AVAILABLE = True
    print("✅ HAWKMOTH Persistent Storage imported successfully")
except ImportError as e:
    print(f"⚠️ Storage system not available: {e}")
    STORAGE_AVAILABLE = False

# Import existing components
try:
    from enhanced_conversation_final import HAWKMOTHEnhancedConversationManager
    ENHANCED_CONVERSATION_AVAILABLE = True
    print("✅ Enhanced Conversation Manager imported successfully")
except ImportError as e:
    print(f"⚠️ Enhanced conversation not available: {e}")
    ENHANCED_CONVERSATION_AVAILABLE = False
    from conversation import ConversationManager

# Import analyzer
from analyzer import GitHubAnalyzer

# Initialize Git configuration immediately on startup
def initialize_git_config():
    """Configure Git for HAWKMOTH operations"""
    try:
        import subprocess
        subprocess.run(['git', 'config', '--global', 'user.name', 'HAWKMOTH-Bot'], 
                     capture_output=True, timeout=3)
        subprocess.run(['git', 'config', '--global', 'user.email', 'hawkmoth@huggingface.co'], 
                     capture_output=True, timeout=3)
        print("✅ HAWKMOTH Git configuration applied")
    except Exception as e:
        print(f"⚠️ Git config warning: {e}")

# Initialize Git on startup
initialize_git_config()

# Create FastAPI app
app = FastAPI(title="HAWKMOTH v0.1.0-dev - LLM Teaming + Auto-Escalation + Persistent Storage")

# Initialize storage system
HF_TOKEN = os.getenv('HF_TOKEN', '')
if STORAGE_AVAILABLE:
    storage_manager = initialize_hawkmoth_storage(HF_TOKEN)
    print("🦅 HAWKMOTH Persistent Storage initialized")
else:
    storage_manager = None

# Initialize other components
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
analyzer = GitHubAnalyzer(GITHUB_TOKEN)

# Initialize Enhanced Conversation or fallback to basic conversation
if ENHANCED_CONVERSATION_AVAILABLE:
    enhanced_conversation_manager = HAWKMOTHEnhancedConversationManager(analyzer)
    print("🦅 HAWKMOTH Enhanced Conversation Manager initialized")
else:
    conversation_manager = ConversationManager(analyzer)
    print("📝 Basic conversation manager initialized (fallback)")

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"
    session_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Enhanced chat endpoint with storage integration"""
    try:
        # Check for storage commands first
        if STORAGE_AVAILABLE and storage_manager:
            storage_result = await handle_storage_commands(chat_message)
            if storage_result:
                return storage_result
        
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

async def handle_storage_commands(chat_message: ChatMessage):
    """Handle storage-related commands in chat"""
    message = chat_message.message.lower().strip()
    
    # Storage command patterns
    if message.startswith("create project "):
        project_name = message.replace("create project ", "").strip()
        result = storage_manager.create_project_workspace(project_name, f"Project created via chat: {project_name}")
        
        if result["success"]:
            response = f"🦅 Project '{project_name}' created successfully! You can now save files to this workspace."
        else:
            response = f"❌ Failed to create project: {result['error']}"
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command",
            "command_type": "create_project",
            "result": result
        })
    
    elif message == "list projects":
        workspaces = storage_manager.storage.list_workspaces()
        
        if workspaces:
            project_list = "\n".join([f"• {ws['project_name']} ({ws['file_count']} files)" for ws in workspaces])
            response = f"🦅 Available Projects:\n{project_list}"
        else:
            response = "🦅 No projects found. Use 'create project <name>' to create one."
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command",
            "command_type": "list_projects",
            "workspaces": workspaces
        })
    
    elif message.startswith("switch to "):
        project_name = message.replace("switch to ", "").strip()
        result = storage_manager.switch_workspace(project_name)
        
        if result["success"]:
            response = f"🦅 Switched to project '{project_name}'"
        else:
            response = f"❌ Could not switch to project: {result['error']}"
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command", 
            "command_type": "switch_project",
            "result": result
        })
    
    elif message == "current project":
        result = storage_manager.get_current_workspace_info()
        
        if result["success"]:
            response = f"""🦅 Current Project: {result['project_name']}
📁 Files: {result['file_count']}
📅 Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result['created_at']))}"""
        else:
            response = f"❌ No active project: {result['error']}"
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command",
            "command_type": "current_project",
            "result": result
        })
    
    elif message == "list files":
        result = storage_manager.list_project_files()
        
        if result["success"] and result["files"]:
            file_list = "\n".join([f"📁 {file_info['path']} ({file_info['storage_layer']})" for file_info in result["files"]])
            response = f"🦅 Project Files:\n{file_list}"
        elif result["success"]:
            response = "🦅 No files in current project."
        else:
            response = f"❌ Could not list files: {result['error']}"
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command",
            "command_type": "list_files", 
            "result": result
        })
    
    elif message == "storage status":
        status = storage_manager.get_hawkmoth_status()
        
        if status["success"]:
            stats = status['storage_statistics']
            response = f"""🦅 HAWKMOTH Storage Status:
💾 Total Files: {stats['total_files']}
📊 Storage Layers: {stats['storage_layers']}
🌐 HuggingFace: {'✅ Available' if stats['hf_available'] else '❌ Not Available'}
📁 Workspaces: {stats['workspaces']}"""
        else:
            response = f"❌ Could not get storage status: {status['error']}"
        
        return JSONResponse({
            "success": True,
            "response": response,
            "status": "storage_command",
            "command_type": "storage_status",
            "result": status
        })
    
    # No storage command matched
    return None

async def enhanced_chat(chat_message: ChatMessage):
    """Process chat using Enhanced Conversation Manager"""
    try:
        session_id = chat_message.session_id or f"{chat_message.user_id}_session"
        
        result = enhanced_conversation_manager.process_message(
            chat_message.user_id, 
            chat_message.message, 
            session_id
        )
        
        response_data = {
            "success": result['success'],
            "response": result['response'],
            "status": "enhanced",
            "session_id": session_id
        }
        
        # Add storage info if available
        if STORAGE_AVAILABLE and storage_manager:
            workspace_info = storage_manager.get_current_workspace_info()
            if workspace_info["success"]:
                response_data["current_project"] = workspace_info["project_name"]
        
        # Add escalation information if used
        if result.get('escalation_used'):
            response_data["escalation_info"] = result.get('escalation_info', {})
            response_data["auto_approved"] = result.get('auto_approved', False)
        
        # Add LLM information if available
        if result.get('llm_info'):
            response_data["llm_teaming"] = result['llm_info']
        
        if result.get('command_type'):
            response_data["command_type"] = result['command_type']
        
        return JSONResponse(response_data)
        
    except Exception as e:
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

@app.get("/enhanced-status")
async def enhanced_status():
    """Get Enhanced Conversation Manager + Storage status"""
    status_response = {
        "enhanced_features_available": ENHANCED_CONVERSATION_AVAILABLE,
        "persistent_storage_available": STORAGE_AVAILABLE
    }
    
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
    
    if STORAGE_AVAILABLE and storage_manager:
        storage_status = storage_manager.get_hawkmoth_status()
        if storage_status["success"]:
            status_response["persistent_storage"] = storage_status
    
    return JSONResponse(status_response)

@app.get("/health")
async def health_check():
    """Enhanced health check with all HAWKMOTH features"""
    base_health = {
        "status": "healthy", 
        "service": "HAWKMOTH v0.1.0-dev", 
        "git_available": True,
        "platform_ready": True,
        "enhanced_features": ENHANCED_CONVERSATION_AVAILABLE,
        "persistent_storage": STORAGE_AVAILABLE
    }
    
    if ENHANCED_CONVERSATION_AVAILABLE:
        session_stats = enhanced_conversation_manager.get_session_stats()
        base_health.update({
            "llm_teaming": session_stats.get('enhanced_mode', False),
            "auto_escalation": session_stats.get('enhanced_mode', False),
            "total_queries": session_stats['total_queries'],
            "escalations_triggered": session_stats['escalations_triggered']
        })
    
    if STORAGE_AVAILABLE and storage_manager:
        storage_status = storage_manager.get_hawkmoth_status()
        if storage_status["success"]:
            base_health["storage_stats"] = storage_status['storage_statistics']
    
    return base_health

@app.get("/version")
async def version():
    """Enhanced version info with all features"""
    features = ["Basic Chat"]
    if ENHANCED_CONVERSATION_AVAILABLE:
        features.extend(["LLM Teaming", "Auto-Escalation", "Sticky Sessions", "Cost Optimization"])
    if STORAGE_AVAILABLE:
        features.extend(["Persistent Storage", "Project Workspaces", "File Management"])
    
    version_info = {
        "version": "0.1.0-dev", 
        "platform": "HAWKMOTH",
        "features": features,
        "git_available": True,
        "deployment_system": "HuggingFace Spaces",
        "storage_layers": ["Git Repositories", "HF Datasets", "Local Memory"] if STORAGE_AVAILABLE else []
    }
    
    return version_info

# Add storage API routes if available
if STORAGE_AVAILABLE:
    add_storage_routes(app)
    print("✅ HAWKMOTH Storage API endpoints added")

if __name__ == "__main__":
    # Ensure Git config is set before starting server
    initialize_git_config()
    
    # Start server
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    
    print("🦅 Starting HAWKMOTH with Persistent Storage...")
    print(f"Enhanced Features: {ENHANCED_CONVERSATION_AVAILABLE}")
    print(f"Persistent Storage: {STORAGE_AVAILABLE}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
