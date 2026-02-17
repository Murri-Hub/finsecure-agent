"""
conversational_agent_improved.py
Funzione conversazionale per l'agente AI
"""
from llama_index.core import Settings
from agent.agent import agent_answer
import re

def conversational_agent_answer(question: str, conversation_history: list = None):
    """
    Risposta conversazionale che:
    - Integra i risultati dei tool in modo naturale
    - Evidenzia chiaramente rischi, omissioni e ambiguità
    - Suggerisce azioni correttive concrete
    - Mantiene un contesto conversazionale coerente
    - Identifica possibili interpretazioni errate
    
    Args:
        question: Domanda dell'utente
        conversation_history: Lista di tuple (user_msg, assistant_msg)
    
    Returns:
        str: Risposta conversazionale strutturata
    """
    
    if conversation_history is None:
        conversation_history = []
    
    # ESEGUE ANALISI CON I TOOL
    analysis = agent_answer(question)
    
    # ESTRAE COMPONENTI DALL'ANALISI
    components = _parse_analysis_components(analysis)
    
    # IDENTIFICA RISCHI E AMBIGUITÀ
    risks = _identify_risks(components)
    ambiguities = _identify_ambiguities(components)
    
    # GENERA AZIONI CORRETTIVE
    actions = _generate_corrective_actions(components, risks)
    
    # COSTRUISCE CONTESTO CONVERSAZIONALE
    context = _build_conversation_context(conversation_history)
    
    # PROMPT PER LLM CONVERSAZIONALE
    prompt = f"""Sei un analista di rischio finanziario senior di FinSecure Analytics.
Il tuo compito è spiegare i risultati dell'analisi in modo chiaro, professionale e prudente.

CONTESTO CONVERSAZIONE
{context}

=== DOMANDA CORRENTE ===
{question}

RISULTATI ANALISI TECNICA
{analysis}

RISCHI IDENTIFICATI
{_format_risks(risks)}

AMBIGUITÀ E POSSIBILI INTERPRETAZIONI ERRATE
{_format_ambiguities(ambiguities)}

AZIONI CORRETTIVE SUGGERITE
{_format_actions(actions)}

ISTRUZIONI PER LA RISPOSTA
Costruisci una risposta che:

1. INIZIA con un riassunto chiaro (2-3 frasi) della situazione
2. SPIEGA i dati principali in linguaggio naturale (evita elenchi puntati)
3. EVIDENZIA esplicitamente:
   - Eventuali omissioni nei dati
   - Rischi critici (se presenti)
   - Ambiguità che potrebbero portare a interpretazioni errate
4. SUGGERISCI azioni concrete (se appropriate)
5. TERMINA con una domanda di follow-up SOLO se:
   - I dati sono insufficienti per una risposta definitiva
   - C'è un'ambiguità che richiede chiarimento dell'utente
   
TONO: Professionale ma accessibile. Usa metafore finanziarie quando aiutano la comprensione.

IMPORTANTE: 
- Se i dati sono insufficienti o ambigui, DICHIARALO CHIARAMENTE
- Non fare supposizioni non supportate dai dati
- Distingui tra FATTI certi e INTERPRETAZIONI possibili

Risposta in italiano:"""
    
    # GENERA RISPOSTA CONVERSAZIONALE
    response = Settings.llm.complete(prompt)
    
    # POST-PROCESSING: Aggiunge box di alert se necessario
    final_response = _add_visual_alerts(response.text, risks, ambiguities)
    
    return final_response


# ============================================================================
# FUNZIONI HELPER
# ============================================================================

def _parse_analysis_components(analysis: str) -> dict:
    """Estrae le componenti strutturate dall'analisi"""
    components = {
        'tool_result': '',
        'tool_used': 'none',
        'decision_reason': ''
    }
    
    # Estrae risultato del tool
    if '[Analisi Tool]' in analysis:
        parts = analysis.split('[Analisi Tool]')
        if len(parts) > 1:
            tool_part = parts[1].split('[Decision')[0].strip()
            components['tool_result'] = tool_part
    
    # Estrae tool utilizzato e motivazione
    if '[Decision Logging]' in analysis:
        decision_section = analysis.split('[Decision Logging]')[1]
        
        tool_match = re.search(r'Tool utilizzato:\s*(.+)', decision_section)
        if tool_match:
            components['tool_used'] = tool_match.group(1).strip()
        
        reason_match = re.search(r'Motivazione:\s*(.+)', decision_section, re.DOTALL)
        if reason_match:
            components['decision_reason'] = reason_match.group(1).strip()
    
    return components


