import streamlit as st
import helpers

# --- App Configuration ---
st.set_page_config(page_title="RAG Q&A with Gemini", layout="wide")
st.title("📄 RAG-based Q&A with Gemini")

# --- Session State Initialization ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "vector_stores" not in st.session_state:
    st.session_state.vector_stores = {}

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("Controls")

    # API Key Input
    gemini_api_key = st.text_input("Gemini API Key", type="password", help="Get your key from https://aistudio.google.com/app/apikey")

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

# --- Main Chat Interface ---

# Display chat messages
for message in st.session_state.conversation:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_question := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.conversation.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # Check for prerequisites
    if not gemini_api_key:
        st.warning("Please enter your Gemini API Key in the sidebar.")
    elif not st.session_state.vector_stores:
        st.warning("Please upload at least one document.")
    else:
        # Filter to get only the selected vector stores
        selected_stores_for_query = {
            name: store for name, store in st.session_state.vector_stores.items()
            if selected_sources_dict.get(name, False)
        }

        if not selected_stores_for_query:
            st.warning("Please select at least one RAG source from the sidebar.")
        else:
            # Generate and display AI response
            with st.spinner("Thinking..."):
                response = helpers.generate_answer(user_question, selected_stores_for_query, gemini_api_key)
                with st.chat_message("assistant"):
                    st.markdown(response)
                # Add AI response to chat history
                st.session_state.conversation.append({"role": "assistant", "content": response})
