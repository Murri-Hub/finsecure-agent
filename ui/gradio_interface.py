"""
ui/gradio_interface.py
Interfaccia Gradio per FinSecure AI Audit Agent
"""
import gradio as gr
import shutil
import os
from agent.agent import agent_answer


def chat(message, history):
    """Funzione chat per Gradio - delega tutto al ReActAgent"""
    try:
        return agent_answer(message)
    except Exception as e:
        return f"Errore nell'elaborazione: {str(e)}\n\nRiformula la domanda."


def audit_completo(progress=gr.Progress()):
    """Audit completo automatico"""
    from reports.report_generator import generate_audit_report
    from tools.visualization import generate_dashboard
    import re

    domande = [
        "Ci sono omissioni nel report Q2 2024?",
        "Come si confrontano Q1 e Q2 2024?",
        "Il documento è conforme alle regole di compliance?",
        "Qual è la predizione del trend di rischio per Q3?",
        "Fai una simulazione di scenario di crisi per Q2 2024.",
    ]

    results = {
        'metadata': {
            'period': 'Q1-Q2 2024',
            'analyst': 'FinSecure AI Agent'
        }
    }

    risultati_testo = []
    q1_metrics = {}
    q2_metrics = {}

    for i, domanda in enumerate(domande):
        progress((i + 1) / len(domande), desc=f"Analisi {i+1}/{len(domande)}...")

        try:
            risposta = agent_answer(domanda)
            risultati_testo.append(f"### {domanda}\n\n{risposta}\n\n{'='*80}\n")

            # Raccoglie risultati per il PDF
            domanda_lower = domanda.lower()
            if "omission" in domanda_lower or "mancanza" in domanda_lower:
                results['omissions'] = risposta
            elif "confront" in domanda_lower or "confrontano" in domanda_lower:
                results['comparison'] = risposta
                # Estrae metriche per dashboard
                ricavi_match = re.search(r'Q1:\s*(\d+\.?\d*)M.*?Q2:\s*(\d+\.?\d*)M', risposta)
                if ricavi_match:
                    q1_metrics['ricavi'] = float(ricavi_match.group(1))
                    q2_metrics['ricavi'] = float(ricavi_match.group(2))
                margine_match = re.search(r'(\d+\.?\d*)%.*?→.*?(\d+\.?\d*)%', risposta)
                if margine_match:
                    q1_metrics['margine'] = float(margine_match.group(1))
                    q2_metrics['margine'] = float(margine_match.group(2))
            elif "compliance" in domanda_lower or "conforme" in domanda_lower:
                results['compliance'] = risposta
            elif "simulazione" in domanda_lower or "scenario" in domanda_lower:
                results['simulation'] = risposta
            elif "predizione" in domanda_lower or "trend" in domanda_lower:
                results['prediction'] = risposta

        except Exception as e:
            risultati_testo.append(f"### {domanda}\n\nErrore: {str(e)}\n\n{'='*80}\n")

    progress(1.0, desc="Generazione report...")

    # Dashboard
    dashboard_path = None
    if q1_metrics and q2_metrics:
        dashboard_path = generate_dashboard(q1_metrics, q2_metrics)

    # PDF
    pdf_tmp = None
    try:
        pdf_path = generate_audit_report(
            analysis_results=results,
            dashboard_path=dashboard_path
        )
        pdf_tmp = "/tmp/audit_report.pdf"
        shutil.copy(pdf_path, pdf_tmp)
    except Exception as e:
        risultati_testo.append(f"\nErrore generazione PDF: {str(e)}")

    dashboard_tmp = None
    if dashboard_path and os.path.exists(dashboard_path):
        dashboard_tmp = "/tmp/dashboard_comparativa.png"
        shutil.copy(dashboard_path, dashboard_tmp)

    return "\n".join(risultati_testo), dashboard_tmp, pdf_tmp


def create_interface():
    """Crea e restituisce l'interfaccia Gradio"""

    esempi = [
        ["Ci sono omissioni nel report Q2 2024?"],
        ["Come si confrontano Q1 e Q2 2024?"],
        ["Il documento è conforme alle regole di compliance?"],
        ["Qual è la predizione del trend di rischio per Q3?"],
        ["Fai una simulazione di scenario di crisi."],
    ]

    with gr.Blocks(theme=gr.themes.Soft(), title="FinSecure AI Audit") as demo:

        gr.Markdown("# FinSecure Analytics - AI Audit Agent")

        with gr.Tabs():
            with gr.Tab("Chat"):
                gr.Markdown("### Fai domande sui report finanziari")
                gr.ChatInterface(
                    fn=chat,
                    examples=esempi,
                    type="messages"
                )

            with gr.Tab("Audit Completo"):
                gr.Markdown("### Genera report automatico")
                audit_btn = gr.Button("Avvia Audit", variant="primary", size="lg")

                with gr.Row():
                    with gr.Column(scale=2):
                        risultati_output = gr.Markdown()
                    with gr.Column(scale=1):
                        dashboard_output = gr.Image(label="Dashboard")

                pdf_output = gr.File(label="Report PDF")

                audit_btn.click(
                    fn=audit_completo,
                    outputs=[risultati_output, dashboard_output, pdf_output]
                )

            with gr.Tab("Info"):
                gr.Markdown("""
                ## FinSecure AI Audit Agent

                **Tecnologie:**
                - LlamaIndex ReActAgent per ragionamento agentico
                - Mistral-7B (4-bit quantized) per risposte conversazionali
                - scikit-learn per predizioni ML
                - Matplotlib/Seaborn per visualizzazioni
                - FPDF per report PDF

                **Funzionalità:**
                - Analisi omissioni documentali
                - Confronto performance Q1 vs Q2
                - Verifica compliance normativa
                - Predizione trend rischio Q3
                - Simulazione scenari di rischio
                - Generazione report PDF con dashboard

                **Documenti analizzati:**
                - Report Finanziario Q1 2024
                - Report Finanziario Q2 2024
                - Note di Audit Interno

                **Tempi di risposta:**
                - Circa 30-90 secondi a domanda in chat
                - Almeno 1 minuto per l'audit completo
                """)

    return demo
