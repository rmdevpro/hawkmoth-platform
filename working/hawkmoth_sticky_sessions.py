# HAWKMOTH LLM Teaming Engine - Sticky Sessions Implementation
import os
import json
import requests
import time
import uuid
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

class ModelProvider(Enum):
    CLAUDE_DIRECT = "claude_direct"
    TOGETHER_AI = "together_ai"
    HAWKMOTH_LOCAL = "hawkmoth_local"

@dataclass
class ModelConfig:
    """Configuration for each LLM model"""
    model_id: str
    provider: ModelProvider
    cost_per_1k_input: float
    cost_per_1k_output: float
    max_tokens: int
    context_length: int
    specialties: List[str]
    description: str
    api_endpoint: str = ""

@dataclass
class ConversationSession:
    """Manages conversation session state"""
    session_id: str
    primary_model: str
    model_config: ModelConfig
    conversation_history: List[Dict[str, Any]]
    total_cost: float
    total_tokens: int
    started_at: datetime
    last_activity: datetime
    context_summary: str = ""

@dataclass
class RoutingDecision:
    target_llm: str
    model_config: ModelConfig
    confidence: float
    reason: str
    estimated_cost: float
    complexity: str
    requires_switch: bool = False
    switch_reason: str = ""

@dataclass
class LLMResponse:
    content: str
    model_used: str
    provider: str
    input_tokens: int
    output_tokens: int
    actual_cost: float
    response_time: float
    session_id: str
    metadata: Dict[str, Any]

