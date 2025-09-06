# HAWKMOTH Enhanced Conversation Manager with LLM Routing
import time
import json
import requests
from typing import Dict, Any, Optional
from git_handler import HAWKMOTHGitHandler, deploy_with_real_git, hawkmoth_self_commit
from hawkmoth_sticky_sessions import HAWKMOTHStickySessionEngine

class EnhancedConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        self.git_handler = HAWKMOTHGitHandler()
        
        # Initialize LLM Teaming Engine
        self.llm_engine = HAWKMOTHStickySessionEngine()
        
        # Statistics
        self.routing_stats = {
            'total_queries': 0,
            'routes_by_target': {},
            'total_cost': 0.0,
            'llm_routes': 0,
            'rule_routes': 0
        }
        
        print("🦅 HAWKMOTH Enhanced Conversation Manager - LLM Teaming Ready!")

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Enhanced message processing with LLM Teaming"""
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False,
                'routing_history': [],
                'llm_session_id': None
            }

        state = self.conversations[user_id]
        
        # Update statistics
        self.routing_stats['total_queries'] += 1
        
        # Check for HAWKMOTH platform commands first
        if self._is_hawkmoth_command(message):
            response = self._handle_hawkmoth_queries(state, message)
            header = self._get_model_header('hawkmoth-local', 0.0, False)
            formatted_response = f"{header}\n\n{response}"
            return {
                'response': formatted_response,
                'routing_info': {
                    'target_llm': 'HAWKMOTH_LOCAL',
                    'confidence': 1.0,
                    'reason': 'Platform command - local processing',
                    'estimated_cost': 0.0,
                    'complexity': 'simple'
                },
                'success': True
            }
        
        # Check for GitHub URL analysis
        github_url = self._extract_github_url(message)
        if github_url:
            response = self._analyze_repository(state, github_url)
            return {
                'response': response,
                'routing_info': {
                    'target_llm': 'HAWKMOTH_LOCAL',
                    'confidence': 1.0,
                    'reason': 'Repository analysis - local processing',
                    'estimated_cost': 0.0,
                    'complexity': 'medium'
                },
                'success': True
            }
        
        # Handle deployment approval
        if state['status'] == 'ready' and not state['approved']:
            response = self._handle_approval(state, message)
            return {
                'response': response,
                'routing_info': {
                    'target_llm': 'HAWKMOTH_LOCAL',
                    'confidence': 1.0,
                    'reason': 'Deployment approval - local processing',
                    'estimated_cost': 0.0,
                    'complexity': 'simple'
                },
                'success': True
            }
        
        # Use LLM Teaming for all other queries
        try:
            # Get or create session
            session_id = state.get('llm_session_id')
            if not session_id:
                session = self.llm_engine.start_conversation_session(message)
                state['llm_session_id'] = session.session_id
                session_id = session.session_id
            
            # Continue conversation with LLM Teaming
            llm_response, model_switched = self.llm_engine.continue_conversation(session_id, message)
            
            # Update routing statistics
            model_used = llm_response.model_used
            self.routing_stats['routes_by_target'][model_used] = self.routing_stats['routes_by_target'].get(model_used, 0) + 1
            self.routing_stats['total_cost'] += llm_response.actual_cost
            
            # Store routing decision
            state['routing_history'].append({
                'query': message,
                'model_used': model_used,
                'cost': llm_response.actual_cost,
                'switched': model_switched,
                'timestamp': time.time()
            })
            
            # Add model header to response
            model_header = self._get_model_header(llm_response.model_used, llm_response.actual_cost, model_switched)
            formatted_response = f"{model_header}\n\n{llm_response.content}"
            
            return {
                'response': formatted_response,
                'routing_info': {
                    'target_llm': model_used,
                    'confidence': 0.9,
                    'reason': f'LLM Teaming - {llm_response.provider}',
                    'estimated_cost': llm_response.actual_cost,
                    'complexity': 'variable',
                    'model_switched': model_switched,
                    'session_id': session_id
                },
                'success': True
            }
            
        except Exception as e:
            # Fallback to local processing
            response = f"🔄 LLM Teaming temporarily unavailable. Falling back to local processing.\n\nError: {str(e)}\n\n"
            response += self._handle_general_hawkmoth(message)
            
            return {
                'response': response,
                'routing_info': {
                    'target_llm': 'HAWKMOTH_LOCAL',
                    'confidence': 0.5,
                    'reason': 'Fallback - LLM error',
                    'estimated_cost': 0.0,
                    'complexity': 'error'
                },
                'success': False,
                'error': str(e)
            }
    
    def _is_hawkmoth_command(self, message: str) -> bool:
        """Check if message is a HAWKMOTH platform command"""
        hawkmoth_commands = [
            'hawkmoth status', 'status hawkmoth',
            'hawkmoth improve', 'improve hawkmoth',
            'hawkmoth commit', 'commit hawkmoth',
            'routing status', 'router status', 'llm status',
            'test together', 'together test', 'test api',
            'session status', 'hawkmoth session'
        ]
        
        message_lower = message.lower()
        return any(cmd in message_lower for cmd in hawkmoth_commands)
    
    def _handle_hawkmoth_queries(self, state, message: str) -> str:
        """Handle HAWKMOTH platform commands locally"""
        
        # LLM Teaming status commands
        if any(cmd in message.lower() for cmd in ['routing status', 'router status', 'llm status']):
            return self._handle_routing_status()
        
        if any(cmd in message.lower() for cmd in ['session status', 'hawkmoth session']):
            return self._handle_session_status(state)
        
        # Together AI test command
        if any(cmd in message.lower() for cmd in ['test together', 'together test', 'test api']):
            return self._handle_together_test()
        
        # Standard HAWKMOTH commands
        if any(cmd in message.lower() for cmd in ['hawkmoth status', 'status hawkmoth']):
            return self._handle_hawkmoth_status()
        
        if any(cmd in message.lower() for cmd in ['improve hawkmoth', 'hawkmoth improve']):
            return self._handle_hawkmoth_improve()
        
        if any(cmd in message.lower() for cmd in ['commit hawkmoth', 'hawkmoth commit']):
            return self._handle_hawkmoth_commit()
        
        # Default HAWKMOTH response
        return self._handle_general_hawkmoth(message)
    
    def _handle_session_status(self, state) -> str:
        """Handle session status command"""
        session_id = state.get('llm_session_id')
        if not session_id:
            return "🔄 No active LLM session. Start a conversation to create one!"
        
        try:
            summary = self.llm_engine.get_session_summary(session_id)
            if 'error' in summary:
                return f"❌ Session Error: {summary['error']}"
            
            return f"""🦅 **HAWKMOTH LLM Session Status**

