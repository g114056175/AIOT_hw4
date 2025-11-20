import streamlit as st
import helpers
from langchain_google_genai import ChatGoogleGenerativeAI
import nest_asyncio
import asyncio
import os
import shutil
from langchain.vectorstores import FAISS
import io
import zipfile

# Apply the patch for asyncio
nest_asyncio.apply()

# --- App Configuration ---
st.set_page_config(page_title="RAG Q&A with Gemini", layout="wide")
st.title("📄 RAG-based Q&A with Gemini")

# --- Session State Initialization ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "vector_stores" not in st.session_state:
    st.session_state.vector_stores = {}

# --- Load Default RAG Indexes on Startup ---
DEFAULT_RAG_ROOT = "./RAG_file"
if "default_loaded" not in st.session_state:
    if os.path.exists(DEFAULT_RAG_ROOT) and os.path.isdir(DEFAULT_RAG_ROOT):
        try:
            with st.spinner("Loading default RAG sources..."):
                embeddings = helpers.get_hf_embeddings()
                for item in os.listdir(DEFAULT_RAG_ROOT):
                    item_path = os.path.join(DEFAULT_RAG_ROOT, item)
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

    st.subheader("Select RAG Sources")
    if not st.session_state.vector_stores:
        st.info("Upload a document or add a default RAG folder to begin.")
    else:
        selected_sources_dict = {}
        for filename, vector_store in st.session_state.vector_stores.items():
            selected_sources_dict[filename] = st.checkbox(filename, value=True, key=f"cb_{filename}")
            
            # --- Stable Two-Step Download Logic ---
            zip_key = f"zip_bytes_{filename}"
            
            if st.button(f"Prepare Download for {filename}", key=f"prep_{filename}"):
                with st.spinner(f"Zipping {filename}..."):
                    TEMP_DIR = "./temp_download"
                    save_path = os.path.join(TEMP_DIR, filename.replace(" ", "_") + "_faiss_index")
                    
                    if os.path.exists(save_path):
                        shutil.rmtree(save_path)
                    
                    vector_store.save_local(save_path)
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                        for root, _, files in os.walk(save_path):
                            for file in files:
                                zip_file.write(os.path.join(root, file), 
                                               os.path.relpath(os.path.join(root, file), save_path))
                    
                    st.session_state[zip_key] = zip_buffer.getvalue()
                    shutil.rmtree(TEMP_DIR) # Clean up after zipping
                    st.success(f"{filename} is ready for download.")

            if zip_key in st.session_state:
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=st.session_state[zip_key],
                    file_name=f"{filename}_faiss_index.zip",
                    mime="application/zip",
                    key=f"dl_{filename}"
                )
        st.session_state.selected_sources_dict = selected_sources_dict

# --- Main Chat Interface ---
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_question := st.chat_input("Ask a question..."):
    st.session_state.conversation.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    selected_stores_for_query = {
        name: store for name, store in st.session_state.vector_stores.items()
        if st.session_state.get("selected_sources_dict", {}).get(name, False)
    }

    if not selected_stores_for_query:
        st.info("No RAG source selected. Answering from general knowledge...")
        with st.spinner("Thinking..."):
            try:
                async def get_llm_response(question):
import streamlit as st
import helpers
from langchain_google_genai import ChatGoogleGenerativeAI
import nest_asyncio
import asyncio
import os
import shutil
from langchain.vectorstores import FAISS
import io
import zipfile

# Apply the patch for asyncio
nest_asyncio.apply()

# --- App Configuration ---
st.set_page_config(page_title="RAG Q&A with Gemini", layout="wide")
st.title("📄 RAG-based Q&A with Gemini")

# --- Session State Initialization ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "vector_stores" not in st.session_state:
    st.session_state.vector_stores = {}
if "view" not in st.session_state:
    st.session_state.view = 'chat' # Default view
if "selected_rag_file_for_details" not in st.session_state:
    st.session_state.selected_rag_file_for_details = None

# --- Load Default RAG Indexes on Startup ---
DEFAULT_RAG_ROOT = "./RAG_file"
if "default_loaded" not in st.session_state:
    if os.path.exists(DEFAULT_RAG_ROOT) and os.path.isdir(DEFAULT_RAG_ROOT):
        try:
            with st.spinner("Loading default RAG sources..."):
                embeddings = helpers.get_hf_embeddings()
                for item in os.listdir(DEFAULT_RAG_ROOT):
                    item_path = os.path.join(DEFAULT_RAG_ROOT, item)
                    if os.path.isdir(item_path) and f"{item} (Default)" not in st.session_state.vector_stores:
                        default_vs = FAISS.load_local(item_path, embeddings, allow_dangerous_deserialization=True)
                        st.session_state.vector_stores[f"{item} (Default)"] = default_vs
            if st.session_state.vector_stores:
                st.toast("Default RAG sources loaded successfully!")
        except Exception as e:
            st.error(f"Failed to load default RAG sources: {e}")
    st.session_state.default_loaded = True

