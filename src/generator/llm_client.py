import os
import yaml
import sys
from typing import List, Dict, Optional
from openai import OpenAI

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from utils.paths import ROOT_DIR

class LLMClient:
    def __init__(self, config_path: str):
        self._load_env()
        self.config = self._load_config(config_path)
        self.client = self._init_client()
    
    def _load_env(self):
        """Simple .env loader to avoid extra dependencies"""
        # Look for .env in the project root
        env_path = ROOT_DIR / ".env"
        
        if env_path.exists():
            print(f"[Info] Loading environment variables from {env_path}")
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        # Only set if not already set (allow override via shell)
                        if key.strip() not in os.environ:
                            os.environ[key.strip()] = value.strip().strip('"').strip("'")

    def _load_config(self, path: str) -> Dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"LLM config not found at {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
            
    def _init_client(self) -> OpenAI:
        provider = self.config.get("provider", "doubao")
        conf = self.config.get(provider)
        
        if not conf:
             raise ValueError(f"Configuration for provider '{provider}' not found in rag_config.yaml")
            
        api_key_env = conf.get("api_key_env")
        api_key = os.environ.get(api_key_env)
        
        # Priority: Env Var > Config
        # Allows local override via .env for public repos
        env_base_url_key = f"{provider.upper()}_BASE_URL"
        base_url = os.environ.get(env_base_url_key, conf.get("base_url"))
        
        if not api_key:
            print(f"[Warning] {api_key_env} not set. LLM calls will fail.")
            
        return OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, messages: List[Dict]) -> str:
        """
        Calls the LLM API to generate a response.
        """
        if not self.client.api_key:
             return "Error: API Key missing. Please set environment variable."

        provider = self.config.get("provider", "doubao")
        conf = self.config.get(provider, {})
        
        # Priority: Environment Variable > Config File > Default
        # Env var naming convention: {PROVIDER}_MODEL (e.g. DEEPSEEK_MODEL)
        env_model_key = f"{provider.upper()}_MODEL"
        model = os.environ.get(env_model_key, conf.get("model"))
        
        temp = conf.get("temperature", 0.1)
        max_tokens = conf.get("max_tokens", 512)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temp,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
