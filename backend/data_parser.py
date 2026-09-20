import os
import re
from langchain_core.documents import Document

def parse_transcripts(data_dir: str = "data") -> list[Document]:
    documents = []
    
    # Fallback to the root directory if 'data' folder is empty or missing
    search_dir = data_dir if os.path.exists(data_dir) and any(f.endswith('.txt') for f in os.listdir(data_dir)) else "."

    for filename in os.listdir(search_dir):
        if not filename.endswith(".txt"):
            continue
            
        file_path = os.path.join(search_dir, filename)
        # Use errors="ignore" to prevent encoding crashes on Windows
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
            
        # Bulletproof split: handles \r\n, \n, and accidental spaces between blocks
        blocks = re.split(r'\n\s*\n', text.strip())
        
        for block in blocks:
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            if len(lines) >= 2:
                timestamp = lines[0]
                
                # Forgiving timestamp regex to catch any MM:SS format
                if re.search(r"\d{1,2}:\d{2}", timestamp):
                    content = " ".join(lines[1:])
                    speaker = content.split(":", 1)[0] if ":" in content else "Unknown"
                    
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": filename,
                            "timestamp": timestamp,
                            "speaker": speaker
                        }
                    )
                    documents.append(doc)
    return documents