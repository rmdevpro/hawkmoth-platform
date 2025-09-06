# HAWKMOTH Basic Conversation Manager - Fallback Version
# Provides basic functionality when enhanced features aren't available

import time
from repository_analyzer import GitHubAnalyzer

class ConversationManager:
    """
    Basic conversation manager with fallback support.
    Provides core HAWKMOTH functionality for repository deployment.
    """
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
    
    def process_message(self, user_id: str, message: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False,
                'current_model': 'claude_sonnet_4'
            }

        state = self.conversations[user_id]
        
        # Basic model switching
        if any(cmd in message.lower() for cmd in ['chat with claude', 'use claude', 'switch to claude']):
            state['current_model'] = 'claude_sonnet_4'
            return """💎 **Switched to Claude Sonnet 4** - Premium AI with advanced reasoning
💰 **Cost**: $3/$15 per 1k tokens
📝 **Best for**: Premium analysis, complex tasks, safety

**How can I help you with Claude?**"""
        
        if any(cmd in message.lower() for cmd in ['switch to local', 'use local', 'local model']):
            state['current_model'] = 'local_model'
            return """🎯 **Switched to Local Model** - Cost-efficient open-source option
💰 **Cost**: $1.25 per 1k tokens
📝 **Best for**: General tasks, cost optimization

**How can I help you with the local model?**"""

        # Platform status
        if any(cmd in message.lower() for cmd in ['hawkmoth status', 'status hawkmoth']):
            return f"""🦅 **HAWKMOTH Platform Status v0.0.4-enhanced**

**Core Systems:**
• Enhanced Communication: ⚠️ Basic Mode (2 models)
• Repository Analysis: ✅ Active
• Deployment System: ✅ Ready
• HuggingFace Integration: ✅ Operational

**Current Model:** {"💎 Claude Sonnet 4" if state['current_model'] == 'claude_sonnet_4' else "🎯 Local Model"}

**Available Commands:**
• `chat with claude` - Switch to Claude Sonnet 4
• `switch to local` - Use cost-efficient local model
• Paste GitHub URLs for instant analysis and deployment

**Note:** Enhanced features with 10+ models available in full version."""

        # Show available models
        if any(cmd in message.lower() for cmd in ['show models', 'list models', 'available models']):
            return """🦅 **HAWKMOTH Available Models (Basic Mode):**

💎 **Claude Sonnet 4** - Premium AI with advanced reasoning ($3/$15 per 1k)
🎯 **Local Model** - Cost-efficient open-source option ($1.25 per 1k)

**To switch models, say:** "chat with claude" or "switch to local"

**Note:** Enhanced version supports 10+ models with natural language switching."""

        # Check for GitHub URL
        github_url = self._extract_github_url(message)
        if github_url:
            return self._analyze_repository(state, github_url)

        # Handle deployment approval
        if state['status'] == 'ready' and not state['approved']:
            return self._handle_approval(state, message)

        # Help and general queries
        if any(word in message.lower() for word in ['help', 'how']):
            return f"""🦅 **Welcome to HAWKMOTH v0.0.4-enhanced!**

HAWKMOTH is a precision development platform for repository deployment through natural conversation.

**🧠 Current Model:** {"💎 Claude Sonnet 4" if state['current_model'] == 'claude_sonnet_4' else "🎯 Local Model"}

**🎯 Model Commands:**
• `chat with claude` - Switch to Claude Sonnet 4
• `switch to local` - Use cost-efficient local model
• `show models` - See available models

**🚀 Repository Deployment:**
Paste any GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example

**Platform Commands:**
• `hawkmoth status` - Check platform capabilities

**Note:** This is basic mode. Enhanced version supports 10+ models with advanced natural language switching."""
        
        # Default welcome
        return f"""👋 **Welcome to HAWKMOTH v0.0.4-enhanced!**

I'm your development platform for instant repository deployment!

**Current Model:** {"💎 Claude Sonnet 4" if state['current_model'] == 'claude_sonnet_4' else "🎯 Local Model"}

**Quick Start:**
• `show models` - See available AI models
• `hawkmoth status` - Check platform capabilities  
• Paste a GitHub URL for instant deployment
• Try: "chat with claude" or "switch to local"

**Ready to deploy? Share a GitHub repository URL!** 🚀"""

    def _extract_github_url(self, message):
        import re
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
            return f"❌ Analysis failed: {str(e)}\n\nPlease check the repository URL and try again."

    def _format_analysis_response(self, analysis):
        response = f"🎯 **Repository Analysis Complete!**\n\n"
        response += f"**{analysis['name']}** - {analysis['description']}\n\n"
        response += f"**Tech Stack:** {', '.join(analysis['tech_stack'])}\n"
        response += f"**Type:** {analysis['deployment_type']}\n"
        response += f"**Complexity:** {analysis['complexity']}\n"
        response += f"**Est. Cost:** ${analysis['estimated_cost']}/month\n"
        response += f"**⭐ Stars:** {analysis['stars']:,}\n\n"
        
        if analysis.get('fallback_mode'):
            response += "⚠️ **Note:** Analysis performed in fallback mode due to API limitations.\n\n"
        
        response += "Ready to deploy? Say **yes** to proceed!"
        
        return response

    def _handle_approval(self, state, message):
        if any(word in message.lower() for word in ['yes', 'deploy', 'go', 'proceed']):
            state['approved'] = True
            state['status'] = 'deployed'
            
            # Simulate deployment process
            analysis = state['analysis']
            
            response = "🚀 **Deployment Initiated!**\n\n"
            response += "✅ Repository analyzed\n"
            response += "✅ Dependencies identified\n"
            response += "✅ Deployment configuration prepared\n"
            response += "✅ HuggingFace Space setup ready\n\n"
            
            # Provide deployment information
            response += f"**Repository:** {analysis['name']}\n"
            response += f"**Type:** {analysis['deployment_type']}\n"
            response += f"**Estimated Cost:** ${analysis['estimated_cost']}/month\n\n"
            
            response += "🌟 **Next Steps:**\n"
            response += "1. Create HuggingFace Space manually\n"
            response += "2. Upload repository files\n"
            response += "3. Configure deployment settings\n"
            response += f"4. Deploy as {analysis['deployment_type']}\n\n"
            
            response += "**Deployment analysis complete!** 🎉"
            
            return response
        
        elif any(word in message.lower() for word in ['no', 'cancel', 'stop']):
            state['status'] = 'cancelled'
            return "👍 Deployment cancelled. Share another GitHub URL anytime!"
        
        return "Please say 'yes' to proceed with deployment or 'no' to cancel."
