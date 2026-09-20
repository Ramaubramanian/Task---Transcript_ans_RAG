# Expert Call Analyzer - RAG Pipeline

A Retrieval-Augmented Generation (RAG) application built to analyze expert call transcripts. It answers specific interview guides, extracts exact quotes, maintains timestamp provenance, and performs cross-document thematic synthesis.

## Architecture & Tech Stack
*   **UI Framework:** Streamlit
*   **Orchestration:** LangChain (using modern LCEL architecture)
*   **LLM:** Google Gemini 3.5 Flash (chosen for fast inference and massive context windows)
*   **Vector Store:** FAISS (runs entirely locally for easy evaluation)
*   **Embeddings:** Google Generative AI Embeddings

## Key Engineering Decisions
1.  **Custom Chunking for Provenance:** Standard text splitters destroy metadata. This pipeline uses a custom parser (`data_parser.py`) to inject the `Speaker` and `Timestamp` directly into the metadata of every chunk.
2.  **LCEL Routing:** Uses LangChain Expression Language (LCEL) over legacy wrapper chains to explicitly format and pipe context, reducing hallucination risk.
3.  **Global Synthesis:** Standard semantic search struggles with global summaries. The "Themes & Disagreements" feature bypasses the vector store to inject the entire document corpus directly into the LLM context window for a holistic analysis.

## Setup Instructions
This project uses `uv` for lightning-fast dependency management.

1.  **Clone the repository and initialize the environment:**
    ```bash
    uv python pin 3.12
    uv venv
    ```
2.  **Activate the virtual environment:**
    *   *Windows:* `.venv\Scripts\activate`
    *   *Mac/Linux:* `source .venv/bin/activate`
3.  **Install dependencies:**
    ```bash
    uv add streamlit langchain langchain-google-genai langchain-community faiss-cpu python-dotenv
    ```
4.  **Environment Variables:**
    Create a `.env` file in the root directory and add your API key:
    ```env
    GOOGLE_API_KEY="your_api_key_here"
    ```
5.  **Run the App:**
    ```bash
    streamlit run app.py
    ```