# --- Helper function to render RAG Details View ---
def render_rag_details_view():
    filename = st.session_state.selected_rag_file_for_details
    if filename and filename in st.session_state.vector_stores:
        st.header(f"Details for: {filename}")
        
        if st.button("← Back to Chat"):
            st.session_state.view = 'chat'
            st.session_state.selected_rag_file_for_details = None
            st.experimental_rerun()

        vector_store = st.session_state.vector_stores[filename]
        
        # --- Stable Two-Step Download Logic ---
        zip_key = f"zip_bytes_{filename}"
        
        if st.button(f"Prepare Download for {filename}", key=f"prep_details_{filename}"):
            with st.spinner(f"Zipping {filename}..."):
                TEMP_DIR = "./temp_download"
                save_path = os.path.join(TEMP_DIR, filename.replace(" ", "_") + "_faiss_index")
                
                if os.path.exists(save_path):
                    shutil.rmtree(save_path)
                
                vector_store.save_local(save_path)
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    for root, _, files in os.walk(save_path):
                        for file in files:
                            zip_file.write(os.path.join(root, file), 
                                           os.path.relpath(os.path.join(root, file), save_path))
                
                st.session_state[zip_key] = zip_buffer.getvalue()
                shutil.rmtree(TEMP_DIR) # Clean up after zipping
                st.success(f"{filename} is ready for download.")

        if zip_key in st.session_state:
            st.download_button(
                label=f"⬇️ Download {filename}",
                data=st.session_state[zip_key],
                file_name=f"{filename}_faiss_index.zip",
                mime="application/zip",
                key=f"dl_details_{filename}"
            )
    else:
        st.error("No RAG file selected for details.")

# --- Sidebar for Controls ---
with st.sidebar:
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
        for filename in st.session_state.vector_stores.keys():
            if st.button(filename, key=f"select_rag_{filename}"):
                st.session_state.selected_rag_file_for_details = filename
                st.session_state.view = 'rag_details'
                st.experimental_rerun()
        
        st.subheader("Active RAG Sources for Chat")
        selected_sources_dict = {}
        for filename in st.session_state.vector_stores.keys():
            selected_sources_dict[filename] = st.checkbox(filename, value=True, key=f"cb_{filename}")
        st.session_state.selected_sources_dict = selected_sources_dict

# --- Main Content Area ---
if st.session_state.view == 'chat':
    # --- Main Chat Interface ---
    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_question := st.chat_input("Ask a question..."):
        st.session_state.conversation.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        selected_stores_for_query = {
            name: store for name, store in st.session_state.vector_stores.items()
            if st.session_state.get("selected_sources_dict", {}).get(name, False)
        }

        if not selected_stores_for_query:
            st.info("No RAG source selected. Answering from general knowledge...")
            with st.spinner("Thinking..."):
                try:
                    async def get_llm_response(question):
                        llm = ChatGoogleGenerativeAI(
                            model="gemini-2.5-flash-image", # Updated model name
                            temperature=0.7,
                            google_api_key="AIzaSyDYG6oTxQrHQxcx5T6ErtqC22sXSzqihmU",
                            convert_system_message_to_human=True,
                            request_timeout=60
                        )
                        response_obj = await llm.ainvoke(question)
                        return response_obj.content
                    response = asyncio.run(get_llm_response(user_question))
                except Exception as e:
                    response = f"An error occurred: {type(e).__name__} - {e}"
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.conversation.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Thinking with RAG..."):
                try:
                    response = asyncio.run(helpers.generate_answer(user_question, selected_stores_for_query, "AIzaSyDYG6oTxQrHQxcx5T6ErtqC22sXSzqihmU"))
                except Exception as e:
                    response = f"An error occurred during RAG processing: {type(e).__name__} - {e}"
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.conversation.append({"role": "assistant", "content": response})
elif st.session_state.view == 'rag_details':
    render_rag_details_view()
                    response_obj = await llm.ainvoke(question)
                    return response_obj.content
                response = asyncio.run(get_llm_response(user_question))
            except Exception as e:
                response = f"An error occurred: {type(e).__name__} - {e}"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.conversation.append({"role": "assistant", "content": response})
    else:
        with st.spinner("Thinking with RAG..."):
            try:
                response = asyncio.run(helpers.generate_answer(user_question, selected_stores_for_query, "AIzaSyDYG6oTxQrHQxcx5T6ErtqC22sXSzqihmU"))
            except Exception as e:
                response = f"An error occurred during RAG processing: {type(e).__name__} - {e}"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.conversation.append({"role": "assistant", "content": response})
