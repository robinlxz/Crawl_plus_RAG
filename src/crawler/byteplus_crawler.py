import requests
import json
import os
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

MAX_PAGES_PER_SOURCE =800

def load_config(config_path: str) -> List[Dict]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        time.sleep(0.3) # Polite delay
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links(html, root_url) -> Set[str]:
    """
    Extracts links strictly from the Sidebar/TOC container.
    Assumption: BytePlus docs use 'arco-menu-inner' class for the main navigation tree.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # 1. Locate Sidebar Container
    sidebar = soup.find(class_="arco-menu-inner")
    
    # Fallback mechanisms if the specific class changes
    if not sidebar:
        # Try finding any nav or sidebar-like container with sufficient links
        candidates = soup.find_all(lambda tag: tag.name in ['div', 'nav', 'aside'] and 
                                             tag.get('class') and 
                                             any('menu' in c or 'sidebar' in c for c in tag.get('class')))
        # Pick the largest candidate (heuristic)
        if candidates:
            sidebar = max(candidates, key=lambda x: len(x.find_all('a')))
            
    if not sidebar:
        print("  [Warning] No sidebar container found. Falling back to full page extraction.")
        sidebar = soup # Fallback to body
    else:
        # Try to identify what we found for debugging
        cls_name = sidebar.get("class", ["unknown"])[0] if sidebar.get("class") else sidebar.name
        print(f"  [Info] Found sidebar container: {cls_name}")

    # 2. Path Constraints
    parsed_root = urlparse(root_url)
    path_parts = parsed_root.path.strip("/").split("/")
    if len(path_parts) > 2:
        base_path = "/" + "/".join(path_parts[:3]) # e.g. /en/docs/ecs
    else:
        base_path = parsed_root.path
        
    # 3. Extract & Filter
    raw_count = 0
    for a in sidebar.find_all("a", href=True):
        raw_count += 1
        href = a["href"]
        full_url = urljoin(root_url, href)
        
        # Filter logic
        if base_path in full_url and full_url.startswith("http"):
            # Remove hash
            if "#" in full_url:
                full_url = full_url.split("#")[0]
            
            if full_url != root_url:
                links.add(full_url)
                
    print(f"  [Stats] Raw links in sidebar: {raw_count} -> Filtered unique links: {len(links)}")
    return links

def get_safe_filename(url):
    return hashlib.md5(url.encode("utf-8")).hexdigest() + ".json"

def save_raw_page(url, html, source_name, source_dir):
    raw_data = {
        "url": url,
        "crawl_time": datetime.now().isoformat(),
        "source_name": source_name,
        # category is now unknown at this stage
        "raw_content": html
    }
    
    filename = get_safe_filename(url)
    save_path = os.path.join(source_dir, filename)
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {filename}")

def main():
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(current_dir, "../../data")
    
    config_path = os.path.join(DATA_DIR, "sources/urls.json")
    raw_dir = os.path.join(DATA_DIR, "raw")
    
    if not os.path.exists(config_path):
        print(f"Config not found at {config_path}")
        return
        
    urls_config = load_config(config_path)
    print(f"Loaded {len(urls_config)} seed URLs.")    
    
    for entry in urls_config:
        seed_url = entry["url"]
        source_name = entry["source_name"]
        
        print(f"\nProcessing Source: {source_name} (Seed: {seed_url})")
        
        source_dir = os.path.join(raw_dir, source_name)
        os.makedirs(source_dir, exist_ok=True)
        
        # 1. Fetch Seed
        print(f"Fetching seed: {seed_url}...")
        seed_html = fetch_page(seed_url)
        
        if not seed_html:
            print("Failed to fetch seed. Skipping.")
            continue
            
        save_raw_page(seed_url, seed_html, source_name, source_dir)
        
        # 2. Discover Links
        print("Discovering links from Sidebar...")
        discovered_links = extract_links(seed_html, seed_url)
        print(f"Found {len(discovered_links)} valid sidebar links.")
        
        # 3. Fetch Discovered (with limit)
        count = 0
        total_discovered = len(discovered_links)
        
        for link in discovered_links:
            if count >= MAX_PAGES_PER_SOURCE:
                print("\n" + "!" * 60)
                print(f"WARNING: Hit MAX_PAGES_PER_SOURCE limit ({MAX_PAGES_PER_SOURCE}).")
                print(f"There are {total_discovered - count} more pages skipped.")
                print("RAG results might be incomplete due to missing data.")
                print("!" * 60 + "\n")
                break
                
            print(f"Fetching [{count+1}/{min(total_discovered, MAX_PAGES_PER_SOURCE)}]: {link}")
            html = fetch_page(link)
            if html:
                save_raw_page(link, html, source_name, source_dir)
                count += 1

if __name__ == "__main__":
    main()
