# HAWKMOTH v0.1.0-dev - Development Platform with LLM Teaming
import os
import subprocess
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from analyzer import GitHubAnalyzer
from enhanced_conversation import EnhancedConversationManager

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

app = FastAPI(title="HAWKMOTH v0.1.0-dev - LLM Teaming Platform")

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
analyzer = GitHubAnalyzer(GITHUB_TOKEN)
conversation_manager = EnhancedConversationManager(analyzer)

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"

class ConfigUpdate(BaseModel):
    service: str
    api_key: str

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    try:
        result = conversation_manager.process_message(
            chat_message.user_id, 
            chat_message.message
        )
        
        return JSONResponse({
            "success": True, 
            "response": result["response"], 
            "routing_info": result.get("routing_info", {}),
            "status": "ok"
        })
    except Exception as e:
        return JSONResponse({
            "success": False, 
            "response": f"Error: {str(e)}", 
            "status": "error"
        })

@app.get("/health")
async def health_check():
    git_available = conversation_manager.git_handler.git_available
    routing_stats = conversation_manager.routing_stats
    
    return {
        "status": "healthy", 
        "service": "HAWKMOTH v0.1.0-dev", 
        "git_available": git_available, 
        "llm_routing": True,
        "total_queries_routed": routing_stats["total_queries"],
        "platform_ready": True
    }

@app.get("/version")
async def version():
    routing_stats = conversation_manager.routing_stats
    
    return {
        "version": "0.1.0-dev", 
        "platform": "HAWKMOTH",
        "features": ["llm_teaming", "intelligent_routing", "cost_optimization"],
        "git_available": conversation_manager.git_handler.git_available, 
        "hf_api_available": conversation_manager.git_handler.hf_api is not None, 
        "routing_system": "active",
        "queries_routed": routing_stats["total_queries"],
        "deployment_system": "Green/Blue"
    }

@app.get("/routing/status")
async def routing_status():
    """Get detailed routing system status"""
    router_info = conversation_manager.router.get_routing_stats()
    routing_stats = conversation_manager.routing_stats
    
    return {
        "routing_enabled": True,
        "total_queries": routing_stats["total_queries"],
        "total_cost": routing_stats["total_cost"],
        "routes_by_target": routing_stats["routes_by_target"],
        "api_status": {
            "together_ai": router_info["together_api_configured"],
            "claude": bool(conversation_manager.claude_api_key),
            "openai": bool(conversation_manager.openai_api_key)
        },
        "available_targets": router_info["targets"]
    }

@app.post("/config/api-key")
async def update_api_key(config: ConfigUpdate):
    """Update API key configuration"""
    try:
        if config.service == "together_ai":
            conversation_manager.router.together_api_key = config.api_key
        elif config.service == "claude":
            conversation_manager.claude_api_key = config.api_key
        elif config.service == "openai":
            conversation_manager.openai_api_key = config.api_key
        else:
            return JSONResponse({
                "success": False, 
                "error": f"Unknown service: {config.service}"
            })
        
        return JSONResponse({
            "success": True, 
            "message": f"API key updated for {config.service}"
        })
    except Exception as e:
        return JSONResponse({
            "success": False, 
            "error": str(e)
        })

@app.get("/routing/test")
async def test_routing():
    """Test routing system with sample queries"""
    test_queries = [
        "hawkmoth status",
        "debug this Python function",
        "design a logo for my startup",
        "what is machine learning?",
        "help me deploy this React app",
        "routing status"
    ]
    
    results = conversation_manager.router.test_routing(test_queries)
    
    return {
        "test_results": {
            query: {
                "target_llm": decision.target_llm,
                "confidence": decision.confidence,
                "reason": decision.reason,
                "estimated_cost": decision.estimated_cost,
                "complexity": decision.complexity
            }
            for query, decision in results.items()
        }
    }

if __name__ == "__main__":
    # Ensure Git config is set before starting server
    initialize_git_config()
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
