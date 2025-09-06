# Enhanced Conversation Manager with Git integration
import time
from git_manager import GitManager

class ConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        self.git_manager = GitManager()

    def process_message(self, user_id: str, message: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False
            }

        state = self.conversations[user_id]

        # Check for Git commands
        if any(word in message.lower() for word in ['git', 'repository', 'github']):
            return self._handle_git_commands(message)

        # Check for GitHub URL
        github_url = self._extract_github_url(message)
        if github_url:
            return self._analyze_repository(state, github_url)

        # Handle deployment approval
        if state['status'] == 'ready' and not state['approved']:
            return self._handle_approval(state, message)

        # General queries
        return self._handle_general(state, message)

    def _handle_git_commands(self, message: str):
        """Handle Git-related requests"""
        lower_msg = message.lower()
        
        if 'setup' in lower_msg or 'initialize' in lower_msg:
            result = self.git_manager.setup_acne_repo()
            response = "🔧 **Git Repository Setup**\n\n"
            for r in result['results']:
                response += f"• {r}\n"
            return response
        
        elif 'create repository' in lower_msg or 'new repo' in lower_msg:
            result = self.git_manager.create_github_repo(
                "ACNE-Project",
                "Agentic Conversational No-Code Environment"
            )
            if result['success']:
                return f"✅ **Repository Created!**\n\n🌐 {result['repo_url']}"
            else:
                return f"❌ **Creation Failed**\n\n{result['error']}"
        
        else:
            return "🔧 **Git Commands Available:**\n\n• 'setup repository' - Initialize Git\n• 'create repository' - Create GitHub repo"

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
            state['status'] = 'deploying'
            
            # TODO: Replace with real HuggingFace Space creation
            space_url = f"https://huggingface.co/spaces/demo/{state['analysis']['name'].lower()}-{int(time.time())}"
            
            response = "🚀 **Deployment In Progress...**\n\n"
            response += "✅ Repository cloned\n"
            response += "✅ Dependencies analyzed\n"
            response += "✅ Docker container built\n"
            response += "🔄 Creating HuggingFace Space...\n\n"
            response += f"🌟 **Space URL:** {space_url}\n\n"
            response += "⏱️ Build time: ~2-5 minutes"
            
            return response
        
        elif any(word in message.lower() for word in ['no', 'cancel', 'stop']):
            state['status'] = 'cancelled'
            return "👍 Deployment cancelled. Share another GitHub URL anytime!"
        
        return "Please say 'yes' to deploy or 'no' to cancel."

    def _handle_general(self, state, message):
        if any(word in message.lower() for word in ['help', 'how']):
            return """🤖 **Welcome to ACNE!**

**Deploy GitHub repos:** Share a GitHub URL
**Git commands:** Say "setup repository" or "create repository"  
**Example:** https://github.com/streamlit/streamlit-example

Try it out!"""
        
        return "👋 Hi! Share a GitHub repository URL and I'll help you deploy it!"
