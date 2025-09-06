# HAWKMOTH Enhanced Conversation Manager with Auto-Escalation
import time
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import the existing components
from git_handler import HAWKMOTHGitHandler, deploy_with_real_git, hawkmoth_self_commit

try:
    from hawkmoth_sticky_sessions import HAWKMOTHStickySessionEngine, LLMResponse
    from auto_escalation_engine import HAWKMOTHAutoEscalationEngine, EscalationTrigger
    ENHANCED_FEATURES_AVAILABLE = True
    print("✅ Enhanced features loaded: Sticky Sessions + Auto-Escalation")
except ImportError as e:
    print(f"⚠️ Enhanced features not available: {e}")
    ENHANCED_FEATURES_AVAILABLE = False

class HAWKMOTHEnhancedConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        self.git_handler = HAWKMOTHGitHandler()
        
        # Initialize enhanced features if available
        if ENHANCED_FEATURES_AVAILABLE:
            self.llm_engine = HAWKMOTHStickySessionEngine()
            self.escalation_engine = HAWKMOTHAutoEscalationEngine()
            self.enhanced_mode = True
            print("🦅 Enhanced conversation manager with LLM Teaming + Auto-Escalation")
        else:
            self.enhanced_mode = False
            print("📝 Basic conversation manager (fallback mode)")
        
        # Statistics
        self.session_stats = {
            'total_queries': 0,
            'escalations_triggered': 0,
            'escalations_successful': 0,
            'total_cost': 0.0,
            'real_time_queries': 0,
            'model_failures': 0
        }
    
    def process_message(self, user_id: str, message: str, session_id: str = None) -> Dict[str, Any]:
        """Enhanced message processing with auto-escalation support"""
        
        # Update statistics
        self.session_stats['total_queries'] += 1
        
        # Use session ID or create default
        if not session_id:
            session_id = f"{user_id}_session"
        
        # Initialize conversation state if needed
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False,
                'escalation_history': []
            }
        
        state = self.conversations[user_id]
        
        # Step 1: Check for escalation needs BEFORE routing
        if self.enhanced_mode:
            escalation_decision = self.escalation_engine.detect_escalation_need(message)
            
            if escalation_decision.should_escalate:
                print(f"🔄 Escalation detected: {escalation_decision.trigger.value}")
                return self._handle_escalation(state, message, escalation_decision, session_id)
        
        # Step 2: Handle HAWKMOTH platform commands (highest priority)
        if self._is_hawkmoth_command(message):
            return self._handle_hawkmoth_commands(state, message)
        
        # Step 3: Enhanced LLM routing if available
        if self.enhanced_mode:
            return self._handle_enhanced_conversation(state, message, session_id)
        else:
            return self._handle_basic_conversation(state, message, session_id)
    
    def _is_hawkmoth_command(self, message: str) -> bool:
        """Check if message is a HAWKMOTH platform command"""
        hawkmoth_keywords = [
            'hawkmoth status', 'status hawkmoth', 'improve hawkmoth', 
            'hawkmoth improve', 'commit hawkmoth', 'hawkmoth commit',
            'routing status', 'escalation status'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in hawkmoth_keywords)
    
    def _handle_escalation(self, state, message: str, escalation_decision, session_id: str) -> Dict[str, Any]:
        """Handle escalation chain execution"""
        
        # Update statistics
        self.session_stats['escalations_triggered'] += 1
        
        if escalation_decision.trigger == EscalationTrigger.REAL_TIME_DATA:
            self.session_stats['real_time_queries'] += 1
        elif escalation_decision.trigger == EscalationTrigger.MODEL_FAILURE:
            self.session_stats['model_failures'] += 1
        
        # Check if escalation should be auto-approved
        auto_approve = self.escalation_engine.should_auto_approve_escalation(escalation_decision)
        
        if auto_approve:
            print(f"✅ Auto-approving escalation: {escalation_decision.reasoning}")
            
            # Execute escalation chain
            escalation_result = self.escalation_engine.handle_escalation_chain(message, escalation_decision)
            
            # Update statistics
            if escalation_result['success']:
                self.session_stats['escalations_successful'] += 1
                self.session_stats['total_cost'] += escalation_result['escalation_info']['total_cost']
            
            # Store escalation in history
            state['escalation_history'].append({
                'query': message,
                'trigger': escalation_decision.trigger.value,
                'result': escalation_result,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'response': escalation_result['response'],
                'escalation_used': True,
                'escalation_info': escalation_result['escalation_info'],
                'auto_approved': True,
                'session_id': session_id
            }
        else:
            # Request user approval for expensive escalation
            return {
                'success': True,
                'response': f"""🔄 **Escalation Required**
                
**Query**: {message}
**Trigger**: {escalation_decision.trigger.value}
**Reasoning**: {escalation_decision.reasoning}
**Estimated Cost**: ${escalation_decision.estimated_cost:.3f}

This query requires escalation to {escalation_decision.target_capability}. 
Say 'yes' to approve or 'no' to cancel.""",
                'escalation_pending': True,
                'escalation_decision': escalation_decision,
                'session_id': session_id
            }
    
    def _handle_enhanced_conversation(self, state, message: str, session_id: str) -> Dict[str, Any]:
        """Handle conversation using enhanced LLM engine"""
        
        try:
            # Use sticky sessions for conversation
            response, switched = self.llm_engine.continue_conversation(session_id, message)
            
            # Check if the model response indicates failure
            escalation_check = self.escalation_engine.detect_escalation_need(message, response.content)
            
            if escalation_check.should_escalate:
                print(f"🔄 Model failure detected, escalating...")
                self.session_stats['model_failures'] += 1
                
                # Execute escalation
                escalation_result = self.escalation_engine.handle_escalation_chain(message, escalation_check)
                
                if escalation_result['success']:
                    self.session_stats['escalations_successful'] += 1
                    self.session_stats['total_cost'] += escalation_result['escalation_info']['total_cost']
                    
                    return {
                        'success': True,
                        'response': escalation_result['response'],
                        'escalation_used': True,
                        'escalation_info': escalation_result['escalation_info'],
                        'original_response': response.content,
                        'session_id': session_id
                    }
            
            # No escalation needed, return original response
            session_summary = self.llm_engine.get_session_summary(session_id)
            self.session_stats['total_cost'] += response.actual_cost
            
            return {
                'success': True,
                'response': response.content,
                'escalation_used': False,
                'llm_info': {
                    'model_used': response.model_used,
                    'provider': response.provider,
                    'cost': response.actual_cost,
                    'response_time': response.response_time,
                    'model_switched': switched,
                    'session_info': {
                        'primary_model': session_summary["primary_model"],
                        'total_cost': session_summary["total_cost"],
                        'total_messages': session_summary["total_messages"]
                    }
                },
                'session_id': session_id
            }
            
        except Exception as e:
            print(f"❌ Enhanced conversation error: {e}")
            # Fallback to basic conversation
            return self._handle_basic_conversation(state, message, session_id)
    
    def _handle_basic_conversation(self, state, message: str, session_id: str) -> Dict[str, Any]:
        """Fallback basic conversation handling"""
        
        # Check for GitHub URL
        github_url = self._extract_github_url(message)
        if github_url:
            return self._analyze_repository(state, github_url, session_id)
        
        # Handle deployment approval
        if state['status'] == 'ready' and not state['approved']:
            return self._handle_approval(state, message, session_id)
        
        # General help
        if any(word in message.lower() for word in ['help', 'how']):
            return {
                'success': True,
                'response': self._get_help_response(),
                'escalation_used': False,
                'session_id': session_id
            }
        
        # Default response
        return {
            'success': True,
            'response': f"👋 Welcome to HAWKMOTH! Share a GitHub URL for analysis or use 'hawkmoth status' for platform info.",
            'escalation_used': False,
            'session_id': session_id
        }
    
    def _handle_hawkmoth_commands(self, state, message: str) -> Dict[str, Any]:
        """Handle HAWKMOTH platform commands"""
        message_lower = message.lower()
        
        if any(cmd in message_lower for cmd in ['hawkmoth status', 'status hawkmoth']):
            return {
                'success': True,
                'response': self._get_hawkmoth_status(),
                'escalation_used': False,
                'command_type': 'status'
            }
        
        if any(cmd in message_lower for cmd in ['routing status', 'escalation status']):
            return {
                'success': True,
                'response': self._get_escalation_status(),
                'escalation_used': False,
                'command_type': 'escalation_status'
            }
        
        if any(cmd in message_lower for cmd in ['improve hawkmoth', 'hawkmoth improve']):
            return {
                'success': True,
                'response': self._handle_hawkmoth_improve(),
                'escalation_used': False,
                'command_type': 'improve'
            }
        
        if any(cmd in message_lower for cmd in ['commit hawkmoth', 'hawkmoth commit']):
            return {
                'success': True,
                'response': self._handle_hawkmoth_commit(),
                'escalation_used': False,
                'command_type': 'commit'
            }
        
        return {
            'success': True,
            'response': "🦅 HAWKMOTH command not recognized. Try 'hawkmoth status'.",
            'escalation_used': False,
            'command_type': 'unknown'
        }
    
    def _get_escalation_status(self) -> str:
        """Get escalation engine status"""
        if not self.enhanced_mode:
            return "⚠️ **Auto-Escalation Not Available**\n\nEnhanced features not loaded. Using basic conversation mode."
        
        stats = self.session_stats
        escalation_stats = self.escalation_engine.get_escalation_stats()
        
        success_rate = (stats['escalations_successful'] / max(stats['escalations_triggered'], 1)) * 100
        
        return f"""🔄 **HAWKMOTH Auto-Escalation Status**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 **Session Statistics:**
• Total Queries: {stats['total_queries']}
• Escalations Triggered: {stats['escalations_triggered']}
• Escalations Successful: {stats['escalations_successful']}
• Success Rate: {success_rate:.1f}%
• Real-time Queries: {stats['real_time_queries']}
• Model Failures Detected: {stats['model_failures']}
• Total Cost: ${stats['total_cost']:.4f}

🔄 **Escalation Engine:**
• Real-time Patterns: {escalation_stats['real_time_patterns']}
• Failure Patterns: {escalation_stats['failure_patterns']}
• Escalation Chains: {escalation_stats['escalation_chains']}
• Auto-approval Threshold: ${escalation_stats['auto_approval_threshold']}

🛣️  **Available Capabilities:**
{chr(10).join(f'• {cap}' for cap in escalation_stats['capabilities'])}

**Test Query**: Try "What is the date today?" to see auto-escalation in action!"""
    
    def _get_hawkmoth_status(self) -> str:
        """Get HAWKMOTH platform status"""
        git_status = "✅ Available" if self.git_handler.git_available else "❌ Unavailable"
        hf_status = "✅ Configured" if self.git_handler.hf_api else "⚠️ Not configured"
        
        enhanced_status = ""
        if self.enhanced_mode:
            llm_status = "✅ LLM Teaming Active"
            escalation_status = "✅ Auto-Escalation Active"
            sessions = len(self.llm_engine.active_sessions)
            enhanced_status = f"""
• LLM Teaming: {llm_status}
• Auto-Escalation: {escalation_status}
• Active Sessions: {sessions}"""
        
        return f"""🦅 **HAWKMOTH Platform Status**

**Core Systems:**
• Git Integration: {git_status}
• HuggingFace API: {hf_status}{enhanced_status}

**Platform Version:** v0.1.0-dev (LLM Teaming + Auto-Escalation)
**Repository Status:** {"✅ Ready" if self.git_handler.git_available else "⚠️ Setup needed"}

**Enhanced Features:**
{f"• {self.session_stats['total_queries']} queries processed" if self.enhanced_mode else "• Basic conversation mode"}
{f"• {self.session_stats['escalations_triggered']} escalations triggered" if self.enhanced_mode else ""}
{f"• ${self.session_stats['total_cost']:.4f} total cost" if self.enhanced_mode else ""}

**Available Commands:**
• `escalation status` - Check auto-escalation system
• `improve hawkmoth` - Create development environment
• `commit hawkmoth` - Deploy platform updates
• Paste GitHub URLs for instant analysis and deployment

**Test Real-time Escalation:** Try "What is the date today?"!"""
    
    def _handle_hawkmoth_improve(self) -> str:
        """Handle hawkmoth improvement request"""
        return """🦗 **HAWKMOTH Development Environment**

Development environment functionality will be available in v0.1.0.

**Current Development (v0.1.0-dev):**
• LLM Routing system with Together AI integration
• Auto-Escalation engine for real-time queries
• Sticky Sessions for conversation context
• Model failure detection and recovery

**Enhanced Features Ready:**
• Real-time data detection (dates, current events)
• Automatic escalation chains (DeepSeek → Claude → Web Search)
• Cost-efficient model routing with failure recovery
• Comprehensive session management

**Next Steps:**
Use `escalation status` to check auto-escalation configuration."""
    
    def _handle_hawkmoth_commit(self) -> str:
        """Handle hawkmoth commit/deployment"""
        try:
            result = hawkmoth_self_commit("HAWKMOTH v0.1.0-dev - Auto-escalation system with real-time data support")
            if result['success']:
                return f"""🚀 **HAWKMOTH Platform Update**

{result['message']}

**Auto-Escalation Update Complete!**
HAWKMOTH now includes intelligent escalation for real-time queries like "What is the date today?"

**New Capabilities:**
• Real-time data detection and routing
• Model failure detection and recovery  
• Automatic escalation chains
• Cost-efficient query processing"""
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
    
    def _analyze_repository(self, state, repo_url, session_id):
        state['status'] = 'analyzing'
        
        try:
            analysis = self.analyzer.analyze_repo(repo_url)
            state['analysis'] = analysis
            state['status'] = 'ready'
            
            return {
                'success': True,
                'response': self._format_analysis_response(analysis),
                'escalation_used': False,
                'session_id': session_id
            }
        
        except Exception as e:
            state['status'] = 'failed'
            return {
                'success': False,
                'response': f"❌ Analysis failed: {str(e)}",
                'escalation_used': False,
                'session_id': session_id
            }
    
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
    
    def _handle_approval(self, state, message, session_id):
        if any(word in message.lower() for word in ['yes', 'deploy', 'go', 'proceed']):
            state['approved'] = True
            state['status'] = 'deployed'
            
            try:
                deployment_result = deploy_with_real_git(state['analysis'])
                
                if deployment_result['success']:
                    response = "🚀 **Deployment Complete!**\n\n"
                    response += "✅ Repository cloned and analyzed\n"
                    response += "✅ Dependencies resolved\n"
                    response += "✅ HuggingFace Space created\n"
                    response += "✅ Application deployed\n\n"
                    response += f"🌟 **Your app is live:** {deployment_result['space_url']}\n\n"
                    response += "Share this URL with anyone!"
                    
                    return {
                        'success': True,
                        'response': response,
                        'escalation_used': False,
                        'session_id': session_id
                    }
                else:
                    return {
                        'success': False,
                        'response': f"❌ Deployment failed: {deployment_result['error']}",
                        'escalation_used': False,
                        'session_id': session_id
                    }
            except Exception as e:
                return {
                    'success': False,
                    'response': f"❌ Deployment failed: {str(e)}",
                    'escalation_used': False,
                    'session_id': session_id
                }
        
        elif any(word in message.lower() for word in ['no', 'cancel', 'stop']):
            state['status'] = 'cancelled'
            return {
                'success': True,
                'response': "👍 Deployment cancelled. Share another GitHub URL anytime!",
                'escalation_used': False,
                'session_id': session_id
            }
        
        return {
            'success': True,
            'response': "Please say 'yes' to deploy or 'no' to cancel.",
            'escalation_used': False,
            'session_id': session_id
        }
    
    def _get_help_response(self) -> str:
        enhanced_features = ""
        if self.enhanced_mode:
            enhanced_features = """
**Enhanced Features:**
• **Auto-Escalation** - Automatic handling of real-time queries
• **LLM Teaming** - Intelligent routing to specialized models
• **Cost Optimization** - 60-80% savings through smart routing

**Try These:**
• "What is the date today?" - See auto-escalation in action
• "escalation status" - Check auto-escalation system"""
        
        return f"""🦅 **Welcome to HAWKMOTH v0.1.0-dev!**

HAWKMOTH is your precision development platform with intelligent AI routing.

**Core Capabilities:**
• **Repository Deployment** - Paste any GitHub URL for instant analysis
• **Platform Management** - Self-improving system with Git integration{enhanced_features}

**Commands:**
• `hawkmoth status` - Check platform health and capabilities
• `improve hawkmoth` - Create development environment for testing
• `commit hawkmoth` - Deploy platform improvements

**Quick Start:**
Paste a GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example"""
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        stats = self.session_stats.copy()
        
        if self.enhanced_mode:
            # Add LLM engine stats
            llm_sessions = len(self.llm_engine.active_sessions)
            total_llm_cost = sum(session.total_cost for session in self.llm_engine.active_sessions.values())
            
            stats.update({
                'enhanced_mode': True,
                'active_llm_sessions': llm_sessions,
                'total_llm_cost': total_llm_cost,
                'escalation_engine_stats': self.escalation_engine.get_escalation_stats()
            })
        else:
            stats['enhanced_mode'] = False
        
        return stats
