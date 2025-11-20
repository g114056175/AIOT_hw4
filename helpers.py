import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

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

    # --- Combine all selected vector stores into a single retriever ---
    # Create a list of all documents from all selected vector stores
    all_retrieved_docs = []
    for store in vector_stores.values():
        # Perform a similarity search on each store to get its documents
        # This is a workaround as FAISS.merge_from requires an existing index
        # and we need to combine documents for a single retriever.
        # For simplicity, we'll just get all documents and create a new FAISS from them.
        # A more efficient approach for very large numbers of documents would be to
        # merge the FAISS indexes directly if possible, or use a custom multi-store retriever.
        all_retrieved_docs.extend(store.similarity_search(user_question, k=5)) # k=5 is arbitrary, can be tuned

    if not all_retrieved_docs:
        return "No relevant information found in the selected documents for your question."

    # Create a temporary FAISS store from the combined documents to act as a single retriever
    # This ensures all selected sources contribute to the retrieval.
    # Note: This re-embeds documents, which is not ideal for performance but ensures correctness.
    # A better approach would be to merge the FAISS indexes directly if possible.
    temp_faiss_store = FAISS.from_documents(all_retrieved_docs, get_hf_embeddings())
    retriever = temp_faiss_store.as_retriever()

    # Create a memory object to hold the conversation history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    for msg in chat_history:
        if isinstance(msg, HumanMessage):
            memory.chat_memory.add_user_message(msg.content)
        else:
            memory.chat_memory.add_ai_message(msg.content)

    # Define the prompt for the final document combination step
    qa_prompt_template = """
    Use the following pieces of context to answer the user's question. If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Please respond in Traditional Chinese.

    Context: {context}
    Question: {question}
    Helpful Answer:"""
    QA_PROMPT = PromptTemplate(
        template=qa_prompt_template, input_variables=["context", "question"]
    )

    # Define the prompt for condensing the question (for conversational chain)
    condense_question_prompt_template = """
    Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    CONDENSE_QUESTION_PROMPT = PromptTemplate(
        template=condense_question_prompt_template, input_variables=["chat_history", "question"]
    )

    # Create the conversational chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT,
        combine_docs_chain_kwargs={"prompt": QA_PROMPT}
    )
    
    # Invoke the chain
    response = conversation_chain({'question': user_question})
    return response['answer']
