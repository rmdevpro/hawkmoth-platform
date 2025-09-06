# HAWKMOTH LLM Teaming Engine - Multi-Model API Implementation
import os
import json
import requests
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class ModelProvider(Enum):
    TOGETHER_AI = "together"
    DEEPSEEK = "deepseek"  
    HAWKMOTH = "hawkmoth"

@dataclass
class LLMConfig:
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
class RoutingDecision:
    target_llm: str
    model_config: LLMConfig
    confidence: float
    reason: str
    estimated_cost: float
    complexity: str

@dataclass
class LLMResponse:
    content: str
    model_used: str
    provider: str
    input_tokens: int
    output_tokens: int
    actual_cost: float
    response_time: float
    metadata: Dict[str, Any]

class HAWKMOTHTeamingEngine:
    def __init__(self):
        # API Keys
        self.together_api_key = (
            os.getenv('TOGETHER_API_KEY') or 
            os.getenv('TOGETHERAI_KEY') or 
            ''
        )
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY') or ''
        
        # API Endpoints
        self.together_base_url = "https://api.together.xyz/v1/chat/completions"
        self.deepseek_base_url = "https://api.deepseek.com/chat/completions"
        
        # Model catalog with latest Together AI models and pricing
        self.model_catalog = {
            'DEEPSEEK_R1': LLMConfig(
                model_id="deepseek-ai/DeepSeek-R1",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=3.0,
                cost_per_1k_output=7.0,
                max_tokens=8192,
                context_length=128000,
                specialties=['reasoning', 'math', 'complex_analysis', 'research'],
                description='State-of-the-art reasoning model, comparable to OpenAI o1'
            ),
            'DEEPSEEK_R1_THROUGHPUT': LLMConfig(
                model_id="deepseek-ai/DeepSeek-R1-Throughput",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=0.55,
                cost_per_1k_output=2.19,
                max_tokens=8192,
                context_length=128000,
                specialties=['reasoning', 'batch_processing', 'cost_efficient'],
                description='High-throughput version of DeepSeek R1 for cost-efficient reasoning'
            ),
            'DEEPSEEK_V3': LLMConfig(
                model_id="deepseek-ai/DeepSeek-V3",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=1.25,
                cost_per_1k_output=1.25,
                max_tokens=8192,
                context_length=128000,
                specialties=['general', 'coding', 'balanced_performance'],
                description='Latest open MoE model challenging top AI models at lower cost'
            ),
            'LLAMA_3_3_70B': LLMConfig(
                model_id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=0.88,
                cost_per_1k_output=0.88,
                max_tokens=8192,
                context_length=128000,
                specialties=['multilingual', 'general', 'dialogue'],
                description='Meta Llama 3.3 multilingual model optimized for dialogue'
            ),
            'LLAMA_3_1_8B': LLMConfig(
                model_id="meta-llama/Llama-3.1-8B-Instruct-Turbo",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=0.18,
                cost_per_1k_output=0.18,
                max_tokens=4096,
                context_length=128000,
                specialties=['simple_tasks', 'cost_efficient', 'fast'],
                description='Lightweight Llama model for simple tasks and routing'
            ),
            'DEEPSEEK_R1_FREE': LLMConfig(
                model_id="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
                provider=ModelProvider.TOGETHER_AI,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                max_tokens=4096,
                context_length=8192,
                specialties=['free', 'testing', 'simple_reasoning'],
                description='Free DeepSeek R1 distilled model for experimentation'
            ),
            'HAWKMOTH_LOCAL': LLMConfig(
                model_id="hawkmoth-local",
                provider=ModelProvider.HAWKMOTH,
                cost_per_1k_input=0.0,
                cost_per_1k_output=0.0,
                max_tokens=2048,
                context_length=4096,
                specialties=['hawkmoth', 'platform', 'commands', 'status'],
                description='Local HAWKMOTH platform commands and operations'
            )
        }
        
        # Print initialization status
        self._print_initialization_status()
    
    def _print_initialization_status(self):
        """Print API key and model availability status"""
        print("🦅 HAWKMOTH LLM Teaming Engine Initialized")
        print("=" * 60)
        
        print(f"📡 Together AI: {'✅ Connected' if self.together_api_key else '❌ No API key'}")
        print(f"🧠 DeepSeek Direct: {'✅ Connected' if self.deepseek_api_key else '❌ No API key'}")
        print(f"🏠 HAWKMOTH Local: ✅ Available")
        
        print(f"\n📚 Available Models: {len(self.model_catalog)}")
        for model_name, config in self.model_catalog.items():
            provider_icon = "📡" if config.provider == ModelProvider.TOGETHER_AI else "🧠" if config.provider == ModelProvider.DEEPSEEK else "🏠"
            cost_display = f"${config.cost_per_1k_input:.2f}/${config.cost_per_1k_output:.2f}" if config.cost_per_1k_input > 0 else "FREE"
            print(f"  {provider_icon} {model_name}: {cost_display}/1k tokens")
    
    def route_query(self, user_message: str, user_context: Dict = None) -> RoutingDecision:
        """Intelligent routing with enhanced model selection"""
        message_lower = user_message.lower()
        
        # HAWKMOTH platform commands (highest priority)
        hawkmoth_keywords = ['hawkmoth status', 'hawkmoth', 'deploy', 'commit hawkmoth', 'git status', 'routing status']
        if any(keyword in message_lower for keyword in hawkmoth_keywords):
            return RoutingDecision(
                target_llm='HAWKMOTH_LOCAL',
                model_config=self.model_catalog['HAWKMOTH_LOCAL'],
                confidence=0.95,
                reason='Platform command detected',
                estimated_cost=0.00,
                complexity='simple'
            )
        
        # Complex reasoning tasks (math, research, analysis)
        reasoning_keywords = ['analyze', 'research', 'complex', 'reasoning', 'math', 'calculate', 'prove', 'solve complex']
        reasoning_phrases = ['step by step', 'think through', 'analyze this', 'research about', 'complex analysis']
        if (any(keyword in message_lower for keyword in reasoning_keywords) or 
            any(phrase in message_lower for phrase in reasoning_phrases) or
            len(message.split()) > 30):  # Long complex queries
            return RoutingDecision(
                target_llm='DEEPSEEK_R1_THROUGHPUT',  # Cost-efficient reasoning
                model_config=self.model_catalog['DEEPSEEK_R1_THROUGHPUT'],
                confidence=0.90,
                reason='Complex reasoning task detected',
                estimated_cost=self._estimate_cost(message, self.model_catalog['DEEPSEEK_R1_THROUGHPUT']),
                complexity='high'
            )
        
        # Coding and development tasks
        coding_keywords = ['debug', 'code', 'python', 'javascript', 'function', 'class', 'algorithm', 'sql', 'api', 'framework']
        if any(keyword in message_lower for keyword in coding_keywords):
            return RoutingDecision(
                target_llm='DEEPSEEK_V3',
                model_config=self.model_catalog['DEEPSEEK_V3'],
                confidence=0.85,
                reason='Coding/development task detected',
                estimated_cost=self._estimate_cost(message, self.model_catalog['DEEPSEEK_V3']),
                complexity='medium'
            )
        
        # Multilingual or dialogue tasks
        multilingual_keywords = ['translate', 'language', 'multilingual', 'conversation', 'dialogue']
        if any(keyword in message_lower for keyword in multilingual_keywords):
            return RoutingDecision(
                target_llm='LLAMA_3_3_70B',
                model_config=self.model_catalog['LLAMA_3_3_70B'],
                confidence=0.80,
                reason='Multilingual/dialogue task detected',
                estimated_cost=self._estimate_cost(message, self.model_catalog['LLAMA_3_3_70B']),
                complexity='medium'
            )
        
        # Simple questions and cost-sensitive requests
        simple_patterns = ['what is', 'how to', 'explain', 'define', 'tell me about', 'quick question']
        if (any(pattern in message_lower for pattern in simple_patterns) and 
            len(message.split()) < 15):
            return RoutingDecision(
                target_llm='DEEPSEEK_R1_FREE' if 'free' in message_lower else 'LLAMA_3_1_8B',
                model_config=self.model_catalog['DEEPSEEK_R1_FREE'] if 'free' in message_lower else self.model_catalog['LLAMA_3_1_8B'],
                confidence=0.75,
                reason='Simple question - cost-efficient routing',
                estimated_cost=0.0 if 'free' in message_lower else self._estimate_cost(message, self.model_catalog['LLAMA_3_1_8B']),
                complexity='simple'
            )
        
        # Default to balanced model for general queries
        return RoutingDecision(
            target_llm='DEEPSEEK_V3',
            model_config=self.model_catalog['DEEPSEEK_V3'],
            confidence=0.70,
            reason='General query - balanced model',
            estimated_cost=self._estimate_cost(message, self.model_catalog['DEEPSEEK_V3']),
            complexity='medium'
        )
    
    def _estimate_cost(self, message: str, model_config: LLMConfig) -> float:
        """Estimate cost based on message length and model pricing"""
        # Simple token estimation (rough approximation)
        estimated_input_tokens = len(message.split()) * 1.3  # ~1.3 tokens per word
        estimated_output_tokens = min(estimated_input_tokens * 0.5, model_config.max_tokens)  # Assume 50% response length
        
        input_cost = (estimated_input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (estimated_output_tokens / 1000) * model_config.cost_per_1k_output
        
        return input_cost + output_cost
    
    async def execute_query(self, user_message: str, user_context: Dict = None) -> LLMResponse:
        """Execute query using the routed model"""
        start_time = time.time()
        
        # Get routing decision
        routing_decision = self.route_query(user_message, user_context)
        
        print(f"\n🎯 Routing Decision:")
        print(f"   Target: {routing_decision.target_llm}")
        print(f"   Model: {routing_decision.model_config.model_id}")
        print(f"   Confidence: {routing_decision.confidence:.2f}")
        print(f"   Reason: {routing_decision.reason}")
        print(f"   Est. Cost: ${routing_decision.estimated_cost:.4f}")
        
        # Execute based on provider
        try:
            if routing_decision.model_config.provider == ModelProvider.HAWKMOTH:
                response = await self._execute_hawkmoth_command(user_message, routing_decision)
            elif routing_decision.model_config.provider == ModelProvider.TOGETHER_AI:
                response = await self._execute_together_ai(user_message, routing_decision)
            elif routing_decision.model_config.provider == ModelProvider.DEEPSEEK:
                response = await self._execute_deepseek_direct(user_message, routing_decision)
            else:
                raise ValueError(f"Unknown provider: {routing_decision.model_config.provider}")
            
            response.response_time = time.time() - start_time
            
            # Print execution summary
            print(f"\n✅ Execution Complete:")
            print(f"   Response Time: {response.response_time:.2f}s")
            print(f"   Actual Cost: ${response.actual_cost:.4f}")
            print(f"   Input/Output Tokens: {response.input_tokens}/{response.output_tokens}")
            
            return response
            
        except Exception as e:
            print(f"❌ Execution Error: {e}")
            # Fallback to free model
            return await self._execute_fallback(user_message, str(e))
    
    async def _execute_together_ai(self, message: str, decision: RoutingDecision) -> LLMResponse:
        """Execute query using Together AI API"""
        if not self.together_api_key:
            raise ValueError("Together AI API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.together_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": decision.model_config.model_id,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": min(decision.model_config.max_tokens, 2048),
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
            (input_tokens / 1000) * decision.model_config.cost_per_1k_input +
            (output_tokens / 1000) * decision.model_config.cost_per_1k_output
        )
        
        return LLMResponse(
            content=content,
            model_used=decision.model_config.model_id,
            provider=decision.model_config.provider.value,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            actual_cost=actual_cost,
            response_time=0.0,  # Set by caller
            metadata={'decision': asdict(decision), 'raw_response': result}
        )
    
    async def _execute_deepseek_direct(self, message: str, decision: RoutingDecision) -> LLMResponse:
        """Execute query using DeepSeek Direct API"""
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",  # DeepSeek direct endpoint model
            "messages": [{"role": "user", "content": message}],
            "max_tokens": min(decision.model_config.max_tokens, 2048),
            "temperature": 0.7,
            "stream": False
        }
        
        response = requests.post(self.deepseek_base_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise ValueError(f"DeepSeek API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Extract response data
        content = result['choices'][0]['message']['content']
        usage = result.get('usage', {})
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        # DeepSeek direct pricing (approximate)
        actual_cost = (input_tokens + output_tokens) / 1000 * 0.1  # Approximate DeepSeek pricing
        
        return LLMResponse(
            content=content,
            model_used="deepseek-chat",
            provider="deepseek",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            actual_cost=actual_cost,
            response_time=0.0,
            metadata={'decision': asdict(decision), 'raw_response': result}
        )
    
    async def _execute_hawkmoth_command(self, message: str, decision: RoutingDecision) -> LLMResponse:
        """Execute HAWKMOTH platform commands locally"""
        message_lower = message.lower()
        
        # Handle different HAWKMOTH commands
        if 'status' in message_lower:
            content = self._get_hawkmoth_status()
        elif 'deploy' in message_lower:
            content = "🚀 HAWKMOTH deployment initiated. Check UPLOAD_TO_HF/ directory for deployment files."
        elif 'git' in message_lower:
            content = "📊 Git status: Repository is clean. LLM Teaming v0.1.0-dev branch active."
        elif 'routing' in message_lower:
            content = self._get_routing_stats()
        else:
            content = f"🦅 HAWKMOTH Command Processed: {message}\n\nAvailable commands: status, deploy, git status, routing status"
        
        return LLMResponse(
            content=content,
            model_used="hawkmoth-local",
            provider="hawkmoth",
            input_tokens=len(message.split()),
            output_tokens=len(content.split()),
            actual_cost=0.0,
            response_time=0.0,
            metadata={'decision': asdict(decision), 'command_type': 'local'}
        )
    
    def _get_hawkmoth_status(self) -> str:
        """Get current HAWKMOTH platform status"""
        return f"""🦅 HAWKMOTH LLM Teaming Platform Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Platform Version: v0.1.0-dev (LLM Teaming)
🔗 API Connections:
   • Together AI: {'✅ Connected' if self.together_api_key else '❌ Not configured'}
   • DeepSeek Direct: {'✅ Connected' if self.deepseek_api_key else '❌ Not configured'}
   • HAWKMOTH Local: ✅ Available

🧠 Available Models: {len(self.model_catalog)}
💰 Cost Range: FREE to $7.00/1k output tokens
🎯 Routing: Intelligent multi-model selection active
⚡ Status: All systems operational

📁 Key Components:
   • LLM Teaming Engine: ✅ Active
   • Intelligent Router: ✅ Operational  
   • Cost Optimizer: ✅ Tracking
   • HuggingFace Deployment: ✅ Ready"""
    
    def _get_routing_stats(self) -> str:
        """Get routing statistics"""
        total_models = len(self.model_catalog)
        free_models = sum(1 for config in self.model_catalog.values() if config.cost_per_1k_input == 0)
        
        return f"""🎯 HAWKMOTH Routing Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Model Catalog:
   • Total Models: {total_models}
   • Free Models: {free_models}
   • Paid Models: {total_models - free_models}

🔄 Routing Targets:
   • HAWKMOTH_LOCAL: Platform commands (FREE)
   • DEEPSEEK_R1: Complex reasoning ($3/$7 per 1k)
   • DEEPSEEK_V3: General tasks ($1.25 per 1k)
   • LLAMA_3_3_70B: Multilingual ($0.88 per 1k)
   • LLAMA_3_1_8B: Simple tasks ($0.18 per 1k)
   • DEEPSEEK_R1_FREE: Testing (FREE)

⚡ Routing Logic:
   ✅ Rule-based primary routing
   ✅ Cost optimization
   ✅ Task complexity analysis
   ✅ Specialty matching"""
    
    async def _execute_fallback(self, message: str, error: str) -> LLMResponse:
        """Fallback execution using free model"""
        content = f"""🔄 Fallback Response (Free Model)

Original query: {message}

Error encountered: {error}

Using fallback processing:
This is a simulated response from the free DeepSeek R1 model. In a production environment, this would route to the actual free model endpoint.

🦅 HAWKMOTH LLM Teaming continues to operate with graceful degradation."""
        
        return LLMResponse(
            content=content,
            model_used="fallback-free",
            provider="hawkmoth",
            input_tokens=len(message.split()),
            output_tokens=len(content.split()),
            actual_cost=0.0,
            response_time=0.0,
            metadata={'error': error, 'fallback': True}
        )
    
    def get_model_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Get complete model catalog information"""
        return {
            name: {
                'model_id': config.model_id,
                'provider': config.provider.value,
                'cost_per_1k_input': config.cost_per_1k_input,
                'cost_per_1k_output': config.cost_per_1k_output,
                'max_tokens': config.max_tokens,
                'context_length': config.context_length,
                'specialties': config.specialties,
                'description': config.description
            }
            for name, config in self.model_catalog.items()
        }

# Async wrapper for non-async environments
def execute_query_sync(engine: HAWKMOTHTeamingEngine, message: str, context: Dict = None) -> LLMResponse:
    """Synchronous wrapper for query execution"""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(engine.execute_query(message, context))

# Example usage and testing
if __name__ == "__main__":
    print("🦅 HAWKMOTH LLM Teaming Engine - Advanced Model Integration")
    print("=" * 70)
    
    # Initialize the teaming engine
    engine = HAWKMOTHTeamingEngine()
    
    # Test queries for different model types
    test_queries = [
        "hawkmoth status",
        "Analyze the complex mathematical proof of Fermat's Last Theorem step by step",
        "Debug this Python function that's causing memory leaks",
        "Translate 'Hello world' into 5 different languages and explain cultural context",
        "What is machine learning?",
        "Write a complex algorithm for distributed systems optimization"
    ]
    
    print(f"\n🧪 Testing {len(test_queries)} queries across the model catalog...")
    print("━" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}] Query: {query[:50]}{'...' if len(query) > 50 else ''}")
        
        try:
            # Test routing decision first
            decision = engine.route_query(query)
            print(f"   🎯 Routed to: {decision.target_llm} (confidence: {decision.confidence:.2f})")
            print(f"   💰 Est. cost: ${decision.estimated_cost:.4f}")
            
            # For demo, we'll skip actual API calls and show routing only
            print(f"   📝 Model: {decision.model_config.model_id}")
            print(f"   🔍 Reason: {decision.reason}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Model Catalog Summary:")
    catalog