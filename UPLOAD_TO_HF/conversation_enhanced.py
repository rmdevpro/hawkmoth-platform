# HAWKMOTH Enhanced Conversation Manager - Production Ready
# Full Model Variety Support for HuggingFace Deployment
import time

# Import Enhanced Component 4: Communication Control with Full Model Variety
try:
    from communication_control_enhanced import enhanced_communication_controller, ModelType
    print("✅ Enhanced Communication Control loaded - Full model variety available")
except ImportError:
    # Graceful fallback for production deployment
    enhanced_communication_controller = None
    ModelType = None
    print("⚠️ Enhanced communication control not available - using basic mode")

# Import other required modules with fallbacks
try:
    from git_handler import HAWKMOTHGitHandler, deploy_with_real_git, hawkmoth_self_commit
    from self_improvement import SelfImprovementManager
    git_available = True
except ImportError:
    # Fallback classes for when git modules aren't available
    class MockGitHandler:
        def __init__(self):
            self.git_available = False
            self.hf_api = False
    
    class MockSelfImprovement:
        def __init__(self, git_handler):
            pass
        def create_green_environment(self):
            return "Git modules not available in this deployment"
    
    HAWKMOTHGitHandler = MockGitHandler
    SelfImprovementManager = MockSelfImprovement
    def deploy_with_real_git(analysis):
        return {"success": False, "error": "Git deployment not available"}
    def hawkmoth_self_commit(message):
        return {"success": False, "error": "Git commit not available"}
    git_available = False

class EnhancedConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        # Initialize Git and self-improvement capabilities with fallbacks
        self.git_handler = HAWKMOTHGitHandler()
        self.self_improvement = SelfImprovementManager(self.git_handler)
        # Initialize enhanced communication control (Component 4)
        self.comm_controller = enhanced_communication_controller
        self.git_available = git_available

    def process_message(self, user_id: str, message: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False,
                'current_model': 'deepseek_v3',  # Default to balanced model
                'temp_switch': False,
                'model_history': []
            }

        state = self.conversations[user_id]
        
        # Enhanced Component 4: Check for model switching requests with full variety
        if self.comm_controller:
            model_switch = self._handle_enhanced_model_switching(message, state)
            if model_switch:
                return model_switch

        # Check for model information requests
        if any(cmd in message.lower() for cmd in ['show models', 'list models', 'available models']):
            return self._show_available_models()
        
        if any(cmd in message.lower() for cmd in ['model status', 'current model']):
            return self._get_detailed_model_status()

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

        # General queries with model recommendations
        return self._handle_general_with_recommendations(state, message)

    def _handle_enhanced_model_switching(self, message: str, state: dict):
        """Handle Enhanced Component 4: Natural language model switching with full variety."""
        if not self.comm_controller:
            return None
            
        model_type, confirmation_msg, permanent = self.comm_controller.parse_model_request(message)
        
        if model_type:
            # Store previous model in history
            if state['current_model'] and state['current_model'] != model_type.value:
                state['model_history'].append({
                    'model': state['current_model'],
                    'switched_at': time.time()
                })
            
            # Update conversation state
            if not permanent:
                state['temp_switch'] = True
            
            # Execute the switch
            switch_msg = self.comm_controller.switch_model(model_type, permanent)
            state['current_model'] = model_type.value if model_type else state['current_model']
            
            # Add enhanced status and recommendations
            enhanced_status = self._get_enhanced_model_status()
            recommendations = self._get_model_recommendations_for_query(message)
            
            response = f"{switch_msg}\n\n{enhanced_status}"
            
            if recommendations:
                response += f"\n\n📋 **Other good options for this query:**\n{recommendations}"
            
            response += "\n\n**How can I help you with this model?**"
            
            return response
        
        return None

    def _show_available_models(self):
        """Show all available models with full details."""
        if not self.comm_controller:
            return """🦅 **HAWKMOTH Available Models (Basic Mode):**

💎 **Claude Sonnet 4** - Premium AI with advanced reasoning ($3/$15 per 1k)
🎯 **Local Model** - Cost-efficient open-source option ($1.25 per 1k)

**Enhanced model variety not available in this deployment.**
**To switch models, say:** "chat with claude" or "switch to local"
"""
        
        models_summary = self.comm_controller.get_all_models_summary()
        current_status = self._get_enhanced_model_status()
        
        return f"{models_summary}\n{current_status}\n\n**To switch models, just say:** \"use [model name]\" or \"switch to [model type]\""

    def _get_enhanced_model_status(self):
        """Get enhanced current model status display."""
        if not self.comm_controller:
            return "🎯 **Current Model:** Basic Mode (enhanced switching not available)"
        
        info = self.comm_controller.get_current_model_info()
        return f"""📊 **Current Model Status:**
{info['icon']} **{info['name']}** ({info['provider']})
💰 **Cost:** {info['cost']}  
⭐ **Best for:** {info['specialties']}
📝 **{info['description']}**"""

    def _get_detailed_model_status(self):
        """Get detailed model status including history."""
        if not self.comm_controller:
            return """⚠️ **Enhanced Model Tracking Not Available**

Currently running in basic mode with limited model switching capabilities.

**Available Commands:**
• "chat with claude" - Switch to Claude Sonnet 4
• "switch to local" - Use cost-efficient local model
"""
        
        current_status = self._get_enhanced_model_status()
        
        # Add usage statistics if available
        total_switches = len([conv for conv in self.conversations.values() if conv.get('model_history')])
        
        return f"""{current_status}

📈 **Session Statistics:**
• Total model switches this session: {total_switches}
• Enhanced model variety: ✅ 10+ models available
• Cost optimization: ✅ Active
• Natural language switching: ✅ Active

**Switch anytime by saying:** "use [model name]" or "switch to [type]"
**See all models:** "show models" """

    def _get_model_recommendations_for_query(self, message: str):
        """Get model recommendations for the current query."""
        if not self.comm_controller:
            return ""
        
        recommendations = self.comm_controller.get_model_recommendations(message)
        if not recommendations:
            return ""
        
        rec_text = ""
        for rec_type, model_type in recommendations.items():
            info = self.comm_controller.model_info[model_type]
            rec_text += f"• **{rec_type.replace('_', ' ').title()}:** {info['icon']} {info['name']} ({info['cost']})\n"
        
        return rec_text

    def _handle_hawkmoth_status(self):
        """Handle hawkmoth status command with enhanced model info."""
        git_status = "✅ Available" if self.git_available else "❌ Not available in this deployment"
        hf_status = "✅ HuggingFace Space" if not self.git_available else "✅ Configured"
        
        # Enhanced communication status
        if self.comm_controller:
            model_count = len(self.comm_controller.model_info)
            comm_status = f"✅ Enhanced Active ({model_count} models)"
        else:
            comm_status = "⚠️ Basic Mode (2 models)"
        
        return f"""🦅 **HAWKMOTH Platform Status v0.0.4-enhanced**

**Core Systems:**
• Git Integration: {git_status}
• HuggingFace Deployment: {hf_status}
• Enhanced Communication Control: {comm_status}
• Repository Analysis: ✅ Active
• Natural Language Switching: {'✅ Active' if self.comm_controller else '⚠️ Basic'}

**Platform Version:** v0.0.4-enhanced (Full Model Variety)
**Deployment Type:** {"HuggingFace Space" if not self.git_available else "Development Environment"}

{self._get_enhanced_model_status()}

**Available Commands:**
• `show models` - View all available AI models
• Natural model switching - "use [model]", "switch to [type]"
• Cost optimization - "use cheapest" or "use free model"
• Quality priority - "use best quality" or "use claude opus"
• Repository deployment - Paste GitHub URLs for instant analysis"""

    def _handle_hawkmoth_improve(self):
        """Handle hawkmoth improvement request"""
        if not self.git_available:
            return """🦗 **HAWKMOTH Development Environment**

⚠️ Git-based improvement not available in HuggingFace Space deployment.

**Current Enhanced Features Active:**
• 10+ AI model options with natural language switching
• Cost optimization and model recommendations
• Enhanced conversation management
• Repository analysis and deployment

**To contribute improvements:**
1. Visit the GitHub repository
2. Fork and create improvements
3. Submit pull requests for new features"""
        
        try:
            result = self.self_improvement.create_green_environment()
            return f"""🦗 **HAWKMOTH Development Environment v0.0.4-enhanced**

{result}

**Enhanced Development Ready!**"""
        except Exception as e:
            return f"❌ Error creating development environment: {str(e)}"

    def _handle_hawkmoth_commit(self):
        """Handle hawkmoth commit/deployment"""
        if not self.git_available:
            return """🚀 **HAWKMOTH Platform Status**

⚠️ Self-deployment not available in HuggingFace Space.

**Current Deployment Status:**
✅ HAWKMOTH v0.0.4-enhanced running successfully
✅ Enhanced model variety active (10+ models)
✅ Natural language switching operational
✅ Cost optimization features active
✅ Repository deployment ready

**Platform is fully operational with enhanced features!**"""
        
        try:
            result = hawkmoth_self_commit("HAWKMOTH v0.0.4-enhanced: Full model variety support")
            if result['success']:
                return f"""🚀 **HAWKMOTH Platform Update v0.0.4-enhanced**

{result['message']}

**Enhanced Self-Improvement Complete!**"""
            else:
                return f"⚠️ **Update Status:** {result['error']}"
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
                # Use deployment through git handler if available
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

    def _handle_general_with_recommendations(self, state, message):
        """Handle general queries with enhanced model recommendations."""
        if any(word in message.lower() for word in ['help', 'how']):
            enhanced_status = "✅ Enhanced" if self.comm_controller else "⚠️ Basic Mode"
            model_count = len(self.comm_controller.model_info) if self.comm_controller else 2
            
            return f"""🦅 **Welcome to HAWKMOTH v0.0.4-enhanced!**

HAWKMOTH is a precision development platform with **{model_count} AI models** available through natural conversation.

**🧠 Model Capabilities ({enhanced_status}):**
{"• **10+ AI Models** - From free to premium with automatic cost optimization" if self.comm_controller else "• **2 AI Models** - Claude and local options available"}
{"• **Natural Language Switching** - \"use claude for this\" or \"switch to free model\"" if self.comm_controller else "• **Basic Switching** - \"chat with claude\" or \"switch to local\""}
{"• **Smart Recommendations** - Get the best model for each task automatically" if self.comm_controller else "• **Manual Selection** - Choose between available models"}
{"• **Cost Transparency** - See exact costs and alternatives for every interaction" if self.comm_controller else "• **Cost Awareness** - Basic cost information available"}

**🎯 Model Commands:**
{"• `show models` - See all available AI models and costs" if self.comm_controller else "• `show models` - See available models"}
{"• `use [model name]` - Switch to specific model (DeepSeek, Claude, Llama)" if self.comm_controller else "• `chat with claude` - Switch to Claude"}
{"• `use cheapest model` - Auto-select most cost-efficient option" if self.comm_controller else "• `switch to local` - Use local model"}
{"• `use best quality` - Get maximum performance regardless of cost" if self.comm_controller else ""}
{"• `let hawkmoth decide` - Intelligent automatic model selection" if self.comm_controller else ""}

**🚀 Repository Deployment:**
Paste any GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example

{self._get_enhanced_model_status()}"""
        
        # Get model recommendations for this query
        recommendations = self._get_model_recommendations_for_query(message) if self.comm_controller else ""
        
        welcome_msg = f"""👋 **Welcome to HAWKMOTH v0.0.4-enhanced!**

I'm your development platform with **{"10+ AI models" if self.comm_controller else "multiple AI models"}** available through natural conversation!

**Quick Start:**
• `show models` - See all available AI models
• `hawkmoth status` - Check platform capabilities
• Paste a GitHub URL for instant deployment
• Try: {"\"use free model\" or \"use claude for analysis\"" if self.comm_controller else "\"chat with claude\" or \"switch to local\""}

{self._get_enhanced_model_status()}"""

        if recommendations:
            welcome_msg += f"\n\n📋 **Recommended models for your query:**\n{recommendations}"
        
        welcome_msg += f"\n\n**Natural Model Switching:** Just say what you want! 🎯"
        
        return welcome_msg

# Backward compatibility alias
ConversationManager = EnhancedConversationManager
