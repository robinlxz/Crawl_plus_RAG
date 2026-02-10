import os
import sys
import json
import time
from typing import List, Dict

# Add src to path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from retrieval.search_engine import SimpleRAGSearcher
from generator.generate import RAGGenerator

def main():
    # 1. Setup Paths
    DATA_DIR = os.path.join(current_dir, "../data")
    index_path = os.path.join(DATA_DIR, "byteplus.index")
    meta_path = os.path.join(DATA_DIR, "byteplus_meta.json")
    
    # 2. Initialize Modules
    print(">>> Initializing RAG System...")
    try:
        searcher = SimpleRAGSearcher(index_path, meta_path)
        generator = RAGGenerator() # Automatically finds config
        print(">>> Initialization Complete.")
    except Exception as e:
        print(f"Initialization failed: {e}")
        return

    # 3. Test Queries
    test_queries = [
        "What happened in October 2025?",
        "Is there any announcement about monitoring plugin upgrade?",
        "ECS 实例如何 resize?", # Mixed Chinese-English
        "什么是 ECS?",          # Pure Chinese
    ]
    
    # 4. Run RAG Loop
    print("\n" + "="*50)
    print("STARTING RAG END-TO-END TEST")
    print("="*50)
    
    for query in test_queries:
        print(f"\n[Question]: {query}")
        
        # Step A: Retrieve
        start_t = time.time()
        results = searcher.search(query, top_k=3)
        retrieve_time = time.time() - start_t
        
        print(f"[Retrieval]: Found {len(results)} chunks in {retrieve_time:.3f}s")
        for i, res in enumerate(results):
            title = res.get("source_meta", {}).get("title", "Unknown")
            print(f"  - [{i+1}] {title} (Score: {res['score']:.4f})")
            
        # Step B: Generate
        print("[Generation]: Calling LLM...")
        start_t = time.time()
        answer = generator.answer(query, results)
        gen_time = time.time() - start_t
        
        print(f"\n[Answer] ({gen_time:.3f}s):")
        print("-" * 30)
        print(answer)
        print("-" * 30)

if __name__ == "__main__":
    main()
