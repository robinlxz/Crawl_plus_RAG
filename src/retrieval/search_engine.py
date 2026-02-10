import faiss
import json
import os
import sys
import numpy as np
from typing import List, Dict, Any

# Add src to path if not already (for relative imports from different contexts)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from utils.paths import DATA_DIR
from embedding.embedder import RAGEmbedder

class SimpleRAGSearcher:
    def __init__(self, index_path: str = None, meta_path: str = None):
        """
        Initializes the searcher with FAISS index and metadata.
        Uses RAGEmbedder for query encoding.
        """
        if index_path is None:
            index_path = str(DATA_DIR / "byteplus.index")
        if meta_path is None:
            meta_path = str(DATA_DIR / "byteplus_meta.json")

        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Index or Metadata not found at {index_path} / {meta_path}")
            
        print("Loading embedder...")
        self.embedder = RAGEmbedder() # Loads from config
        
        print("Loading index and metadata...")
        self.index = faiss.read_index(index_path)
        self.blocks = self._load_blocks(meta_path)
        
        print(f"Searcher ready. Index: {self.index.ntotal} vectors.")

    def _load_blocks(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches the index for the given query.
        Returns a list of block dictionaries with an added 'score' field.
        """
        # Use centralized embedder
        query_vector = self.embedder.encode(query)
        D, I = self.index.search(query_vector, top_k)
        
        results = []
        for i in range(top_k):
            idx = I[0][i]
            score = float(D[0][i]) # Convert numpy float to python float
            
            if idx < 0 or idx >= len(self.blocks):
                continue
                
            block = self.blocks[idx].copy()
            block['score'] = score
            results.append(block)
            
        return results
