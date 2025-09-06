# HAWKMOTH Auto-Escalation Engine - Real-time Data Detection and Model Chaining
import re
import time
import requests
from datetime import datetime, date
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

class EscalationTrigger(Enum):
    REAL_TIME_DATA = "real_time_data"
    MODEL_FAILURE = "model_failure"
    CAPABILITY_LIMIT = "capability_limit"
    USER_REQUEST = "user_request"
    COST_THRESHOLD = "cost_threshold"

@dataclass
class EscalationDecision:
    should_escalate: bool
    trigger: EscalationTrigger
    target_capability: str
    reasoning: str
    confidence: float
    estimated_cost: float = 0.0

@dataclass
class EscalationChain:
    chain_id: str
    steps: List[str]
    current_step: int
    max_retries: int
    total_cost: float
    success: bool = False

class HAWKMOTHAutoEscalationEngine:
    def __init__(self):
        # Real-time data detection patterns
        self.real_time_patterns = {
            'current_date': [
                r'\btoday\b', r'\bcurrent date\b', r'\bwhat date\b', r'\btoday\'s date\b',
                r'\bdate today\b', r'\bwhat is the date\b', r'\bwhat\'s the date\b'
            ],
            'current_time': [
                r'\bcurrent time\b', r'\bwhat time\b', r'\btime now\b', r'\btime is it\b'
            ],
            'live_data': [
                r'\bcurrent\b.*\b(price|stock|weather|news|score)\b',
                r'\blive\b.*\b(updates|data|feed)\b',
                r'\blatest\b.*\b(news|information|update)\b',
                r'\breal[- ]?time\b.*\b(data|info|update)\b'
            ],
            'recent_events': [
                r'\byesterday\b', r'\blast week\b', r'\brecent\b.*\b(news|events)\b',
                r'\bhappened today\b', r'\blatest\b.*\b(news|development)\b'
            ],
            'web_search_needed': [
                r'\bsearch for\b', r'\blook up\b', r'\bfind information about\b',
                r'\bwho is\b.*\b(recently|new|current)\b',
                r'\bwhat happened\b.*\b(today|recently|latest)\b'
            ]
        }
        
        # Model failure patterns
        self.failure_patterns = [
            r"I don't have access to",
            r"I cannot access",
            r"I don't have real-time",
            r"I cannot browse",
            r"I don't have the ability to",
            r"my knowledge cutoff",
            r"I cannot provide current",
            r"I don't have current information",
            r"I cannot retrieve live data",
            r"I'm not able to access"
        ]
        
        # Escalation chains by capability
        self.escalation_chains = {
            'real_time_data': ['DEEPSEEK_V3', 'CLAUDE_SONNET_4', 'WEB_SEARCH'],
            'complex_analysis': ['DEEPSEEK_R1', 'CLAUDE_SONNET_4', 'CLAUDE_OPUS_4'],
            'web_capabilities': ['CLAUDE_SONNET_4', 'WEB_SEARCH'],
            'current_events': ['WEB_SEARCH'],
            'premium_analysis': ['CLAUDE_SONNET_4', 'CLAUDE_OPUS_4']
        }
        
        # Cost thresholds for auto-approval
        self.auto_approval_threshold = 5.0  # Auto-approve escalations under $5
        
        print("🔄 HAWKMOTH Auto-Escalation Engine initialized")
        print(f"   • Real-time detection patterns: {len(sum(self.real_time_patterns.values(), []))}")
        print(f"   • Failure patterns: {len(self.failure_patterns)}")
        print(f"   • Escalation chains: {len(self.escalation_chains)}")
    
    def detect_escalation_need(self, user_query: str, model_response: str = None) -> EscalationDecision:
        """Detect if query needs escalation based on content or model response"""
        
        # Check for real-time data needs in user query
        real_time_check = self._detect_real_time_needs(user_query)
        if real_time_check.should_escalate:
            return real_time_check
        
        # Check for model failure patterns in response
        if model_response:
            failure_check = self._detect_model_failure(model_response)
            if failure_check.should_escalate:
                return failure_check
        
        # Check for capability limits
        capability_check = self._detect_capability_limits(user_query)
        if capability_check.should_escalate:
            return capability_check
        
        # No escalation needed
        return EscalationDecision(
            should_escalate=False,
            trigger=EscalationTrigger.USER_REQUEST,
            target_capability="none",
            reasoning="No escalation triggers detected",
            confidence=0.95
        )
    
    def _detect_real_time_needs(self, query: str) -> EscalationDecision:
        """Detect if query requires real-time data"""
        query_lower = query.lower()
        
        # Check each real-time pattern category
        for category, patterns in self.real_time_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Special handling for date queries
                    if category == 'current_date':
                        return EscalationDecision(
                            should_escalate=True,
                            trigger=EscalationTrigger.REAL_TIME_DATA,
                            target_capability="current_date",
                            reasoning=f"Query requires current date information: '{pattern}' matched",
                            confidence=0.95,
                            estimated_cost=0.0  # Date is free
                        )
                    
                    # General real-time data
                    return EscalationDecision(
                        should_escalate=True,
                        trigger=EscalationTrigger.REAL_TIME_DATA,
                        target_capability="real_time_data",
                        reasoning=f"Query requires real-time data: '{pattern}' in category '{category}'",
                        confidence=0.90,
                        estimated_cost=0.05  # Web search cost
                    )
        
        return EscalationDecision(
            should_escalate=False,
            trigger=EscalationTrigger.REAL_TIME_DATA,
            target_capability="none",
            reasoning="No real-time data patterns detected",
            confidence=0.8
        )
    
    def _detect_model_failure(self, model_response: str) -> EscalationDecision:
        """Detect model failure patterns in response"""
        response_lower = model_response.lower()
        
        for pattern in self.failure_patterns:
            if re.search(pattern.lower(), response_lower):
                return EscalationDecision(
                    should_escalate=True,
                    trigger=EscalationTrigger.MODEL_FAILURE,
                    target_capability="web_capabilities",
                    reasoning=f"Model failure detected: '{pattern}' found in response",
                    confidence=0.95,
                    estimated_cost=0.10  # Web search + processing
                )
        
        return EscalationDecision(
            should_escalate=False,
            trigger=EscalationTrigger.MODEL_FAILURE,
            target_capability="none",
            reasoning="No failure patterns detected in response",
            confidence=0.9
        )
    
    def _detect_capability_limits(self, query: str) -> EscalationDecision:
        """Detect if query exceeds normal model capabilities"""
        query_lower = query.lower()
        
        # Premium analysis indicators
        premium_indicators = [
            'comprehensive analysis', 'strategic review', 'executive summary',
            'in-depth analysis', 'detailed evaluation', 'thorough assessment'
        ]
        
        for indicator in premium_indicators:
            if indicator in query_lower:
                return EscalationDecision(
                    should_escalate=True,
                    trigger=EscalationTrigger.CAPABILITY_LIMIT,
                    target_capability="premium_analysis",
                    reasoning=f"Premium analysis capability needed: '{indicator}' detected",
                    confidence=0.85,
                    estimated_cost=5.0  # Claude Sonnet cost
                )
        
        return EscalationDecision(
            should_escalate=False,
            trigger=EscalationTrigger.CAPABILITY_LIMIT,
            target_capability="none",
            reasoning="Query within normal model capabilities",
            confidence=0.8
        )
    
    def create_escalation_chain(self, escalation_decision: EscalationDecision) -> EscalationChain:
        """Create escalation chain based on decision"""
        
        # Get appropriate escalation chain
        chain_steps = self.escalation_chains.get(
            escalation_decision.target_capability, 
            ['CLAUDE_SONNET_4', 'WEB_SEARCH']  # Default chain
        )
        
        chain_id = f"escalation_{int(time.time())}_{escalation_decision.trigger.value}"
        
        return EscalationChain(
            chain_id=chain_id,
            steps=chain_steps,
            current_step=0,
            max_retries=len(chain_steps),
            total_cost=0.0
        )
    
    def execute_escalation_step(self, chain: EscalationChain, query: str) -> Dict[str, Any]:
        """Execute current step in escalation chain"""
        
        if chain.current_step >= len(chain.steps):
            return {
                'success': False,
                'error': 'Escalation chain exhausted',
                'final_step': True
            }
        
        current_step = chain.steps[chain.current_step]
        
        print(f"🔄 Executing escalation step {chain.current_step + 1}/{len(chain.steps)}: {current_step}")
        
        try:
            if current_step == 'WEB_SEARCH':
                return self._execute_web_search(query)
            elif current_step == 'CLAUDE_SONNET_4':
                return self._execute_claude_escalation(query)
            elif current_step.startswith('DEEPSEEK'):
                return self._execute_deepseek_escalation(query, current_step)
            else:
                return {
                    'success': False,
                    'error': f'Unknown escalation step: {current_step}',
                    'step': current_step
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Escalation step failed: {str(e)}',
                'step': current_step
            }
    
    def _execute_web_search(self, query: str) -> Dict[str, Any]:
        """Execute web search escalation"""
        
        # Special handling for date queries
        if any(pattern in query.lower() for pattern in ['date', 'today', 'current date']):
            current_date = datetime.now().strftime("%B %d, %Y")
            current_day = datetime.now().strftime("%A")
            
            return {
                'success': True,
                'response': f"Today is {current_day}, {current_date}.",
                'method': 'local_date',
                'cost': 0.0,
                'escalation_successful': True
            }
        
        # For other queries, indicate web search would be used
        return {
            'success': True,
            'response': f"🔍 **Web Search Result**: This query would be handled by web search in production. Query: '{query}'",
            'method': 'web_search_placeholder',
            'cost': 0.05,
            'escalation_successful': True
        }
    
    def _execute_claude_escalation(self, query: str) -> Dict[str, Any]:
        """Execute Claude escalation (placeholder)"""
        return {
            'success': True,
            'response': f"🧠 **Claude Escalation**: This query would be processed by Claude Sonnet 4 for premium analysis. Query: '{query}'",
            'method': 'claude_placeholder',
            'cost': 3.0,
            'escalation_successful': True
        }
    
    def _execute_deepseek_escalation(self, query: str, model: str) -> Dict[str, Any]:
        """Execute DeepSeek escalation (placeholder)"""
        return {
            'success': True,
            'response': f"🤖 **{model} Escalation**: This query would be processed by {model} for enhanced capabilities. Query: '{query}'",
            'method': 'deepseek_placeholder',
            'cost': 1.25,
            'escalation_successful': True
        }
    
    def handle_escalation_chain(self, query: str, escalation_decision: EscalationDecision) -> Dict[str, Any]:
        """Handle complete escalation chain execution"""
        
        chain = self.create_escalation_chain(escalation_decision)
        
        print(f"\n🚀 Starting Escalation Chain")
        print(f"   Chain ID: {chain.chain_id}")
        print(f"   Trigger: {escalation_decision.trigger.value}")
        print(f"   Target: {escalation_decision.target_capability}")
        print(f"   Steps: {' → '.join(chain.steps)}")
        
        # Execute escalation steps
        for step_num in range(len(chain.steps)):
            chain.current_step = step_num
            
            result = self.execute_escalation_step(chain, query)
            chain.total_cost += result.get('cost', 0.0)
            
            if result.get('success') and result.get('escalation_successful'):
                chain.success = True
                
                print(f"✅ Escalation successful at step {step_num + 1}: {chain.steps[step_num]}")
                
                return {
                    'success': True,
                    'response': result['response'],
                    'escalation_info': {
                        'chain_id': chain.chain_id,
                        'trigger': escalation_decision.trigger.value,
                        'successful_step': chain.steps[step_num],
                        'total_steps': step_num + 1,
                        'total_cost': chain.total_cost,
                        'reasoning': escalation_decision.reasoning
                    }
                }
            else:
                print(f"❌ Step {step_num + 1} failed: {result.get('error', 'Unknown error')}")
        
        # All steps failed
        return {
            'success': False,
            'response': f"🔄 Escalation chain failed after {len(chain.steps)} attempts. Unable to process query: '{query}'",
            'escalation_info': {
                'chain_id': chain.chain_id,
                'trigger': escalation_decision.trigger.value,
                'failed_steps': chain.steps,
                'total_cost': chain.total_cost,
                'reasoning': escalation_decision.reasoning
            }
        }
    
    def should_auto_approve_escalation(self, escalation_decision: EscalationDecision) -> bool:
        """Determine if escalation should be auto-approved"""
        
        # Auto-approve if under cost threshold
        if escalation_decision.estimated_cost <= self.auto_approval_threshold:
            return True
        
        # Auto-approve real-time data requests (usually low cost)
        if escalation_decision.trigger == EscalationTrigger.REAL_TIME_DATA:
            return True
        
        # Auto-approve model failures (need to provide answer)
        if escalation_decision.trigger == EscalationTrigger.MODEL_FAILURE:
            return True
        
        return False
    
    def get_escalation_stats(self) -> Dict[str, Any]:
        """Get escalation engine statistics"""
        return {
            'real_time_patterns': len(sum(self.real_time_patterns.values(), [])),
            'failure_patterns': len(self.failure_patterns),
            'escalation_chains': len(self.escalation_chains),
            'auto_approval_threshold': self.auto_approval_threshold,
            'capabilities': list(self.escalation_chains.keys())
        }