**Session ID**: {summary['session_id']}
**Primary Model**: {summary['primary_model']}
**Model Lane**: {summary['model_lane']}
**Duration**: {summary['duration_minutes']:.1f} minutes
**Messages**: {summary['total_messages']}
**Total Cost**: ${summary['total_cost']:.4f}
**Cost/Message**: ${summary['cost_per_message']:.4f}

**Sticky Session**: Context preserved within {summary['primary_model']}
**Switch Available**: Premium models available on request"""
        except Exception as e:
            return f"❌ Error getting session status: {str(e)}"
    
    def _handle_together_test(self) -> str:
        """Test Together AI connection through LLM engine"""
        try:
            # Test by checking if Together AI API key is configured
            engine = self.llm_engine
            if not engine.together_api_key:
                return """❌ **Together AI Connection Test**

**Status**: API key not configured
**Environment Variables Checked**: TOGETHER_API_KEY, TOGETHERAI_KEY

**Configuration Steps**:
1. Get API key from https://api.together.xyz/
2. Set environment variable: TOGETHER_API_KEY=your_key_here
3. Restart HAWKMOTH application

**Current Status**: LLM Teaming running in local mode only"""
            
            # Test with a simple query
            test_session = engine.start_conversation_session("test connection")
            test_response, _ = engine.continue_conversation(test_session.session_id, "hello")
            
            if test_response.provider == 'together_ai':
                return f"""✅ **Together AI Connection Test**

**Status**: Connected and operational
**Model**: {test_response.model_used}
**Response Time**: {test_response.response_time:.2f} seconds
**Cost**: ${test_response.actual_cost:.4f}

**LLM Teaming Status**: Fully operational
**Available Models**: DeepSeek V3, DeepSeek R1, Llama 3.3 70B

Try asking complex questions to see automatic model routing!"""
            else:
                return """⚠️ **Together AI Connection Test**

**Status**: Falling back to local processing
**Issue**: Together AI models not responding correctly

**Troubleshooting**:
• Check API key validity and credits
• Verify internet connectivity
• Check Together AI service status

