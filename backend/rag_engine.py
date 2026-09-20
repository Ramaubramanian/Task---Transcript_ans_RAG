from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.data_parser import parse_transcripts

class TranscriptRAG:
    def __init__(self):
        # Using the current active embedding model
        self.embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
        self.llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0)
        self.vector_store = None

    def initialize_knowledge_base(self) -> bool:
        docs = parse_transcripts()
        if docs:
            self.vector_store = FAISS.from_documents(docs, self.embeddings)
            return True
        return False

    def ask_question(self, query: str) -> dict:
        if not self.vector_store:
            return {"answer": "Knowledge base not initialized.", "context": []}

        # INCREASE k=20 to ensure chunks from France, Germany, and the UK are ALL retrieved
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 20})
        docs = retriever.invoke(query)
        
        # Format the chunks manually to inject the metadata cleanly
        context_text = "\n\n".join(
            [f"[{doc.metadata.get('source', 'Unknown')} - {doc.metadata.get('speaker', 'Unknown')} - {doc.metadata.get('timestamp', '00:00')}]:\n{doc.page_content}" 
             for doc in docs]
        )
        
        # Update the prompt to aggressively demand answers for all 3 experts
        prompt = ChatPromptTemplate.from_template(
            """Answer the user's question using ONLY the provided context. 
            You MUST provide a comprehensive answer that includes the perspectives of ALL THREE experts (France, Germany, UK).
            Break down your answer paragraph by paragraph for each expert.
            You MUST include exact quotes. Append the timestamp and speaker from the context metadata directly after every quote: [Speaker - MM:SS].
            
            Context: {context}
            Question: {question}
            Answer:"""
        )
        
        chain = prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context_text, "question": query})
        
        return {"answer": answer, "context": docs}

    def get_themes_and_disagreements(self) -> str:
        all_docs = parse_transcripts()
        
        context_text = "\n\n".join(
            [f"[{doc.metadata.get('source', 'Unknown')} - {doc.metadata.get('speaker', 'Unknown')}]: {doc.page_content}" 
             for doc in all_docs]
        )
        
        prompt = ChatPromptTemplate.from_template(
            """You are analyzing 3 expert call transcripts about robotic surgery adoption.
            Based on the overarching context of these discussions:
            1. Identify 3 common themes all experts agree on.
            2. Identify any specific disagreements or differences in opinion across the markets (France, Germany, UK).
            
            Context: {context}
            Analysis:"""
        )
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"context": context_text})