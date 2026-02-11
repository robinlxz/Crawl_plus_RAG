import os
import sys
from typing import List, Dict, Any

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from utils.paths import CONFIG_DIR

from .llm_client import LLMClient
from .prompt_builder import build_rag_prompt

class RAGGenerator:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default from centralized config
            config_path = str(CONFIG_DIR / "rag_config.yaml")
            
        self.client = LLMClient(config_path)
        
    def answer(self, question: str, retrieved_chunks: List[Dict]) -> Dict[str, Any]:
        """
        End-to-end generation: Prompt Build -> LLM Call -> Answer
        Returns:
            Dict containing:
            - 'answer': str
            - 'debug': Dict containing 'final_messages'
        """
        # 1. Build Prompt
        messages = build_rag_prompt(question, retrieved_chunks)
        
        # 2. Call LLM
        answer_text = self.client.generate(messages)
        
        return {
            "answer": answer_text,
            "debug": {
                "final_messages": messages
            }
        }
