# HAWKMOTH Configuration Management
import os
import json
from typing import Dict, Any, Optional

class HAWKMOTHConfig:
    """Centralized configuration management for HAWKMOTH LLM Teaming"""
    
    def __init__(self):
        self.config_file = "hawkmoth_config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file and environment variables"""
        # Default configuration
        default_config = {
            "llm_routing": {
                "enabled": True,
                "default_fallback": "GPT4",
                "confidence_threshold": 0.7,
                "cost_optimization": True
            },
            "api_keys": {
                "together_ai": "",
                "openai": "",
                "claude": "",
                "huggingface": ""
            },
            "routing_preferences": {
                "prefer_local": True,
                "max_cost_per_query": 0.50,
                "cache_routing_decisions": True
            },
            "hf_spaces": {
                "auto_deploy": True,
                "cpu_template": "hawkmoth-cpu-template",
                "gpu_template": "hawkmoth-gpu-template"
            }
        }
        
        # Try to load from file
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                default_config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
        
        # Override with environment variables
        env_mappings = {
            "TOGETHER_API_KEY": ["api_keys", "together_ai"],
            "OPENAI_API_KEY": ["api_keys", "openai"],
            "CLAUDE_API_KEY": ["api_keys", "claude"],
            "HF_TOKEN": ["api_keys", "huggingface"]
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                if len(config_path) == 2:
                    default_config[config_path[0]][config_path[1]] = env_value
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Don't save API keys to file for security
            save_config = self.config.copy()
            save_config["api_keys"] = {k: "***" if v else "" for k, v in self.config["api_keys"].items()}
            
            with open(self.config_file, 'w') as f:
                json.dump(save_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        key = self.config["api_keys"].get(service, "")
        return key if key and key != "***" else None
    
    def set_api_key(self, service: str, key: str):
        """Set API key for a service"""
        self.config["api_keys"][service] = key
    
    def get_routing_config(self) -> Dict[str, Any]:
        """Get LLM routing configuration"""
        return self.config["llm_routing"]
    
    def get_hf_config(self) -> Dict[str, Any]:
        """Get HuggingFace Spaces configuration"""
        return self.config["hf_spaces"]
    
    def is_service_configured(self, service: str) -> bool:
        """Check if a service is properly configured"""
        api_key = self.get_api_key(service)
        return api_key is not None and len(api_key) > 10
    
    def get_configuration_status(self) -> Dict[str, str]:
        """Get status of all service configurations"""
        services = ["together_ai", "openai", "claude", "huggingface"]
        return {
            service: "✅ Configured" if self.is_service_configured(service) else "⚠️ Not configured"
            for service in services
        }
    
    def update_routing_preference(self, preference: str, value: Any):
        """Update routing preference"""
        if preference in self.config["routing_preferences"]:
            self.config["routing_preferences"][preference] = value
            self.save_config()

# Global configuration instance
hawkmoth_config = HAWKMOTHConfig()

# Configuration helper functions
def get_together_api_key() -> Optional[str]:
    return hawkmoth_config.get_api_key("together_ai")

def get_openai_api_key() -> Optional[str]:
    return hawkmoth_config.get_api_key("openai")

def get_claude_api_key() -> Optional[str]:
    return hawkmoth_config.get_api_key("claude")

def get_hf_token() -> Optional[str]:
    return hawkmoth_config.get_api_key("huggingface")

def is_routing_enabled() -> bool:
    return hawkmoth_config.get_routing_config().get("enabled", True)

def get_cost_limit() -> float:
    return hawkmoth_config.config["routing_preferences"].get("max_cost_per_query", 0.50)
