"""
agent.py
Agente AI con tool per audit finanziari
"""

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from tools.tools import find_omissions, compare_periods, audit_compliance, predict_risk_trend
from tools.simulation import simulate_risk_scenario
from config.settings import BASE_DIR, RAW_DATA_DIR, PROCESSED_DIR, OUTPUT_DIR
from utils.color import B, X        # ANSI per print in grassetto
import os
import re

from config.models import setup_models
setup_models()

# PATH
BASE_DIR = "/content/finsecure-agent"
RAW_DATA_DIR = os.path.join(BASE_DIR, "data/raw")
INDEX_PATH = os.path.join(BASE_DIR, "data/processed/")

# LOAD / CREATE INDEX
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

# RETRIEVE CHUNKS
def retrieve_chunks(query, top_k=5):
    index = load_index()
    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="no_text"
    )
    response = query_engine.query(query)
    chunks = [node.node.text for node in response.source_nodes]
    return chunks, str(response)

# RETRIEVE CHUNKS BY METADATA
def retrieve_chunks_by_metadata(period, top_k=10):
    """
    Recupera chunk filtrati per periodo usando i metadata
    """
    index = load_index()
    
    filters = MetadataFilters(
        filters=[ExactMatchFilter(key="period", value=period)]
    )
    
    retriever = index.as_retriever(
        similarity_top_k=top_k,
        filters=filters
    )
    
    # Query generica per recuperare tutti i chunk del periodo
    nodes = retriever.retrieve("KPI ricavi margine rischio credito liquidità")
    chunks = [node.node.text for node in nodes]
    
    return chunks

# AGENT
def agent_answer(question: str):
    decision_log: dict[str, str] = {
        "tool_used": "none",
        "decision_reason": "Nessun tool specifico necessario"
    }
    
    chunks, base_answer = retrieve_chunks(question)
    question_lower = question.lower()
    
    # TOOL: Omissioni
    if "omission" in question_lower or "mancanza" in question_lower:
        decision_log["tool_used"] = "find_omissions"
        decision_log["decision_reason"] = (
            "La domanda richiede l'individuazione di informazioni mancanti "
            "o sezioni poco dettagliate nei documenti."
        )
        tool_result = find_omissions(chunks)
    
    # TOOL: Confronto periodi
    elif ("confront" in question_lower) or ("q1" in question_lower and "q2" in question_lower):
        decision_log["tool_used"] = "compare_periods"
        decision_log["decision_reason"] = (
            "La domanda richiede un confronto tra periodi temporali distinti "
            "per identificare variazioni di rischio."
        )
        # Usa il filtro metadata per separare Q1 e Q2
        chunks_q1 = retrieve_chunks_by_metadata("Q1 2024", top_k=15)
        chunks_q2 = retrieve_chunks_by_metadata("Q2 2024", top_k=15)
        tool_result = compare_periods(chunks_q1, chunks_q2)
    
    # TOOL: Compliance
    elif "compliance" in question_lower or "conforme" in question_lower:
        decision_log["tool_used"] = "audit_compliance"
        decision_log["decision_reason"] = (
            "La domanda riguarda la conformità normativa e richiede "
            "una verifica di possibili violazioni o eccezioni."
        )
        tool_result = audit_compliance(chunks)

    # TOOL: Predizione Trend
    elif "predizione" in question_lower or "previsione" in question_lower or "trend" in question_lower:
        decision_log["tool_used"] = "predict_risk_trend"
        decision_log["decision_reason"] = (
            "La domanda richiede una predizione del trend futuro "
            "basata sui dati storici disponibili."
        )
    
        # Estrae metriche Q1 e Q2
        chunks_q1 = retrieve_chunks_by_metadata("Q1 2024", top_k=15)
        chunks_q2 = retrieve_chunks_by_metadata("Q2 2024", top_k=15)
        
        # Estrae rischio da entrambi i periodi
        def extract_risk(chunks):
            for chunk in chunks:
                match = re.search(r'rischio.*?(\d+[,.]?\d*)\s*milioni', chunk.lower())
                if match:
                    return float(match.group(1).replace(',', '.'))
            return None
        
        q1_risk = extract_risk(chunks_q1)
        q2_risk = extract_risk(chunks_q2)
        
        if q1_risk and q2_risk:
            historical_data = {'q1_risk': q1_risk, 'q2_risk': q2_risk}
            tool_result = predict_risk_trend(historical_data)
        else:
            tool_result = "Impossibile predire: dati storici insufficienti"
    else:
        tool_result = None
        
    response = ""
    
    if tool_result:
        response = "[Analisi Tool]\n" + tool_result
    else:
        response = base_answer if base_answer else ""
    
    response += (
        "\n\n[Decision Logging]\n"
        f"Tool utilizzato: {decision_log['tool_used']}\n"
        f"Motivazione: {decision_log['decision_reason']}"
    )

    return response

