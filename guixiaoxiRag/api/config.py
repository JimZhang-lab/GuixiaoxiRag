"""
GuiXiaoXiRag API configuration
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OllamaServerInfos:
    """Ollama server configuration information"""
    base_url: str = "http://localhost:11434"
    model: str = "llama2"
    api_key: Optional[str] = None
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "base_url": self.base_url,
            "model": self.model,
            "api_key": self.api_key,
            "timeout": self.timeout
        }
