import os
import sys
import json
import faiss
import numpy as np

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from utils.paths import DATA_DIR
from embedding.embedder import RAGEmbedder

def main():
    # Setup Paths
    processed_file = DATA_DIR / "processed/simple_rag_blocks.json"
    index_file = DATA_DIR / "byteplus.index"
    meta_file = DATA_DIR / "byteplus_meta.json"
    
    # Load Blocks
    print(f"Loading blocks from {processed_file.name}...")
    with open(processed_file, "r", encoding="utf-8") as f:
        blocks = json.load(f)
    print(f"Loaded {len(blocks)} blocks.")
    
    # Initialize Embedder
    embedder = RAGEmbedder() # Loads from rag_config.yaml
    
    # Generate Embeddings
    print("Generating embeddings...")
    contents = [b["content"] for b in blocks]
    # Note: SentenceTransformer handles batching automatically
    embeddings = embedder.encode(contents)
    
    # Create FAISS Index
    dimension = embedder.embedding_dim
    print(f"Embedding dimension: {dimension}")
    
    # Use IndexFlatIP for Cosine Similarity (since vectors are normalized)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    print(f"Indexed {index.ntotal} vectors.")
    
    # Save Index and Metadata
    print("Saving artifacts...")
    faiss.write_index(index, str(index_file))
    
    # Save metadata (same as blocks for now, but could be lighter)
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)
        
    print(f"\nIndex saved successfully to {index_file}")
    print(f"Metadata saved successfully to {meta_file}")

if __name__ == "__main__":
    main()
