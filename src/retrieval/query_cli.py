import argparse
import json
import os
import sys
from pathlib import Path

# Ensure src imports work when called from anywhere
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from retrieval.search_engine import SimpleRAGSearcher


def main():
    parser = argparse.ArgumentParser(description="Query BytePlus ECS RAG index")
    parser.add_argument("--query", required=True, help="Query text")
    parser.add_argument("--top_k", type=int, default=3, help="Top-K results")
    parser.add_argument(
        "--index_path",
        default=str(Path(current_dir).parent.parent / "data" / "byteplus.index"),
        help="FAISS index path",
    )
    parser.add_argument(
        "--meta_path",
        default=str(Path(current_dir).parent.parent / "data" / "byteplus_meta.json"),
        help="Metadata JSON path",
    )
    parser.add_argument("--verbose", action="store_true", help="Print full content")
    args = parser.parse_args()

    # Initialize searcher
    searcher = SimpleRAGSearcher(index_path=args.index_path, meta_path=args.meta_path)
    results = searcher.search(args.query, top_k=args.top_k)

    # Output
    print(f"Query: {args.query}")
    print(f"Top-{len(results)} results:")
    for i, r in enumerate(results, 1):
        title = r.get("source_meta", {}).get("title", "Unknown")
        url = r.get("source_meta", {}).get("url", "#")
        score = r.get("score", 0.0)
        print(f"\n[{i}] Score={score:.4f}")
        print(f"Title: {title}")
        print(f"URL:   {url}")
        snippet = r.get("content", "")
        if args.verbose:
            print(f"Content:\n{snippet}")
        else:
            print(f"Content:\n{snippet[:300]}{'...' if len(snippet) > 300 else ''}")


if __name__ == "__main__":
    main()