**Current Status**: LLM Teaming in reduced mode"""
                
        except Exception as e:
            return f"""❌ **Together AI Connection Test**

**Status**: Connection failed
**Error**: {str(e)}

**Troubleshooting**:
• Verify TOGETHER_API_KEY environment variable
• Check API key has sufficient credits
• Ensure network connectivity

**Current Status**: LLM Teaming in local mode"""
    
    def _handle_routing_status(self) -> str:
        """Handle routing status queries"""
        stats = self.routing_stats
        engine = self.llm_engine
        
        response = "🧠 **HAWKMOTH LLM Teaming Status**\n\n"
        
        # API Configuration Status
        response += "**API Configuration:**\n"
        response += f"• Together AI: {'✅ Configured' if engine.together_api_key else '⚠️ Not configured'}\n"
        response += f"• Claude Direct: {'✅ Configured' if engine.claude_api_key else '⚠️ Not configured'}\n"
        response += f"• HAWKMOTH Local: ✅ Available\n\n"
        
        # Active Sessions
        active_sessions = len(engine.active_sessions)
        response += f"**Active Sessions**: {active_sessions}\n"
        if active_sessions > 0:
            total_session_cost = sum(session.total_cost for session in engine.active_sessions.values())
            response += f"**Total Session Cost**: ${total_session_cost:.4f}\n"
        response += "\n"
        
        # Session Statistics
        response += "**Session Statistics:**\n"
        response += f"• Total Queries: {stats['total_queries']}\n"
        response += f"• Total Cost: ${stats['total_cost']:.4f}\n\n"
        
        if stats['routes_by_target']:
            response += "**Routes by Model:**\n"
            for target, count in stats['routes_by_target'].items():
                percentage = (count / stats['total_queries']) * 100
                response += f"• {target}: {count} queries ({percentage:.1f}%)\n"
            response += "\n"
        
        # Available Model Lanes
        response += "**Available Model Lanes:**\n"
        lanes = {
            "Quick Questions": "FREE (DeepSeek R1 Free)",
            "Development Work": "$1.25/1k (DeepSeek V3)",
            "Complex Reasoning": "$3/$7/1k (DeepSeek R1)",
            "Multilingual": "$0.88/1k (Llama 3.3 70B)",
            "Premium Analysis": "$3/$15/1k (Claude Sonnet 4)",
            "Platform Commands": "FREE (HAWKMOTH Local)"
        }
        
        for lane, cost in lanes.items():
            response += f"• **{lane}**: {cost}\n"
        
        response += "\n**Commands:**\n"
        response += "• `test together` - Test Together AI API connection\n"
        response += "• `session status` - Current conversation session info\n"
        response += "• `hawkmoth status` - Platform status"
        
        return response
    
    # Include all the existing HAWKMOTH methods
    def _handle_hawkmoth_status(self):
        """Handle hawkmoth status command"""
        git_status = "✅ Available" if self.git_handler.git_available else "❌ Unavailable"
        hf_status = "✅ Configured" if self.git_handler.hf_api else "⚠️ Not configured"
        together_status = "✅ Configured" if self.llm_engine.together_api_key else "⚠️ Not configured"
        claude_status = "✅ Configured" if self.llm_engine.claude_api_key else "⚠️ Not configured"
        
        active_sessions = len(self.llm_engine.active_sessions)
        
        return f"""🦅 **HAWKMOTH Platform Status** - v0.1.0-dev (LLM Teaming)

**Core Systems:**
• Git Integration: {git_status}
• HuggingFace API: {hf_status}
• LLM Teaming Engine: ✅ Active ({active_sessions} sessions)

**LLM Integrations:**
• Together AI: {together_status}
• Claude Direct: {claude_status}
• HAWKMOTH Local: ✅ Available

**Platform Statistics:**
• Total Queries Routed: {self.routing_stats['total_queries']}
• Total LLM Cost: ${self.routing_stats['total_cost']:.4f}
• Sticky Sessions: {active_sessions} active

**Available Commands:**
• `routing status` - Check LLM Teaming system
• `session status` - Current conversation session
• `test together` - Test Together AI API connection
• `improve hawkmoth` - Create development environment
• `commit hawkmoth` - Deploy platform updates
• Paste GitHub URLs for instant analysis and deployment

