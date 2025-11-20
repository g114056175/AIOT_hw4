import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage

def get_hf_embeddings():
    """Initializes and returns the HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def create_vector_store(text_chunks):
    """
    Creates and returns a FAISS vector store from text chunks using a HuggingFace model.
    Args:
        text_chunks (list): A list of text chunks.
    Returns:
        FAISS: A FAISS vector store object, or None if input is empty.
    """
    if not text_chunks:
        print("Warning: Text chunks are empty. Cannot create vector store.")
        return None
    embeddings = get_hf_embeddings()
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def generate_answer(user_question, vector_stores, api_key, chat_history):
    """
    Generates an answer based on the user's question, selected vector stores, and chat history.
    This is a synchronous function.
    Args:
        user_question (str): The user's question.
        vector_stores (dict): A dictionary of available vector stores.
        api_key (str): The Google Gemini API key.
        chat_history (list): A list of AIMessage and HumanMessage objects.
    Returns:
        str: The generated answer.
    """
    if not vector_stores:
        return "Please upload and select at least one document to ask questions."

    # Initialize the model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.3,
        google_api_key=api_key,
        convert_system_message_to_human=True,
        request_timeout=60
    )

    # Create a unified retriever from all selected vector stores
    # This is a simplified approach. A more robust solution would merge the FAISS indexes.
    # For now, we'll just use the first one selected. This is a limitation to be aware of.
    # A better approach would be to merge the stores, but FAISS doesn't support that directly.
    # We will create a retriever from the first selected store.
    if vector_stores:
        main_store = list(vector_stores.values())[0]
        # We can merge documents from other stores into the main one if needed, but for now, we use one.
        retriever = main_store.as_retriever()
    else:
        return "No RAG source selected."

    # Create a memory object to hold the conversation history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            memory.chat_memory.add_user_message(msg.content)
        else:
            memory.chat_memory.add_ai_message(msg.content)

    # Create the conversational chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory
    )
    
    # Invoke the chain
    response = conversation_chain({'question': user_question})
    return response['answer']
