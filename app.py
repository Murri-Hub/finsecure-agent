"""
app.py
Interfaccia Gradio per FinSecure AI Audit Agent
"""
import gradio as gr
import sys
import os

# Aggiungi path per import
sys.path.append("/content/finsecure-agent")

from agent.agent import agent_answer, generate_full_audit
from ingestion.parse_docs import parse_and_index

# Inizializzazione
print(" Avvio FinSecure AI Audit Agent...")
print(" Indicizzazione documenti...")
parse_and_index()
print(" Sistema pronto!")

# --- FUNZIONE CHAT SEMPLICE ---
# Usa agent_answer
def chat(message, history):
    """
    Funzione per chat interattiva
    
    Args:
        message: messaggio utente
        history: storico conversazione (gestito da Gradio)
    
    Returns:
        str: risposta dell'agente
    """
    try:
        response = agent_answer(message)
        return response
    except Exception as e:
        return f"Errore: {str(e)}\n\nRiprova con una domanda diversa."

# --- FUNZIONE AUDIT COMPLETO ---
# Usa generate_full_audit
def audit_completo(progress=gr.Progress()):
    """
    Esegue audit completo e restituisce risultati
    """
    try:
        progress(0, desc="Preparazione audit...")
        
        domande = [
            "Ci sono omissioni nel report Q2 2024?",
            "Come si confrontano Q1 e Q2 2024?",
            "Il documento è conforme alle regole di compliance?",
            "Qual è la predizione del trend di rischio per Q3?"
        ]
        
        risultati_testo = []
        
        for i, domanda in enumerate(domande):
            progress((i+1)/len(domande), desc=f"Analisi {i+1}/4...")
            risposta = agent_answer(domanda)
            risultati_testo.append(f"### ❓ {domanda}\n\n{risposta}\n\n{'='*80}\n")
        
        progress(1.0, desc="Generazione report...")
        risultati = generate_full_audit(domande)
        
        return (
            "\n".join(risultati_testo),
            risultati['dashboard'],
            risultati['pdf']
        )
    
    except Exception as e:
        return f"Errore durante l'audit: {str(e)}", None, None

# --- ESEMPI DI DOMANDE ---
esempi = [
    ["Ci sono omissioni nel report Q2 2024?"],
    ["Come si confrontano Q1 e Q2 2024?"],
    ["Il documento è conforme alle regole di compliance?"],
    ["Qual è la predizione del trend di rischio per Q3?"],
    ["Simula uno scenario di crisi sui dati Q2 2024"],
]

# --- INTERFACCIA GRADIO ---
with gr.Blocks(theme=gr.themes.Soft(), title="FinSecure AI Audit") as demo:
    
    gr.Markdown("""
    # FinSecure Analytics - AI Audit Agent
    
    Agente AI per la gestione del rischio finanziario e audit interattivi.
    Utilizza LlamaIndex, Machine Learning e analisi predittiva per supportare decisioni finanziarie.
    """)
    
    with gr.Tabs():
        
        # --- TAB 1: CHAT INTERATTIVA ---
        with gr.Tab(" Chat Interattiva"):
            gr.Markdown("""
            ### Fai domande sui report finanziari
            
            L'agente AI analizza i documenti Q1 e Q2 2024 per rispondere alle tue domande.
            """)
            
            chatbot = gr.ChatInterface(
                fn=chat,
                examples=esempi,
                title="",
                description="",
                retry_btn=None,
                undo_btn=None,
                clear_btn="🗑️ Pulisci chat",
            )
        
        # --- TAB 2: AUDIT COMPLETO ---
        with gr.Tab(" Audit Completo"):
            gr.Markdown("""
            ### Genera report completo automatico
            
            Esegue tutte le analisi (omissioni, confronto periodi, compliance, predizioni)
            e genera dashboard + PDF professionale.
            """)
            
            audit_btn = gr.Button(" Avvia Audit Completo", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column(scale=2):
                    risultati_output = gr.Markdown(label="Risultati Analisi")
                
                with gr.Column(scale=1):
                    dashboard_output = gr.Image(label="Dashboard Q1 vs Q2")
            
            pdf_output = gr.File(label="📄 Scarica Report PDF")
            
            audit_btn.click(
                fn=audit_completo,
                outputs=[risultati_output, dashboard_output, pdf_output]
            )
        
        # --- TAB 3: INFO ---
        with gr.Tab(" Informazioni"):
            gr.Markdown("""
            ## Funzionalità Implementate
            
            ### Analisi Automatizzata
            - Estrazione KPI (ricavi, margini, rischio, liquidità)
            - Identificazione omissioni e anomalie
            - Alert automatici su soglie critiche
            
            ### Simulazione Scenari
            - Scenario di crisi (ricavi -20%, rischio +50%)
            - Scenario di crescita (ricavi +15%, rischio -10%)
            - Scenario rialzo tassi (costi +10%, rischio +25%)
            
            ### Predizione Trend
            - Regressione lineare su dati storici Q1-Q2
            - Stima rischio Q3 con intervallo di confidenza
            - Raccomandazioni automatiche
            
            ### Dashboard e Report
            - Grafici comparativi professionali
            - Report PDF con tutte le analisi
            - Export dati per ulteriori elaborazioni
            
            ---
            
            ## Tecnologie Utilizzate
            
            - **LlamaIndex**: RAG e retrieval semantico
            - **HuggingFace**: Embeddings (bge-small) + LLM (Zephyr-7B)
            - **scikit-learn**: Predizioni ML
            - **Matplotlib/Seaborn**: Visualizzazioni
            - **FPDF**: Generazione report PDF
            
            ---
            
            ## Documenti Analizzati
            
            - Report Finanziario Q1 2024
            - Report Finanziario Q2 2024
            - Note di Audit Interno
            
            ---
            
            **Progetto**: Agente AI per Gestione Rischio Finanziario  
            **Versione**: 1.0  
            **Ambiente**: Google Colab + Gradio
            """)
    
    gr.Markdown("""
    ---
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
     Powered by LlamaIndex & HuggingFace | Dati fittizi per scopi dimostrativi
    </div>
    """)

# --- LANCIO APP ---
if __name__ == "__main__":
    demo.launch(
        share=True,  # Crea link pubblico temporaneo (72h)
        debug=True,
        server_name="0.0.0.0",  # Accessibile da qualsiasi IP
        server_port=7860
    )
