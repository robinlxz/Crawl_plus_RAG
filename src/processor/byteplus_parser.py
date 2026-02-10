import re
import json
from bs4 import BeautifulSoup

def parse_delta_ops(ops):
    """
    Parses Quill Delta operations to extract text with structure.
    """
    structured_lines = []
    text_buffer = ""
    
    for op in ops:
        insert = op.get("insert")
        attributes = op.get("attributes", {})
        
        if isinstance(insert, str):
            if insert == "\n":
                # End of a block (paragraph, header, list item)
                line_content = text_buffer.strip()
                text_buffer = "" # Reset buffer
                
                if not line_content:
                    continue
                
                if attributes.get("header"):
                    level = attributes["header"]
                    structured_lines.append(f"{'#' * level} {line_content}")
                elif attributes.get("list"):
                    # List item
                    structured_lines.append(f"- {line_content}")
                else:
                    # Normal paragraph
                    structured_lines.append(line_content)
            else:
                text_buffer += insert
        elif isinstance(insert, dict):
            # Handle non-text inserts (images, etc.) if needed
            pass
            
    # Flush remaining buffer
    if text_buffer.strip():
         structured_lines.append(text_buffer.strip())
         
    return "\n\n".join(structured_lines)

def extract_data(html):
    """
    Extracts structured data from BytePlus documentation HTML.
    Returns a dictionary with title, parent, type, and content (json or raw string).
    """
    # 1. Try to find structured Content (Quill Delta)
    # Pattern: "Content":"{\"version\"...}"
    # We use a non-greedy match for the content value, but ensure it starts with {\"version
    content_pattern = r'"Content"\s*:\s*"(\{\\\"version\\\".*?})"'
    content_matches = list(re.finditer(content_pattern, html))
    
    for match in content_matches:
        raw_content = match.group(1)
        start_index = match.start()
        
        # Look backwards for Title and ParentCode
        search_window = html[max(0, start_index-1000):start_index]
        
        title_m = re.search(r'"Title"\s*:\s*"(.*?)"', search_window)
        parent_m = re.search(r'"ParentCode"\s*:\s*"(.*?)"', search_window)
        
        title = title_m.group(1) if title_m else "Unknown"
        parent = parent_m.group(1) if parent_m else "Unknown"
        
        try:
            unescaped = json.loads(f'"{raw_content}"')
            content_json = json.loads(unescaped)
            return {
                "title": title,
                "parent": parent,
                "type": "quill",
                "content": content_json
            }
        except:
            continue

    # 2. Try to find MDContent (Markdown)
    # Pattern: "MDContent":"..."
    # We look for MDContent that is NOT empty
    md_pattern = r'"MDContent"\s*:\s*"((?:[^"\\]|\\.)+)"'
    md_matches = list(re.finditer(md_pattern, html))
    
    for match in md_matches:
        raw_content = match.group(1)
        if not raw_content: 
            continue
            
        start_index = match.start()
        search_window = html[max(0, start_index-1000):start_index]
        
        title_m = re.search(r'"Title"\s*:\s*"(.*?)"', search_window)
        parent_m = re.search(r'"ParentCode"\s*:\s*"(.*?)"', search_window)
        
        title = title_m.group(1) if title_m else "Unknown"
        parent = parent_m.group(1) if parent_m else "Unknown"
        
        try:
            # Unescape JSON string
            unescaped = json.loads(f'"{raw_content}"')
            return {
                "title": title,
                "parent": parent,
                "type": "markdown",
                "content": unescaped
            }
        except:
            continue
            
    return None
