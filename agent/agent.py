"""
agent.py
Agente AI con ReActAgent per audit finanziari
"""
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.react.base import ReActAgent
from tools.tools import omissions_tool, comparison_tool, compliance_tool, risk_trend_tool, scenario_tool
from config.settings import RAW_DATA_DIR, PROCESSED_DIR
import os

# INDICE CACHATO - evita ricostruzione ad ogni chiamata
_index = None

def load_index():
    global _index
    if _index is not None:
        return _index
    
    if os.path.exists(os.path.join(PROCESSED_DIR, "docstore.json")):
        storage_context = StorageContext.from_defaults(persist_dir=PROCESSED_DIR)
        _index = load_index_from_storage(storage_context)
    else:
        documents = SimpleDirectoryReader(RAW_DATA_DIR).load_data()
        _index = VectorStoreIndex.from_documents(documents)
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        _index.storage_context.persist(persist_dir=PROCESSED_DIR)
    
    return _index

def retrieve_chunks(query, top_k=5):
    index = load_index()
    query_engine = index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="no_text"
    )
    response = query_engine.query(query)
    chunks = [node.node.text for node in response.source_nodes]
    return chunks, str(response)

def retrieve_chunks_by_metadata(period, top_k=10):
    index = load_index()
    filters = MetadataFilters(
        filters=[ExactMatchFilter(key="period", value=period)]
    )
    retriever = index.as_retriever(
        similarity_top_k=top_k,
        filters=filters
    )
    nodes = retriever.retrieve("KPI ricavi margine rischio credito liquidità")
    return [node.node.text for node in nodes]

def build_agent():
    """Costruisce e restituisce il ReActAgent con tutti i tool"""
    tools = [
        FunctionTool.from_defaults(
            fn=omissions_tool,
            name="find_omissions",
            description=(
                "Analizza i documenti finanziari e identifica omissioni, "
                "vaghezze o dati mancanti. Usare quando si chiedono dati mancanti, "
                "sezioni incomplete o informazioni non specificate."
            )
        ),
        FunctionTool.from_defaults(
            fn=comparison_tool,
            name="compare_periods",
            description=(
                "Confronta le metriche finanziarie tra Q1 2024 e Q2 2024. "
                "Usare quando si chiede un confronto tra trimestri o variazioni "
                "di ricavi, margine operativo o esposizione al rischio."
            )
        ),
        FunctionTool.from_defaults(
            fn=compliance_tool,
            name="audit_compliance",
            description=(
                "Verifica la conformità normativa dei documenti finanziari. "
                "Usare quando si chiede di compliance, violazioni normative "
                "o completezza documentale."
            )
        ),
        FunctionTool.from_defaults(
            fn=risk_trend_tool,
            name="predict_risk_trend",
            description=(
                "Predice il trend del rischio per Q3 2024 usando regressione "
                "lineare su dati storici Q1-Q2. Usare per previsioni, "
                "predizioni o trend futuri del rischio."
            )
        ),
        FunctionTool.from_defaults(
            fn=scenario_tool,
            name="simulate_scenario",
            description=(
                "Simula scenari di rischio finanziario (crisis, growth, interest_hike). "
                "Usare quando si chiede una simulazione, uno scenario ipotetico "
                "o un'analisi what-if."
            )
        ),
    ]
    
    return ReActAgent.from_tools(
        tools,
        llm=Settings.llm,
        verbose=True,
        max_iterations=10,
    )

# AGENT CACHATO
_agent = None

def agent_answer(question: str) -> str:
    global _agent
    if _agent is None:
        try:
            _agent = build_agent()
        except Exception as e:
            return f"Errore in build_agent: {type(e).__name__}: {str(e)}"
    
    try:
        response = _agent.chat(question)
        return str(response)
    except Exception as e:
        return f"Errore in chat: {type(e).__name__}: {str(e)}"

def extract_metrics_for_dashboard() -> tuple[dict, dict]:
    """
    Estrae metriche Q1 e Q2 direttamente dai chunk indicizzati,
    senza dipendere dal formato testuale della risposta del ReActAgent.
    """
    import re

    chunks_q1 = retrieve_chunks_by_metadata("Q1 2024")
    chunks_q2 = retrieve_chunks_by_metadata("Q2 2024")

    def extract_from_chunks(chunks):
        metrics = {}
        all_text = " ".join(chunks).lower()

        match = re.search(r'ricavi.*?(\d+[,.]?\d*)\s*milioni', all_text)
        if match:
            metrics['ricavi'] = float(match.group(1).replace(',', '.'))

        match = re.search(r'margine operativo.*?(\d+[,.]?\d*)%', all_text)
        if match:
            metrics['margine'] = float(match.group(1).replace(',', '.'))

        match = re.search(r'rischio di credito.*?(\d+[,.]?\d*)\s*milioni', all_text)
        if match:
            metrics['rischio'] = float(match.group(1).replace(',', '.'))

        return metrics

    return extract_from_chunks(chunks_q1), extract_from_chunks(chunks_q2)


