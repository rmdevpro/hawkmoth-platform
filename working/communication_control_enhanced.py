"""
HAWKMOTH Component 4: Enhanced Communication Control UI
Natural Language Model Selection System - Full Model Variety Support
Version: v0.0.4-enhanced
"""

import re
from typing import Dict, Tuple, Optional
from enum import Enum

class ModelType(Enum):
    # Premium Reasoning Models
    DEEPSEEK_R1 = "deepseek_r1"                    # $3/$7 per 1k - Top reasoning
    DEEPSEEK_R1_THROUGHPUT = "deepseek_r1_throughput"  # $0.55/$2.19 per 1k - Cost-efficient reasoning
    
    # General Purpose Models  
    DEEPSEEK_V3 = "deepseek_v3"                   # $1.25 per 1k - Balanced performance
    LLAMA_3_3_70B = "llama_3_3_70b"               # $0.88 per 1k - Multilingual dialogue
    
    # Cost-Efficient Models
    LLAMA_3_1_8B = "llama_3_1_8b"                 # $0.18 per 1k - Simple tasks
    DEEPSEEK_R1_FREE = "deepseek_r1_free"         # FREE - Testing and experimentation
    
    # Premium Claude Models (when available)
    CLAUDE_SONNET_4 = "claude_sonnet_4"           # $3/$15 per 1k - Premium analysis
    CLAUDE_OPUS_4 = "claude_opus_4"               # $15/$75 per 1k - Critical tasks
    
    # Platform Controls
    HAWKMOTH_LOCAL = "hawkmoth_local"             # FREE - Platform commands
    AUTO_SELECT = "auto_select"                   # Variable - Intelligent routing