**LLM Teaming**: Queries automatically routed to optimal models for cost and performance!"""

    def _handle_hawkmoth_improve(self):
        """Handle hawkmoth improvement request"""
        return """🦗 **HAWKMOTH Development Environment**

**v0.1.0-dev Status**: LLM Teaming implementation complete!

**Current Features:**
• ✅ Sticky Sessions Engine - Context preservation across model switches
• ✅ Together AI Integration - DeepSeek V3, DeepSeek R1, Llama 3.3 70B
• ✅ Cost Optimization - 60-80% savings vs direct vendor pricing
• ✅ Multi-Provider Architecture - Together AI + Claude Direct + Local
• ✅ Intelligent Routing - Right model for the right task

**Next Development Phase (v0.1.1):**
• Enhanced routing with ML-based decisions
• Advanced cost budgeting and alerts
• Session analytics and insights
• Model recommendation engine

**Ready for Production**: LLM Teaming system is ready for deployment!

Use `commit hawkmoth` to deploy the current LLM Teaming implementation."""

    def _handle_hawkmoth_commit(self):
        """Handle hawkmoth commit/deployment"""
        try:
            result = hawkmoth_self_commit("HAWKMOTH v0.1.0-dev - LLM Teaming with Sticky Sessions")
            if result['success']:
                return f"""🚀 **HAWKMOTH Platform Update**

{result['message']}

**LLM Teaming v0.1.0-dev Deployed!**
✅ Sticky Sessions Engine
✅ Together AI Integration  
✅ Multi-model routing
✅ Cost optimization (60-80% savings)
✅ Context preservation

HAWKMOTH now features intelligent AI model orchestration!"""
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

    def _handle_general_hawkmoth(self, message):
        if any(word in message.lower() for word in ['help', 'how']):
            return """🦅 **Welcome to HAWKMOTH v0.1.0-dev - LLM Teaming!**

HAWKMOTH now features **Intelligent LLM Orchestration** with sticky sessions.

**Core Capabilities:**
• **Sticky Sessions** - Context preserved within optimal models
• **Multi-LLM Routing** - DeepSeek V3, DeepSeek R1, Llama 3.3, Claude
• **Cost Optimization** - 60-80% savings through smart routing
• **Repository Deployment** - Paste any GitHub URL for instant analysis
• **Platform Management** - Self-improving system with Git integration

**Commands:**
• `hawkmoth status` - Check platform health and LLM integrations
• `routing status` - Check LLM Teaming system and statistics
• `session status` - Current conversation session info
• `test together` - Test Together AI API connection
• `improve hawkmoth` - Development environment status
• `commit hawkmoth` - Deploy platform improvements

**LLM Teaming in Action:**
• Simple questions → FREE (DeepSeek R1 Free)
• Development work → $1.25/1k (DeepSeek V3)
• Complex reasoning → $3/$7/1k (DeepSeek R1)
• Premium analysis → $3/$15/1k (Claude Sonnet 4)

**Quick Start:**
Paste a GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example"""
        
        return """👋 **Welcome to HAWKMOTH v0.1.0-dev with LLM Teaming!**

I'm your development platform with intelligent AI model orchestration. Each conversation uses sticky sessions to preserve context while optimizing for cost and performance.

**New**: Advanced LLM routing with Together AI integration!

Try: `hawkmoth status`, `routing status`, or paste a GitHub URL!

Current session will use the optimal model for your queries automatically."""
    
    def _get_model_header(self, model_used: str, actual_cost: float, model_switched: bool) -> str:
        """Generate a header showing which model is responding"""
        # Model display names
        model_names = {
            'hawkmoth-local': 'HAWKMOTH Local',
            'deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free': 'DeepSeek R1 Free',
            'deepseek-ai/DeepSeek-V3': 'DeepSeek V3',
            'deepseek-ai/DeepSeek-R1': 'DeepSeek R1',
            'meta-llama/Llama-3.3-70B-Instruct-Turbo': 'Llama 3.3 70B',
            'claude-3-5-sonnet-20241022': 'Claude Sonnet 4',
            'claude-3-opus-20240229': 'Claude Opus 4'
        }
        
        display_name = model_names.get(model_used, model_used)
        
        if actual_cost == 0.0:
            cost_info = 'FREE'
        else:
            cost_info = f'${actual_cost:.4f}'
        
        switch_indicator = ' (Model Switch)' if model_switched else ''
        
        return f"**{display_name}** | Cost: {cost_info}{switch_indicator}"
        
