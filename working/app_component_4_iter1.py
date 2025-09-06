# HAWKMOTH v0.1.0-dev - LLM Teaming Platform with Auto-Escalation + Component 4
import os
import subprocess
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
from analyzer import GitHubAnalyzer

# Add working directory to path for LLM Teaming imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'working'))

try:
    from enhanced_conversation_final import HAWKMOTHEnhancedConversationManager
    ENHANCED_CONVERSATION_AVAILABLE = True
    print("✅ Enhanced Conversation Manager (LLM Teaming + Auto-Escalation) imported successfully")
except ImportError as e:
    print(f"⚠️ Enhanced conversation not available: {e}")
    ENHANCED_CONVERSATION_AVAILABLE = False
    # Fallback to basic conversation
    from conversation import ConversationManager

# Import Component 4: Communication Control
try:
    from communication_control_iter1 import communication_controller, ModelType
    COMMUNICATION_CONTROL_AVAILABLE = True
    print("✅ Component 4: Communication Control imported successfully")
except ImportError as e:
    print(f"⚠️ Component 4 not available: {e}")
    COMMUNICATION_CONTROL_AVAILABLE = False
    communication_controller = None
    ModelType = None

# Initialize Git configuration immediately on startup
def initialize_git_config():
    """Configure Git for HAWKMOTH operations"""
    try:
        # Basic Git configuration for HAWKMOTH
        subprocess.run(['git', 'config', '--global', 'user.name', 'HAWKMOTH-Bot'], 
                     capture_output=True, timeout=3)
        subprocess.run(['git', 'config', '--global', 'user.email', 'hawkmoth@huggingface.co'], 
                     capture_output=True, timeout=3)
        print("✅ HAWKMOTH Git configuration applied")
    except Exception as e:
        print(f"⚠️ Git config warning: {e}")

# Initialize Git on startup
initialize_git_config()

app = FastAPI(title="HAWKMOTH v0.1.0-dev - LLM Teaming Platform with Component 4")

# Initialize components
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
analyzer = GitHubAnalyzer(GITHUB_TOKEN)

# Initialize Enhanced Conversation or fallback to basic conversation
if ENHANCED_CONVERSATION_AVAILABLE:
    enhanced_conversation_manager = HAWKMOTHEnhancedConversationManager(analyzer)
    print("🦅 HAWKMOTH Enhanced Conversation Manager initialized (LLM Teaming + Auto-Escalation)")
else:
    conversation_manager = ConversationManager(analyzer)
    print("📝 Basic conversation manager initialized (fallback)")

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"
    session_id: Optional[str] = None

class ModelSwitchRequest(BaseModel):
    target_model: str
    session_id: Optional[str] = None
    permanent: bool = True

