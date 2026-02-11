import streamlit as st
import os
import sys
import time

# Robust path setup for deployment
current_dir = os.path.dirname(os.path.abspath(__file__))
# Ensure we can import from utils
sys.path.append(current_dir)

from utils.paths import DATA_DIR, CONFIG_DIR, add_src_to_path
add_src_to_path()

from retrieval.search_engine import SimpleRAGSearcher
from generator.generate import RAGGenerator

# Page Configuration
st.set_page_config(
    page_title="BytePlus RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize Resources (Cached)
@st.cache_resource
def load_rag_system():
    # Define paths using centralized config
    index_path = DATA_DIR / "byteplus.index"
    meta_path = DATA_DIR / "byteplus_meta.json"
    config_path = CONFIG_DIR / "rag_config.yaml"
    
    # Convert Path objects to strings for compatibility
    searcher = SimpleRAGSearcher(str(index_path), str(meta_path))
    generator = RAGGenerator(str(config_path))
    return searcher, generator

try:
    searcher, generator = load_rag_system()
except Exception as e:
    st.error(f"Failed to load RAG system: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    st.write("Current Model Provider:")
    
    # Read provider from config for display (optional)
    try:
        provider = generator.client.config.get("provider", "Unknown")
        st.info(f"**{provider.upper()}**")
    except:
        st.warning("Unknown Provider")
        
    top_k = st.slider("Top-K Retrieval", min_value=1, max_value=10, value=3)
    st.divider()
    st.markdown("### About")
    st.markdown("This is a RAG demo for BytePlus ECS documentation.")

# Main Chat Interface
st.title("🤖 BytePlus ECS Assistant")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If there are sources in the message metadata, display them
        if "sources" in message:
            with st.expander("🔍 Retrieved Context (Source Documents)"):
                for idx, source in enumerate(message["sources"]):
                    url = source.get("url", "#")
                    st.markdown(f"**{idx+1}. [{source['title']}]({url})** (Score: {source['score']:.4f})")
                    st.caption(source['content'][:300] + "...")

# Accept user input
if prompt := st.chat_input("Ask a question about ECS..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 1. Retrieval
        with st.status("Thinking...", expanded=False) as status:
            st.write("Searching knowledge base...")
            start_t = time.time()
            results = searcher.search(prompt, top_k=top_k)
            retrieve_time = (time.time() - start_t) * 1000 # ms
            st.write(f"Found {len(results)} documents in {retrieve_time:.0f}ms.")
            
            # 2. Generation
            st.write("Generating answer...")
            start_t = time.time()
            response = generator.answer(prompt, results)
            gen_time = (time.time() - start_t) * 1000 # ms
            
            answer = response["answer"]
            debug_info = response["debug"]
            
            status.update(label=f"Done! (Total: {(retrieve_time + gen_time):.0f}ms)", state="complete", expanded=False)
            
        message_placeholder.markdown(answer)
        
        # Prepare sources for history (Simplified for display)
        sources_meta = []
        for res in results:
            sources_meta.append({
                "title": res.get("source_meta", {}).get("title", "Unknown"),
                "url": res.get("source_meta", {}).get("url", "#"),
                "score": res.get("score", 0.0),
                "content": res.get("content", "")
            })
            
        # ---------------------------------------------------------
        # P1: Enhanced Debug Console
        # ---------------------------------------------------------
        with st.expander("🛠️ Debug Console", expanded=False):
            tab1, tab2, tab3 = st.tabs(["🔍 Retrieval", "🧠 Prompt", "⏱️ Stats"])
            
            # Tab 1: Retrieval
            with tab1:
                st.caption(f"Top-{len(results)} Retrieved Chunks")
                for idx, res in enumerate(results):
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.metric(f"Rank {idx+1}", f"{res.get('score', 0.0):.4f}")
                        with col2:
                            source = res.get('source_meta', {})
                            st.markdown(f"**Source:** [{source.get('title', 'Untitled')}]({source.get('url', '#')})")
                            st.markdown(f"**Block ID:** `{res.get('block_id', 'N/A')}`")
                            with st.expander("Show Content", expanded=False):
                                st.code(res.get('content', ''), language='text')
                        st.divider()
            
            # Tab 2: Prompt
            with tab2:
                st.caption("Final messages sent to LLM")
                st.json(debug_info.get("final_messages", []))
                
            # Tab 3: Stats
            with tab3:
                col1, col2, col3 = st.columns(3)
                col1.metric("Retrieval Latency", f"{retrieve_time:.0f} ms")
                col2.metric("Generation Latency", f"{gen_time:.0f} ms")
                col3.metric("Total Latency", f"{(retrieve_time + gen_time):.0f} ms")

    # Add assistant message to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "sources": sources_meta,
        "debug": debug_info # Store debug info in history too
    })
