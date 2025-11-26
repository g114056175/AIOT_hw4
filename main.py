import streamlit as st
import nest_asyncio

# Apply the patch for asyncio right at the start
nest_asyncio.apply()

import helpers
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import asyncio
import os
import shutil
from langchain.vectorstores import FAISS
import io
import zipfile

def get_zip_file_bytes(vector_store, filename):
    TEMP_DIR = "./temp_download"
    save_path = os.path.join(TEMP_DIR, filename.replace(" ", "_") + "_faiss_index")
    
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    
    vector_store.save_local(save_path)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, _, files in os.walk(save_path):
            for file in files:
                zip_file.write(os.path.join(root, file), 
                               os.path.relpath(os.path.join(root, file), save_path))
    
    shutil.rmtree(TEMP_DIR) # Clean up after zipping
    return zip_buffer.getvalue()

# --- App Configuration ---
st.set_page_config(page_title="RAG Q&A with Gemini", layout="wide")
st.title("📄 RAG-based Q&A with Gemini")

# --- Session State Initialization ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "vector_stores" not in st.session_state:
    st.session_state.vector_stores = {}
if "selected_sources_dict" not in st.session_state:
    st.session_state.selected_sources_dict = {}

# --- Load Default RAG Indexes on Startup ---
DEFAULT_RAG_ROOT = "./RAG_file"
if "default_loaded" not in st.session_state:
    if os.path.exists(DEFAULT_RAG_ROOT) and os.path.isdir(DEFAULT_RAG_ROOT):
        try:
            with st.spinner("Loading default RAG sources..."):
                embeddings = helpers.get_hf_embeddings()
                for item in sorted(os.listdir(DEFAULT_RAG_ROOT), reverse=True):
                    item_path = os.path.join(DEFAULT_RAG_ROOT, item)
                    # Check if it's a directory and not already loaded
                    if os.path.isdir(item_path) and f"{item} (Default)" not in st.session_state.vector_stores:
                        default_vs = FAISS.load_local(item_path, embeddings, allow_dangerous_deserialization=True)
                        st.session_state.vector_stores[f"{item} (Default)"] = default_vs
            if st.session_state.vector_stores:
                st.toast("Default RAG sources loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load default RAG sources: {e}")
    st.session_state.default_loaded = True

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("API Key Configuration")
    google_api_key = st.text_input(
        "Enter your Google API Key:",
        value="AIzaSyDYG6oTxQrHQxcx5T6ErtqC22sXSzqihmU", # Default value as requested
        type="password" # Use password type for security
    )
    if not google_api_key:
        st.warning("Please enter your Google API Key to proceed.")
        st.stop()

    st.header("RAG Document Management")
    
    uploaded_files = st.file_uploader("Upload new PDF documents", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        with st.spinner("Processing documents..."):
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.vector_stores:
                    raw_text = helpers.process_text_from_pdfs([uploaded_file])
                    text_chunks = helpers.get_text_chunks(raw_text)
                    vector_store = helpers.create_vector_store(text_chunks)
                    if vector_store:
                        st.session_state.vector_stores[uploaded_file.name] = vector_store
                        st.success(f"Processed and indexed: {uploaded_file.name}")
                    else:
                        st.warning(f"Could not process text from: {uploaded_file.name}")

    st.subheader("Available RAG Sources")
    if not st.session_state.vector_stores:
        st.info("Upload a document or add a default RAG folder to begin.")
    else:
        # Use a dictionary to track checkbox states
        selected_sources_dict = {}
        for filename, vector_store in st.session_state.vector_stores.items():
            # Display checkbox and store its state
            is_selected = st.checkbox(filename, value=st.session_state.selected_sources_dict.get(filename, True), key=f"cb_{filename}")
            selected_sources_dict[filename] = is_selected
            
            # --- Single-Step Download Logic ---
            st.download_button(
                label="⬇️ Download",
                data=get_zip_file_bytes(vector_store, filename),
                file_name=f"{filename}_faiss_index.zip",
                mime="application/zip",
                key=f"dl_{filename}"
            )
            st.markdown("---") # Separator
        
        # Update the master dictionary of checkbox states
        st.session_state.selected_sources_dict = selected_sources_dict

# --- Main Chat Interface ---
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_question := st.chat_input("Ask a question..."):
    st.session_state.conversation.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Determine which vector stores are selected for the query
    selected_stores_for_query = {
        name: store for name, store in st.session_state.vector_stores.items()
        if st.session_state.selected_sources_dict.get(name, True)
    }

    # --- Query Logic ---
    if not selected_stores_for_query:
        # Fallback to direct LLM if no RAG source is selected
        st.info("No RAG source selected. Answering from general knowledge...")
        with st.spinner("Thinking..."):
            try:
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-lite",
                    temperature=0.7,
                    google_api_key=google_api_key,
                    convert_system_message_to_human=True,
                    request_timeout=120
                )
                
                # Send only the current question to the LLM, with Traditional Chinese instruction
                response_obj = llm.invoke(f"{user_question}\n\nPlease respond in Traditional Chinese.")
                response = response_obj.content
            except Exception as e:
                response = f"An error occurred while contacting the LLM: {type(e).__name__} - {e}"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.conversation.append({"role": "assistant", "content": response})

    else:
        # Use RAG to generate an answer (stateless)
        with st.spinner("Thinking with RAG..."):
            try:
                # Call the helper function with the original question
                response = helpers.generate_answer(
                    user_question,
                    selected_stores_for_query,
                    google_api_key
                )
            except Exception as e:
                response = f"An error occurred during RAG processing: {type(e).__name__} - {e}"
        
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.conversation.append({"role": "assistant", "content": response})