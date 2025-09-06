"""
HAWKMOTH Component 4: Communication Control UI - Enhanced
Natural Language Model Selection System with Full Model Variety
Version: v0.0.4-enhanced
"""

import re
from typing import Dict, Tuple, Optional
from enum import Enum

class ModelType(Enum):
    # Premium Models
    CLAUDE_SONNET = "claude-sonnet"
    CLAUDE_OPUS = "claude-opus"
    
    # Reasoning Models
    DEEPSEEK_R1 = "deepseek-r1"
    DEEPSEEK_R1_THROUGHPUT = "deepseek-r1-throughput"
    
    # General Purpose
    DEEPSEEK_V3 = "deepseek-v3"
    LLAMA_3_3_70B = "llama-3.3-70b"
    LLAMA_3_1_8B = "llama-3.1-8b"
    
    # Free Models
    DEEPSEEK_R1_FREE = "deepseek-r1-free"
    
    # Control Options
    AUTO = "auto"
    LOCAL = "local"  # Alias for cost-optimized

class EnhancedCommunicationController:
    """
    Enhanced natural language model selection supporting full HAWKMOTH model variety.
    Detects user intent for specific model switching with rich model ecosystem.
    """
    
    def __init__(self):
        self.current_model = ModelType.DEEPSEEK_V3  # Default to balanced model
        self.previous_model = ModelType.DEEPSEEK_V3
        self.switch_patterns = self._initialize_patterns()
        self.model_info = self._initialize_model_info()
        
    def _initialize_patterns(self) -> Dict[str, list]:
        """Initialize comprehensive pattern matching for all model types."""
        return {
            # Claude Models
            'claude_sonnet_patterns': [
                r'\b(?:chat with|use|switch to|talk to) claude\b',
                r'\buse claude sonnet\b',
                r'\bswitch to claude\b',
                r'\buse anthropic\b',
                r'\bclaude please\b',
                r'\bask claude\b',
                r'\buse premium ai\b'
            ],
            'claude_opus_patterns': [
                r'\b(?:use|switch to) claude opus\b',
                r'\b(?:use|switch to) opus\b',
                r'\buse best model\b',
                r'\buse highest quality\b',
                r'\buse premium model\b',
                r'\bclaude opus please\b'
            ],
            
            # Reasoning Models
            'deepseek_r1_patterns': [
                r'\b(?:use|switch to) (?:deepseek )?r1\b',
                r'\buse reasoning model\b',
                r'\bswitch to reasoning\b',
                r'\buse deepseek r1\b',
                r'\bneed reasoning\b',
                r'\bcomplex analysis\b'
            ],
            'deepseek_r1_throughput_patterns': [
                r'\b(?:use|switch to) r1 throughput\b',
                r'\buse throughput model\b',
                r'\bcost efficient reasoning\b',
                r'\bbatch processing\b'
            ],
            
            # General Purpose Models
            'deepseek_v3_patterns': [
                r'\b(?:use|switch to) (?:deepseek )?v3\b',
                r'\buse deepseek v3\b',
                r'\bswitch to deepseek\b',
                r'\buse balanced model\b',
                r'\bgeneral purpose\b'
            ],
            'llama_3_3_patterns': [
                r'\b(?:use|switch to) llama\b',
                r'\buse llama 3\.3\b',
                r'\bswitch to meta\b',
                r'\bmultilingual model\b',
                r'\buse llama model\b'
            ],
            'llama_3_1_patterns': [
                r'\b(?:use|switch to) llama 3\.1\b',
                r'\buse small model\b',
                r'\bfast model\b',
                r'\bsimple tasks\b'
            ],
            
            # Free Models
            'free_patterns': [
                r'\b(?:use|switch to) free\b',
                r'\bfree model\b',
                r'\bno cost\b',
                r'\buse free version\b',
                r'\bswitch to free\b'
            ],
            
            # Generic Categories
            'local_patterns': [
                r'\b(?:use|switch to) local\b',
                r'\buse open source\b',
                r'\bswitch to open\b',
                r'\bcost optimized\b',
                r'\buse cheaper model\b'
            ],
            'auto_patterns': [
                r'\bauto select\b',
                r'\bchoose best model\b',
                r'\blet (?:hawkmoth|you) decide\b',
                r'\boptimal model\b',
                r'\bbest model for this\b',
                r'\bintelligent routing\b'
            ],
            'confirmation_patterns': [
                r'\byes,? (?:switch|change)\b',
                r'\bconfirm switch\b',
                r'\byes please\b',
                r'\b(?:go ahead|proceed)\b'
            ]
        }
    
    def _initialize_model_info(self) -> Dict[ModelType, Dict[str, str]]:
        """Initialize detailed model information."""
        return {
            ModelType.CLAUDE_SONNET: {
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "cost": "$3/$15 per 1k tokens",
                "icon": "🎯",
                "description": "Premium AI with advanced reasoning and analysis",
                "specialties": "Complex reasoning, analysis, writing"
            },
            ModelType.CLAUDE_OPUS: {
                "name": "Claude Opus 4", 
                "provider": "Anthropic",
                "cost": "$15/$75 per 1k tokens",
                "icon": "🏆",
                "description": "Highest quality AI for critical tasks",
                "specialties": "Critical analysis, complex research, premium quality"
            },
            ModelType.DEEPSEEK_R1: {
                "name": "DeepSeek R1",
                "provider": "Together AI",
                "cost": "$3/$7 per 1k tokens",
                "icon": "🧠",
                "description": "State-of-the-art reasoning model",
                "specialties": "Mathematical reasoning, complex analysis, research"
            },
            ModelType.DEEPSEEK_R1_THROUGHPUT: {
                "name": "DeepSeek R1 Throughput",
                "provider": "Together AI", 
                "cost": "$0.55/$2.19 per 1k tokens",
                "icon": "⚡",
                "description": "High-throughput reasoning with cost efficiency",
                "specialties": "Batch processing, cost-efficient reasoning"
            },
            ModelType.DEEPSEEK_V3: {
                "name": "DeepSeek V3",
                "provider": "Together AI",
                "cost": "$1.25/$1.25 per 1k tokens",
                "icon": "🔧",
                "description": "Latest balanced model for general tasks",
                "specialties": "General purpose, coding, balanced performance"
            },
            ModelType.LLAMA_3_3_70B: {
                "name": "Llama 3.3 70B",
                "provider": "Meta/Together AI",
                "cost": "$0.88/$0.88 per 1k tokens",
                "icon": "🌍",
                "description": "Multilingual model optimized for dialogue",
                "specialties": "Multilingual, dialogue, conversation"
            },
            ModelType.LLAMA_3_1_8B: {
                "name": "Llama 3.1 8B",
                "provider": "Meta/Together AI",
                "cost": "$0.18/$0.18 per 1k tokens",
                "icon": "🚀",
                "description": "Fast lightweight model for simple tasks",
                "specialties": "Simple tasks, fast responses, cost-efficient"
            },
            ModelType.DEEPSEEK_R1_FREE: {
                "name": "DeepSeek R1 Free",
                "provider": "Together AI",
                "cost": "FREE",
                "icon": "🆓",
                "description": "Free reasoning model for experimentation",
                "specialties": "Free access, testing, simple reasoning"
            },
            ModelType.AUTO: {
                "name": "Auto-Select",
                "provider": "HAWKMOTH",
                "cost": "Optimized routing",
                "icon": "🤖",
                "description": "Intelligent model selection based on query",
                "specialties": "Optimal routing, cost optimization, smart selection"
            },
            ModelType.LOCAL: {
                "name": "Cost-Optimized",
                "provider": "HAWKMOTH",
                "cost": "Best available price",
                "icon": "💰",
                "description": "Automatically selects most cost-effective model",
                "specialties": "Cost optimization, open-source preference"
            }
        }
    
    def parse_model_request(self, user_input: str) -> Tuple[Optional[ModelType], str, bool]:
        """
        Parse user input for specific model switching requests.
        
        Returns:
            Tuple[Optional[ModelType], str, bool]:
                - ModelType if switch detected, None otherwise
                - Confirmation message
                - Whether this is a permanent switch (True) or one-time use (False)
        """
        user_input_lower = user_input.lower().strip()
        permanent = not ('for this' in user_input_lower or 'this time' in user_input_lower)
        
        # Check for specific model patterns in priority order
        
        # Claude Models (Premium)
        for pattern in self.switch_patterns['claude_opus_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.CLAUDE_OPUS, self._generate_switch_message(ModelType.CLAUDE_OPUS, permanent), permanent
        
        for pattern in self.switch_patterns['claude_sonnet_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.CLAUDE_SONNET, self._generate_switch_message(ModelType.CLAUDE_SONNET, permanent), permanent
        
        # Reasoning Models
        for pattern in self.switch_patterns['deepseek_r1_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.DEEPSEEK_R1, self._generate_switch_message(ModelType.DEEPSEEK_R1, permanent), permanent
        
        for pattern in self.switch_patterns['deepseek_r1_throughput_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.DEEPSEEK_R1_THROUGHPUT, self._generate_switch_message(ModelType.DEEPSEEK_R1_THROUGHPUT, permanent), permanent
        
        # General Purpose Models
        for pattern in self.switch_patterns['deepseek_v3_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.DEEPSEEK_V3, self._generate_switch_message(ModelType.DEEPSEEK_V3, permanent), permanent
        
        for pattern in self.switch_patterns['llama_3_3_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.LLAMA_3_3_70B, self._generate_switch_message(ModelType.LLAMA_3_3_70B, permanent), permanent
        
        for pattern in self.switch_patterns['llama_3_1_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.LLAMA_3_1_8B, self._generate_switch_message(ModelType.LLAMA_3_1_8B, permanent), permanent
        
        # Free Models
        for pattern in self.switch_patterns['free_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.DEEPSEEK_R1_FREE, self._generate_switch_message(ModelType.DEEPSEEK_R1_FREE, permanent), permanent
        
        # Generic Categories
        for pattern in self.switch_patterns['local_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.LOCAL, self._generate_switch_message(ModelType.LOCAL, permanent), permanent
        
        for pattern in self.switch_patterns['auto_patterns']:
            if re.search(pattern, user_input_lower):
                return ModelType.AUTO, self._generate_switch_message(ModelType.AUTO, permanent), permanent
        
        return None, "", False
    
    def _generate_switch_message(self, target_model: ModelType, permanent: bool) -> str:
        """Generate appropriate confirmation message for model switch."""
        model_info = self.model_info[target_model]
        duration = "permanently" if permanent else "for this query"
        
        return f"{model_info['icon']} **Switched to {model_info['name']}** {duration}\n" \
               f"📊 Provider: {model_info['provider']} | Cost: {model_info['cost']}\n" \
               f"🎯 Specialties: {model_info['specialties']}"
    
    def switch_model(self, target_model: ModelType, permanent: bool = True) -> str:
        """
        Execute model switch and return confirmation message.
        
        Args:
            target_model: The model to switch to
            permanent: Whether this is a permanent switch or temporary
            
        Returns:
            str: Confirmation message
        """
        if not permanent:
            # Store current model for restoration
            self.previous_model = self.current_model
        
        self.current_model = target_model
        return self._generate_switch_message(target_model, permanent)
    
    def restore_previous_model(self) -> str:
        """Restore previous model after temporary switch."""
        if self.previous_model != self.current_model:
            old_model = self.current_model
            self.current_model = self.previous_model
            model_info = self.model_info[self.current_model]
            return f"↩️ **Restored to {model_info['name']}** - Temporary switch complete."
        return ""
    
    def get_current_model_info(self) -> Dict[str, str]:
        """Get current model information for display."""
        return self.model_info.get(self.current_model, {
            "name": "Unknown",
            "provider": "Unknown", 
            "cost": "Unknown",
            "icon": "❓",
            "description": "Model information unavailable",
            "specialties": "Unknown"
        })
    
    def get_status_display(self) -> str:
        """Get formatted status for display in chat interface."""
        info = self.get_current_model_info()
        return f"{info['icon']} **{info['name']}** ({info['cost']})"
    
    def is_model_switch_query(self, user_input: str) -> bool:
        """Quick check if input contains model switching intent."""
        user_input_lower = user_input.lower()
        
        # Check all pattern categories
        all_patterns = []
        for pattern_list in self.switch_patterns.values():
            all_patterns.extend(pattern_list)
        
        for pattern in all_patterns:
            if re.search(pattern, user_input_lower):
                return True
        
        return False
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """Get complete model catalog for display."""
        return {model_type.value: info for model_type, info in self.model_info.items()}
    
    def get_model_by_category(self) -> Dict[str, list]:
        """Organize models by category for UI display."""
        return {
            "Premium AI": [ModelType.CLAUDE_OPUS, ModelType.CLAUDE_SONNET],
            "Reasoning": [ModelType.DEEPSEEK_R1, ModelType.DEEPSEEK_R1_THROUGHPUT], 
            "General Purpose": [ModelType.DEEPSEEK_V3, ModelType.LLAMA_3_3_70B, ModelType.LLAMA_3_1_8B],
            "Free": [ModelType.DEEPSEEK_R1_FREE],
            "Smart Selection": [ModelType.AUTO, ModelType.LOCAL]
        }

# Global instance for the application
enhanced_communication_controller = EnhancedCommunicationController()

# Test function for development
def test_enhanced_communication_control():
    """Test the enhanced communication control patterns."""
    controller = EnhancedCommunicationController()
    
    test_cases = [
        # Claude Models
        "Can you chat with Claude about this?",
        "Use Claude Opus for this critical analysis",
        "Switch to Claude Sonnet please",
        
        # Reasoning Models
        "Switch to DeepSeek R1 for complex math",
        "Use reasoning model for this problem",
        "Switch to R1 Throughput for batch processing",
        
        # General Purpose
        "Use DeepSeek V3 for coding",
        "Switch to Llama for multilingual support",
        "Use Llama 3.1 for simple questions",
        
        # Free Models
        "Switch to free model",
        "Use free version for testing",
        
        # Categories
        "Use local model for cost optimization",
        "Let HAWKMOTH decide the best model",
        "Auto select optimal model",
        
        # Regular queries
        "Regular question without model switching",
        "What is machine learning?"
    ]
    
    print("🧪 Testing Enhanced Communication Control Patterns:")
    print("=" * 60)
    
    for test_input in test_cases:
        model_type, message, permanent = controller.parse_model_request(test_input)
        
        print(f"Input: '{test_input}'")
        print(f"Detected: {model_type}")
        if model_type:
            info = controller.model_info[model_type]
            print(f"Model: {info['name']} ({info['cost']})")
        print(f"Permanent: {permanent}")
        print("-" * 40)
    
    print(f"\n📊 Model Categories:")
    categories = controller.get_model_by_category()
    for category, models in categories.items():
        print(f"  {category}:")
        for model in models:
            info = controller.model_info[model]
            print(f"    {info['icon']} {info['name']} - {info['cost']}")

if __name__ == "__main__":
    test_enhanced_communication_control()
