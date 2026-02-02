"""
agent.py
Agente AI con tool per audit finanziari (Agentic AI)
"""
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from tools.tools import find_omissions, compare_periods, audit_compliance
import os

# --- CONFIGURAZIONE MODELLI LOCALI ---
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

Settings.llm = HuggingFaceLLM(
    model_name="HuggingFaceH4/zephyr-7b-beta",
    tokenizer_name="HuggingFaceH4/zephyr-7b-beta",
    context_window=3900,
    max_new_tokens=256,
    generate_kwargs={"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    device_map="auto",
)

# --- PATH ---
BASE_DIR = "/content/finsecure-agent"
RAW_DATA_DIR = os.path.join(BASE_DIR, "data/raw")
INDEX_PATH = os.path.join(BASE_DIR, "data/processed/")

# --- LOAD / CREATE INDEX ---
def load_index():
    if os.path.exists(os.path.join(INDEX_PATH, "docstore.json")):
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_PATH)
        index = load_index_from_storage(storage_context)
    else:
        documents = SimpleDirectoryReader(RAW_DATA_DIR).load_data()
        index = VectorStoreIndex.from_documents(documents)
        os.makedirs(INDEX_PATH, exist_ok=True)
        index.storage_context.persist(persist_dir=INDEX_PATH)
    return index

# --- RETRIEVE CHUNKS ---
def retrieve_chunks(query, top_k=5):
    index = load_index()
    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="no_text"
    )
    response = query_engine.query(query)
    chunks = [node.node.text for node in response.source_nodes]
    return chunks, str(response)

# --- AGENT ---
def agent_answer(question: str):
    decision_log: dict[str, str] = {
        "tool_used": "none",
        "decision_reason": "Nessun tool specifico necessario"
    }
    
    chunks, base_answer = retrieve_chunks(question)
    question_lower = question.lower()
    
    # --- TOOL: Omissioni ---
    if "omission" in question_lower or "mancanza" in question_lower:
        decision_log["tool_used"] = "find_omissions"
        decision_log["decision_reason"] = (
            "La domanda richiede l'individuazione di informazioni mancanti "
            "o sezioni poco dettagliate nei documenti."
        )
        tool_result = find_omissions(chunks)
    
    # --- TOOL: Confronto periodi ---
    elif ("confront" in question_lower) or ("q1" in question_lower and "q2" in question_lower):
        decision_log["tool_used"] = "compare_periods"
        decision_log["decision_reason"] = (
            "La domanda richiede un confronto tra periodi temporali distinti "
            "per identificare variazioni di rischio."
        )
        chunks_q1, _ = retrieve_chunks("Q1 2024 rischio finanziario")
        chunks_q2, _ = retrieve_chunks("Q2 2024 rischio finanziario")
        tool_result = compare_periods(chunks_q1, chunks_q2)
    
    # --- TOOL: Compliance ---
    elif "compliance" in question_lower or "conforme" in question_lower:
        decision_log["tool_used"] = "audit_compliance"
        decision_log["decision_reason"] = (
            "La domanda riguarda la conformità normativa e richiede "
            "una verifica di possibili violazioni o eccezioni."
        )
        tool_result = audit_compliance(chunks)
    
    else:
        tool_result = None
    
    response = base_answer
    if tool_result:
        response += "\n\n[Analisi Tool]\n" + tool_result
    
    response += (
        "\n\n[Decision Logging]\n"
        f"Tool utilizzato: {decision_log['tool_used']}\n"
        f"Motivazione: {decision_log['decision_reason']}"
    )
    
    return response

# --- MAIN ---
if __name__ == "__main__":
    print("FinSecure Agent – Modalità Agentic\n")
    while True:
        q = input("Domanda: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("\nRisposta:\n")
        print(agent_answer(q))
        print("\n" + "-" * 60 + "\n")
