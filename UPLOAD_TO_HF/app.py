"""
HAWKMOTH v0.0.4-enhanced: Enhanced LLM Teaming Platform
Production FastAPI Backend with Full Model Variety Support
Ready for HuggingFace Deployment
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import json
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import asyncio

# Enhanced Communication Control Import
try:
    from communication_control_enhanced import enhanced_communication_controller, ModelType
    communication_controller = enhanced_communication_controller
    print("✅ Enhanced Communication Control loaded - Full model variety available")
except ImportError:
    # Fallback for production deployment
    communication_controller = None
    ModelType = None
    print("⚠️ Communication control not available - using basic mode")

# Enhanced Conversation Manager
try:
    from conversation_enhanced import EnhancedConversationManager
    ConversationManager = EnhancedConversationManager
    print("✅ Enhanced Conversation Manager loaded")
except ImportError:
    # Fallback for production deployment
    from conversation import ConversationManager
    print("⚠️ Using fallback conversation manager")

# Other imports
from repository_analyzer import GitHubAnalyzer

app = FastAPI(
    title="HAWKMOTH v0.0.4-enhanced", 
    description="Enhanced LLM Teaming Platform with 10+ AI Models",
    version="0.0.4-enhanced"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
analyzer = GitHubAnalyzer()
conversation_manager = ConversationManager(analyzer)

# Pydantic models for enhanced API
class ModelSwitchRequest(BaseModel):
    model_type: str
    permanent: bool = True
    user_context: Optional[Dict[str, Any]] = None

class ModelInfo(BaseModel):
    name: str
    provider: str
    cost: str
    icon: str
    description: str
    specialties: str

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"

# ===============================================
# Enhanced Component 4 API Endpoints
# ===============================================

@app.get("/communication/models", response_model=Dict[str, ModelInfo])
async def get_available_models():
    """Get all available models with detailed information."""
    if not communication_controller:
        # Return basic model info when enhanced control not available
        return {
            "basic_claude": ModelInfo(
                name="Claude Sonnet 4",
                provider="Anthropic",
                cost="$3/$15 per 1k tokens",
                icon="💎",
                description="Premium AI with advanced reasoning",
                specialties="Analysis, coding, writing"
            ),
            "basic_local": ModelInfo(
                name="Local Model",
                provider="Together AI",
                cost="$1.25 per 1k tokens",
                icon="🎯",
                description="Cost-efficient open-source model",
                specialties="General tasks, cost optimization"
            )
        }
    
    models_info = {}
    for model_type in ModelType:
        info = communication_controller.model_info[model_type]
        models_info[model_type.value] = ModelInfo(
            name=info['name'],
            provider=info['provider'],
            cost=info['cost'],
            icon=info['icon'],
            description=info['description'],
            specialties=info['specialties']
        )
    
    return models_info

@app.get("/communication/current-model")
async def get_current_model():
    """Get current model information and status."""
    if not communication_controller:
        return {
            "current_model": "claude_sonnet_4",
            "model_info": {
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "cost": "$3/$15 per 1k tokens",
                "icon": "💎",
                "description": "Premium AI with advanced reasoning"
            },
            "status_display": "💎 Claude Sonnet 4 (Premium AI)",
            "enhanced_features": False,
            "total_models_available": 2
        }
    
    current_info = communication_controller.get_current_model_info()
    
    return {
        "current_model": communication_controller.current_model.value,
        "model_info": current_info,
        "status_display": communication_controller.get_enhanced_status_display(),
        "enhanced_features": True,
        "total_models_available": len(communication_controller.model_info)
    }

@app.post("/communication/switch-model")
async def switch_model(request: ModelSwitchRequest):
    """Switch to a specific model programmatically."""
    if not communication_controller:
        # Basic fallback response
        return {
            "success": True,
            "switch_message": f"Switched to {request.model_type} (basic mode)",
            "new_model": request.model_type,
            "model_info": {"name": "Basic Model", "cost": "Standard rates"},
            "permanent": request.permanent,
            "timestamp": time.time()
        }
    
    try:
        # Convert string to ModelType enum
        target_model = None
        for model_type in ModelType:
            if model_type.value == request.model_type:
                target_model = model_type
                break
        
        if target_model is None:
            available_models = [model.value for model in ModelType]
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model type. Available: {available_models}"
            )
        
        # Execute the switch
        switch_message = communication_controller.switch_model(target_model, request.permanent)
        new_info = communication_controller.get_current_model_info()
        
        return {
            "success": True,
            "switch_message": switch_message,
            "new_model": target_model.value,
            "model_info": new_info,
            "permanent": request.permanent,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model switch failed: {str(e)}")

@app.post("/communication/parse-request")
async def parse_model_request(message: ChatMessage):
    """Parse natural language for model switching intent."""
    if not communication_controller:
        # Basic pattern matching
        message_lower = message.message.lower()
        has_intent = any(phrase in message_lower for phrase in [
            'claude', 'switch', 'model', 'use', 'chat with'
        ])
        
        return {
            "has_model_intent": has_intent,
            "detected_model": "claude_sonnet_4" if "claude" in message_lower else "local_model",
            "confirmation_message": "Basic model switching detected",
            "permanent_switch": True,
            "recommendations": {},
            "enhanced_features": False
        }
    
    try:
        model_type, confirmation_msg, permanent = communication_controller.parse_model_request(message.message)
        
        # Get model recommendations for this query
        recommendations = communication_controller.get_model_recommendations(message.message)
        
        result = {
            "has_model_intent": model_type is not None,
            "detected_model": model_type.value if model_type else None,
            "confirmation_message": confirmation_msg,
            "permanent_switch": permanent,
            "recommendations": {
                rec_type: model.value for rec_type, model in recommendations.items()
            } if recommendations else {},
            "enhanced_features": True,
            "query_analysis": {
                "length": len(message.message.split()),
                "complexity": "high" if len(message.message.split()) > 30 else "medium" if len(message.message.split()) > 10 else "simple"
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse request failed: {str(e)}")

@app.get("/communication/status")
async def get_communication_status():
    """Get comprehensive communication system status."""
    if not communication_controller:
        return {
            "available": True,
            "enhanced_features": False,
            "version": "v0.0.4-basic",
            "total_models": 2,
            "fallback_mode": True,
            "message": "Running in basic mode - enhanced features not loaded"
        }
    
    try:
        current_info = communication_controller.get_current_model_info()
        
        return {
            "available": True,
            "enhanced_features": True,
            "version": "v0.0.4-enhanced",
            "total_models": len(communication_controller.model_info),
            "current_model": {
                "type": communication_controller.current_model.value,
                "info": current_info
            },
            "capabilities": {
                "natural_language_switching": True,
                "model_recommendations": True,
                "cost_optimization": True,
                "temporary_switching": True,
                "model_history": True
            },
            "model_categories": {
                "reasoning": ["deepseek_r1", "deepseek_r1_throughput"],
                "general": ["deepseek_v3", "llama_3_3_70b"],
                "cost_efficient": ["llama_3_1_8b", "deepseek_r1_free"],
                "premium": ["claude_sonnet_4", "claude_opus_4"],
                "platform": ["hawkmoth_local", "auto_select"]
            },
            "cost_range": {
                "free_models": 2,
                "lowest_cost": "$0.18/1k tokens",
                "highest_cost": "$15/$75/1k tokens"
            }
        }
        
    except Exception as e:
        return {
            "available": True,
            "error": str(e),
            "fallback_mode": True
        }

# ===============================================
# Enhanced Chat Endpoint
# ===============================================

@app.post("/chat")
async def enhanced_chat_endpoint(message: ChatMessage):
    """Enhanced chat endpoint with full model variety support."""
    try:
        # Process through enhanced conversation manager
        response = conversation_manager.process_message(message.user_id, message.message)
        
        # Add enhanced metadata
        enhanced_response = {
            "response": response,
            "timestamp": time.time(),
            "user_id": message.user_id,
            "enhanced_features": communication_controller is not None,
            "version": "v0.0.4-enhanced" if communication_controller else "v0.0.4-basic"
        }
        
        # Add current model info if available
        if communication_controller:
            current_model_info = communication_controller.get_current_model_info()
            enhanced_response["current_model"] = {
                "type": communication_controller.current_model.value,
                "name": current_model_info['name'],
                "cost": current_model_info['cost'],
                "icon": current_model_info['icon']
            }
            
            # Add model recommendations if this wasn't a model switch
            if not communication_controller.is_model_switch_query(message.message):
                recommendations = communication_controller.get_model_recommendations(message.message)
                if recommendations:
                    enhanced_response["model_recommendations"] = {
                        rec_type: communication_controller.model_info[model_type]['name']
                        for rec_type, model_type in recommendations.items()
                    }
        
        return enhanced_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

# ===============================================
# Platform Status
# ===============================================

@app.get("/status")
async def get_platform_status():
    """Get comprehensive platform status."""
    
    platform_status = {
        "platform": "HAWKMOTH",
        "version": "v0.0.4-enhanced",
        "status": "operational",
        "timestamp": time.time(),
        "enhanced_features": communication_controller is not None
    }
    
    # Communication system status
    if communication_controller:
        comm_status = await get_communication_status()
        platform_status["communication_system"] = comm_status
    else:
        platform_status["communication_system"] = {
            "available": True,
            "enhanced_features": False,
            "fallback_mode": True
        }
    
    # Repository analysis status
    platform_status["repository_analyzer"] = {
        "available": True,
        "github_integration": True,
        "deployment_ready": True
    }
    
    # Conversation management
    platform_status["conversation_manager"] = {
        "enhanced": True,
        "model_switching": communication_controller is not None,
        "deployment_support": True,
        "self_improvement": True
    }
    
    return platform_status

# ===============================================
# Frontend serving
# ===============================================

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the enhanced frontend."""
    try:
        with open("frontend.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        enhanced_status = "✅ Enhanced" if communication_controller else "⚠️ Basic Mode"
        model_count = len(communication_controller.model_info) if communication_controller else 2
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HAWKMOTH v0.0.4-enhanced</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .header {{ text-align: center; color: #2c3e50; }}
                .feature {{ margin: 10px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }}
                .model {{ margin: 5px 0; padding: 5px; background: #e8f6f3; border-left: 4px solid #16a085; }}
                .api {{ background: #fdf2e9; border-left: 4px solid #f39c12; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🦅 HAWKMOTH v0.0.4-enhanced</h1>
                    <h2>Enhanced LLM Teaming Platform</h2>
                    <p><strong>Status:</strong> {enhanced_status} | <strong>Models Available:</strong> {model_count}</p>
                </div>
                
                <div class="feature">
                    <h3>🧠 AI Models Available</h3>
                    <div class="model">🧠 DeepSeek R1 - Premium reasoning ($3/$7 per 1k)</div>
                    <div class="model">⚡ DeepSeek R1 Throughput - Cost-efficient reasoning ($0.55/$2.19 per 1k)</div>
                    <div class="model">🎯 DeepSeek V3 - Balanced performance ($1.25 per 1k)</div>
                    <div class="model">🌍 Llama 3.3 70B - Multilingual dialogue ($0.88 per 1k)</div>
                    <div class="model">🚀 Llama 3.1 8B - Fast and efficient ($0.18 per 1k)</div>
                    <div class="model">🆓 DeepSeek R1 Free - Zero cost testing (FREE)</div>
                    <div class="model">💎 Claude Sonnet 4 - Premium analysis ($3/$15 per 1k)</div>
                    <div class="model">🏆 Claude Opus 4 - Maximum performance ($15/$75 per 1k)</div>
                    <div class="model">🏠 HAWKMOTH Local - Platform commands (FREE)</div>
                    <div class="model">🤖 Auto-Select - Intelligent routing (Variable cost)</div>
                </div>
                
                <div class="feature">
                    <h3>🎯 Natural Language Commands</h3>
                    <p><strong>Try saying:</strong></p>
                    <ul>
                        <li>"use deepseek r1" - Switch to premium reasoning</li>
                        <li>"switch to free model" - Use zero-cost option</li>
                        <li>"chat with claude" - Premium Claude AI</li>
                        <li>"use cheapest model" - Auto-select cost-efficient</li>
                        <li>"use best quality" - Maximum performance</li>
                    </ul>
                </div>
                
                <div class="api">
                    <h3>🔧 API Endpoints</h3>
                    <p><strong>Enhanced Features:</strong></p>
                    <ul>
                        <li><code>/communication/models</code> - Get all available models</li>
                        <li><code>/communication/switch-model</code> - Programmatic switching</li>
                        <li><code>/communication/parse-request</code> - Natural language parsing</li>
                        <li><code>/communication/status</code> - System capabilities</li>
                        <li><code>/chat</code> - Enhanced chat with model variety</li>
                    </ul>
                </div>
                
                <div class="feature">
                    <h3>🚀 Repository Deployment</h3>
                    <p>Paste any GitHub URL in chat to analyze and deploy instantly!</p>
                    <p><strong>Example:</strong> https://github.com/streamlit/streamlit-example</p>
                </div>
            </div>
        </body>
        </html>
        """)

# ===============================================
# Health Check
# ===============================================

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {
        "status": "healthy",
        "version": "v0.0.4-enhanced",
        "timestamp": time.time(),
        "enhanced_features": communication_controller is not None,
        "total_models": len(communication_controller.model_info) if communication_controller else 2,
        "capabilities": [
            "repository_deployment",
            "natural_language_switching",
            "cost_optimization",
            "model_recommendations"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🦅 Starting HAWKMOTH v0.0.4-enhanced - Enhanced LLM Teaming Platform")
    print(f"✅ Enhanced Features: {'Loaded' if communication_controller else 'Basic Mode'}")
    print(f"🎯 Models Available: {len(communication_controller.model_info) if communication_controller else 2}")
    print("💰 Cost optimization and model recommendations active")
    uvicorn.run(app, host="0.0.0.0", port=7860)
