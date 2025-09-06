# ACNE - Enhanced with real Git and HF deployment
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from analyzer import GitHubAnalyzer
from conversation_v2 import ConversationManager
from hf_deployer import HuggingFaceDeployer

# Initialize FastAPI app
app = FastAPI(title="ACNE - Deploy GitHub Repos Through Conversation")

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
        # Check if this is a deployment request
        if (conversation_manager.conversations.get(chat_message.user_id, {}).get('status') == 'ready' 
            and any(word in chat_message.message.lower() for word in ['yes', 'deploy', 'go'])):
            
            # Real deployment
            analysis = conversation_manager.conversations[chat_message.user_id]['analysis']
            deploy_result = hf_deployer.deploy_repo_to_hf(analysis)
            
            if deploy_result['success']:
                response = f"""🚀 **Real Deployment Complete!**

✅ Repository analyzed
✅ HuggingFace Space created  
✅ Docker container configured
✅ Application deployed

🌟 **Live URL:** {deploy_result['space_url']}

Share this URL with anyone!"""
            else:
                response = f"❌ **Deployment Failed**\n\n{deploy_result['error']}"
        else:
            # Regular conversation
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
    return {"status": "healthy", "service": "ACNE v1.1 - Real Deployment"}

# Self-management endpoints
@app.post("/admin/git-setup")
async def setup_git():
    """Let ACNE set up its own Git repository"""
    try:
        from git_manager import GitManager
        git_mgr = GitManager(GITHUB_TOKEN)
        result = git_mgr.setup_acne_repo()
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
