import os
import sys
import yaml
from typing import List, Union
from sentence_transformers import SentenceTransformer
import numpy as np

# Robust import of paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from utils.paths import CONFIG_DIR

class RAGEmbedder:
    _instance = None
    _model = None
    
    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            cls._instance = super(RAGEmbedder, cls).__new__(cls)
            cls._instance._initialize(config_path)
        return cls._instance
    
    def _initialize(self, config_path: str):
        if not config_path:
             # Default path from centralized config
             config_path = str(CONFIG_DIR / "rag_config.yaml")
            
        if not os.path.exists(config_path):
             raise FileNotFoundError(f"Config not found at {config_path}")
             
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        model_name = self.config.get("embedding", {}).get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
        print(f"[RAGEmbedder] Loading model: {model_name}...")
        self._model = SentenceTransformer(model_name)
        
    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Encodes text(s) into embeddings.
        Output is L2 normalized.
        """
        if isinstance(texts, str):
            texts = [texts]
        # normalize_embeddings=True ensures dot product equals cosine similarity
        return self._model.encode(texts, normalize_embeddings=True)
    
    @property
    def embedding_dim(self) -> int:
        return self._model.get_sentence_embedding_dimension()
