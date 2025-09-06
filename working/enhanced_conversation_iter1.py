# HAWKMOTH Enhanced Conversation Manager with LLM Routing
import time
import json
import requests
from typing import Dict, Any, Optional
from git_handler import HAWKMOTHGitHandler, deploy_with_real_git, hawkmoth_self_commit
from llm_router import HAWKMOTHRouter, RoutingDecision

class EnhancedConversationManager:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.conversations = {}
        self.git_handler = HAWKMOTHGitHandler()
        self.router = HAWKMOTHRouter()
        
        # API configurations
        self.claude_api_key = ""  # Will be configured later
        self.openai_api_key = ""  # Will be configured later
        
        # Statistics
        self.routing_stats = {
            'total_queries': 0,
            'routes_by_target': {},
            'total_cost': 0.0
        }

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Enhanced message processing with LLM routing"""
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'analysis': None,
                'status': 'waiting',
                'approved': False,
                'routing_history': []
            }

        state = self.conversations[user_id]
        
        # Update statistics
        self.routing_stats['total_queries'] += 1
        
        # Get routing decision
        routing_decision = self.router.route_query(message, self._get_user_context(user_id))
        
        # Store routing decision
        state['routing_history'].append({
            'query': message,
            'routing': routing_decision,
            'timestamp': time.time()
        })
        
        # Update routing statistics
        target = routing_decision.target_llm
        self.routing_stats['routes_by_target'][target] = self.routing_stats['routes_by_target'].get(target, 0) + 1
        self.routing_stats['total_cost'] += routing_decision.estimated_cost / 1000  # Convert to actual cost
        
        # Route to appropriate handler
        if routing_decision.target_llm == 'HAWKMOTH':
            response = self._handle_hawkmoth_queries(state, message)
        elif routing_decision.target_llm == 'CLAUDE':
            response = self._handle_claude_queries(state, message, routing_decision)
        elif routing_decision.target_llm == 'GPT4':
            response = self._handle_gpt4_queries(state, message, routing_decision)
        elif routing_decision.target_llm == 'ROUTER':
            response = self._handle_router_queries(state, message, routing_decision)
        else:
            response = self._handle_fallback(state, message, routing_decision)
        
        # Add routing information to response
        return {
            'response': response,
            'routing_info': {
                'target_llm': routing_decision.target_llm,
                'confidence': routing_decision.confidence,
                'reason': routing_decision.reason,
                'estimated_cost': routing_decision.estimated_cost,
                'complexity': routing_decision.complexity
            },
            'success': True
        }
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context for better routing decisions"""
        state = self.conversations.get(user_id, {})
        
        return {
            'current_status': state.get('status', 'waiting'),
            'has_analysis': state.get('analysis') is not None,
            'recent_routes': [h['routing'].target_llm for h in state.get('routing_history', [])[-3:]],
            'session_type': 'development' if any('code' in h['query'].lower() for h in state.get('routing_history', [])) else 'general'
        }
    
    def _handle_hawkmoth_queries(self, state, message: str) -> str:
        """Handle HAWKMOTH platform commands locally"""
        
        # Routing status command
        if any(cmd in message.lower() for cmd in ['routing status', 'router status', 'llm status']):
            return self._handle_routing_status()
        
        # Standard HAWKMOTH commands
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
        
        # Default HAWKMOTH response
        return self._handle_general_hawkmoth(message)
    
    def _handle_claude_queries(self, state, message: str, routing: RoutingDecision) -> str:
        """Handle queries routed to Claude"""
        # For now, return a placeholder - will implement Claude API integration
        return f"""🧠 **Claude Integration** (Routed for: {routing.reason})

This query has been identified as requiring Claude's coding expertise.

**Current Status**: Claude API integration in development
**Confidence**: {routing.confidence:.2f}
**Estimated Cost**: ${routing.estimated_cost:.3f}/1k tokens

**Coming Soon**: Direct Claude API integration for:
• Complex debugging and code analysis  
• Architecture recommendations
• Algorithm optimization
• Technical problem solving

**For now**: Please continue the conversation in this Claude interface, or use `hawkmoth status` for platform commands."""
    
    def _handle_gpt4_queries(self, state, message: str, routing: RoutingDecision) -> str:
        """Handle queries routed to GPT-4"""
        # Placeholder for GPT-4 integration
        return f"""🎨 **GPT-4 Integration** (Routed for: {routing.reason})

This query has been identified as best suited for GPT-4's capabilities.

**Current Status**: GPT-4 API integration in development  
**Confidence**: {routing.confidence:.2f}
**Estimated Cost**: ${routing.estimated_cost:.3f}/1k tokens

**Coming Soon**: Direct GPT-4 API integration for:
• Design and graphics assistance
• Creative writing and content
• General conversation and brainstorming
• Visual concept development

**For now**: The routing system is working! This would be sent to GPT-4 in production."""
    
    def _handle_router_queries(self, state, message: str, routing: RoutingDecision) -> str:
        """Handle simple queries with the router LLM (Together AI)"""
        if not self.router.together_api_key:
            return f"""🤖 **Router Response** (Cost-optimized routing)

**Query identified as**: Simple question suitable for efficient processing
**Confidence**: {routing.confidence:.2f}
**Estimated Cost**: ${routing.estimated_cost:.3f}/1k tokens

**Current Status**: Together AI integration ready - configure TOGETHER_API_KEY to enable.

**This query would be processed by**: Llama 3.1 8B via Together AI for cost-efficient responses."""
        
        # TODO: Implement actual Together AI call for simple queries
        return f"""🤖 **Router Processing** 

Together AI integration would handle this simple query cost-effectively.
(Implementation in progress - configure TOGETHER_API_KEY)"""
    
    def _handle_routing_status(self) -> str:
        """Handle routing status queries"""
        stats = self.routing_stats
        router_info = self.router.get_routing_stats()
        
        response = "🧠 **HAWKMOTH LLM Routing Status**\n\n"
        
        # API Configuration Status
        response += "**API Configuration:**\n"
        response += f"• Together AI: {'✅ Configured' if router_info['together_api_configured'] else '⚠️ Not configured'}\n"
        response += f"• Claude API: {'✅ Configured' if self.claude_api_key else '⚠️ Not configured'}\n"
        response += f"• OpenAI API: {'✅ Configured' if self.openai_api_key else '⚠️ Not configured'}\n\n"
        
        # Routing Statistics
        response += "**Session Statistics:**\n"
        response += f"• Total Queries: {stats['total_queries']}\n"
        response += f"• Estimated Cost: ${stats['total_cost']:.4f}\n\n"
        
        if stats['routes_by_target']:
            response += "**Routes by Target:**\n"
            for target, count in stats['routes_by_target'].items():
                percentage = (count / stats['total_queries']) * 100
                response += f"• {target}: {count} queries ({percentage:.1f}%)\n"
            response += "\n"
        
        # Available Targets
        response += "**Available LLM Targets:**\n"
        for target, info in router_info['targets'].items():
            response += f"• **{target}**: {info['description']} (${info['cost_per_1k']:.2f}/1k tokens)\n"
        
        response += "\n**Routing Methods**: Rule-based + LLM-based + Fallback"
        
        return response
    
    def _handle_fallback(self, state, message: str, routing: RoutingDecision) -> str:
        """Handle fallback cases"""
        return f"""⚠️ **Fallback Routing**

**Routing Decision**: {routing.reason}
**Confidence**: {routing.confidence:.2f}

This query couldn't be confidently routed to a specific LLM. It would normally go to {routing.target_llm}.

**Available Commands:**
• `routing status` - Check LLM routing configuration
• `hawkmoth status` - Platform status
• Standard GitHub URL analysis and deployment

**The routing system is working** - this demonstrates the fallback mechanism!"""
    
    # Include all the existing HAWKMOTH methods
    def _handle_hawkmoth_status(self):
        """Handle hawkmoth status command"""
        git_status = "✅ Available" if self.git_handler.git_available else "❌ Unavailable"
        hf_status = "✅ Configured" if self.git_handler.hf_api else "⚠️ Not configured"
        
        return f"""🦅 **HAWKMOTH Platform Status**

**Core Systems:**
• Git Integration: {git_status}
• HuggingFace API: {hf_status}
• LLM Routing: ✅ Active ({self.routing_stats['total_queries']} queries routed)
• Green/Blue Deployment: ✅ Ready

**Platform Version:** v0.1.0-dev (LLM Teaming)
**Repository Status:** {"✅ Ready" if self.git_handler.git_available else "⚠️ Setup needed"}

**Available Commands:**
• `routing status` - Check LLM routing system
• `improve hawkmoth` - Create development environment
• `commit hawkmoth` - Deploy platform updates
• Paste GitHub URLs for instant analysis and deployment"""

    def _handle_hawkmoth_improve(self):
        """Handle hawkmoth improvement request"""
        return """🦗 **HAWKMOTH Development Environment**

Development environment functionality will be available in v0.1.0.

**Current Development (v0.1.0-dev):**
• LLM Routing system with Together AI integration
• Multi-LLM architecture framework
• Enhanced conversation management
• HuggingFace modular service preparation

**Coming Soon:**
• Green/Blue development environments for LLM services
• Auto-deployment of HF CPU modules
• Enhanced routing with user learning
• Full API integrations

**Next Steps:**
Use `routing status` to check LLM configuration and routing statistics."""

    def _handle_hawkmoth_commit(self):
        """Handle hawkmoth commit/deployment"""
        try:
            result = hawkmoth_self_commit("HAWKMOTH v0.1.0-dev - LLM routing system")
            if result['success']:
                return f"""🚀 **HAWKMOTH Platform Update**

{result['message']}

**LLM Teaming Update Complete!**
HAWKMOTH now includes intelligent routing to specialized LLMs for optimal query handling."""
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
            return """🦅 **Welcome to HAWKMOTH v0.1.0-dev!**

HAWKMOTH now features **LLM Teaming** - intelligent routing to specialized AI models.

**Core Capabilities:**
• **Intelligent Routing** - Queries go to the best LLM for the task
• **Repository Deployment** - Paste any GitHub URL for instant analysis
• **Platform Management** - Self-improving system with Git integration
• **Cost Optimization** - Efficient use of AI APIs

**Commands:**
• `hawkmoth status` - Check platform health and capabilities
• `routing status` - Check LLM routing system and statistics
• `improve hawkmoth` - Create development environment for testing
• `commit hawkmoth` - Deploy platform improvements

**LLM Routing:**
Queries are automatically routed to Claude (coding), GPT-4 (design), Together AI (general), or handled locally (platform commands).

**Quick Start:**
Paste a GitHub repository URL to analyze and deploy instantly!

**Example:** https://github.com/streamlit/streamlit-example"""
        
        return """👋 **Welcome to HAWKMOTH v0.1.0-dev with LLM Teaming!**

I'm your development platform companion with intelligent LLM routing. Share a GitHub repository URL and I'll analyze and deploy it instantly, or use hawkmoth commands to manage the platform.

**New**: Try `routing status` to see the LLM routing system in action!

Try: `hawkmoth status` or paste a GitHub URL!"""
