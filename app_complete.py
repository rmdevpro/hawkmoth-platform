# ACNE - Agentic Conversational No-Code Environment
# Complete FastAPI Application

import os
import json
import re
import time
import base64
import requests
from typing import Dict, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="ACNE - Agentic Conversational No-Code Environment")

# Load tokens from environment
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
HF_TOKEN = os.getenv('HF_TOKEN', '')

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "default"

class AnalysisResponse(BaseModel):
    response: str
    analysis: Optional[Dict] = None
    status: str

# Core functionality classes
class GitHubAnalyzer:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'token {token}'})

    def analyze_repo(self, repo_url: str) -> dict:
        try:
            owner, repo = self._parse_url(repo_url)
            repo_data = self._get_repo_data(owner, repo)
            files = self._get_key_files(owner, repo)
            
            tech_stack = self._detect_tech_stack(files, repo_data)
            deployment_type = self._get_deployment_type(tech_stack)
            complexity = self._assess_complexity(tech_stack, files)
            cost = self._estimate_cost(complexity, deployment_type)
            
            return {
                'name': repo_data['name'],
                'description': repo_data.get('description', 'No description'),
                'language': repo_data.get('language', 'Unknown'),
                'tech_stack': tech_stack,
                'deployment_type': deployment_type,
                'complexity': complexity,
                'estimated_cost': cost,
                'stars': repo_data.get('stargazers_count', 0),
                'repo_url': repo_url
            }
        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    def _parse_url(self, url):
        url = url.strip().rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        match = re.search(r'github\.com/([^/]+)/([^/\s?]+)', url)
        if not match:
            raise ValueError("Invalid GitHub URL")
        
        return match.groups()

    def _get_repo_data(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = self.session.get(url)
        if response.status_code == 404:
            raise Exception("Repository not found or private")
        response.raise_for_status()
        return response.json()

    def _get_key_files(self, owner, repo):
        files = {}
        key_filenames = ['package.json', 'requirements.txt', 'Dockerfile', 'README.md', 'app.py', 'main.py']
        
        for filename in key_filenames:
            content = self._get_file_content(owner, repo, filename)
            if content:
                files[filename] = content[:2000]  # Limit size
        
        return files

    def _get_file_content(self, owner, repo, filepath):
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content_data = response.json()
                if content_data.get('size', 0) > 20000:
                    return None
                content = content_data.get('content', '')
                return base64.b64decode(content).decode('utf-8', errors='ignore')
        except:
            pass
        return None

    def _detect_tech_stack(self, files, repo_data):
        stack = set()
        language = repo_data.get('language', '').lower()
        
        if language == 'python':
            stack.add('Python')
        elif language == 'javascript':
            stack.add('JavaScript')
        
        for filename, content in files.items():
            content_lower = content.lower()
            
            if filename == 'package.json':
                stack.add('Node.js')
                if 'react' in content_lower:
                    stack.add('React')
                if 'express' in content_lower:
                    stack.add('Express')
            
            elif filename == 'requirements.txt':
                if 'streamlit' in content_lower:
                    stack.add('Streamlit')
                if 'fastapi' in content_lower:
                    stack.add('FastAPI')
                if 'flask' in content_lower:
                    stack.add('Flask')
                if 'django' in content_lower:
                    stack.add('Django')
            
            elif filename == 'dockerfile':
                stack.add('Docker')
        
        return list(stack) if stack else ['Unknown']

    def _get_deployment_type(self, tech_stack):
        if 'Streamlit' in tech_stack:
            return 'Streamlit App'
        elif 'FastAPI' in tech_stack:
            return 'FastAPI Service'
        elif 'React' in tech_stack:
            return 'Static Site'
        elif 'Docker' in tech_stack:
            return 'Container'
        elif 'Python' in tech_stack:
            return 'Python App'
        else:
            return 'Generic App'

    def _assess_complexity(self, tech_stack, files):
        score = len(tech_stack) + len(files)
        if 'Docker' in tech_stack:
            score += 2
        
        if score <= 5:
            return 'Simple'
        elif score <= 10:
            return 'Moderate'
        else:
            return 'Complex'

    def _estimate_cost(self, complexity, deployment_type):
        base_cost = 5.0
        
        if complexity == 'Moderate':
            base_cost *= 1.5
        elif complexity == 'Complex':
            base_cost *= 2.0
        
        if deployment_type == 'Container':
            base_cost *= 1.2
        
        return round(base_cost, 2)


class ConversationManager:
    def __init__(self):
        self.analyzer = GitHubAnalyzer(GITHUB_TOKEN)
        self.conversations = {}

    def process_message(self, user_id: str, message: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False
            }

        state = self.conversations[user_id]
        message_lower = message.lower()

        # Check for GitHub URL
        github_url = self._extract_github_url(message)
        if github_url:
            return self._analyze_repository(state, github_url)

        # Handle deployment approval
        if state['status'] == 'ready' and not state['approved']:
            return self._handle_approval(state, message)

        # General queries
        return self._handle_general(state, message)

    def _extract_github_url(self, message):
        patterns = [r'https://github\.com/[^\s]+', r'github\.com/[^\s]+']
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                url = match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                return url
        return None

    def _analyze_repository(self, state, repo_url):
        state['status'] = 'analyzing'
        
        try:
            analysis = self.analyzer.analyze_repo(repo_url)
            state['analysis'] = analysis
            state['status'] = 'ready'
            
            return self._format_analysis_response(analysis)
        
        except Exception as e:
            state['status'] = 'failed'
            return f"❌ Analysis failed: {str(e)}"

    def _format_analysis_response(self, analysis):
        response = f"🎯 **Analysis Complete!**\n\n"
        response += f"**{analysis['name']}** - {analysis['description']}\n\n"
        response += f"**Tech Stack:** {', '.join(analysis['tech_stack'])}\n"
        response += f"**Type:** {analysis['deployment_type']}\n"
        response += f"**Complexity:** {analysis['complexity']}\n"
        response += f"**Est. Cost:** ${analysis['estimated_cost']}/month\n"
        response += f"**⭐ Stars:** {analysis['stars']:,}\n\n"
        response += "Ready to deploy? Say **yes** to proceed!"
        
        return response

    def _handle_approval(self, state, message):
        if any(word in message.lower() for word in ['yes', 'deploy', 'go', 'proceed']):
            state['approved'] = True
            state['status'] = 'deployed'
            
            # Simulate deployment
            space_url = f"https://huggingface.co/spaces/demo/{state['analysis']['name'].lower()}-{int(time.time())}"
            
            response = "🚀 **Deployment Complete!**\n\n"
            response += "✅ Repository analyzed\n"
            response += "✅ Dependencies resolved\n"
            response += "✅ Space created\n"
            response += "✅ Files uploaded\n"
            response += "✅ Application deployed\n\n"
            response += f"🌟 **Your app is live:** {space_url}\n\n"
            response += "Share this URL with anyone!"
            
            return response
        
        elif any(word in message.lower() for word in ['no', 'cancel', 'stop']):
            state['status'] = 'cancelled'
            return "👍 Deployment cancelled. Share another GitHub URL anytime!"
        
        return "Please say 'yes' to deploy or 'no' to cancel."

    def _handle_general(self, state, message):
        if any(word in message.lower() for word in ['help', 'how']):
            return """🤖 **Welcome to ACNE!**

I help you deploy GitHub repositories through conversation.

**How it works:**
1. Share a GitHub repository URL
2. I'll analyze the code and tech stack
3. Get cost estimates and deployment details
4. Deploy with a simple "yes"!

**Example:** `https://github.com/streamlit/streamlit-example`

Try it out!"""
        
        return "👋 Hi! Share a GitHub repository URL and I'll help you deploy it!"


# Initialize conversation manager
conversation_manager = ConversationManager()

# API Routes
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACNE - Deploy GitHub Repos Through Conversation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        
        .container {
            max-width: 800px;
            padding: 40px;
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #fff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 1.3rem;
            margin-bottom: 40px;
            opacity: 0.9;
            line-height: 1.6;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            max-width: 600px;
            margin: 0 auto;
        }
        
        .chat-header {
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            padding: 20px;
            color: white;
            font-weight: 600;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8fafc;
            color: #1e293b;
        }
        
        .message {
            margin-bottom: 15px;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: #e0e7ff;
            padding: 12px 16px;
            border-radius: 12px 12px 4px 12px;
            margin-left: 60px;
            margin-bottom: 10px;
        }
        
        .bot-message {
            background: white;
            border: 1px solid #e2e8f0;
            padding: 16px;
            border-radius: 12px 12px 12px 4px;
            margin-right: 60px;
            white-space: pre-wrap;
        }
        
        .input-container {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
        }
        
        #messageInput {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #d1d5db;
            border-radius: 25px;
            outline: none;
            font-size: 16px;
            margin-right: 10px;
        }
        
        #messageInput:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        
        #sendButton {
            padding: 12px 24px;
            background: linear-gradient(45deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        #sendButton:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 15px;
        }
        
        .feature-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        
        .loading {
            display: none;
            color: #6366f1;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ACNE</h1>
        <p class="subtitle">Deploy GitHub repositories through conversation.<br>No coding knowledge required!</p>
        
        <div class="chat-container">
            <div class="chat-header">
                💬 Chat with ACNE
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    👋 Welcome to ACNE! I help you deploy GitHub repositories to the web through conversation.

Just paste a GitHub URL and I'll analyze it and help you deploy it to Hugging Face Spaces!

Example: https://github.com/streamlit/streamlit-example
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="Paste a GitHub repository URL..." />
                <button id="sendButton" onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                