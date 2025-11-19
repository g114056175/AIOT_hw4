# OpenSpec Change Proposal: RAG Q&A System with Streamlit

## 1. Feature Description

This proposal outlines the plan to build a web-based Question-Answering (Q&A) application using a Retrieval-Augmented Generation (RAG) architecture. The application will be built with Python and deployed using Streamlit.

The system will be able to answer questions based on a knowledge base provided by a document. Initially, it will use the "國立中興大學學生獎懲辦法.pdf" file. The core feature is to allow users to upload their own documents, which will then become the knowledge base for the RAG system.

The application will use the Gemini API for its Large Language Model (LLM) capabilities and will be explicitly configured to prevent web searching, ensuring answers are sourced only from the provided documents.

## 2. Files to be Created / Modified

### New Files:

- **`main.py`**: This will be the main entry point for the Streamlit application. It will contain all the UI logic and backend processing for the RAG chain.
- **`README.md`**: The main project README file. It will be populated with a project description, features, installation guide, and usage instructions.
- **`requirements.txt`**: A text file listing all the necessary Python dependencies for the project, ensuring reproducibility.
- **`helpers.py`** (Optional but recommended): A helper script to contain the RAG logic (document processing, vector store creation, Gemini API calls) to keep `main.py` clean and focused on UI.

### Modified Files:

- This is a new feature, so no existing project files will be modified.

## 3. Implementation Plan

The implementation will be broken down into the following key areas:

### a. `requirements.txt`

This file will contain the following packages:

```
streamlit
langchain
google-generativeai
pypdf
faiss-cpu
langchain-google-genai
```

### b. `README.md`

The README will be structured as follows:
- **Project Title:** AIOT HW4 - RAG Q&A with Streamlit
- **Description:** A Streamlit application that answers questions based on user-uploaded documents using RAG and the Gemini API.
- **Features:**
    - Interactive chat interface.
    - Dynamic knowledge base via multi-file upload (.pdf).
    - Checkbox-based selection of active RAG sources.
    - Answers generated exclusively from the provided document(s).
- **Installation:** `pip install -r requirements.txt`
- **Configuration:** Instructions on how to set the `GEMINI_API_KEY`.
- **Usage:** `streamlit run main.py`

### c. `main.py` (and `helpers.py`)

This will be the core of the application. The implementation will closely follow the patterns established in the user's provided `.ipynb` files.

**Phase 1: RAG Core Logic (`helpers.py`)**

1.  **Document Processing Function:**
    - Takes an uploaded file object as input.
    - Uses `PyPDFLoader` to load the document's content.
    - Uses `RecursiveCharacterTextSplitter` to break the text into manageable chunks.
    - Returns a list of document chunks.

2.  **Vector Store Creation Function:**
    - Takes the document chunks as input.
    - Uses `GoogleGenerativeAIEmbeddings` to convert the text chunks into vector embeddings.
    - Uses `FAISS` to create an in-memory vector store from the embeddings.
    - Returns the FAISS vector store object.

3.  **Answer Generation Function:**
    - Takes a user question and a *list* of selected FAISS retrievers as input.
    - Iterates through each selected retriever to find relevant document chunks.
    - Aggregates all retrieved chunks into a single context string.
    - Constructs a detailed prompt for the Gemini model. The prompt will include the aggregated chunks and the user's question, and will contain a strict instruction: **"You are a helpful assistant. Answer the user's question based ONLY on the following context. Do not use any external knowledge or web search. If the answer is not found in the context, state that you cannot find the answer in the provided documents."**
    - Initializes the `ChatGoogleGenerativeAI` model.
    - Sends the prompt to the Gemini API and returns the generated answer.

**Phase 2: Streamlit UI (`main.py`)**

1.  **UI Layout:**
    - The main area will be for the chat interface.
    - A sidebar on the left (`st.sidebar`) will be dedicated to RAG source management.

2.  **Sidebar (RAG Management):**
    - **API Key:** `st.text_input` for the Gemini API Key.
    - **File Uploader:** `st.file_uploader` configured for multi-file uploads (`accept_multiple_files=True`).
    - **RAG Source Selection:**
        - When files are uploaded, they will be processed into vector stores. A dictionary mapping filenames to their corresponding vector stores will be stored in `st.session_state`.
        - The sidebar will display a list of uploaded documents with a checkbox (`st.checkbox`) next to each one.
        - Users can tick the checkboxes to select which documents should be used as context for the next question.

3.  **Chat Interface (Main Area):**
    - Use `st.session_state` to store the chat history.
    - Display the conversation using `st.chat_message`.
    - Use `st.chat_input` for the user to type their question.
    - When a question is submitted:
        - Check which RAG sources are selected in the sidebar.
        - Call the answer generation function, passing the list of selected vector stores.
        - Add the user's question and the AI's answer to the chat history.
        - Rerun the app to display the new messages.

## 4. Next Steps

- Await user approval of this revised proposal.
- Upon approval, begin implementation by creating the `requirements.txt` and `README.md` files.
- Proceed with the implementation of `main.py` and `helpers.py`.
- Test the application with the provided PDF file.
- Commit the new files to the Git repository.
