"""
ui/gradio_interface.py
Interfaccia Gradio per FinSecure AI Audit Agent
"""
import gradio as gr
import shutil
import os
from agent.agent import agent_answer, generate_full_audit
from llama_index.core import Settings


def chat(message, history):
    """
    Funzione chat conversazionale intelligente
    Gestisce sia domande analitiche (con tool) che conversazionali
    """
    try:
        # ESTRAE CONTESTO DALLA CONVERSAZIONE
        conversation_summary = _extract_conversation_context(history)

        # DETERMINA SE È UNA DOMANDA DI FOLLOW-UP
        is_followup = _is_followup_question(message, history)

        # ESEGUE ANALISI CON I TOOL
        tool_analysis = agent_answer(message)

        # PULISCE IL RISULTATO DEL TOOL
        tool_result, tool_used = _extract_tool_result(tool_analysis)

        # GENERA RISPOSTA CONVERSAZIONALE
        if is_followup and conversation_summary:
            response = _generate_followup_response(
                message, conversation_summary, tool_result, tool_used
            )
        elif tool_result and tool_result != "None":
            response = _generate_analytical_response(
                message, tool_result, tool_used
            )
        else:
            response = _generate_generic_response(message, conversation_summary)

        return response

    except Exception as e:
        return f"Errore nell'elaborazione: {str(e)}\n\nRiformula la domanda."


def _extract_conversation_context(history):
    """Estrae contesto conversazionale"""
    if not history or len(history) == 0:
        return None

    last_exchange = history[-1] if history else None
    if not last_exchange:
        return None

    try:
        if isinstance(last_exchange, dict):
            return {
                'user_question': last_exchange.get('content', ''),
                'assistant_answer': ''
            }
        elif isinstance(last_exchange, (list, tuple)) and len(last_exchange) >= 2:
            return {
                'user_question': last_exchange[0],
                'assistant_answer': last_exchange[1]
            }
    except:
        pass

    return None


def _is_followup_question(message, history):
    """Determina se è una domanda di follow-up"""
    if not history or len(history) == 0:
        return False

    followup_keywords = [
        'aggiuntive', 'altro', 'inoltre', 'anche', 'più', 'ancora',
        'dettagli', 'approfondisci', 'spiega', 'intendi', 'puoi',
        'maggiori', 'quindi', 'consigli', 'raccomand', 'fare'
    ]

    return any(kw in message.lower() for kw in followup_keywords)


def _extract_tool_result(analysis):
    """Estrae risultato tool"""
    tool_result = None
    tool_used = "none"

    if '[Analisi Tool]' in analysis:
        parts = analysis.split('[Analisi Tool]')
        if len(parts) > 1:
            tool_result = parts[1].split('[Decision')[0].strip()

    if '[Decision Logging]' in analysis:
        import re
        match = re.search(r'Tool utilizzato:\s*(.+)', analysis)
        if match:
            tool_used = match.group(1).strip()

    return tool_result, tool_used


