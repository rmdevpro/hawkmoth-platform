# ACNE - Main FastAPI Application
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from analyzer import GitHubAnalyzer
from conversation import ConversationManager

# Initialize FastAPI app
app = FastAPI(title="ACNE - Agentic Conversational No-Code Environment")

# Load tokens
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Initialize components
analyzer = GitHubAnalyzer(GITHUB_TOKEN)
conversation_manager = ConversationManager(analyzer)

# Pydantic models
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
            "status": conversation_manager.conversations.get(chat_message.user_id, {}).get('status', 'waiting')
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "response": f"Error: {str(e)}",
            "status": "error"
        })

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ACNE"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