class LLMResponse(BaseModel):
    content: str
    model_used: str
    provider: str
    cost: float
    response_time: float
    session_id: str
    routing_info: dict

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Enhanced chat endpoint with LLM Teaming + Auto-Escalation + Component 4 support"""
    try:
        if ENHANCED_CONVERSATION_AVAILABLE:
            # Use Enhanced Conversation Manager (LLM Teaming + Auto-Escalation)
            return await enhanced_chat(chat_message)
        else:
            # Fallback to basic conversation
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
        
        # Add Component 4 model information if available
        if COMMUNICATION_CONTROL_AVAILABLE:
            model_info = communication_controller.get_current_model_info()
            response_data["current_model"] = {
                "name": model_info['name'],
                "provider": model_info['provider'],
                "cost": model_info['cost'],
                "icon": model_info['icon']
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

# Component 4: Natural Language Model Switching API Endpoints

@app.get("/communication/current-model")
async def get_current_model():
    """Get current model information (Component 4)"""
    if not COMMUNICATION_CONTROL_AVAILABLE:
        return JSONResponse({
            "available": False,
            "message": "Component 4: Communication Control not available"
        })
    
    model_info = communication_controller.get_current_model_info()
    return JSONResponse({
        "available": True,
        "current_model": communication_controller.current_model.value,
        "model_info": model_info,
        "status_display": communication_controller.get_status_display()
    })

@app.post("/communication/switch-model")
async def switch_model_api(request: ModelSwitchRequest):
    """API endpoint for programmatic model switching (Component 4)"""
    if not COMMUNICATION_CONTROL_AVAILABLE:
        raise HTTPException(status_code=404, detail="Component 4: Communication Control not available")
    
    # Validate target model
    valid_models = ["claude", "local", "auto"]
    if request.target_model not in valid_models:
        raise HTTPException(status_code=400, detail=f"Invalid model. Valid options: {valid_models}")
    
    # Convert string to ModelType
    model_type = ModelType(request.target_model)
    
    # Execute switch
    confirmation_msg = communication_controller.switch_model(model_type, request.permanent)
    
    return JSONResponse({
        "success": True,
        "message": confirmation_msg,
        "previous_model": communication_controller.previous_model.value,
        "current_model": communication_controller.current_model.value,
        "permanent": request.permanent,
        "model_info": communication_controller.get_current_model_info()
    })

@app.post("/communication/parse-request")
async def parse_model_request(chat_message: ChatMessage):
    """Parse natural language for model switching intent (Component 4)"""
    if not COMMUNICATION_CONTROL_AVAILABLE:
        raise HTTPException(status_code=404, detail="Component 4: Communication Control not available")
    
    model_type, message, permanent = communication_controller.parse_model_request(chat_message.message)
    
    return JSONResponse({
        "model_switch_detected": model_type is not None,
        "target_model": model_type.value if model_type else None,
        "confirmation_message": message,
        "permanent_switch": permanent,
        "is_model_switch_query": communication_controller.is_model_switch_query(chat_message.message)
    })

@app.get("/communication/status")
async def communication_status():
    """Get Component 4 communication control status"""
    if not COMMUNICATION_CONTROL_AVAILABLE:
        return JSONResponse({
            "component_4_available": False,
            "communication_control": False,
            "natural_language_switching": False
        })
    
    return JSONResponse({
        "component_4_available": True,
        "communication_control": True,
        "natural_language_switching": True,
        "current_model": communication_controller.current_model.value,
        "previous_model": communication_controller.previous_model.value,
        "supported_models": ["claude", "local", "auto"],
        "pattern_categories": list(communication_controller.switch_patterns.keys()),
        "model_info": communication_controller.get_current_model_info()
    })

@app.get("/enhanced-status")
async def enhanced_status():
    """Get Enhanced Conversation Manager status (LLM Teaming + Auto-Escalation + Component 4)"""
    base_status = {
        "enhanced_features_available": ENHANCED_CONVERSATION_AVAILABLE,
        "component_4_available": COMMUNICATION_CONTROL_AVAILABLE
    }
    
    if not ENHANCED_CONVERSATION_AVAILABLE:
        base_status["message"] = "Enhanced features not available - using basic conversation"
        return JSONResponse(base_status)
    
    # Get comprehensive status from enhanced manager
    session_stats = enhanced_conversation_manager.get_session_stats()
    
    status_response = {
        **base_status,
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
    }
    
    # Add Component 4 status
    if COMMUNICATION_CONTROL_AVAILABLE:
        status_response["communication_control"] = {
            "current_model": communication_controller.current_model.value,
            "model_info": communication_controller.get_current_model_info(),
            "natural_language_patterns": len(sum(communication_controller.switch_patterns.values(), []))
        }
    
    # Add LLM engine info if available
    if session_stats.get('enhanced_mode') and hasattr(enhanced_conversation_manager, 'llm_engine'):
        llm_engine = enhanced_conversation_manager.llm_engine
        status_response["llm_teaming"] = {
            "active_sessions": session_stats.get('active_llm_sessions', 0),
            "total_llm_cost": session_stats.get('total_llm_cost', 0.0),
            "api_connections": {
                "together_ai": bool(getattr(llm_engine, 'together_api_key', False)),
                "claude_direct": bool(getattr(llm_engine, 'claude_api_key', False)),
                "hawkmoth_local": True
            }
        }
    
    # Add escalation engine info if available
    if session_stats.get('escalation_engine_stats'):
        status_response["auto_escalation"] = session_stats['escalation_engine_stats']
    
    return JSONResponse(status_response)

@app.get("/session/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get detailed session summary"""
    if not ENHANCED_CONVERSATION_AVAILABLE:
        raise HTTPException(status_code=404, detail="Enhanced features not available")
    
    # Get session statistics from enhanced manager
    session_stats = enhanced_conversation_manager.get_session_stats()
    
    # Try to get specific session info if LLM engine is available
    if hasattr(enhanced_conversation_manager, 'llm_engine') and enhanced_conversation_manager.enhanced_mode:
        try:
            llm_summary = enhanced_conversation_manager.llm_engine.get_session_summary(session_id)
            if "error" not in llm_summary:
                return JSONResponse(llm_summary)
        except:
            pass
    
    # Return general session statistics
    return JSONResponse({
        "session_id": session_id,
        "enhanced_features": True,
        "statistics": session_stats
    })

