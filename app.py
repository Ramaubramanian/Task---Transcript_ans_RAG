import streamlit as st
from dotenv import load_dotenv
from backend.rag_engine import TranscriptRAG
from backend.data_parser import parse_transcripts
import time

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Interview Guide – European Robotic Surgery Market ", layout="wide")

@st.cache_resource
def load_engine():
    engine = TranscriptRAG()
    success = engine.initialize_knowledge_base()
    return engine, success

def main():
    st.title("Interview Guide – European Robotic Surgery Market ")
    
    # --- SYSTEM DEBUGGER & CACHE CONTROL ---
    with st.sidebar:
        st.header("System Status")
        
        # This button forces Streamlit to wipe memory and re-index the folder
        if st.button("🔄 Clear Cache & Reload Data"):
            st.cache_resource.clear()
            st.rerun()
            
        st.divider()
        st.subheader("Loaded Files in Memory:")
        loaded_docs = parse_transcripts()
        if not loaded_docs:
            st.error("No valid chunks found. Check file formatting.")
        else:
            unique_files = list(set(doc.metadata["source"] for doc in loaded_docs))
            for f in unique_files:
                st.success(f"✅ {f}")
            st.caption(f"Total semantic chunks parsed: {len(loaded_docs)}")
            
    engine, is_ready = load_engine()
    
    if not is_ready:
        st.error("Failed to load transcripts. Ensure the .txt files are present.")
        return

    tab1, tab2, tab3 = st.tabs(["Interactive Q&A", "Interview Guide Answers", "Themes & Disagreements"])
    
    # --- TAB 1: Chat Interface ---
    with tab1:
        st.subheader("Cross-Transcript Q&A")
        user_query = st.chat_input("Ask a question (e.g., 'What is holding adoption back?')")
        
        if user_query:
            st.chat_message("user").write(user_query)
            with st.spinner("Searching transcripts..."):
                response = engine.ask_question(user_query)
            
            with st.chat_message("assistant"):
                st.write(response["answer"])
                
                with st.expander("View Source Citations"):
                    for doc in response["context"]:
                        st.markdown(f"**{doc.metadata.get('speaker')} ({doc.metadata.get('timestamp')})** - `{doc.metadata.get('source')}`")
                        st.write(doc.page_content)
                        st.divider()

    # --- TAB 2: Interview Guide ---
    with tab2:
        st.subheader("Automated Interview Guide Extraction")
        st.write("Click below to extract key answers across all markets.")
        if st.button("Run Extraction"):
            questions = [
                "What are the main barriers to adoption?",
                "How important is ROI and economics?",
                "What is the outlook for the next three to five years?",
                "How long does a purchase decision normally take?"
            ]
            for q in questions:
                st.markdown(f"### Q: {q}")
                with st.spinner(f"Extracting context for: {q}..."):
                    ans = engine.ask_question(q)
                st.write(ans["answer"])
                st.divider()
            if st.button("Run Extraction"):
                questions = [
                    "What are the main barriers to adoption?",
                    "How important is ROI and economics?",
                    "What is the outlook for the next three to five years?",
                    "How long does a purchase decision normally take?"
                ]
                for q in questions:
                    st.markdown(f"### Q: {q}")
                    with st.spinner(f"Extracting context for: {q}..."):
                        ans = engine.ask_question(q)
                    st.write(ans["answer"])
                    st.divider()
                
                    # Add a 3-second delay to prevent RESOURCE_EXHAUSTED errors
                    time.sleep(3)

    # --- TAB 3: Themes & Disagreements ---
    with tab3:
        st.subheader("Global Synthesis")
        if st.button("Analyze Transcripts"):
            with st.spinner("Synthesizing cross-market themes..."):
                analysis = engine.get_themes_and_disagreements()
                st.write(analysis)

if __name__ == "__main__":
    main()