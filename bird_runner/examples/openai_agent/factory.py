import yaml
import os
from typing import Optional
from bird_runner import AgentFactory
from .agent import OpenAIAgent


class OpenAIAgentFactory(AgentFactory):
    def create_agent(self, config_path: str, storage_root: Optional[str] = None) -> OpenAIAgent:
        """
        Create an OpenAI agent instance.
        
        Args:
            config_path: Path to the configuration file
            storage_root: Optional storage root (not used in this implementation)
            
        Returns:
            OpenAIAgent: Configured agent instance
        """
        config = self._load_config(config_path)
        
        # Override with environment variables if available
        if "OPENAI_API_KEY" in os.environ:
            config["openai"]["api_key"] = os.environ["OPENAI_API_KEY"]
        
        if not config["openai"]["api_key"]:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            
        return OpenAIAgent(config)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)