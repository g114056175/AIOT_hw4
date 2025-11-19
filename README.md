# AIOT HW4 - RAG Q&A with Streamlit

## Description

A Streamlit application that answers questions based on user-uploaded documents using a Retrieval-Augmented Generation (RAG) architecture and the Google Gemini API.

## Features

-   **Interactive Chat Interface:** A user-friendly chat UI to ask questions and get answers.
-   **Dynamic Knowledge Base:** Upload one or more PDF documents (`.pdf`) to create a dynamic knowledge base.
-   **Source Selection:** Use checkboxes in the sidebar to dynamically select which uploaded documents should be used as context for the RAG system.
-   **Context-Aware Answers:** The LLM is instructed to answer questions based *only* on the content of the selected documents, preventing reliance on external knowledge.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/g114056175/AIOT_hw4.git
    cd AIOT_hw4
    ```

2.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the application, you need to get a Google Gemini API Key.

1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create an API key.
2.  When you run the application, paste this key into the "Gemini API Key" input box in the sidebar.

## Usage

Run the Streamlit application with the following command:

```bash
streamlit run main.py
```

The application will open in your web browser. You can then upload your documents and start asking questions.
