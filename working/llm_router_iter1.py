# HAWKMOTH LLM Router - Together AI Integration
import os
import json
import requests
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class RoutingDecision:
    target_llm: str
    confidence: float
    reason: str
    estimated_cost: float
    complexity: str

class HAWKMOTHRouter:
    def __init__(self):
        self.together_api_key = os.getenv('TOGETHER_API_KEY', '')
        self.together_base_url = "https://api.together.xyz/v1/chat/completions"
        self.fallback_enabled = True
        
        # Routing targets
        self.targets = {
            'CLAUDE': {
                'description': 'Complex coding, debugging, architecture, technical analysis',
                'cost_per_1k': 0.50,  # Approximate
                'specialties': ['python', 'javascript', 'debugging', 'architecture', 'algorithms']
            },
            'GPT4': {
                'description': 'Graphics, design, creative writing, general conversation',
                'cost_per_1k': 0.30,  # Approximate  
                'specialties': ['design', 'graphics', 'creative', 'writing', 'general']
            },
            'HAWKMOTH': {
                'description': 'Platform commands, deployment, git operations, status',
                'cost_per_1k': 0.00,  # Local processing
                'specialties': ['hawkmoth', 'deploy', 'git', 'status', 'platform']
            },
            'ROUTER': {
                'description': 'Simple Q&A, routing decisions, basic help',
                'cost_per_1k': 0.02,  # Together AI routing cost
                'specialties': ['help', 'simple', 'basic', 'info']
            }
        }
    
    def route_query(self, user_message: str, user_context: Dict = None) -> RoutingDecision:
        """Route user query to the most appropriate LLM"""
        try:
            # First try rule-based routing (fast and free)
            rule_decision = self._rule_based_routing(user_message)
            if rule_decision.confidence > 0.8:
                return rule_decision
            
            # Use LLM routing for complex cases
            if self.together_api_key:
                llm_decision = self._llm_based_routing(user_message, user_context)
                if llm_decision:
                    return llm_decision
            
            # Fallback to rule-based if LLM fails
            return rule_decision
            
        except Exception as e:
            # Ultimate fallback
            return RoutingDecision(
                target_llm='GPT4',
                confidence=0.5,
                reason=f'Fallback due to routing error: {str(e)}',
                estimated_cost=0.30,
                complexity='unknown'
            )
    
    def _rule_based_routing(self, message: str) -> RoutingDecision:
        """Fast rule-based routing for common patterns"""
        message_lower = message.lower()
        
        # HAWKMOTH platform commands (highest priority)
        hawkmoth_keywords = ['hawkmoth status', 'hawkmoth', 'deploy', 'commit hawkmoth', 'improve hawkmoth', 'git status']
        if any(keyword in message_lower for keyword in hawkmoth_keywords):
            return RoutingDecision(
                target_llm='HAWKMOTH',
                confidence=0.95,
                reason='Platform command detected',
                estimated_cost=0.00,
                complexity='simple'
            )
        
        # Coding/development (high confidence patterns)
        coding_keywords = ['debug', 'code', 'python', 'javascript', 'function', 'class', 'algorithm', 'sql', 'api', 'framework']
        coding_phrases = ['fix this', 'error in', 'optimize this', 'write a function', 'review this code']
        if (any(keyword in message_lower for keyword in coding_keywords) or 
            any(phrase in message_lower for phrase in coding_phrases)):
            return RoutingDecision(
                target_llm='CLAUDE',
                confidence=0.85,
                reason='Coding/development query detected',
                estimated_cost=0.50,
                complexity='medium'
            )
        
        # Design/graphics keywords
        design_keywords = ['design', 'logo', 'graphic', 'color', 'layout', 'ui', 'ux', 'visual', 'image', 'creative']
        if any(keyword in message_lower for keyword in design_keywords):
            return RoutingDecision(
                target_llm='GPT4',
                confidence=0.80,
                reason='Design/graphics query detected',
                estimated_cost=0.30,
                complexity='medium'
            )
        
        # Simple questions (route to ROUTER for cost efficiency)
        simple_patterns = ['what is', 'how to', 'explain', 'define', 'tell me about']
        if any(pattern in message_lower for pattern in simple_patterns) and len(message.split()) < 10:
            return RoutingDecision(
                target_llm='ROUTER',
                confidence=0.75,
                reason='Simple question - cost-efficient routing',
                estimated_cost=0.02,
                complexity='simple'
            )
        
        # Default to GPT4 for general queries
        return RoutingDecision(
            target_llm='GPT4',
            confidence=0.60,
            reason='General query - default routing',
            estimated_cost=0.30,
            complexity='medium'
        )
    
    def _llm_based_routing(self, message: str, user_context: Dict = None) -> Optional[RoutingDecision]:
        """Use Llama 3.1 8B for intelligent routing decisions"""
        try:
            routing_prompt = self._build_routing_prompt(message, user_context)
            
            response = requests.post(
                self.together_base_url,
                headers={
                    "Authorization": f"Bearer {self.together_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/Llama-3.1-8B-Instruct-Turbo",
                    "messages": [{"role": "user", "content": routing_prompt}],
                    "max_tokens": 150,
                    "temperature": 0.1,  # Consistent routing decisions
                    "stop": ["</decision>"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                decision_text = result['choices'][0]['message']['content']
                return self._parse_routing_decision(decision_text)
            else:
                return None
                
        except Exception as e:
            print(f"LLM routing failed: {e}")
            return None
    
    def _build_routing_prompt(self, message: str, user_context: Dict = None) -> str:
        """Build routing prompt for Llama 3.1 8B"""
        context_info = ""
        if user_context:
            context_info = f"User context: {json.dumps(user_context, indent=2)}\n"
        
        return f"""You are HAWKMOTH's routing system. Analyze this query and route to the best LLM specialist.

{context_info}
User Query: "{message}"

Available routing targets:
- CLAUDE: Complex coding, debugging, architecture, technical analysis ($0.50/1k tokens)
- GPT4: Graphics, design, creative writing, general conversation ($0.30/1k tokens)  
- HAWKMOTH: Platform commands, deployment, git operations ($0.00/1k tokens)
- ROUTER: Simple Q&A, basic help, definitions ($0.02/1k tokens)

Consider:
1. Query complexity and required expertise
2. Cost efficiency for the task
3. User's likely intent and expected response quality

Respond in this exact format:
<decision>
{{
    "target_llm": "CLAUDE",
    "confidence": 0.92,
    "reason": "Complex Python debugging requiring detailed analysis",
    "estimated_cost": 0.50,
    "complexity": "high"
}}
</decision>"""
    
    def _parse_routing_decision(self, decision_text: str) -> Optional[RoutingDecision]:
        """Parse LLM routing decision response"""
        try:
            # Extract JSON from decision tags
            start = decision_text.find('{')
            end = decision_text.rfind('}') + 1
            
            if start == -1 or end == 0:
                return None
            
            decision_data = json.loads(decision_text[start:end])
            
            return RoutingDecision(
                target_llm=decision_data.get('target_llm', 'GPT4'),
                confidence=float(decision_data.get('confidence', 0.5)),
                reason=decision_data.get('reason', 'LLM routing decision'),
                estimated_cost=float(decision_data.get('estimated_cost', 0.30)),
                complexity=decision_data.get('complexity', 'medium')
            )
            
        except Exception as e:
            print(f"Failed to parse routing decision: {e}")
            return None
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics and target information"""
        return {
            'targets': self.targets,
            'together_api_configured': bool(self.together_api_key),
            'fallback_enabled': self.fallback_enabled,
            'routing_methods': ['rule_based', 'llm_based', 'fallback']
        }
    
    def test_routing(self, test_queries: list) -> Dict[str, RoutingDecision]:
        """Test routing decisions for a list of queries"""
        results = {}
        for query in test_queries:
            results[query] = self.route_query(query)
        return results

# Example usage and testing
if __name__ == "__main__":
    router = HAWKMOTHRouter()
    
    # Test queries
    test_queries = [
        "hawkmoth status",
        "debug this Python function",
        "design a logo for my startup", 
        "what is machine learning?",
        "help me deploy this app",
        "write a complex algorithm for sorting"
    ]
    
    print("🦅 HAWKMOTH Router Testing:")
    print("=" * 50)
    
    results = router.test_routing(test_queries)
    for query, decision in results.items():
        print(f"\nQuery: {query}")
        print(f"→ Target: {decision.target_llm}")
        print(f"→ Confidence: {decision.confidence}")
        print(f"→ Reason: {decision.reason}")
        print(f"→ Cost: ${decision.estimated_cost:.3f}/1k tokens")
