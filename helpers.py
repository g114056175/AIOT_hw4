import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate

def process_text_from_pdfs(pdf_docs):
    """
    Extracts and concatenates text from a list of uploaded PDF files.
    Args:
        pdf_docs (list): A list of uploaded file objects from Streamlit.
    Returns:
        str: A single string containing all the extracted text.
    """
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def get_text_chunks(text):
    """
    Splits a long text into smaller, manageable chunks.
    Args:
        text (str): The input text.
    Returns:
        list: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    return chunks

def create_vector_store(text_chunks, api_key):
    """
    Creates and returns a FAISS vector store from text chunks.
    Args:
        text_chunks (list): A list of text chunks.
        api_key (str): The Google Gemini API key.
    Returns:
        FAISS: A FAISS vector store object.
    """
    if not text_chunks:
        return None
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

async def generate_answer(user_question, vector_stores, api_key):
    """
    Generates an answer based on the user's question and selected vector stores.
    This is an async function.
    Args:
        user_question (str): The user's question.
        vector_stores (dict): A dictionary of available vector stores, keyed by filename.
        api_key (str): The Google Gemini API key.
    Returns:
        str: The generated answer.
    """
    if not vector_stores:
        return "Please upload and select at least one document to ask questions."

    # Define the prompt template with strict instructions
    prompt_template = """
    You are a helpful assistant. Answer the user's question based ONLY on the following context.
    Do not use any external knowledge or web search.
    If the answer is not found in the context, state that you cannot find the answer in the provided documents.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # Initialize the model and the QA chain
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", # Updated model name as per user's correction
        temperature=0.3,
        google_api_key=api_key,
        convert_system_message_to_human=True,
        request_timeout=60
    )
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    # Retrieve relevant documents from all selected vector stores
    all_docs = []
    for store in vector_stores.values():
        # FAISS similarity_search is not async, so we run it normally
        all_docs.extend(store.similarity_search(user_question))

    if not all_docs:
        return "No relevant information found in the selected documents for your question."

    # Generate the response asynchronously
    response = await chain.ainvoke({"input_documents": all_docs, "question": user_question}, return_only_outputs=True)
    return response["output_text"]
