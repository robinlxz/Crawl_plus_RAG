import json
import re
import os
import sys
import hashlib
import glob
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from byteplus_parser import extract_data, parse_delta_ops

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
from utils.paths import DATA_DIR

# --- Configuration & Regex ---
MONTHS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
DATE_ANCHOR_PATTERN = re.compile(
    rf"^\s*\*?\s*({MONTHS}\s+\d{{1,2}},?\s+\d{{4}}|{MONTHS}\s+\d{{4}})", 
    re.MULTILINE | re.IGNORECASE
)

# --- Core Logic ---

def extract_time_from_text(text: str) -> Optional[str]:
    """Finds the first occurrence of a date string in the text."""
    match = DATE_ANCHOR_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return None

def generate_block_id(content: str, url: str) -> str:
    """Generates a stable ID based on content and source."""
    raw = f"{url}|{content}".encode("utf-8")
    return hashlib.md5(raw).hexdigest()

def split_by_time_anchors(text: str, meta: Dict) -> List[Dict]:
    """Splits a document's content into blocks based on date anchors."""
    matches = list(DATE_ANCHOR_PATTERN.finditer(text))
    
    if not matches:
        if len(text.strip()) > 50:
             return [{
                "block_type": "release_version",
                "product": "ECS",
                "subtype": "release_note",
                "time": None,
                "content": text.strip(),
                "source_url": meta["url"],
                "source_page_title": meta["title"]
            }]
        return []

    blocks = []
    for i, match in enumerate(matches):
        version_time = match.group(1).strip()
        start_idx = match.start()
        end_idx = matches[i+1].start() if i < len(matches) - 1 else len(text)
        
        block_content = text[start_idx:end_idx].strip()
        content_without_date = block_content.replace(version_time, "").replace("*", "").strip()
        
        if len(content_without_date) < 10:
            continue
            
        blocks.append({
            "block_type": "release_version",
            "product": "ECS",
            "subtype": "release_note",
            "time": version_time,
            "content": block_content,
            "source_url": meta["url"],
            "source_page_title": meta["title"]
        })
        
    return blocks

def process_raw_file(file_path: str) -> List[Dict]:
    """Reads a raw JSON file, parses HTML, and splits into blocks."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
        
    html = raw_data.get("raw_content", "")
    url = raw_data.get("url", "")
    category = raw_data.get("category", "unknown")
    
    # 1. Parse HTML to Text using byteplus_parser logic
    data = extract_data(html)
    
    text = ""
    title = "Unknown"
    parent = "Unknown"
    
    if data:
        if data["type"] == "quill":
            content_json = data["content"]
            if "data" in content_json and "0" in content_json["data"]:
                ops = content_json["data"]["0"].get("ops", [])
                text = parse_delta_ops(ops)
        elif data["type"] == "markdown":
            text = data["content"]
        title = data["title"]
        parent = data["parent"]
    else:
        # Fallback: simple text extraction if structured parsing fails
        soup = BeautifulSoup(html, "html.parser")
        if soup.title:
            title = soup.title.string.split("--")[0].strip()
        # Try to find main content div if possible, or just get text
        text = soup.get_text(separator="\n", strip=True)

    # Fallback: Extract title from URL if missing or Unknown
    if not title or title == "Unknown":
        try:
            slug = url.rstrip('/').split('/')[-1]
            # Replace dashes/underscores with spaces and capitalize
            title = slug.replace('-', ' ').replace('_', ' ').strip().capitalize()
            # If slug is empty (e.g. root url), try second to last
            if not title and len(url.split('/')) > 1:
                 slug = url.rstrip('/').split('/')[-2]
                 title = slug.replace('-', ' ').replace('_', ' ').strip().capitalize()
        except:
            title = "Untitled Document"

    if not text.strip():
        return []

    meta = {
        "url": url,
        "title": title,
        "parent": parent
    }
    
    # 2. Structure Blocks based on Category
    blocks = []
    
    if category == "release_notes":
        # Logic for release notes splitting
        if "Image release notes" in title:
             # Heuristic for image release notes (mixed content)
             first_match = DATE_ANCHOR_PATTERN.search(text)
             if first_match:
                intro = text[:first_match.start()].strip()
                if len(intro) > 20:
                    blocks.append({
                        "block_type": "reference",
                        "product": "ECS",
                        "subtype": "image_lifecycle_rules",
                        "time": None,
                        "content": intro,
                        "source_url": url,
                        "source_page_title": title
                    })
                blocks.extend(split_by_time_anchors(text, meta))
             else:
                # Treat as one ref block
                blocks.append({
                    "block_type": "reference",
                    "product": "ECS",
                    "subtype": "image_lifecycle_rules",
                    "time": None,
                    "content": text,
                    "source_url": url,
                    "source_page_title": title
                })
        else:
             blocks.extend(split_by_time_anchors(text, meta))
             
    elif category == "announcement":
        event_time = extract_time_from_text(text)
        blocks.append({
            "block_type": "announcement_event",
            "product": "ECS",
            "subtype": "announcement",
            "time": event_time,
            "content": text,
            "source_url": url,
            "source_page_title": title
        })
        
    else: # concept or unknown
        blocks.append({
            "block_type": "concept" if category == "concept" else "reference",
            "product": "ECS",
            "subtype": "general_doc",
            "time": None,
            "content": text,
            "source_url": url,
            "source_page_title": title
        })
        
    # 3. Enrich Blocks with IDs
    for block in blocks:
        block["block_id"] = generate_block_id(block["content"], url)
        # Ensure source_meta field exists for backward compatibility or clarity if needed
        # But per requirements, we have flat fields now.
        # Let's add a nested source_meta just in case the embedder expects it (it does!)
        block["source_meta"] = {
            "title": block["source_page_title"],
            "url": block["source_url"]
        }
        
    return blocks

def main():
    # Setup paths
    raw_dir = DATA_DIR / "raw"
    output_file = DATA_DIR / "processed/simple_rag_blocks.json"
    
    # Find all JSON files in raw subdirectories
    raw_files = glob.glob(os.path.join(raw_dir, "**/*.json"), recursive=True)
    
    if not raw_files:
        print(f"No raw files found in {raw_dir}. Please run crawler first.")
        return
        
    print(f"Found {len(raw_files)} raw files to process.")
    
    all_blocks = []
    for file_path in raw_files:
        print(f"Processing {os.path.basename(file_path)}...")
        try:
            file_blocks = process_raw_file(file_path)
            all_blocks.extend(file_blocks)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    # Save output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_blocks, f, ensure_ascii=False, indent=2)
        
    print(f"\nProcessing complete!")
    print(f"Generated {len(all_blocks)} structured blocks.")
    print(f"Output saved to: {output_file}")
    
    # Preview
    print("\n" + "="*30 + " BLOCK PREVIEW " + "="*30)
    for i, block in enumerate(all_blocks[:3]):
        print(f"\n[Block {i+1}] ID: {block['block_id'][:8]} | Type: {block['block_type']}")
        print(f"Title: {block['source_page_title']}")
        print("-" * 20)
        print(block['content'][:100].replace("\n", " ") + "...")

if __name__ == "__main__":
    main()