class EnhancedCommunicationController:
    """
    Enhanced natural language model selection supporting full HAWKMOTH model variety.
    Detects user intent and routes to 10+ different AI models with cost optimization.
    """
    
    def __init__(self):
        self.current_model = ModelType.DEEPSEEK_V3  # Default to balanced model
        self.previous_model = ModelType.DEEPSEEK_V3
        self.switch_patterns = self._initialize_enhanced_patterns()
        self.model_info = self._initialize_model_catalog()
        
    def _initialize_enhanced_patterns(self) -> Dict[str, list]:
        """Initialize comprehensive pattern matching for all model types."""
        return {
            # Premium Reasoning Models
            'deepseek_r1_patterns': [
                r'\b(?:use|switch to|chat with) (?:deepseek )?r1\b',
                r'\b(?:reasoning|complex reasoning|advanced reasoning) model\b',
                r'\buse (?:the )?best reasoning\b',
                r'\bdeepseek r1(?:\s+model)?\b',
                r'\b(?:premium|top) reasoning\b',
                r'\bcomplex analysis model\b'
            ],
            'deepseek_r1_throughput_patterns': [
                r'\b(?:use|switch to) (?:deepseek )?r1 throughput\b',
                r'\bcost[- ]efficient reasoning\b',
                r'\bcheaper reasoning model\b',
                r'\bthroughput (?:version|model)\b',
                r'\bbatch reasoning\b'
            ],
            
            # General Purpose Models
            'deepseek_v3_patterns': [
                r'\b(?:use|switch to|chat with) (?:deepseek )?v3\b',
                r'\b(?:use|switch to) (?:local|open|free) (?:llm|model|ai)\b',
                r'\bbalanced model\b',
                r'\bgeneral purpose model\b',
                r'\bdeepseek v3\b',
                r'\bdefault model\b'
            ],
            'llama_3_3_70b_patterns': [
                r'\b(?:use|switch to|chat with) llama\b',
                r'\bmultilingual model\b',
                r'\bdialogue model\b',
                r'\bllama 3\.3\b',
                r'\bmeta llama\b',
                r'\bconversation model\b'
            ],
            
            # Cost-Efficient Models  
            'llama_3_1_8b_patterns': [
                r'\b(?:use|switch to) (?:small|lightweight|fast) model\b',
                r'\bcheap model\b',
                r'\bsimple tasks model\b',
                r'\bllama 8b\b',
                r'\bquick (?:model|llm)\b',
                r'\bcost[- ]efficient model\b'
            ],
            'deepseek_r1_free_patterns': [
                r'\b(?:use|switch to) free model\b',
                r'\bfree (?:llm|ai|model)\b',
                r'\bzero cost model\b',
                r'\bfree deepseek\b',
                r'\bno cost model\b',
                r'\btesting model\b'
            ],
            
            # Premium Claude Models
            'claude_sonnet_4_patterns': [
                r'\b(?:chat with|use|switch to|talk to) claude\b',
                r'\buse claude for this\b',
                r'\blet me talk to claude\b',
                r'\bswitch to anthropic\b',
                r'\buse anthropic\b',
                r'\bclaude please\b',
                r'\bask claude\b',
                r'\bpremium (?:ai|model)\b'
            ],
            'claude_opus_4_patterns': [
                r'\b(?:use|switch to|chat with) (?:claude )?opus\b',
                r'\bbest (?:ai|model) available\b',
                r'\btop tier model\b',
                r'\bcritical task model\b',
                r'\bmaximum (?:quality|performance)\b',
                r'\bopus model\b'
            ],
            
            # Platform Controls
            'hawkmoth_local_patterns': [
                r'\bhawkmoth (?:status|commands|local)\b',
                r'\bplatform commands?\b',
                r'\blocal hawkmoth\b',
                r'\buse hawkmoth\b'
            ],
            'auto_select_patterns': [
                r'\bauto select\b',
                r'\bchoose best model\b',
                r'\blet (?:hawkmoth|you) decide\b',
                r'\boptimal model\b',
                r'\bbest model for this\b',
                r'\bintelligent routing\b',
                r'\bautomatic selection\b'
            ],
            
            # Generic switches (context-dependent)
            'confirmation_patterns': [
                r'\byes,? (?:switch|change)\b',
                r'\bconfirm switch\b',
                r'\byes please\b',
                r'\b(?:go ahead|proceed)\b'
            ],
            'cost_patterns': [
                r'\bcheapest model\b',
                r'\blowest cost\b',
                r'\bfree option\b',
                r'\bsave (?:money|cost)\b'
            ],
            'quality_patterns': [
                r'\bbest quality\b',
                r'\bhighest quality\b',
                r'\btop performance\b',
                r'\bmaximum capability\b'
            ]
        }
    
    def _initialize_model_catalog(self) -> Dict[ModelType, Dict[str, str]]:
        """Initialize comprehensive model information catalog."""
        return {
            ModelType.DEEPSEEK_R1: {
                "name": "DeepSeek R1",
                "provider": "Together AI",
                "cost": "$3/$7 per 1k tokens",
                "icon": "🧠",
                "description": "State-of-the-art reasoning model, comparable to OpenAI o1",
                "specialties": "Complex reasoning, math, research, analysis"
            },
            ModelType.DEEPSEEK_R1_THROUGHPUT: {
                "name": "DeepSeek R1 Throughput",
                "provider": "Together AI", 
                "cost": "$0.55/$2.19 per 1k tokens",
                "icon": "⚡",
                "description": "Cost-efficient reasoning with high throughput",
                "specialties": "Batch processing, cost-efficient reasoning"
            },
            ModelType.DEEPSEEK_V3: {
                "name": "DeepSeek V3",
                "provider": "Together AI",
                "cost": "$1.25 per 1k tokens",
                "icon": "🎯",
                "description": "Latest balanced MoE model for general tasks",
                "specialties": "General tasks, coding, balanced performance"
            },
            ModelType.LLAMA_3_3_70B: {
                "name": "Llama 3.3 70B",
                "provider": "Meta/Together AI",
                "cost": "$0.88 per 1k tokens",
                "icon": "🌍",
                "description": "Multilingual dialogue-optimized model",
                "specialties": "Multilingual, dialogue, conversation"
            },
            ModelType.LLAMA_3_1_8B: {
                "name": "Llama 3.1 8B",
                "provider": "Meta/Together AI",
                "cost": "$0.18 per 1k tokens",
                "icon": "🚀",
                "description": "Lightweight model for simple tasks",
                "specialties": "Simple tasks, fast responses, cost-efficient"
            },
            ModelType.DEEPSEEK_R1_FREE: {
                "name": "DeepSeek R1 Free",
                "provider": "Together AI",
                "cost": "FREE",
                "icon": "🆓",
                "description": "Free distilled reasoning model",
                "specialties": "Free testing, experimentation, simple reasoning"
            },
            ModelType.CLAUDE_SONNET_4: {
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "cost": "$3/$15 per 1k tokens",
                "icon": "💎",
                "description": "Premium AI with advanced reasoning",
                "specialties": "Premium analysis, complex tasks, safety"
            },
            ModelType.CLAUDE_OPUS_4: {
                "name": "Claude Opus 4", 
                "provider": "Anthropic",
                "cost": "$15/$75 per 1k tokens",
                "icon": "🏆",
                "description": "Top-tier model for critical tasks",
                "specialties": "Critical tasks, maximum quality, best performance"
            },
            ModelType.HAWKMOTH_LOCAL: {
                "name": "HAWKMOTH Local",
                "provider": "HAWKMOTH",
                "cost": "FREE",
                "icon": "🏠",
                "description": "Local platform commands and operations",
                "specialties": "Platform control, status, commands"
            },
            ModelType.AUTO_SELECT: {
                "name": "Auto-Select",
                "provider": "HAWKMOTH",
                "cost": "Variable (optimized)",
                "icon": "🤖",
                "description": "Intelligent model selection based on task",
                "specialties": "Automatic routing, cost optimization"
            }
        }
    
    def parse_model_request(self, user_input: str) -> Tuple[Optional[ModelType], str, bool]:
        """
        Parse user input for enhanced model switching requests supporting all model types.
        
        Returns:
            Tuple[Optional[ModelType], str, bool]:
                - ModelType if switch detected, None otherwise
                - Confirmation message  
                - Whether this is a permanent switch (True) or one-time use (False)
        """
        user_input_lower = user_input.lower().strip()
        
        # Check each model type with comprehensive patterns
        model_checks = [
            (ModelType.DEEPSEEK_R1, 'deepseek_r1_patterns'),
            (ModelType.DEEPSEEK_R1_THROUGHPUT, 'deepseek_r1_throughput_patterns'),
            (ModelType.DEEPSEEK_V3, 'deepseek_v3_patterns'),
            (ModelType.LLAMA_3_3_70B, 'llama_3_3_70b_patterns'),
            (ModelType.LLAMA_3_1_8B, 'llama_3_1_8b_patterns'),
            (ModelType.DEEPSEEK_R1_FREE, 'deepseek_r1_free_patterns'),
            (ModelType.CLAUDE_SONNET_4, 'claude_sonnet_4_patterns'),
            (ModelType.CLAUDE_OPUS_4, 'claude_opus_4_patterns'),
            (ModelType.HAWKMOTH_LOCAL, 'hawkmoth_local_patterns'),
            (ModelType.AUTO_SELECT, 'auto_select_patterns')
        ]
        
        # Check specific model patterns first
        for model_type, pattern_key in model_checks:
            for pattern in self.switch_patterns[pattern_key]:
                if re.search(pattern, user_input_lower):
                    permanent = not ('for this' in user_input_lower or 'this time' in user_input_lower)
                    message = self._generate_enhanced_switch_message(model_type, permanent)
                    return model_type, message, permanent
        
        # Check context-dependent patterns
        if any(re.search(pattern, user_input_lower) for pattern in self.switch_patterns['cost_patterns']):
            # Route to cheapest available model
            message = self._generate_enhanced_switch_message(ModelType.DEEPSEEK_R1_FREE, True)
            return ModelType.DEEPSEEK_R1_FREE, message, True
        
        if any(re.search(pattern, user_input_lower) for pattern in self.switch_patterns['quality_patterns']):
            # Route to highest quality model
            message = self._generate_enhanced_switch_message(ModelType.CLAUDE_OPUS_4, True)
            return ModelType.CLAUDE_OPUS_4, message, True
        
        return None, "", False
    
    def _generate_enhanced_switch_message(self, target_model: ModelType, permanent: bool) -> str:
        """Generate rich confirmation message for model switch with full model info."""
        model_info = self.model_info[target_model]
        
        duration_text = "for all responses" if permanent else "for this query only"
        
        return f"""{model_info['icon']} **Switched to {model_info['name']}** ({duration_text})
💰 **Cost**: {model_info['cost']}  
🔧 **Provider**: {model_info['provider']}  
⭐ **Best for**: {model_info['specialties']}  
📝 **{model_info['description']}**"""
    
    def switch_model(self, target_model: ModelType, permanent: bool = True) -> str:
        """
        Execute enhanced model switch with full model information.
        
        Args:
            target_model: The model to switch to
            permanent: Whether this is a permanent switch or temporary
            
        Returns:
            str: Rich confirmation message with model details
        """
        if not permanent:
            # Store current model for restoration
            self.previous_model = self.current_model
        
        self.current_model = target_model
        return self._generate_enhanced_switch_message(target_model, permanent)
    
    def get_model_recommendations(self, user_input: str) -> Dict[str, ModelType]:
        """Get model recommendations based on query analysis."""
        user_input_lower = user_input.lower()
        recommendations = {}
        
        # Analyze query characteristics
        if any(keyword in user_input_lower for keyword in ['math', 'calculate', 'analyze', 'research', 'complex', 'reasoning']):
            recommendations['best_for_task'] = ModelType.DEEPSEEK_R1
            recommendations['cost_efficient'] = ModelType.DEEPSEEK_R1_THROUGHPUT
            
        elif any(keyword in user_input_lower for keyword in ['code', 'debug', 'python', 'javascript', 'programming']):
            recommendations['best_for_task'] = ModelType.DEEPSEEK_V3
            recommendations['premium_option'] = ModelType.CLAUDE_SONNET_4
            
        elif any(keyword in user_input_lower for keyword in ['translate', 'language', 'multilingual']):
            recommendations['best_for_task'] = ModelType.LLAMA_3_3_70B
            
        else:
            # General query recommendations
            recommendations['balanced'] = ModelType.DEEPSEEK_V3
            recommendations['premium'] = ModelType.CLAUDE_SONNET_4
            recommendations['cost_efficient'] = ModelType.LLAMA_3_1_8B
            recommendations['free'] = ModelType.DEEPSEEK_R1_FREE
        
        return recommendations
    
    def get_current_model_info(self) -> Dict[str, str]:
        """Get comprehensive current model information."""
        return self.model_info.get(self.current_model, {
            "name": "Unknown Model",
            "provider": "Unknown", 
            "cost": "Unknown",
            "icon": "❓",
            "description": "Model information unavailable",
            "specialties": "Unknown"
        })
    
    def get_enhanced_status_display(self) -> str:
        """Get rich formatted status for display in chat interface."""
        info = self.get_current_model_info()
        return f"{info['icon']} **{info['name']}** ({info['cost']}) - {info['description']}"
    
    def get_all_models_summary(self) -> str:
        """Get summary of all available models with costs and specialties."""
        summary = "🦅 **HAWKMOTH Available Models:**\n\n"
        
        categories = {
            "🧠 **Reasoning Models**": [ModelType.DEEPSEEK_R1, ModelType.DEEPSEEK_R1_THROUGHPUT],
            "🎯 **General Purpose**": [ModelType.DEEPSEEK_V3, ModelType.LLAMA_3_3_70B],
            "🚀 **Cost-Efficient**": [ModelType.LLAMA_3_1_8B, ModelType.DEEPSEEK_R1_FREE],
            "💎 **Premium (Claude)**": [ModelType.CLAUDE_SONNET_4, ModelType.CLAUDE_OPUS_4],
            "🏠 **Platform**": [ModelType.HAWKMOTH_LOCAL, ModelType.AUTO_SELECT]
        }
        
        for category, models in categories.items():
            summary += f"{category}\n"
            for model in models:
                info = self.model_info[model]
                summary += f"  {info['icon']} **{info['name']}** - {info['cost']}\n"
            summary += "\n"
        
        return summary
    
    def is_model_switch_query(self, user_input: str) -> bool:
        """Enhanced check if input contains model switching intent."""
        user_input_lower = user_input.lower()
        
        # Check all pattern categories
        all_patterns = []
        for pattern_list in self.switch_patterns.values():
            all_patterns.extend(pattern_list)
        
        for pattern in all_patterns:
            if re.search(pattern, user_input_lower):
                return True
        
        return False

