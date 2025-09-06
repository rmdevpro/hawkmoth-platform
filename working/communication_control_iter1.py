"""
HAWKMOTH Component 4: Communication Control UI
Natural Language Model Selection System
Version: v0.0.4-dev
"""

import re
from typing import Dict, Tuple, Optional
from enum import Enum

class ModelType(Enum):
    CLAUDE = "claude"
    LOCAL = "local"
    AUTO = "auto"

class CommunicationController:
    """
    Natural language model selection and switching system.
    Detects user intent to switch between Claude and local LLM models.
    """
    
    def __init__(self):
        self.current_model = ModelType.CLAUDE  # Default to Claude
        self.previous_model = ModelType.CLAUDE
        self.switch_patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, list]:
        """Initialize pattern matching for model switching requests."""
        return {
            'claude_patterns': [
                r'\b(?:chat with|use|switch to|talk to) claude\b',
                r'\buse claude for this\b',
                r'\blet me talk to claude\b',
                r'\bswitch to anthropic\b',
                r'\buse anthropic\b',
                r'\bclaude please\b',
                r'\bask claude\b'
            ],
            'local_patterns': [
                r'\b(?:chat with|use|switch to|talk to) (?:local|open|free) (?:llm|model|ai)\b',
                r'\buse (?:local|open|free) model\b',
                r'\bswitch to (?:local|open|free)\b',
                r'\buse deepseek\b',
                r'\buse llama\b',
                r'\blet me talk to (?:local|open|free)\b',
                r'\buse open source\b'
            ],
            'auto_patterns': [
                r'\bauto select\b',
                r'\bchoose best model\b',
                r'\blet (?:hawkmoth|you) decide\b',
                r'\boptimal model\b',
                r'\bbest model for this\b'
            ],
            'confirmation_patterns': [
                r'\byes,? (?:switch|change)\b',
                r'\bconfirm switch\b',
                r'\byes please\b',
                r'\b(?:go ahead|proceed)\b'
            ]
        }
    
    def parse_model_request(self, user_input: str) -> Tuple[Optional[ModelType], str, bool]:
        """
        Parse user input for model switching requests.
        
        Returns:
            Tuple[Optional[ModelType], str, bool]:
                - ModelType if switch detected, None otherwise
                - Confirmation message
                - Whether this is a permanent switch (True) or one-time use (False)
        """
        user_input_lower = user_input.lower().strip()
        
        # Check for Claude patterns
        for pattern in self.switch_patterns['claude_patterns']:
            if re.search(pattern, user_input_lower):
                permanent = not ('for this' in user_input_lower or 'this time' in user_input_lower)
                message = self._generate_switch_message(ModelType.CLAUDE, permanent)
                return ModelType.CLAUDE, message, permanent
        
        # Check for local model patterns
        for pattern in self.switch_patterns['local_patterns']:
            if re.search(pattern, user_input_lower):
                permanent = not ('for this' in user_input_lower or 'this time' in user_input_lower)
                message = self._generate_switch_message(ModelType.LOCAL, permanent)
                return ModelType.LOCAL, message, permanent
        
        # Check for auto selection patterns
        for pattern in self.switch_patterns['auto_patterns']:
            if re.search(pattern, user_input_lower):
                message = "🤖 HAWKMOTH will automatically select the optimal model for each query."
                return ModelType.AUTO, message, True
        
        return None, "", False
    
    def _generate_switch_message(self, target_model: ModelType, permanent: bool) -> str:
        """Generate appropriate confirmation message for model switch."""
        if target_model == ModelType.CLAUDE:
            if permanent:
                return "🎯 **Switched to Claude Sonnet 4** - Now using premium AI for all responses."
            else:
                return "🎯 **Using Claude for this query** - Will return to previous model after response."
        
        elif target_model == ModelType.LOCAL:
            if permanent:
                return "🆓 **Switched to Local LLM** - Now using open-source models (cost-optimized)."
            else:
                return "🆓 **Using Local LLM for this query** - Will return to previous model after response."
        
        return "✅ Model selection updated."
    
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
            return f"↩️ **Restored to {self.current_model.value}** - Temporary switch complete."
        return ""
    
    def get_current_model_info(self) -> Dict[str, str]:
        """Get current model information for display."""
        model_info = {
            ModelType.CLAUDE: {
                "name": "Claude Sonnet 4",
                "provider": "Anthropic",
                "cost": "$3/$15 per 1k tokens",
                "icon": "🎯",
                "description": "Premium AI with advanced reasoning"
            },
            ModelType.LOCAL: {
                "name": "DeepSeek-V3",
                "provider": "Together AI",
                "cost": "$1.25 per 1k tokens",
                "icon": "🆓",
                "description": "Cost-optimized open-source model"
            },
            ModelType.AUTO: {
                "name": "Auto-Select",
                "provider": "HAWKMOTH",
                "cost": "Optimized routing",
                "icon": "🤖",
                "description": "Intelligent model selection"
            }
        }
        
        return model_info.get(self.current_model, {
            "name": "Unknown",
            "provider": "Unknown", 
            "cost": "Unknown",
            "icon": "❓",
            "description": "Model information unavailable"
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

# Global instance for the application
communication_controller = CommunicationController()

# Test function for development
def test_communication_control():
    """Test the communication control patterns."""
    controller = CommunicationController()
    
    test_cases = [
        "Can you chat with Claude about this?",
        "Switch to local LLM please",
        "Use Claude for this analysis",
        "Let me talk to the open source model",
        "Use DeepSeek to answer this",
        "Let HAWKMOTH decide the best model",
        "Regular question without model switching"
    ]
    
    print("🧪 Testing Communication Control Patterns:")
    print("=" * 50)
    
    for test_input in test_cases:
        model_type, message, permanent = controller.parse_model_request(test_input)
        
        print(f"Input: '{test_input}'")
        print(f"Detected: {model_type}")
        print(f"Message: {message}")
        print(f"Permanent: {permanent}")
        print("-" * 30)

if __name__ == "__main__":
    test_communication_control()