@app.post("/session/{session_id}/switch-model")
async def request_model_switch(session_id: str, target_model: str):
    """Request manual model switch for session"""
    if not ENHANCED_CONVERSATION_AVAILABLE:
        raise HTTPException(status_code=404, detail="Enhanced features not available")
    
    # Check if LLM engine is available for model switching
    if not (hasattr(enhanced_conversation_manager, 'llm_engine') and enhanced_conversation_manager.enhanced_mode):
        raise HTTPException(status_code=404, detail="LLM Teaming not available for model switching")
    
    llm_engine = enhanced_conversation_manager.llm_engine
    session = llm_engine.active_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if target_model not in llm_engine.model_catalog:
        raise HTTPException(status_code=400, detail="Invalid target model")
    
    # Update session model
    old_model = session.primary_model
    session.primary_model = target_model
    session.model_config = llm_engine.model_catalog[target_model]
    
    return JSONResponse({
        "success": True,
        "message": f"Session {session_id} switched from {old_model} to {target_model}",
        "old_model": old_model,
        "new_model": target_model,
        "model_lane": llm_engine._get_model_lane(target_model)
    })

@app.get("/health")
async def health_check():
    """Enhanced health check with Enhanced Conversation Manager + Component 4 status"""
    base_health = {
        "status": "healthy", 
        "service": "HAWKMOTH v0.1.0-dev", 
        "git_available": True,
        "platform_ready": True,
        "component_4": COMMUNICATION_CONTROL_AVAILABLE
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
        
        # Add LLM engine status if available
        if session_stats.get('enhanced_mode') and hasattr(enhanced_conversation_manager, 'llm_engine'):
            llm_engine = enhanced_conversation_manager.llm_engine
            base_health.update({
                "together_ai": bool(getattr(llm_engine, 'together_api_key', False)),
                "claude_direct": bool(getattr(llm_engine, 'claude_api_key', False)),
                "active_sessions": session_stats.get('active_llm_sessions', 0)
            })
    else:
        base_health.update({
            "enhanced_features": False,
            "fallback_mode": True
        })
    
    # Add Component 4 status
    if COMMUNICATION_CONTROL_AVAILABLE:
        base_health["communication_control"] = {
            "current_model": communication_controller.current_model.value,
            "natural_language_switching": True
        }
    
    return base_health

@app.get("/version")
async def version():
    """Enhanced version info with Enhanced Features + Component 4 details"""
    features = ["Basic Chat"]
    if ENHANCED_CONVERSATION_AVAILABLE:
        features = ["LLM Teaming", "Auto-Escalation", "Sticky Sessions", "Cost Optimization", "Real-time Data Detection"]
    
    if COMMUNICATION_CONTROL_AVAILABLE:
        features.append("Natural Language Model Switching")
    
    version_info = {
        "version": "0.1.0-dev", 
        "platform": "HAWKMOTH",
        "features": features,
        "git_available": True,
        "deployment_system": "HuggingFace Spaces",
        "components": {
            "component_1": "Persistent Storage ✅",
            "component_2": "File Upload Handling ✅", 
            "component_3": "Claude File Integration ✅",
            "component_4": "Communication Control ✅" if COMMUNICATION_CONTROL_AVAILABLE else "Communication Control ⚠️"
        }
    }
    
    if ENHANCED_CONVERSATION_AVAILABLE:
        session_stats = enhanced_conversation_manager.get_session_stats()
        version_info.update({
            "enhanced_features": {
                "engine_version": "LLM Teaming + Auto-Escalation v1.0",
                "capabilities": ["Real-time Data", "Model Failure Recovery", "Intelligent Routing", "Cost Optimization"],
                "escalation_patterns": session_stats.get('escalation_engine_stats', {}).get('real_time_patterns', 0),
                "escalation_chains": session_stats.get('escalation_engine_stats', {}).get('escalation_chains', 0),
                "cost_optimization": "60-80% savings vs direct vendors"
            }
        })
        
        # Add LLM teaming info if available
        if session_stats.get('enhanced_mode') and hasattr(enhanced_conversation_manager, 'llm_engine'):
            llm_engine = enhanced_conversation_manager.llm_engine
            version_info["enhanced_features"]["model_providers"] = ["Together AI", "Claude Direct", "HAWKMOTH Local"]
            version_info["enhanced_features"]["model_count"] = len(getattr(llm_engine, 'model_catalog', {}))
    
    return version_info

if __name__ == "__main__":
    # Ensure Git config is set before starting server
    initialize_git_config()
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