class HAWKMOTHStickySessionEngine:
    def __init__(self):
        # API Keys
        self.claude_api_key = os.getenv('ANTHROPIC_API_KEY') or ''
        self.together_api_key = (
            os.getenv('TOGETHER_API_KEY') or 
            os.getenv('TOGETHERAI_KEY') or 
            ''
        )
        
        # API Endpoints
        self.claude_base_url = "https://api.anthropic.com/v1/messages"
        self.together_base_url = "https://api.together.xyz/v1/chat/completions"
        
        # Active conversation sessions
        self.active_sessions: Dict[str, ConversationSession] = {}
        
        # Model catalog optimized for sticky sessions
        self.model_catalog = {
            # HAWKMOTH Local
            'HAWKMOTH_LOCAL': ModelConfig(
                model_id="hawkmoth-local",
                provider=ModelProvider.HAWKMOTH_LOCAL,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                max_tokens=2048,
                context_length=4096,
                specialties=['hawkmoth', 'platform', 'commands', 'status'],
                description='Local HAWKMOTH platform commands and operations'
            ),
            
            # Together AI Models (Open Source - Primary Lane)
            'DEEPSEEK_R1_FREE': ModelConfig(
                model_id="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                max_tokens=4096,
                context_length=8192,
                specialties=['free', 'testing', 'simple_reasoning', 'quick_questions'],
                description='Free DeepSeek R1 distilled model - ideal for quick questions'
            ),
            
            'DEEPSEEK_V3': ModelConfig(
                model_id="deepseek-ai/DeepSeek-V3",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=1.25,
                cost_per_1k_output=1.25,
                max_tokens=8192,
                context_length=128000,
                specialties=['general', 'coding', 'balanced_performance', 'development'],
                description='Balanced workhorse for general development and coding tasks'
            ),
            
            'DEEPSEEK_R1': ModelConfig(
                model_id="deepseek-ai/DeepSeek-R1",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=3.0,
                cost_per_1k_output=7.0,
                max_tokens=8192,
                context_length=128000,
                specialties=['reasoning', 'math', 'complex_analysis', 'research'],
                description='Advanced reasoning model for complex problem solving'
            ),
            
            'LLAMA_3_3_70B': ModelConfig(
                model_id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=0.88,
                cost_per_1k_output=0.88,
                max_tokens=8192,
                context_length=128000,
                specialties=['multilingual', 'dialogue', 'translation', 'cultural_context'],
                description='Multilingual specialist for global applications'
            ),
            
            # Claude Direct (Premium Lane)
            'CLAUDE_SONNET_4': ModelConfig(
                model_id="claude-3-5-sonnet-20241022",
                provider=ModelProvider.CLAUDE_DIRECT,
                cost_per_1k_input=3.0,
                cost_per_1k_output=15.0,
                max_tokens=8192,
                context_length=200000,
                specialties=['premium_analysis', 'architecture', 'strategic_thinking'],
                description='Premium Claude model for high-value analysis'
            ),
            
            'CLAUDE_OPUS_4': ModelConfig(
                model_id="claude-3-opus-20240229",
                provider=ModelProvider.CLAUDE_DIRECT,
                cost_per_1k_input=15.0,
                cost_per_1k_output=75.0,
                max_tokens=8192,
                context_length=200000,
                specialties=['critical_analysis', 'complex_reasoning', 'premium_tasks'],
                description='Highest capability Claude for critical analysis'
            )
        }
        
        # Session management settings
        self.session_timeout_minutes = 60
        self.max_switch_threshold = 3.0  # Dollar threshold for auto-switching
        
        print("🦅 HAWKMOTH Sticky Sessions Engine Initialized")
        self._print_initialization_status()
    
    def _print_initialization_status(self):
        """Print API connections and sticky session info"""
        print("=" * 60)
        print(f"🔗 Claude Direct: {'✅ Connected' if self.claude_api_key else '❌ No API key'}")
        print(f"📡 Together AI: {'✅ Connected' if self.together_api_key else '❌ No API key'}")
        print(f"🏠 HAWKMOTH Local: ✅ Available")
        
        print(f"\n🎯 Sticky Sessions Strategy:")
        print(f"   • Start with optimal model for first query")
        print(f"   • Maintain context within same model")
        print(f"   • Switch only for premium analysis requests")
        print(f"   • Auto-switch threshold: ${self.max_switch_threshold}")
        
        print(f"\n📚 Model Lanes Available:")
        lanes = {
            "Quick Questions": ["DEEPSEEK_R1_FREE"],
            "Development Work": ["DEEPSEEK_V3", "DEEPSEEK_R1"],
            "Multilingual": ["LLAMA_3_3_70B"],
            "Premium Analysis": ["CLAUDE_SONNET_4", "CLAUDE_OPUS_4"],
            "Platform Commands": ["HAWKMOTH_LOCAL"]
        }
        
        for lane, models in lanes.items():
            model_costs = [f"${self.model_catalog[m].cost_per_1k_input}" for m in models]
            print(f"   🛣️  {lane}: {', '.join(model_costs)}/1k tokens")
    
    def start_conversation_session(self, user_message: str, session_id: str = None) -> ConversationSession:
        """Start a new conversation session with optimal model selection"""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
        
        # Route initial query to determine primary model
        routing_decision = self.route_initial_query(user_message)
        
        # Create conversation session
        session = ConversationSession(
            session_id=session_id,
            primary_model=routing_decision.target_llm,
            model_config=routing_decision.model_config,
            conversation_history=[],
            total_cost=0.0,
            total_tokens=0,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            context_summary=""
        )
        
        self.active_sessions[session_id] = session
        
        print(f"\n🆕 New Conversation Session Started")
        print(f"   Session ID: {session_id}")
        print(f"   Primary Model: {routing_decision.target_llm}")
        print(f"   Model: {routing_decision.model_config.model_id}")
        print(f"   Reason: {routing_decision.reason}")
        print(f"   Lane: {self._get_model_lane(routing_decision.target_llm)}")
        
        return session
    
    def continue_conversation(self, session_id: str, user_message: str) -> tuple[LLMResponse, bool]:
        """Continue conversation in existing session or handle model switching"""
        session = self.active_sessions.get(session_id)
        if not session:
            # Create new session if not found
            session = self.start_conversation_session(user_message, session_id)
        
        # Update session activity
        session.last_activity = datetime.now()
        
        # Check if we should consider switching models
        switch_decision = self.evaluate_model_switch(session, user_message)
        
        if switch_decision.requires_switch:
            return self.handle_model_switch(session, user_message, switch_decision)
        else:
            # Continue with current model (sticky session)
            return self.execute_with_current_model(session, user_message), False
    
    def route_initial_query(self, user_message: str) -> RoutingDecision:
        """Route the very first query to determine primary model for session"""
        message_lower = user_message.lower()
        
        # HAWKMOTH platform commands (local processing)
        hawkmoth_keywords = ['hawkmoth status', 'hawkmoth', 'deploy', 'git status', 'routing status']
        if any(keyword in message_lower for keyword in hawkmoth_keywords):
            return RoutingDecision(
                target_llm='HAWKMOTH_LOCAL',
                model_config=self.model_catalog['HAWKMOTH_LOCAL'],
                confidence=0.95,
                reason='Platform command - local processing',
                estimated_cost=0.0,
                complexity='simple'
            )
        
        # Premium analysis indicators
        premium_keywords = ['comprehensive analysis', 'strategic', 'architecture review', 'critical decision']
        if any(keyword in message_lower for keyword in premium_keywords):
            return RoutingDecision(
                target_llm='CLAUDE_SONNET_4',
                model_config=self.model_catalog['CLAUDE_SONNET_4'],
                confidence=0.90,
                reason='Premium analysis request detected',
                estimated_cost=self._estimate_cost(user_message, self.model_catalog['CLAUDE_SONNET_4']),
                complexity='high'
            )
        
        # Complex reasoning tasks
        reasoning_keywords = ['analyze', 'research', 'complex', 'reasoning', 'math', 'prove', 'step by step']
        if (any(keyword in message_lower for keyword in reasoning_keywords) or
            len(user_message.split()) > 30):
            return RoutingDecision(
                target_llm='DEEPSEEK_R1',
                model_config=self.model_catalog['DEEPSEEK_R1'],
                confidence=0.85,
                reason='Complex reasoning task - DeepSeek R1 optimal',
                estimated_cost=self._estimate_cost(user_message, self.model_catalog['DEEPSEEK_R1']),
                complexity='high'
            )
        
        # Development and coding tasks
        coding_keywords = ['code', 'debug', 'python', 'javascript', 'function', 'api', 'algorithm']
        if any(keyword in message_lower for keyword in coding_keywords):
            return RoutingDecision(
                target_llm='DEEPSEEK_V3',
                model_config=self.model_catalog['DEEPSEEK_V3'],
                confidence=0.85,
                reason='Development task - DeepSeek V3 optimal for coding',
                estimated_cost=self._estimate_cost(user_message, self.model_catalog['DEEPSEEK_V3']),
                complexity='medium'
            )
        
        # Multilingual tasks
        multilingual_keywords = ['translate', 'language', 'multilingual', 'español', 'français']
        if any(keyword in message_lower for keyword in multilingual_keywords):
            return RoutingDecision(
                target_llm='LLAMA_3_3_70B',
                model_config=self.model_catalog['LLAMA_3_3_70B'],
                confidence=0.80,
                reason='Multilingual task - Llama 3.3 70B optimal',
                estimated_cost=self._estimate_cost(user_message, self.model_catalog['LLAMA_3_3_70B']),
                complexity='medium'
            )
        
        # Simple questions (free tier)
        simple_patterns = ['what is', 'how to', 'explain', 'define', 'tell me about']
        if (any(pattern in message_lower for pattern in simple_patterns) and 
            len(user_message.split()) < 15):
            return RoutingDecision(
                target_llm='DEEPSEEK_R1_FREE',
                model_config=self.model_catalog['DEEPSEEK_R1_FREE'],
                confidence=0.75,
                reason='Simple question - using free tier',
                estimated_cost=0.0,
                complexity='simple'
            )
        
        # Default to balanced model for general queries
        return RoutingDecision(
            target_llm='DEEPSEEK_V3',
            model_config=self.model_catalog['DEEPSEEK_V3'],
            confidence=0.70,
            reason='General query - balanced DeepSeek V3',
            estimated_cost=self._estimate_cost(user_message, self.model_catalog['DEEPSEEK_V3']),
            complexity='medium'
        )
    
    def evaluate_model_switch(self, session: ConversationSession, user_message: str) -> RoutingDecision:
        """Evaluate if we should switch models for this query in existing session"""
        message_lower = user_message.lower()
        
        # Check for explicit premium requests
        premium_requests = [
            'need claude', 'use claude', 'premium analysis', 'comprehensive review',
            'architectural analysis', 'strategic planning', 'critical evaluation'
        ]
        
        if any(request in message_lower for request in premium_requests):
            if session.primary_model.startswith('CLAUDE'):
                # Already on Claude, no switch needed
                return RoutingDecision(
                    target_llm=session.primary_model,
                    model_config=session.model_config,
                    confidence=1.0,
                    reason='Already using Claude model',
                    estimated_cost=self._estimate_cost(user_message, session.model_config),
                    complexity='high',
                    requires_switch=False
                )
            else:
                # Switch to Claude needed
                claude_model = 'CLAUDE_SONNET_4'
                estimated_cost = self._estimate_cost(user_message, self.model_catalog[claude_model])
                
                return RoutingDecision(
                    target_llm=claude_model,
                    model_config=self.model_catalog[claude_model],
                    confidence=0.95,
                    reason='Premium analysis requested - switching to Claude',
                    estimated_cost=estimated_cost,
                    complexity='high',
                    requires_switch=True,
                    switch_reason=f'Premium analysis request (Est. cost: ${estimated_cost:.3f})'
                )
        
        # No switch needed - stay with current model (sticky session)
        return RoutingDecision(
            target_llm=session.primary_model,
            model_config=session.model_config,
            confidence=0.9,
            reason='Continuing with current model (sticky session)',
            estimated_cost=self._estimate_cost(user_message, session.model_config),
            complexity='medium',
            requires_switch=False
        )
    
    def handle_model_switch(self, session: ConversationSession, user_message: str, 
                          switch_decision: RoutingDecision) -> tuple[LLMResponse, bool]:
        """Handle switching models with context transfer"""
        
        # Check if switch cost is within auto-approval threshold
        if switch_decision.estimated_cost <= self.max_switch_threshold:
            auto_approve = True
        else:
            # In real implementation, this would prompt user
            # For now, we'll auto-approve for demo
            auto_approve = True
            print(f"💰 Model switch cost: ${switch_decision.estimated_cost:.3f} (Auto-approved)")
        
        if auto_approve:
            # Prepare context transfer
            context_summary = self._prepare_context_transfer(session, user_message)
            
            # Update session to new model
            old_model = session.primary_model
            session.primary_model = switch_decision.target_llm
            session.model_config = switch_decision.model_config
            
            print(f"\n🔄 Model Switch Executed")
            print(f"   From: {old_model}")
            print(f"   To: {switch_decision.target_llm}")
            print(f"   Reason: {switch_decision.switch_reason}")
            print(f"   Context: Transferring {len(context_summary)} chars")
            
            # Execute with context transfer
            response = self.execute_with_context_transfer(session, user_message, context_summary)
            return response, True
        else:
            # Switch denied - continue with current model
            return self.execute_with_current_model(session, user_message), False
    
    def _prepare_context_transfer(self, session: ConversationSession, current_query: str) -> str:
        """Prepare compressed context for model switching"""
        if not session.conversation_history:
            return "No previous context."
        
        # Extract key information from conversation history
        key_topics = []
        decisions_made = []
        technical_context = []
        
        for entry in session.conversation_history[-10:]:  # Last 10 messages
            if entry['role'] == 'user':
                if any(word in entry['content'].lower() for word in ['project', 'build', 'create']):
                    key_topics.append(entry['content'][:100])
            elif entry['role'] == 'assistant':
                if any(word in entry['content'].lower() for word in ['recommend', 'suggest', 'solution']):
                    decisions_made.append(entry['content'][:150])
        
        context_summary = f"""
CONVERSATION CONTEXT TRANSFER:

Previous Model: {session.primary_model}
Session Cost So Far: ${session.total_cost:.3f}
Messages Exchanged: {len(session.conversation_history)}

KEY TOPICS DISCUSSED:
{chr(10).join(f"- {topic}" for topic in key_topics[-3:])}

RECENT DECISIONS/RECOMMENDATIONS:
{chr(10).join(f"- {decision}" for decision in decisions_made[-2:])}

CURRENT REQUEST:
{current_query}

Please continue this conversation naturally, maintaining consistency with the previous discussion.
"""
        
        return context_summary
    
    def execute_with_current_model(self, session: ConversationSession, user_message: str) -> LLMResponse:
        """Execute query with current session model"""
        start_time = time.time()
        
        print(f"\n🎯 Executing with Current Model")
        print(f"   Model: {session.primary_model}")
        print(f"   Session: {session.session_id}")
        print(f"   Messages in session: {len(session.conversation_history)}")
        
        try:
            if session.model_config.provider == ModelProvider.HAWKMOTH_LOCAL:
                response = self._execute_hawkmoth_local(user_message, session)
            elif session.model_config.provider == ModelProvider.TOGETHER_AI:
                response = self._execute_together_ai(user_message, session)
            elif session.model_config.provider == ModelProvider.CLAUDE_DIRECT:
                response = self._execute_claude_direct(user_message, session)
            else:
                raise ValueError(f"Unknown provider: {session.model_config.provider}")
            
            # Update session
            session.conversation_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            session.conversation_history.append({
                'role': 'assistant',
                'content': response.content,
                'timestamp': datetime.now().isoformat(),
                'model': session.primary_model,
                'cost': response.actual_cost
            })
            
            session.total_cost += response.actual_cost
            session.total_tokens += response.input_tokens + response.output_tokens
            
            response.response_time = time.time() - start_time
            response.session_id = session.session_id
            
            return response
            
        except Exception as e:
            print(f"❌ Execution Error: {e}")
            return self._create_error_response(str(e), session.session_id)
    
    def execute_with_context_transfer(self, session: ConversationSession, user_message: str, 
                                    context_summary: str) -> LLMResponse:
        """Execute query with context transfer to new model"""
        
        # Combine context summary with user message
        enhanced_message = f"{context_summary}\n\nCURRENT USER REQUEST:\n{user_message}"
        
        # Execute with the new model
        return self.execute_with_current_model(session, enhanced_message)
    
    def _execute_together_ai(self, message: str, session: ConversationSession) -> LLMResponse:
        """Execute query using Together AI API"""
        if not self.together_api_key:
            raise ValueError("Together AI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        # Build conversation history for context
        messages = []
        for entry in session.conversation_history[-20:]:  # Last 20 messages for context
            if entry['role'] in ['user', 'assistant']:
                messages.append({
                    "role": entry['role'],
                    "content": entry['content']
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": session.model_config.model_id,
            "messages": messages,
            "max_tokens": min(session.model_config.max_tokens, 2048),
            "temperature": 0.7,
            "stream": False
        }
        
        response = requests.post(self.together_base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise ValueError(f"Together AI API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract response data
        content = result['choices'][0]['message']['content']
        usage = result.get('usage', {})
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        # Calculate actual cost
        actual_cost = (
            (input_tokens / 1000) * session.model_config.cost_per_1k_input +
            (output_tokens / 1000) * session.model_config.cost_per_1k_output
        )
        
        return LLMResponse(
            content=content,
            model_used=session.model_config.model_id,
            provider=session.model_config.provider.value,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            actual_cost=actual_cost,
            response_time=0.0,
            session_id=session.session_id,
            metadata={'raw_response': result, 'session_info': session.session_id}
        )
    
    def _execute_claude_direct(self, message: str, session: ConversationSession) -> LLMResponse:
        """Execute query using Claude Direct API"""
        if not self.claude_api_key:
            raise ValueError("Claude API key not configured")
        
        headers = {
            "x-api-key": self.claude_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Build conversation history
        messages = []
        for entry in session.conversation_history[-20:]:
            if entry['role'] in ['user', 'assistant']:
                messages.append({
                    "role": entry['role'],
                    "content": entry['content']
                })
        
        messages.append({"role": "user", "content": message})
        
        payload = {
            "model": session.model_config.model_id,
            "max_tokens": min(session.model_config.max_tokens, 2048),
            "messages": messages
        }
        
        response = requests.post(self.claude_base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise ValueError(f"Claude API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract response data
        content = result['content'][0]['text']
        usage = result.get('usage', {})
        input_tokens = usage.get('input_tokens', 0)
        output_tokens = usage.get('output_tokens', 0)
        
        # Calculate actual cost
        actual_cost = (
            (input_tokens / 1000) * session.model_config.cost_per_1k_input +
            (output_tokens / 1000) * session.model_config.cost_per_1k_output
        )
        
        return LLMResponse(
            content=content,
            model_used=session.model_config.model_id,
            provider=session.model_config.provider.value,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            actual_cost=actual_cost,
            response_time=0.0,
            session_id=session.session_id,
            metadata={'raw_response': result, 'session_info': session.session_id}
        )
    
    def _execute_hawkmoth_local(self, message: str, session: ConversationSession) -> LLMResponse:
        """Execute HAWKMOTH platform commands locally"""
        message_lower = message.lower()
        
        if 'status' in message_lower:
            content = self._get_hawkmoth_status()
        elif 'session' in message_lower:
            content = self._get_session_status(session)
        elif 'deploy' in message_lower:
            content = "🚀 HAWKMOTH deployment initiated. Check UPLOAD_TO_HF/ directory."
        else:
            content = f"🦅 HAWKMOTH Command: {message}\n\nProcessed locally in session {session.session_id}"
        
        return LLMResponse(
            content=content,
            model_used="hawkmoth-local",
            provider="hawkmoth_local",
            input_tokens=len(message.split()),
            output_tokens=len(content.split()),
            actual_cost=0.0,
            response_time=0.0,
            session_id=session.session_id,
            metadata={'command_type': 'local', 'session_info': session.session_id}
        )
    
    def _get_session_status(self, session: ConversationSession) -> str:
        """Get current session status"""
        duration = datetime.now() - session.started_at
        
        return f"""🦅 HAWKMOTH Session Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Session ID: {session.session_id}
🤖 Primary Model: {session.primary_model}
⏱️  Duration: {duration.total_seconds()/60:.1f} minutes
💬 Messages: {len(session.conversation_history)}
💰 Total Cost: ${session.total_cost:.4f}
🎯 Model Lane: {self._get_model_lane(session.primary_model)}

🔧 Sticky Session Active:
   • Context preserved within {session.primary_model}
   • Switch available to Claude for premium analysis
   • Cost-efficient conversation management"""
    
    def _get_model_lane(self, model_name: str) -> str:
        """Get the lane name for a model"""
        lane_mapping = {
            'HAWKMOTH_LOCAL': 'Platform Commands',
            'DEEPSEEK_R1_FREE': 'Quick Questions (FREE)',
            'DEEPSEEK_V3': 'Development Work ($1.25)',
            'DEEPSEEK_R1': 'Complex Reasoning ($3/$7)',
            'LLAMA_3_3_70B': 'Multilingual ($0.88)',
            'CLAUDE_SONNET_4': 'Premium Analysis ($3/$15)',
            'CLAUDE_OPUS_4': 'Critical Analysis ($15/$75)'
        }
        return lane_mapping.get(model_name, 'Unknown Lane')
    
    def _get_hawkmoth_status(self) -> str:
        """Get HAWKMOTH platform status"""
        active_sessions_count = len(self.active_sessions)
        total_cost = sum(session.total_cost for session in self.active_sessions.values())
        
        return f"""🦅 HAWKMOTH LLM Teaming Platform - Sticky Sessions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Platform Status: ✅ Operational
🔄 Strategy: Sticky Sessions (Context Preservation)
📡 API Connections:
   • Claude Direct: {'✅ Connected' if self.claude_api_key else '❌ Not configured'}
   • Together AI: {'✅ Connected' if self.together_api_key else '❌ Not configured'}

💬 Active Sessions: {active_sessions_count}
💰 Total Session Cost: ${total_cost:.4f}
🎯 Switch Threshold: ${self.max_switch_threshold}

🛣️  Available Lanes:
   • Quick Questions: FREE (DeepSeek R1 Free)
   • Development: $1.25/1k (DeepSeek V3)
   • Complex Reasoning: $3/$7/1k (DeepSeek R1)
   • Multilingual: $0.88/1k (Llama 3.3 70B)
   • Premium Analysis: $3/$15/1k (Claude Sonnet 4)"""
    
    def _estimate_cost(self, message: str, model_config: ModelConfig) -> float:
        """Estimate cost for a message"""
        estimated_input_tokens = len(message.split()) * 1.3
        estimated_output_tokens = min(estimated_input_tokens * 0.5, model_config.max_tokens)
        
        input_cost = (estimated_input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (estimated_output_tokens / 1000) * model_config.cost_per_1k_output
        
        return input_cost + output_cost
    
    def _create_error_response(self, error_message: str, session_id: str) -> LLMResponse:
        """Create error response"""
        content = f"🔄 HAWKMOTH Error: {error_message}\n\nFalling back to local processing."
        
        return LLMResponse(
            content=content,
            model_used="error-fallback",
            provider="hawkmoth_local",
            input_tokens=0,
            output_tokens=len(content.split()),
            actual_cost=0.0,
            response_time=0.0,
            session_id=session_id,
            metadata={'error': True, 'error_message': error_message}
        )
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        return {
            "session_id": session.session_id,
            "primary_model": session.primary_model,
            "model_lane": self._get_model_lane(session.primary_model),
            "duration_minutes": (datetime.now() - session.started_at).total_seconds() / 60,
            "total_messages": len(session.conversation_history),
            "total_cost": session.total_cost,
            "total_tokens": session.total_tokens,
            "cost_per_message": session.total_cost / max(len(session.conversation_history), 1),
            "model_config": asdict(session.model_config)
        }

# Example usage and testing
if __name__ == "__main__":
    print("🦅 HAWKMOTH Sticky Sessions Engine - Testing")
    print("=" * 70)
    
    # Initialize the engine
    engine = HAWKMOTHStickySessionEngine()
    
    # Test conversation scenarios
    test_scenarios = [
        {
            "scenario": "Development Session",
            "messages": [
                "Help me debug this Python function",
                "Now optimize the algorithm for performance",
                "Add error handling to the code",
                "I need comprehensive architecture review"  # Should trigger switch
            ]
        },
        {
            "scenario": "Quick Questions Session", 
            "messages": [
                "What is machine learning?",
                "Explain neural networks simply",
                "How does training work?"
            ]
        },
        {
            "scenario": "Premium Analysis Session",
            "messages": [
                "I need comprehensive business strategy analysis",  # Starts with Claude
                "What are the market risks?",
                "Develop implementation roadmap"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing Scenario: {scenario['scenario']}")
        print("=" * 50)
        
        # Start session with first message
        session = engine.start_conversation_session(scenario['messages'][0])
        session_id = session.session_id
        
        # Process first message
        response, switched = engine.continue_conversation(session_id, scenario['messages'][0])
        print(f"✅ Initial Response: {response.content[:100]}...")
        
        # Continue with remaining messages
        for message in scenario['messages'][1:]:
            print(f"\n📝 User: {message}")
            response, switched = engine.continue_conversation(session_id, message)
            
            if switched:
                print(f"🔄 Model switched during this response")
            
            print(f"🤖 Response: {response.content[:100]}...")
            print(f"💰 Cost: ${response.actual_cost:.4f}")
        
        # Session summary
        summary = engine.get_session_summary(session_id)
        print(f"\n📊 Session Summary:")
        print(f"   Total Cost: ${summary['total_cost']:.4f}")
        print(f"   Messages: {summary['total_messages']}")
        print(f"   Model Lane: {summary['model_lane']}")
        print(f"   Duration: {summary['duration_minutes']:.1f} minutes")
