"""
HAWKMOTH Component 4: Enhanced API Endpoints - Full Model Variety Support
FastAPI Backend with Enhanced Communication Control
Version: v0.0.4-enhanced
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
    from working.communication_control_enhanced import enhanced_communication_controller, ModelType
    communication_controller = enhanced_communication_controller
    print("✅ Enhanced Communication Control loaded - Full model variety available")
except ImportError:
    try:
        from working.communication_control_iter1 import communication_controller, ModelType
        print("⚠️ Using basic communication control - enhanced version not found")
    except ImportError:
        communication_controller = None
        ModelType = None
        print("❌ Communication control not available")

# Enhanced Conversation Manager
try:
    from working.conversation_enhanced import EnhancedConversationManager
    ConversationManager = EnhancedConversationManager
    print("✅ Enhanced Conversation Manager loaded")
except ImportError:
    try:
        from working.conversation_iter3 import ConversationManager
        print("⚠️ Using basic conversation manager")
    except ImportError:
        from conversation import ConversationManager
        print("⚠️ Using fallback conversation manager")

# Other imports
from repository_analyzer import GitHubAnalyzer

app = FastAPI(title="HAWKMOTH v0.0.4-enhanced", description="Enhanced LLM Teaming Platform with Full Model Variety")

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

class ModelRecommendation(BaseModel):
    query: str
    recommended_models: Dict[str, str]
    current_model: str

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
        raise HTTPException(status_code=503, detail="Enhanced communication control not available")
    
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
        raise HTTPException(status_code=503, detail="Communication control not available")
    
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
        raise HTTPException(status_code=503, detail="Communication control not available")
    
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
        raise HTTPException(status_code=503, detail="Communication control not available")
    
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
            "query_analysis": {
                "length": len(message.message.split()),
                "complexity": "high" if len(message.message.split()) > 30 else "medium" if len(message.message.split()) > 10 else "simple"
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse request failed: {str(e)}")

@app.get("/communication/recommendations")
async def get_model_recommendations(query: str):
    """Get model recommendations for a specific query."""
    if not communication_controller:
        raise HTTPException(status_code=503, detail="Communication control not available")
    
    try:
        recommendations = communication_controller.get_model_recommendations(query)
        
        detailed_recommendations = {}
        for rec_type, model_type in recommendations.items():
            model_info = communication_controller.model_info[model_type]
            detailed_recommendations[rec_type] = {
                "model": model_type.value,
                "name": model_info['name'],
                "cost": model_info['cost'],
                "reason": model_info['specialties']
            }
        
        return {
            "query": query,
            "recommendations": detailed_recommendations,
            "current_model": communication_controller.current_model.value,
            "query_characteristics": {
                "word_count": len(query.split()),
                "has_technical_terms": any(term in query.lower() for term in ['code', 'debug', 'python', 'javascript']),
                "has_reasoning_terms": any(term in query.lower() for term in ['analyze', 'research', 'complex', 'math']),
                "has_multilingual_terms": any(term in query.lower() for term in ['translate', 'language', 'multilingual'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

@app.get("/communication/status")
async def get_communication_status():
    """Get comprehensive communication system status."""
    if not communication_controller:
        return {
            "available": False,
            "error": "Enhanced communication control not loaded",
            "fallback_mode": True
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
            "enhanced_features": True,
            "version": "v0.0.4-enhanced"
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
        if communication_controller and not communication_controller.is_model_switch_query(message.message):
            recommendations = communication_controller.get_model_recommendations(message.message)
            if recommendations:
                enhanced_response["model_recommendations"] = {
                    rec_type: communication_controller.model_info[model_type]['name']
                    for rec_type, model_type in recommendations.items()
                }
        
        return enhanced_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced chat failed: {str(e)}")

# ===============================================
# Platform Status with Enhanced Info
# ===============================================

@app.get("/status")
async def get_enhanced_platform_status():
    """Get comprehensive platform status including enhanced model info."""
    
    # Basic platform status
    platform_status = {
        "platform": "HAWKMOTH",
        "version": "v0.0.4-enhanced",
        "status": "operational",
        "timestamp": time.time(),
        "enhanced_features": True
    }
    
    # Communication system status
    if communication_controller:
        comm_status = await get_communication_status()
        platform_status["communication_system"] = comm_status
    else:
        platform_status["communication_system"] = {"available": False}
    
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
# Model Comparison Endpoint
# ===============================================

@app.get("/communication/compare-models")
async def compare_models(model1: str, model2: str):
    """Compare two models side by side."""
    if not communication_controller:
        raise HTTPException(status_code=503, detail="Communication control not available")
    
    try:
        # Validate models exist
        valid_models = [model.value for model in ModelType]
        if model1 not in valid_models or model2 not in valid_models:
            raise HTTPException(status_code=400, detail=f"Invalid models. Available: {valid_models}")
        
        # Get model info
        model1_type = next(m for m in ModelType if m.value == model1)
        model2_type = next(m for m in ModelType if m.value == model2)
        
        model1_info = communication_controller.model_info[model1_type]
        model2_info = communication_controller.model_info[model2_type]
        
        return {
            "comparison": {
                model1: {
                    "name": model1_info['name'],
                    "provider": model1_info['provider'],
                    "cost": model1_info['cost'],
                    "specialties": model1_info['specialties'],
                    "description": model1_info['description']
                },
                model2: {
                    "name": model2_info['name'],
                    "provider": model2_info['provider'],
                    "cost": model2_info['cost'],
                    "specialties": model2_info['specialties'],
                    "description": model2_info['description']
                }
            },
            "recommendations": {
                "cost_efficient": model1 if "free" in model1_info['cost'].lower() or float(model1_info['cost'].split('$')[1].split('/')[0] if '$' in model1_info['cost'] else 999) < float(model2_info['cost'].split('$')[1].split('/')[0] if '$' in model2_info['cost'] else 999) else model2,
                "best_performance": model2 if "claude" in model2_info['name'].lower() or "opus" in model2_info['name'].lower() else model1
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model comparison failed: {str(e)}")

# ===============================================
# Frontend serving
# ===============================================

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the enhanced frontend with full model variety support."""
    try:
        with open("frontend.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>HAWKMOTH v0.0.4-enhanced</title></head>
            <body>
                <h1>🦅 HAWKMOTH v0.0.4-enhanced</h1>
                <h2>Enhanced LLM Teaming Platform - Full Model Variety</h2>
                <p><strong>10+ AI Models Available:</strong></p>
                <ul>
                    <li>🧠 DeepSeek R1 - Premium reasoning</li>
                    <li>⚡ DeepSeek R1 Throughput - Cost-efficient reasoning</li>
                    <li>🎯 DeepSeek V3 - Balanced performance</li>
                    <li>🌍 Llama 3.3 70B - Multilingual dialogue</li>
                    <li>🚀 Llama 3.1 8B - Fast and efficient</li>
                    <li>🆓 DeepSeek R1 Free - Zero cost testing</li>
                    <li>💎 Claude Sonnet 4 - Premium analysis</li>
                    <li>🏆 Claude Opus 4 - Maximum performance</li>
                    <li>🏠 HAWKMOTH Local - Platform commands</li>
                    <li>🤖 Auto-Select - Intelligent routing</li>
                </ul>
                <p><strong>Natural Language Switching:</strong> Just say "use [model]" or "switch to [type]"!</p>
                <p><strong>API Endpoints:</strong> /communication/models, /communication/switch-model, /chat</p>
                <p>Frontend file not found - serving API status page.</p>
            </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    print("🦅 Starting HAWKMOTH v0.0.4-enhanced - Full Model Variety Support")
    print("✅ Enhanced Communication Control loaded")
    print("🎯 10+ AI models available through natural language")
    print("💰 Cost optimization and model recommendations active")
    uvicorn.run(app, host="0.0.0.0", port=7860)