# Global enhanced instance for the application
enhanced_communication_controller = EnhancedCommunicationController()

# Test function for enhanced communication control
def test_enhanced_communication_control():
    """Test the enhanced communication control with full model variety."""
    controller = EnhancedCommunicationController()
    
    test_cases = [
        "Use DeepSeek R1 for complex reasoning",
        "Switch to cost-efficient reasoning model",
        "Chat with Claude about this analysis",
        "Use the free model for testing",
        "Switch to Llama for multilingual support",
        "Use the cheapest model available",
        "Give me the best quality response",
        "Let HAWKMOTH decide the optimal model",
        "Use Claude Opus for this critical task",
        "Switch to local model for coding",
        "Regular question without model switching"
    ]
    
    print("🧪 Testing Enhanced Communication Control Patterns:")
    print("=" * 60)
    
    for test_input in test_cases:
        model_type, message, permanent = controller.parse_model_request(test_input)
        
        print(f"Input: '{test_input}'")
        print(f"Detected: {model_type}")
        if model_type:
            print(f"Model Info: {controller.model_info[model_type]['name']}")
            print(f"Cost: {controller.model_info[model_type]['cost']}")
        print(f"Permanent: {permanent}")
        print("-" * 40)
    
    print("\n📊 Model Recommendations Test:")
    print("=" * 60)
    
    test_queries = [
        "Calculate the derivative of this complex function",
        "Debug this Python code that's crashing",
        "Translate this text into Spanish and French",
        "Write a simple hello world program"
    ]
    
    for query in test_queries:
        recommendations = controller.get_model_recommendations(query)
        print(f"Query: {query}")
        print(f"Recommendations: {recommendations}")
        print("-" * 40)

if __name__ == "__main__":
    test_enhanced_communication_control()