def _identify_risks(components: dict) -> list:
    """Identifica i rischi presenti nell'analisi"""
    risks = []
    tool_result = components.get('tool_result', '')
    
    # Pattern di rischio critico
    critical_patterns = [
        (r'CRITICO|ALERT CRITICO', 'CRITICO'),
        (r'Situazione critica|GRAVE', 'ALTO'),
        (r'alert|significativo', 'MEDIO'),
    ]
    
    for pattern, level in critical_patterns:
        matches = re.finditer(pattern, tool_result, re.IGNORECASE)
        for match in matches:
            # Estrae contesto (50 caratteri prima e dopo)
            start = max(0, match.start() - 50)
            end = min(len(tool_result), match.end() + 100)
            context = tool_result[start:end].strip()
            
            risks.append({
                'level': level,
                'context': context,
                'full_text': tool_result
            })
    
    return risks

def _identify_ambiguities(components: dict) -> list:
    """Identifica ambiguità che potrebbero portare a interpretazioni errate"""
    ambiguities = []
    tool_result = components.get('tool_result', '')
    
    # Pattern di ambiguità
    ambiguity_signals = [
        'non specificato',
        'stimato',
        'potrebbe',
        'circa',
        'approssimativamente',
        'in fase di valutazione',
        'dati insufficienti',
        'impossibile determinare',
        'vaghezza rilevata',
        'VALORE MANCANTE',
        'non dettagliato',
        'senza contesto'
    ]
    
    for signal in ambiguity_signals:
        if signal.lower() in tool_result.lower():
            # Trova la frase completa
            sentences = tool_result.split('\n')
            for sentence in sentences:
                if signal.lower() in sentence.lower():
                    ambiguities.append({
                        'signal': signal,
                        'context': sentence.strip(),
                        'interpretation_risk': _assess_interpretation_risk(sentence)
                    })
    
    # Identifica numeri senza unità o contesto
    orphan_numbers = re.findall(r'(?:^|\s)(\d+(?:[.,]\d+)?)\s*(?:$|\n)', tool_result)
    if orphan_numbers:
        ambiguities.append({
            'signal': 'numeri senza contesto',
            'context': f'Trovati {len(orphan_numbers)} valori numerici senza unità di misura',
            'interpretation_risk': 'MEDIO'
        })
    
    return ambiguities

def _assess_interpretation_risk(text: str) -> str:
    """Valuta il rischio di interpretazione errata"""
    high_risk_keywords = ['stimato', 'potrebbe', 'circa', 'non specificato']
    medium_risk_keywords = ['valutazione', 'approssimativo', 'indicativo']
    
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in high_risk_keywords):
        return 'ALTO'
    elif any(kw in text_lower for kw in medium_risk_keywords):
        return 'MEDIO'
    else:
        return 'BASSO'


def _generate_corrective_actions(components: dict, risks: list) -> list:
    """Genera azioni correttive basate sui risultati"""
    actions = []
    tool_result = components.get('tool_result', '')
    tool_used = components.get('tool_used', '')
    
    # Azioni basate sul tipo di tool
    if tool_used == 'find_omissions':
        if 'MANCANTE' in tool_result or 'omissione' in tool_result.lower():
            actions.append({
                'priority': 'ALTA',
                'action': 'Integrare i dati mancanti identificati',
                'detail': 'Richiedere ai responsabili di reparto la compilazione delle sezioni incomplete'
            })
    
    if tool_used == 'compare_periods':
        if any(r['level'] == 'CRITICO' for r in risks):
            actions.append({
                'priority': 'CRITICA',
                'action': 'Implementare piano di mitigazione del rischio immediato',
                'detail': 'Convocare comitato rischi entro 48h per valutare azioni correttive'
            })
        
        if 'margine' in tool_result.lower() and 'cal' in tool_result.lower():
            actions.append({
                'priority': 'MEDIA',
                'action': 'Analizzare le cause del calo del margine operativo',
                'detail': 'Esaminare struttura costi e strategie di pricing'
            })
    
    if tool_used == 'audit_compliance':
        if 'disclaimer' in tool_result.lower() and 'assente' in tool_result.lower():
            actions.append({
                'priority': 'ALTA',
                'action': 'Aggiungere disclaimer legale alla documentazione',
                'detail': 'Consultare ufficio legale per formulazione conforme'
            })
        
        if 'violazione' in tool_result.lower() or 'non conforme' in tool_result.lower():
            actions.append({
                'priority': 'CRITICA',
                'action': 'Sanare immediatamente le non conformità',
                'detail': 'Rischio di sanzioni regolamentari'
            })
    
    if tool_used == 'predict_risk_trend':
        if 'CRITICO' in tool_result:
            actions.append({
                'priority': 'CRITICA',
                'action': 'Ridurre esposizione al rischio prima del Q3',
                'detail': 'Implementare le raccomandazioni del modello predittivo'
            })
    
    return actions

