import streamlit as st
import helpers
from langchain_google_genai import ChatGoogleGenerativeAI
import nest_asyncio

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
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = "RAG Mode" # Default mode

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("Controls")

    # API Key Hardcoded as per user's request
    gemini_api_key = "AIzaSyDYG6oTxQrHQxcx5T6ErtqC22sXSzqihmU"

    # Mode Selection
    st.session_state.chat_mode = st.radio(
        "Select Chat Mode",
        ("RAG Mode", "Direct LLM Chat Mode"),
        index=0 if st.session_state.chat_mode == "RAG Mode" else 1
    )

    if st.session_state.chat_mode == "RAG Mode":
        st.subheader("RAG Document Management")
        # File Uploader
        uploaded_files = st.file_uploader("Upload your PDF documents", type="pdf", accept_multiple_files=True)

        # Process and Store Vector Stores
        if uploaded_files and gemini_api_key:
            with st.spinner("Processing documents..."):
                for uploaded_file in uploaded_files:
                    # Only process new files
                    if uploaded_file.name not in st.session_state.vector_stores:
                        raw_text = helpers.process_text_from_pdfs([uploaded_file])
                        text_chunks = helpers.get_text_chunks(raw_text)
                        vector_store = helpers.create_vector_store(text_chunks, gemini_api_key)
                        if vector_store:
                            st.session_state.vector_stores[uploaded_file.name] = vector_store
                            st.success(f"Processed and indexed: {uploaded_file.name}")
                        else:
                            st.warning(f"Could not process text from: {uploaded_file.name}")

        st.subheader("Select RAG Sources")
        if not st.session_state.vector_stores:
            st.info("Upload documents to see available RAG sources.")
        else:
            # Use a dictionary to track the state of checkboxes
            selected_sources_dict = {}
            for filename in st.session_state.vector_stores.keys():
                selected_sources_dict[filename] = st.checkbox(filename, value=True, key=f"cb_{filename}")
            st.session_state.selected_sources_dict = selected_sources_dict # Store in session state

# --- Main Chat Interface ---

# Display chat messages
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_question := st.chat_input("Ask a question..."):
    # Add user message to chat history
    st.session_state.conversation.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Check for prerequisites
    if not gemini_api_key:
        st.warning("Please enter your Gemini API Key in the sidebar.")
    else:
        if st.session_state.chat_mode == "Direct LLM Chat Mode":
            with st.spinner("Thinking..."):
                try:
                    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, google_api_key=gemini_api_key)
                    response_obj = llm.invoke(user_question)
                    response = response_obj.content
                except Exception as e:
                    response = f"Error communicating with Gemini LLM: {e}"
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.conversation.append({"role": "assistant", "content": response})

        elif st.session_state.chat_mode == "RAG Mode":
            if not st.session_state.vector_stores:
                st.warning("Please upload at least one document for RAG Mode.")
            else:
                # Filter to get only the selected vector stores
                selected_stores_for_query = {
                    name: store for name, store in st.session_state.vector_stores.items()
                    if st.session_state.selected_sources_dict.get(name, False)
                }

                if not selected_stores_for_query:
                    st.warning("Please select at least one RAG source from the sidebar.")
                else:
                    # Generate and display AI response
                    with st.spinner("Thinking..."):
                        try:
                            response = helpers.generate_answer(user_question, selected_stores_for_query, gemini_api_key)
                        except Exception as e:
                            response = f"Error during RAG processing: {e}"
                    with st.chat_message("assistant"):
                        st.markdown(response)
                    # Add AI response to chat history
                    st.session_state.conversation.append({"role": "assistant", "content": response})
