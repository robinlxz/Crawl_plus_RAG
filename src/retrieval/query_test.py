import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
import os

def load_blocks(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # Use robust path handling
    current_dir = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(current_dir, "../../data")
    
    index_file = os.path.join(DATA_DIR, "byteplus.index")
    meta_file = os.path.join(DATA_DIR, "byteplus_meta.json")
    
    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        print("Error: Index or Metadata not found. Please run build_index.py first.")
        return

    print("Loading model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading index and metadata...")
    index = faiss.read_index(index_file)
    blocks = load_blocks(meta_file)
    
    print(f"Index loaded with {index.ntotal} vectors.")
    print(f"Metadata loaded with {len(blocks)} blocks.")
    
    print("\n" + "="*30 + " QUERY TEST " + "="*30)
    
    # Define your test queries here
    test_queries = [
        # "What happened in October 2025?",
        "Is there any announcement about monitoring plugin upgrade?",
        "What is ECS?",
        # Add your own queries below
        "Does ECS support local SSD?",
        "What is TOS in Byteplus?",
        "Is AWS a competitor of GCP?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Embed query
        query_vector = model.encode([query])
        
        # Search index
        k = 3
        D, I = index.search(query_vector, k)
        
        for i in range(k):
            idx = I[0][i]
            score = D[0][i]
            
            if idx < 0 or idx >= len(blocks):
                continue
                
            block = blocks[idx]
            title = block['source_meta']['title']
            time_val = block.get('time', 'N/A')
            
            print(f"  [{i+1}] Score: {score:.4f} | Title: {title} | Time: {time_val}")
            preview = block['content'][:100].replace('\n', ' ')
            print(f"      Preview: {preview}...")

if __name__ == "__main__":
    main()
