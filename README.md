# AIOT HW4 - RAG 問答系統

## 作業心得與流程
(此處由我填寫)

---

## 專案簡介 (Project Description)
這是一個使用 Streamlit、LangChain 和 Google Gemini API 構建的檢索增強生成 (Retrieval-Augmented Generation, RAG) 問答系統。它允許使用者透過互動式聊天介面，針對特定文件內容進行提問。

此專案不僅支援使用者即時上傳 PDF 文件作為知識庫，還能自動載入預先處理好的本地知識庫（存放於 `RAG_file` 資料夾中）。這使得本系統兼具了動態擴充知識與擁有基礎知識庫的能力。

為了展示 RAG 技術的價值，當沒有選擇任何 RAG 文件來源時，系統會直接與 Gemini 模型進行對話，此時模型可能會因為缺乏特定領域知識而產生「幻覺」(Hallucination)；而當選擇了文件來源後，模型則會根據文件內容提供精確的回答。

此外，系統具備對話記憶功能，無論在哪種模式下，都能理解上下文，進行有連貫性的多輪對話。

## 主要功能 (Features)

-   **互動式聊天介面**：提供一個直觀的 UI 來進行問答。
-   **支援 PDF 文件上傳**：使用者可以上傳自己的 PDF 文件，系統會自動處理並將其轉換為可供檢索的向量資料庫。
-   **自動載入本地知識庫**：啟動時會自動掃描並載入 `RAG_file` 目錄下的所有預處理好的 FAISS 索引，作為預設知識庫。
-   **多重知識來源選擇**：使用者可以透過側邊欄的核取方塊，自由選擇要啟用哪些文件（包含上傳的與預設的）作為當前回應的上下文。
-   **對話記憶**：在純聊天和 RAG 模式下，模型都能記住先前的對話，允許進行有上下文的追問。
-   **向量資料庫下載**：使用者可以將處理完成的向量資料庫 (FAISS index) 打包成 `.zip` 檔下載，方便未來直接載入使用。
-   **模型與 API 金鑰配置**：可在 UI 介面中直接輸入 Google API Key，並已配置使用 `gemini-2.0-flash-lite` 模型。

## DEMO 連結

您可以透過以下連結與部署在 Streamlit Cloud 上的應用程式進行互動：

[https://aiothw4-884u3yufyrjytbb2fya242.streamlit.app/](https://aiothw4-884u3yufyrjytbb2fya242.streamlit.app/)

## 參考資料 (References)

-   **教學影片**: [【李宏毅】生成式AI導論(2024)](https://www.youtube.com/watch?v=jF80Y8_BvEA&list=PL-eaXJVCzwbsXqWvQncPuuCg3wASAWWfO&index=7)
-   **RAG 技術實作參考**: [【Demo06a】RAG01_打造向量資料庫.ipynb](https://github.com/yenlung/AI-Demo/blob/master/%E3%80%90Demo06a%E3%80%91RAG01_%E6%89%93%E9%80%A0%E5%90%91%E9%87%8F%E8%B3%87%E6%96%99%E5%BA%AB.ipynb)

## 如何在本機端運行 (Local Setup)

1.  **複製專案庫**:
    ```bash
    git clone https://github.com/g114056175/AIOT_hw4.git
    cd AIOT_hw4
    ```

2.  **安裝所需套件**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **運行 Streamlit 應用**:
    ```bash
    streamlit run main.py
    ```
    應用程式將在您的瀏覽器中打開。您可以在側邊欄的輸入框中貼上您的 Google API Key 來開始使用。
