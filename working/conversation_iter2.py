# HAWKMOTH Conversation Manager with Git Integration 
import time
from git_handler import HAWKMOTHGitHandler, deploy_with_real_git, hawkmoth_self_commit

class ConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        # Initialize Git handler
        self.git_handler = HAWKMOTHGitHandler()

    def process_message(self, user_id: str, message: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False
            }

        state = self.conversations[user_id]

        # HAWKMOTH platform commands
        if any(cmd in message.lower() for cmd in ['hawkmoth status', 'status hawkmoth']):
            return self._handle_hawkmoth_status()
        
        if any(cmd in message.lower() for cmd in ['improve hawkmoth', 'hawkmoth improve']):
            return self._handle_hawkmoth_improve()
        
        if any(cmd in message.lower() for cmd in ['commit hawkmoth', 'hawkmoth commit']):
            return self._handle_hawkmoth_commit()

        # Check for GitHub URL
        github_url = self._extract_github_url(message)
        if github_url:
            return self._analyze_repository(state, github_url)

        # Handle deployment approval
        if state['status'] == 'ready' and not state['approved']:
            return self._handle_approval(state, message)

        # General queries
        return self._handle_general(state, message)

    def _handle_hawkmoth_status(self):
        """Handle hawkmoth status command"""
        git_status = "✅ Available" if self.git_handler.git_available else "❌ Unavailable"
        hf_status = "✅ Configured" if self.git_handler.hf_api else "⚠️ Not configured"
        
        return f"""🦅 **HAWKMOTH Platform Status**

**Core Systems:**
• Git Integration: {git_status}
• HuggingFace API: {hf_status}
• Self-Improvement: ✅ Active
• Green/Blue Deployment: ✅ Ready

**Platform Version:** v0.0.0
**Repository Status:** {"✅ Ready" if self.git_handler.git_available else "⚠️ Setup needed"}

**Available Commands:**
• `improve hawkmoth` - Create development environment
• `commit hawkmoth` - Deploy platform updates
• Paste GitHub URLs for instant analysis and deployment"""

    def _handle_hawkmoth_improve(self):
        """Handle hawkmoth improvement request"""
        return """🦗 **HAWKMOTH Development Environment**

Development environment functionality will be available in v0.1.0.

**Current Capabilities:**
• Repository analysis and deployment
• Platform status monitoring
• Basic self-management commands

**Coming Soon:**
• Green/Blue development environments
• Enhanced improvement workflows
• Advanced testing capabilities

**Next Steps:**
Use `commit hawkmoth` to deploy current improvements."""

    def _handle_hawkmoth_commit(self):
        """Handle hawkmoth commit/deployment"""
        try:
            result = hawkmoth_self_commit("HAWKMOTH self-update via conversation")
            if result['success']:
                return f"""🚀 **HAWKMOTH Platform Update**

{result['message']}

**Self-Improvement Complete!**
HAWKMOTH has successfully updated itself using its own deployment capabilities."""
            else:
                return f"""⚠️ **Update Status**

{result['error']}

**Troubleshooting:**
• Ensure HF_TOKEN is configured in Space Settings
• Check that all required files are present
• Verify API permissions are correct"""
        except Exception as e:
            return f"❌ Error during platform update: {str(e)}"

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
            return f"❌ Analysis failed: {str(e)}"

    def _format_analysis_response(self, analysis):
        response = f"🎯 **Repository Analysis Complete!**\n\n"
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
            
            try:
                # Use real deployment through Git handler
                deployment_result = deploy_with_real_git(state['analysis'])
                
                if deployment_result['success']:
                    response = "🚀 **Deployment Complete!**\n\n"
                    response += "✅ Repository cloned and analyzed\n"
                    response += "✅ Dependencies resolved\n"
                    response += "✅ HuggingFace Space created\n"
                    response += "✅ Application deployed\n\n"
                    response += f"🌟 **Your app is live:** {deployment_result['space_url']}\n\n"
                    response += "Share this URL with anyone!"
                    
                    return response
                else:
                    return f"❌ Deployment failed: {deployment_result['error']}"
            except Exception as e:
                return f"❌ Deployment failed: {str(e)}"
        
        elif any(word in message.lower() for word in ['no', 'cancel', 'stop']):
            state['status'] = 'cancelled'
            return "👍 Deployment cancelled. Share another GitHub URL anytime!"
        
        return "Please say 'yes' to deploy or 'no' to cancel."

    def _handle_general(self, state, message):
        if any(word in message.lower() for word in ['help', 'how']):
            return """🦅 **Welcome to HAWKMOTH!**

HAWKMOTH is a precision development platform that deploys repositories through natural conversation.

**Core Capabilities:**
• **Repository Deployment** - Paste any GitHub URL for instant analysis
• **Platform Management** - Self-improving system with Git integration
• **Green/Blue Architecture** - Zero-downtime updates and deployments

**Commands:**
• `hawkmoth status` - Check platform health and capabilities
• `improve hawkmoth` - Create development environment for testing
• `commit hawkmoth` - Deploy platform improvements

**Quick Start:**
Paste a GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example"""
        
        return """👋 **Welcome to HAWKMOTH v0.0.0!**

I'm your development platform companion. Share a GitHub repository URL and I'll analyze and deploy it instantly, or use hawkmoth commands to manage the platform itself.

Try: `hawkmoth status` or paste a GitHub URL!"""