def _generate_followup_response(message, context, tool_result, tool_used):
    """Genera risposta follow-up con LLM"""
    
    prompt = f"""Sei un analista finanziario senior di FinSecure Analytics.

CONVERSAZIONE PRECEDENTE:
Domanda: {context['user_question']}
Risposta: {context['assistant_answer'][:400]}

NUOVA DOMANDA:
{message}

DATI DISPONIBILI:
{tool_result if tool_result and tool_result != "None" else "Nessun nuovo dato"}

COMPITO:
Rispondi in modo professionale ma accessibile:
- Fornisci informazioni aggiuntive contestuali
- Interpreta i dati in termini pratici
- Suggerisci azioni concrete se appropriato
- Scrivi in prosa naturale (max 200 parole)

Risposta in italiano:"""

    try:
        response = Settings.llm.complete(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback se LLM fallisce
        return f"[Contesto precedente]\n{context['assistant_answer'][:300]}\n\n[Dati aggiuntivi]\n{tool_result if tool_result else 'Nessun dato disponibile'}"


def _generate_analytical_response(message, tool_result, tool_used):
    """Genera risposta analitica con LLM"""
    
    risk_level = "normale"
    if "CRITICO" in tool_result.upper():
        risk_level = "critico"
    elif "SIGNIFICATIVO" in tool_result.upper():
        risk_level = "elevato"

    prompt = f"""Sei un analista finanziario senior di FinSecure Analytics.

DOMANDA:
{message}

RISULTATI ANALISI:
{tool_result}

LIVELLO RISCHIO: {risk_level}

COMPITO:
Spiega i risultati in modo professionale:
1. Sintesi esecutiva (2-3 frasi)
2. Spiegazione dati in linguaggio naturale
3. Evidenzia rischi se presenti
4. Suggerisci azioni se rischio elevato/critico

Scrivi in prosa continua, evita troppi elenchi.
Tono: professionale come parlare a un CFO.
Max 250 parole.

Risposta in italiano:"""

    try:
        response = Settings.llm.complete(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback
        header = {
            'find_omissions': 'Analisi Omissioni',
            'compare_periods': 'Confronto Q1 vs Q2',
            'audit_compliance': 'Audit Compliance',
            'predict_risk_trend': 'Predizione Trend'
        }.get(tool_used, 'Analisi')
        
        return f"**{header}**\n\n{tool_result}"


def _generate_generic_response(message, context):
    """Genera risposta generica con LLM"""
    
    context_text = ""
    if context:
        context_text = f"\nContesto: {context['user_question'][:100]}"

    prompt = f"""Sei un analista finanziario senior di FinSecure Analytics.
{context_text}

DOMANDA:
{message}

Non sono disponibili dati analitici. Rispondi in modo utile:
- Se chiede capacità → spiega cosa puoi fare
- Se vaga → chiedi chiarimenti
- Se dati non disponibili → indica cosa serve

Professionale, max 150 parole.

Risposta in italiano:"""

    try:
        response = Settings.llm.complete(prompt)
        return response.text.strip()
    except Exception as e:
        return """**FinSecure AI Audit Agent**

Analisi report finanziari Q1-Q2 2024.

**Capacità:**
Omissioni, Confronti, Compliance, Predizioni

**Esempi:**
• "Come si confrontano Q1 e Q2?"
• "Ci sono omissioni nel report Q2?"

Fai una domanda specifica!"""


def audit_completo(progress=gr.Progress()):
    """Audit completo automatico"""
    try:
        progress(0, desc="Preparazione...")

        domande = [
            "Ci sono omissioni nel report Q2 2024?",
            "Come si confrontano Q1 e Q2 2024?",
            "Il documento è conforme alle regole di compliance?",
            "Qual è la predizione del trend di rischio per Q3?"
        ]

        risultati_testo = []
        for i, domanda in enumerate(domande):
            progress((i+1)/len(domande), desc=f"Analisi {i+1}/4...")

            try:
                risposta = agent_answer(domanda)
                if '[Analisi Tool]' in risposta:
                    risposta = risposta.split('[Analisi Tool]')[1].split('[Decision')[0].strip()
                risultati_testo.append(f"###{domanda}\n\n{risposta}\n\n{'='*80}\n")
            except Exception as e:
                risultati_testo.append(f"###{domanda}\n\nErrore: {str(e)}\n\n{'='*80}\n")

        progress(1.0, desc="Generazione report...")

        try:
            risultati = generate_full_audit(domande)

            dashboard_tmp = None
            pdf_tmp = None

            if risultati.get('dashboard'):
                dashboard_tmp = "/tmp/dashboard_comparativa.png"
                shutil.copy(risultati['dashboard'], dashboard_tmp)

            if risultati.get('pdf'):
                pdf_tmp = "/tmp/audit_report.pdf"
                shutil.copy(risultati['pdf'], pdf_tmp)

            return ("\n".join(risultati_testo), dashboard_tmp, pdf_tmp)
        except Exception as e:
            return ("\n".join(risultati_testo) + f"\n\nErrore: {str(e)}", None, None)

    except Exception as e:
        return f"Errore: {str(e)}", None, None


def create_interface():
    """Crea e restituisce l'interfaccia Gradio"""
    
    esempi = [
        ["Ci sono omissioni nel report Q2 2024?"],
        ["Come si confrontano Q1 e Q2 2024?"],
        ["Il documento è conforme alle regole di compliance?"],
        ["Qual è la predizione del trend di rischio per Q3?"],
    ]

    with gr.Blocks(theme=gr.themes.Soft(), title="FinSecure AI Audit") as demo:

        gr.Markdown("# FinSecure Analytics - AI Audit Agent")

        with gr.Tabs():
            with gr.Tab("Chat"):
                gr.Markdown("### Fai domande sui report finanziari")
                chatbot = gr.ChatInterface(
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
                - LlamaIndex per RAG e retrieval semantico
                - Mistral-7B (4-bit quantized) per risposte conversazionali
                - scikit-learn per predizioni ML
                - Matplotlib/Seaborn per visualizzazioni
                - FPDF per report PDF
                
                **Funzionalità:**
                - Analisi omissioni documentali
                - Confronto performance Q1 vs Q2
                - Verifica compliance normativa
                - Predizione trend rischio Q3
                - Generazione report PDF con dashboard
                
                **Documenti analizzati:**
                - Report Finanziario Q1 2024
                - Report Finanziario Q2 2024
                - Note di Audit Interno

                **Tempi di risposta:**
                - Circa 30-90 secondi a domanda in chat
                - Almeno 1 minuto per l'audit
                """)

    return demo
