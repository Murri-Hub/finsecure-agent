"""
parse_docs.py
Parsing e indicizzazione documenti finanziari (versione Colab)
"""

import os
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# --- PATH ---
BASE_DIR = "/content/drive/MyDrive/finsecure-agent"
RAW_DATA_DIR = f"{BASE_DIR}/data/raw"
PROCESSED_DIR = f"{BASE_DIR}/data/processed"
INDEX_SAVE_PATH = PROCESSED_DIR

os.makedirs(PROCESSED_DIR, exist_ok=True)

def parse_and_index():
    documents = []

    for filename in os.listdir(RAW_DATA_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(RAW_DATA_DIR, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            doc_type = "audit" if "audit" in filename.lower() else "report"

            if "Q1" in filename:
                period = "Q1 2024"
            elif "Q2" in filename:
                period = "Q2 2024"
            else:
                period = "2024"

            paragraphs = content.split("\n\n")

            for idx, para in enumerate(paragraphs):
                if para.strip():
                    documents.append(
                        Document(
                            text=para.strip(),
                            metadata={
                                "source_file": filename,
                                "type": doc_type,
                                "period": period,
                                "chunk_id": idx
                            }
                        )
                    )

    print(f"[INFO] Chunk creati: {len(documents)}")

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=INDEX_SAVE_PATH)

    print(f"[INFO] Indice salvato in {INDEX_SAVE_PATH}")

if __name__ == "__main__":
    parse_and_index()