def _build_conversation_context(history: list) -> str:
    """Costruisce il contesto conversazionale"""
    if not history:
        return "Questa è la prima domanda della conversazione."
    
    # Prende ultimi 3 scambi
    recent_history = history[-3:] if len(history) > 3 else history
    
    context_lines = []
    for i, (user_msg, assistant_msg) in enumerate(recent_history, 1):
        context_lines.append(f"Scambio {i}:")
        context_lines.append(f"  Utente: {user_msg[:100]}...")
        context_lines.append(f"  Assistente: {assistant_msg[:100]}...")
    
    return '\n'.join(context_lines)


def _format_risks(risks: list) -> str:
    """Formatta i rischi per il prompt"""
    if not risks:
        return "Nessun rischio critico identificato."
    
    formatted = []
    for risk in risks:
        formatted.append(f"[{risk['level']}] {risk['context']}")
    
    return '\n'.join(formatted)

def _format_ambiguities(ambiguities: list) -> str:
    """Formatta le ambiguità per il prompt"""
    if not ambiguities:
        return "Nessuna ambiguità significativa rilevata."
    
    formatted = []
    for amb in ambiguities:
        formatted.append(
            f"[Rischio: {amb['interpretation_risk']}] "
            f"{amb['signal']} - {amb['context']}"
        )
    
    return '\n'.join(formatted)

def _format_actions(actions: list) -> str:
    """Formatta le azioni correttive per il prompt"""
    if not actions:
        return "Nessuna azione correttiva immediata richiesta. Continuare il monitoraggio periodico."
    
    formatted = []
    for action in actions:
        formatted.append(
            f"[{action['priority']}] {action['action']}\n"
            f"  Dettaglio: {action['detail']}"
        )
    
    return '\n\n'.join(formatted)

def _add_visual_alerts(response: str, risks: list, ambiguities: list) -> str:
    """Aggiunge box di alert visivi alla risposta"""
    alerts = []
    
    # Alert per rischi critici
    critical_risks = [r for r in risks if r['level'] == 'CRITICO']
    if critical_risks:
        alerts.append(
            "\n\n**ALERT CRITICO**\n"
            "Sono stati identificati rischi che richiedono attenzione immediata. "
            "Consulta la sezione azioni correttive sopra."
        )
    
    # Alert per ambiguità ad alto rischio
    high_risk_ambiguities = [a for a in ambiguities if a['interpretation_risk'] == 'ALTO']
    if high_risk_ambiguities:
        alerts.append(
            "\n\n**ATTENZIONE: DATI AMBIGUI**\n"
            "Alcuni dati presentano ambiguità che potrebbero portare a interpretazioni errate. "
            "Verificare le fonti prima di prendere decisioni strategiche."
        )
    
    if alerts:
        return response + '\n' + '\n'.join(alerts)
    
    return response


# ============================================================================
# FUNZIONE PER GRADIO
# ============================================================================

def chat(message, history):
    """
    Wrapper per Gradio ChatInterface
    Converte il formato history di Gradio in quello atteso dalla funzione principale
    
    Args:
        message: str - messaggio corrente dell'utente
        history: list - storia conversazione in formato Gradio
    
    Returns:
        str: risposta dell'assistente
    """
    try:
        # Converte history da formato Gradio a lista di tuple
        conversation_history = []
        
        if history:
            for h in history:
                # Formato Gradio: [user_msg, assistant_msg]
                if len(h) >= 2:
                    conversation_history.append((h[0], h[1]))
        
        # Genera risposta
        response = conversational_agent_answer(
            question=message,
            conversation_history=conversation_history
        )
        
        return response
    
    except Exception as e:
        error_msg = (
            f"Mi dispiace, si è verificato un errore nell'elaborazione della richiesta.\n\n"
            f"Dettagli tecnici: {str(e)}\n\n"
            f"Ti consiglio di riformulare la domanda o di provare con una query più specifica."
        )
        return error_msg
        

if __name__ == "__main__":
    # Test della funzione
    test_question = "Ci sono omissioni nel report Q2 2024?"
    test_history = [
        ("Ciao, vorrei fare un audit dei documenti", "Certo, sono qui per aiutarti...")
    ]
    
    print("=== TEST CONVERSATIONAL AGENT ===\n")
    print(f"Domanda: {test_question}\n")
    
    response = conversational_agent_answer(test_question, test_history)
    print(f"Risposta:\n{response}")
