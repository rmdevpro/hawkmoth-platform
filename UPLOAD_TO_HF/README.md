# HAWKMOTH v0.0.4-enhanced - Enhanced LLM Teaming Platform

🦅 **HAWKMOTH** is a precision development platform that orchestrates multiple AI models for optimal cost and performance through natural conversation.

## 🚀 v0.0.4-enhanced Features

### 🧠 **10+ AI Models Available**
- **🧠 DeepSeek R1** - State-of-the-art reasoning ($3/$7 per 1k tokens)
- **⚡ DeepSeek R1 Throughput** - Cost-efficient reasoning ($0.55/$2.19 per 1k tokens)
- **🎯 DeepSeek V3** - Balanced performance ($1.25 per 1k tokens)
- **🌍 Llama 3.3 70B** - Multilingual dialogue ($0.88 per 1k tokens)
- **🚀 Llama 3.1 8B** - Fast and efficient ($0.18 per 1k tokens)
- **🆓 DeepSeek R1 Free** - Zero cost testing (FREE)
- **💎 Claude Sonnet 4** - Premium analysis ($3/$15 per 1k tokens)
- **🏆 Claude Opus 4** - Maximum performance ($15/$75 per 1k tokens)
- **🏠 HAWKMOTH Local** - Platform commands (FREE)
- **🤖 Auto-Select** - Intelligent routing (Variable cost)

### 🎯 **Natural Language Model Switching**
Switch between models seamlessly through conversation:
- `"use deepseek r1"` → Premium reasoning model
- `"switch to free model"` → Zero-cost option
- `"chat with claude"` → Premium Claude AI
- `"use cheapest model"` → Auto-select most cost-efficient
- `"use best quality"` → Route to highest performance
- `"let hawkmoth decide"` → Intelligent automatic selection

### 💰 **Cost Optimization**
- **FREE models available** (DeepSeek R1 Free, HAWKMOTH Local)
- **Cost range**: $0.00 to $75/1k tokens
- **Smart recommendations** based on query complexity
- **Transparent cost display** for all models
- **Automatic cost-efficient routing** when requested

### 🔧 **Enhanced API Endpoints**
- `/communication/models` - Get all available models with details
- `/communication/switch-model` - Programmatic model switching
- `/communication/parse-request` - Parse natural language requests
- `/communication/recommendations` - Get model suggestions for queries
- `/communication/status` - System capabilities and model info
- `/chat` - Enhanced chat with full model variety support

### 🚀 **Repository Deployment**
Paste any GitHub repository URL to:
- **Analyze** tech stack and complexity automatically
- **Deploy** to HuggingFace Spaces instantly
- **Get cost estimates** and deployment recommendations
- **Share live URLs** immediately after deployment

## 📋 Quick Start

### **Try These Commands:**
```
show models                    # See all available AI models
hawkmoth status               # Check platform capabilities
use free model for testing    # Switch to zero-cost option
chat with claude about AI     # Use premium Claude model
use best quality model        # Maximum performance mode
```

### **Deploy a Repository:**
```
https://github.com/streamlit/streamlit-example
```
Just paste any GitHub URL and HAWKMOTH will analyze and deploy it automatically!

## 🛠️ **Technical Specifications**

### **Runtime Requirements**
- Python 3.9+
- FastAPI + Uvicorn
- Port 7860 (HuggingFace standard)

### **Dependencies**
```python
fastapi>=0.68.0
uvicorn>=0.15.0
requests>=2.25.0
pydantic>=1.8.0
```

### **Model Integration**
- **Together AI API** - For DeepSeek and Llama models
- **Anthropic API** - For Claude models (when available)
- **Fallback Support** - Graceful degradation when APIs unavailable

## 🎯 **Model Selection Intelligence**

### **Automatic Recommendations**
HAWKMOTH analyzes your query and suggests optimal models:

**For Complex Reasoning:**
- Best: DeepSeek R1 ($3/$7)
- Cost-Efficient: DeepSeek R1 Throughput ($0.55/$2.19)

**For Coding Tasks:**
- Best: DeepSeek V3 ($1.25)
- Premium: Claude Sonnet 4 ($3/$15)

**For Multilingual:**
- Best: Llama 3.3 70B ($0.88)

**For Simple Tasks:**
- Cost-Efficient: Llama 3.1 8B ($0.18)
- Free: DeepSeek R1 Free ($0.00)

## 📊 **Enhanced Features**

### **Pattern Recognition**
Advanced natural language understanding for model switching:
- Detects intent from context and keywords
- Supports temporary vs permanent switching
- Handles cost-priority vs quality-priority requests
- Provides rich confirmation messages with model details

### **Cost Transparency**
- Real-time cost display for current model
- Cost comparisons between model options
- Free model alternatives always suggested
- Estimated costs for different query types

### **Session Management**
- Persistent model preferences per user
- Model switching history tracking
- Temporary model switches with auto-restore
- Enhanced conversation state management

## 🔄 **Deployment Architecture**

### **Production Ready**
- **Fallback Support** - Works even when enhanced features unavailable
- **Error Handling** - Graceful degradation for missing dependencies
- **API Resilience** - Continues operating if external APIs fail
- **HuggingFace Optimized** - Built specifically for Spaces deployment

### **Development Features**
- **Component-Based Architecture** - Modular design for easy enhancement
- **Comprehensive Testing** - Full test suite for model switching
- **Version Control** - Proper git integration and release management
- **Self-Improvement** - Platform can update itself through conversation

## 🎉 **What's New in v0.0.4-enhanced**

✅ **10+ AI Model Support** - Expanded from 3 to 10+ models
✅ **Enhanced Natural Language** - Advanced pattern recognition
✅ **Cost Optimization** - Smart model recommendations and free options
✅ **Rich Model Information** - Detailed specs, costs, and specialties
✅ **Production Deployment** - HuggingFace-ready with fallback support
✅ **API Enhancement** - New endpoints for programmatic control
✅ **Improved UX** - Better model switching and status display

## 🚀 **Ready for Testing**

HAWKMOTH v0.0.4-enhanced is production-ready for HuggingFace Spaces deployment with:
- ✅ Full model variety support (10+ models)
- ✅ Enhanced natural language switching
- ✅ Cost optimization and recommendations
- ✅ Fallback support for production reliability
- ✅ Comprehensive API endpoints
- ✅ Repository deployment capabilities

**Deploy and test the enhanced HAWKMOTH experience!** 🦅