# Dopo aver raccolto tutti i risultati, genera il report
def generate_full_audit(questions):
    """
    Esegue audit completo e genera report PDF + dashboard
    """
    from reports.report_generator import generate_audit_report
    from tools.visualization import generate_dashboard
    import re
    
    results = {
        'metadata': {
            'period': 'Q1-Q2 2024',
            'analyst': 'FinSecure AI Agent'
        }
    }
    
    # Variabili per dashboard
    q1_metrics = {}
    q2_metrics = {}
    
    # Esegue tutte le analisi
    for q in questions:
        answer = agent_answer(q)
        
        if "omission" in q.lower() or "mancanza" in q.lower():
            results['omissions'] = answer.split('[Analisi Tool]')[1].split('[Decision')[0].strip()
        
        elif "confront" in q.lower() or ("q1" in q.lower() and "q2" in q.lower()):
            comparison_text = answer.split('[Analisi Tool]')[1].split('[Decision')[0].strip()
            results['comparison'] = comparison_text
            
            # ESTRAE METRICHE PER IL DASHBOARD
            # Cerca pattern tipo "Q1: 11.8M → Q2: 12.4M"
            ricavi_match = re.search(r'Q1:\s*(\d+\.?\d*)M.*?Q2:\s*(\d+\.?\d*)M', comparison_text)
            if ricavi_match:
                q1_metrics['ricavi'] = float(ricavi_match.group(1))
                q2_metrics['ricavi'] = float(ricavi_match.group(2))
            
            margine_match = re.search(r'(\d+\.?\d*)%.*?→.*?(\d+\.?\d*)%', comparison_text)
            if margine_match:
                q1_metrics['margine'] = float(margine_match.group(1))
                q2_metrics['margine'] = float(margine_match.group(2))
            
            rischio_match = re.search(r'Q1:\s*(\d+\.?\d*)M.*?Q2:\s*(\d+\.?\d*)M', 
                                     comparison_text[comparison_text.find('rischio'):])
            if rischio_match:
                q1_metrics['rischio'] = float(rischio_match.group(1))
                q2_metrics['rischio'] = float(rischio_match.group(2))
        
        elif "compliance" in q.lower() or "conforme" in q.lower():
            results['compliance'] = answer.split('[Analisi Tool]')[1].split('[Decision')[0].strip()
        
        elif "simulazione" in q.lower() or "scenario" in q.lower():
            results['simulation'] = answer.split('[Analisi Tool]')[1].split('[Decision')[0].strip()
        
        elif "predizione" in q.lower() or "trend" in q.lower():
            results['prediction'] = answer.split('[Analisi Tool]')[1].split('[Decision')[0].strip()
    
    # GENERA DASHBOARD SE CI SONO METRICHE
    dashboard_path = None
    if q1_metrics and q2_metrics:
        print("\nGenerazione dashboard...")
        dashboard_path = generate_dashboard(q1_metrics, q2_metrics)
        print(f"Dashboard generata: {B}{dashboard_path}{X}")
    
    # Genera PDF (passa dashboard_path)
    pdf_path = generate_audit_report(analysis_results=results, dashboard_path=dashboard_path)
    print(f"Report PDF generato: {B}{pdf_path}{X}")
    
    return {
        'pdf': pdf_path,
        'dashboard': dashboard_path
    }
    

# MAIN
if __name__ == "__main__":
    print("FinSecure Agent – Modalità Agentic\n")
    while True:
        q = input("Domanda: ")
        if q.lower() in ["exit", "quit"]:
            break
        print("\nRisposta:\n")
        print(agent_answer(q))
        print("\n" + "-" * 60 + "\n")




