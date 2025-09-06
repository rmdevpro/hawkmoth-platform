# ACNE v1.1.0 - Enhanced with real Git and HF deployment
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from analyzer import GitHubAnalyzer
from conversation_v2 import ConversationManager
from hf_deployer import HuggingFaceDeployer

# Initialize FastAPI app
app = FastAPI(title="ACNE v1.1.0 - Deploy GitHub Repos Through Conversation")

# Load environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
HF_TOKEN = os.getenv('HF_TOKEN', '')

# Initialize components
analyzer = GitHubAnalyzer(GITHUB_TOKEN)
conversation_manager = ConversationManager(analyzer)
hf_deployer = HuggingFaceDeployer(HF_TOKEN)

# Request models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"

# Routes
@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open("frontend.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    try:
        response = conversation_manager.process_message(
            chat_message.user_id, 
            chat_message.message
        )
        
        return JSONResponse({
            "success": True,
            "response": response,
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
    return {"status": "healthy", "service": "ACNE v1.1.0"}

@app.get("/version")
async def version_info():
    """Return current version information"""
    import json
    try:
        with open("version.json", "r") as f:
            version_data = json.load(f)
        return JSONResponse(version_data)
    except:
        return JSONResponse({"version": "1.1.0-dev", "status": "development"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
