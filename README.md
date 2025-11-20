# AIOT HW4 - RAG Q&A System

## Project Summary & Process
(To be filled in by me)

---

## Project Description
This is a Retrieval-Augmented Generation (RAG) question-answering system built with Streamlit, LangChain, and the Google Gemini API. It allows users to ask questions about specific document content through an interactive chat interface.

This project not only supports real-time PDF document uploads as a knowledge base but also automatically loads pre-processed local knowledge bases stored in the `RAG_file` directory. This gives the system the dual capabilities of dynamic knowledge expansion and having a foundational knowledge base.

To demonstrate the value of RAG technology, the system will chat directly with the Gemini model when no RAG document source is selected. In this mode, the model may "hallucinate" due to a lack of specific domain knowledge. When a document source is selected, the model will provide precise answers based on the document's content.

Furthermore, the system features conversational memory, enabling it to understand context and engage in coherent, multi-turn dialogues in both RAG and non-RAG modes.

## Features

-   **Interactive Chat Interface**: Provides an intuitive UI for asking questions and receiving answers.
-   **PDF Document Upload**: Users can upload their own PDF files, which the system automatically processes into a searchable vector database.
-   **Automatic Loading of Local Knowledge Base**: On startup, the application automatically scans and loads all pre-processed FAISS indexes from the `RAG_file` directory to serve as a default knowledge base.
-   **Multiple Knowledge Source Selection**: Users can freely select which documents (both uploaded and default) to use as context for the current response via checkboxes in the sidebar.
-   **Conversational Memory**: In both pure chat and RAG modes, the model remembers previous conversations, allowing for context-aware follow-up questions.
-   **Vector Database Download**: Users can package and download the processed vector database (FAISS index) as a `.zip` file for future direct use.
-   **Model and API Key Configuration**: The Google API Key can be entered directly in the UI, and the system is configured to use the `gemini-2.0-flash-lite` model.

## Live Demo

You can interact with the application deployed on Streamlit Cloud via the following link:

[https://aiothw4-884u3yufyrjytbb2fya242.streamlit.app/](https://aiothw4-884u3yufyrjytbb2fya242.streamlit.app/)

### Example Usage: Demonstrating the Power of RAG

To see the difference RAG makes, try the following comparison. The default knowledge base `國立中興大學學生獎懲辦法.pdf_faiss_index (Default)` should be loaded automatically.

1.  **Without RAG**:
    -   In the sidebar, **uncheck** the box for `國立中興大學學生獎懲辦法.pdf_faiss_index (Default)`.
    -   Ask the question: `What does Article 5 of the NCHU Student Rewards and Punishments Regulations state?`
    -   **Expected Result**: The model has no specific knowledge of this document. It will likely apologize for not knowing the answer or provide a generic, made-up response (a "hallucination").

2.  **With RAG**:
    -   In the sidebar, **check** the box for `國立中興大學學生獎懲辦法.pdf_faiss_index (Default)`.
    -   Ask the same question: `What does Article 5 of the NCHU Student Rewards and Punishments Regulations state?`
    -   **Expected Result**: The model will now use the document as context and provide a precise answer based on the content of Article 5.

This comparison clearly illustrates how RAG grounds the model in factual, domain-specific knowledge, leading to more accurate and reliable answers.

## References

-   **Instructional Video**: [【李宏毅】生成式AI導論(2024)](https://www.youtube.com/watch?v=jF80Y8_BvEA&list=PL-eaXJVCzwbsXqWvQncPuuCg3wASAWWfO&index=7)
-   **RAG Implementation Reference**: [【Demo06a】RAG01_打造向量資料庫.ipynb](https://github.com/yenlung/AI-Demo/blob/master/%E3%80%90Demo06a%E3%80%91RAG01_%E6%89%93%E9%80%A0%E5%90%91%E9%87%8F%E8%B3%87%E6%96%99%E5%BA%AB.ipynb)

## Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/g114056175/AIOT_hw4.git
    cd AIOT_hw4
    ```

2.  **Install required packages**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit application**:
    ```bash
    streamlit run main.py
    ```
    The application will open in your browser. You can paste your Google API Key into the input box in the sidebar to get started.
