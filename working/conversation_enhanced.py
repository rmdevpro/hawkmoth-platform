# HAWKMOTH Enhanced Conversation Manager with Full Model Variety Support
import time
from git_handler import HAWKMOTHGitHandler, deploy_with_real_git, hawkmoth_self_commit
from self_improvement import SelfImprovementManager

# Import Enhanced Component 4: Communication Control with Full Model Variety
try:
    from working.communication_control_enhanced import enhanced_communication_controller, ModelType
except ImportError:
    # Fallback to basic communication control
    try:
        from working.communication_control_iter1 import communication_controller as basic_controller, ModelType
        enhanced_communication_controller = basic_controller
        print("⚠️ Using basic communication control - enhanced version not available")
    except ImportError:
        print("⚠️ Communication control not available - using basic mode")
        enhanced_communication_controller = None
        ModelType = None

class EnhancedConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        # Initialize Git and self-improvement capabilities
        self.git_handler = HAWKMOTHGitHandler()
        self.self_improvement = SelfImprovementManager(self.git_handler)
        # Initialize enhanced communication control (Component 4)
        self.comm_controller = enhanced_communication_controller

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
            return "⚠️ Enhanced model switching not available."
        
        models_summary = self.comm_controller.get_all_models_summary()
        current_status = self._get_enhanced_model_status()
        
        return f"{models_summary}\n{current_status}\n\n**To switch models, just say:** \"use [model name]\" or \"switch to [model type]\""

    def _get_enhanced_model_status(self):
        """Get enhanced current model status display."""
        if not self.comm_controller:
            return "🎯 **Current Model:** Basic (enhanced switching not available)"
        
        info = self.comm_controller.get_current_model_info()
        return f"""📊 **Current Model Status:**
{info['icon']} **{info['name']}** ({info['provider']})
💰 **Cost:** {info['cost']}  
⭐ **Best for:** {info['specialties']}
📝 **{info['description']}**"""

    def _get_detailed_model_status(self):
        """Get detailed model status including history."""
        if not self.comm_controller:
            return "⚠️ Enhanced model tracking not available."
        
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
        git_status = "✅ Available" if self.git_handler.git_available else "❌ Unavailable"
        hf_status = "✅ Configured" if self.git_handler.hf_api else "⚠️ Not configured"
        
        # Enhanced communication status
        if self.comm_controller:
            model_count = len(self.comm_controller.model_info)
            comm_status = f"✅ Enhanced Active ({model_count} models)"
        else:
            comm_status = "⚠️ Not available"
        
        return f"""🦅 **HAWKMOTH Platform Status v0.0.4-enhanced**

**Core Systems:**
• Git Integration: {git_status}
• HuggingFace API: {hf_status}
• Enhanced Communication Control: {comm_status}
• Self-Improvement: ✅ Active
• Green/Blue Deployment: ✅ Ready

**Platform Version:** v0.0.4-enhanced (Full Model Variety)
**Repository Status:** {"✅ Ready" if self.git_handler.git_available else "⚠️ Setup needed"}

{self._get_enhanced_model_status()}

**Available Commands:**
• `improve hawkmoth` - Create development environment
• `commit hawkmoth` - Deploy platform updates
• `show models` - View all available AI models
• Natural model switching - "use [model]", "switch to [type]"
• Cost optimization - "use cheapest" or "use free model"
• Quality priority - "use best quality" or "use claude opus"
• Paste GitHub URLs for instant analysis and deployment"""

    def _handle_hawkmoth_improve(self):
        """Handle hawkmoth improvement request"""
        try:
            result = self.self_improvement.create_green_environment()
            return f"""🦗 **HAWKMOTH Development Environment v0.0.4-enhanced**

{result}

**Enhanced Development Ready!**
The green environment contains the latest HAWKMOTH platform code with full model variety support:

**New Features Available:**
• 10+ AI model options with natural language switching
• Cost optimization and model recommendations
• Enhanced conversation management
• Full model variety support

**Next Steps:**
• Test enhanced model switching capabilities
• Validate cost optimization features
• Use `commit hawkmoth` to promote changes to production"""
        except Exception as e:
            return f"❌ Error creating development environment: {str(e)}"

    def _handle_hawkmoth_commit(self):
        """Handle hawkmoth commit/deployment"""
        try:
            result = hawkmoth_self_commit("HAWKMOTH v0.0.4-enhanced: Full model variety support")
            if result['success']:
                return f"""🚀 **HAWKMOTH Platform Update v0.0.4-enhanced**

{result['message']}

**Enhanced Self-Improvement Complete!**
HAWKMOTH has successfully updated itself with full model variety support:

✅ **10+ AI models** now available through natural language
✅ **Cost optimization** with automatic model recommendations  
✅ **Enhanced conversation** management with model history
✅ **Production deployment** ready for testing

**Try the new features:** "show models" or "use best quality model"!"""
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

    def _handle_general_with_recommendations(self, state, message):
        """Handle general queries with enhanced model recommendations."""
        if any(word in message.lower() for word in ['help', 'how']):
            return f"""🦅 **Welcome to HAWKMOTH v0.0.4-enhanced!**

HAWKMOTH is a precision development platform with **10+ AI models** available through natural conversation.

**🧠 Enhanced Model Capabilities:**
• **10+ AI Models** - From free to premium with automatic cost optimization
• **Natural Language Switching** - "use claude for this" or "switch to free model"
• **Smart Recommendations** - Get the best model for each task automatically
• **Cost Transparency** - See exact costs and alternatives for every interaction

**🎯 Model Commands:**
• `show models` - See all available AI models and costs
• `use [model name]` - Switch to specific model (DeepSeek, Claude, Llama)
• `use cheapest model` - Auto-select most cost-efficient option
• `use best quality` - Get maximum performance regardless of cost
• `let hawkmoth decide` - Intelligent automatic model selection

**🛠️ Platform Commands:**
• `hawkmoth status` - Check platform health and model availability
• `improve hawkmoth` - Create development environment for testing
• `commit hawkmoth` - Deploy platform improvements

**🚀 Repository Deployment:**
Paste any GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example

{self._get_enhanced_model_status()}"""
        
        # Get model recommendations for this query
        recommendations = self._get_model_recommendations_for_query(message)
        
        welcome_msg = f"""👋 **Welcome to HAWKMOTH v0.0.4-enhanced!**

I'm your development platform with **10+ AI models** available through natural conversation!

**Quick Start:**
• `show models` - See all available AI models
• `hawkmoth status` - Check platform capabilities
• Paste a GitHub URL for instant deployment
• Try: "use free model" or "use claude for analysis"

{self._get_enhanced_model_status()}"""

        if recommendations:
            welcome_msg += f"\n\n📋 **Recommended models for your query:**\n{recommendations}"
        
        welcome_msg += "\n\n**Natural Model Switching:** Just say what you want! 🎯"
        
        return welcome_msg

# Backward compatibility alias
ConversationManager = EnhancedConversationManager
