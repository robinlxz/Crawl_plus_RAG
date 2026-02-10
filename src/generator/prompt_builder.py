from typing import List, Dict

def build_rag_prompt(question: str, chunks: List[Dict]) -> List[Dict]:
    """
    Constructs a chat prompt for the LLM using retrieved chunks.
    
    Args:
        question: User's question.
        chunks: List of retrieved blocks (metadata + content).
        
    Returns:
        A list of message dictionaries for the chat completion API.
    """
    
    system_prompt = (
        "You are a helpful documentation assistant for BytePlus ECS (Elastic Compute Service).\n"
        "Your task is to answer user questions based ONLY on the provided context.\n"
        "If the answer cannot be found in the context, clearly state that you don't know.\n"
        "IMPORTANT: When mentioning specific features, steps, or concepts from the context, "
        "you MUST create a Markdown link using the URL provided in the context header. "
        "Example: 'You can configure this in the [Console](https://...)'."
    )
    
    context_str = ""
    for i, chunk in enumerate(chunks):
        title = chunk.get("source_meta", {}).get("title", "Unknown Title")
        url = chunk.get("source_meta", {}).get("url", "")
        content = chunk.get("content", "").strip()
        
        context_str += f"[Context {i+1} | Title: {title} | URL: {url}]\n"
        context_str += f"{content}\n\n"
        
    user_content = (
        f"Context information is below:\n"
        f"---------------------\n"
        f"{context_str}"
        f"---------------------\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
