"""
tools.py
Tool agentici per audit finanziari e gestione del rischio
"""
import re

def find_omissions(text_chunks):
    """
    Analizza i chunk recuperati e cerca segnali di omissioni o vaghezza.
    """
    signals = ["non specificato", "non dettagliato", "stimato", "potrebbe", "in fase di valutazione"]
    findings = []
    
    for chunk in text_chunks:
        # Cerca parole chiave di vaghezza
        for signal in signals:
            if signal in chunk.lower():
                findings.append(f"⚠️ Vaghezza rilevata: '{signal}' → {chunk[:150]}...")
        
        # Cerca campi con valori mancanti (es. "Campo: " senza valore dopo)
        missing_values = re.findall(r'[-•]\s*([^:]+):\s*$', chunk, re.MULTILINE)
        for field in missing_values:
            findings.append(f"❌ VALORE MANCANTE: '{field.strip()}' non ha un valore specificato")
        
        # Cerca percentuali o numeri senza contesto
        if re.search(r'\d+%?\s*$', chunk):
            findings.append(f"⚠️ Dato numerico senza contesto: {chunk[:100]}...")
    
    if not findings:
        return "✅ Nessuna omissione evidente rilevata."
    
    return "\n".join(findings)


def compare_periods(chunks_q1, chunks_q2):
    """
    Confronta due periodi e segnala differenze qualitative e quantitative.
    """
    summary = []
    
    # Confronto lunghezza/complessità
    if len(chunks_q2) > len(chunks_q1) * 1.2:
        summary.append("📊 Q2 mostra maggiore complessità documentale rispetto a Q1 (+20% chunk)")
    
    # Estrai numeri chiave (ricavi, costi, margini)
    def extract_numbers(chunks):
        numbers = {}
        for chunk in chunks:
            # Ricavi
            ricavi = re.search(r'ricavi.*?(\d+[,.]?\d*)\s*milioni', chunk.lower())
            if ricavi:
                numbers['ricavi'] = float(ricavi.group(1).replace(',', '.'))
            # Margine
            margine = re.search(r'margine.*?(\d+)%', chunk.lower())
            if margine:
                numbers['margine'] = int(margine.group(1))
            # Rischio
            rischio = re.search(r'rischio.*?(\d+[,.]?\d*)\s*milioni', chunk.lower())
            if rischio:
                numbers['rischio'] = float(rischio.group(1).replace(',', '.'))
        return numbers
    
    q1_nums = extract_numbers(chunks_q1)
    q2_nums = extract_numbers(chunks_q2)
    
    # Confronta i numeri
    if 'ricavi' in q1_nums and 'ricavi' in q2_nums:
        diff = ((q2_nums['ricavi'] - q1_nums['ricavi']) / q1_nums['ricavi']) * 100
        if diff > 0:
            summary.append(f"📈 Ricavi aumentati del {diff:.1f}% (Q1: {q1_nums['ricavi']}M → Q2: {q2_nums['ricavi']}M)")
        else:
            summary.append(f"📉 Ricavi diminuiti del {abs(diff):.1f}% (Q1: {q1_nums['ricavi']}M → Q2: {q2_nums['ricavi']}M)")
    
    if 'margine' in q1_nums and 'margine' in q2_nums:
        diff = q2_nums['margine'] - q1_nums['margine']
        if diff < 0:
            summary.append(f"⚠️ Margine operativo calato di {abs(diff)} punti percentuali ({q1_nums['margine']}% → {q2_nums['margine']}%)")
        elif diff > 0:
            summary.append(f"✅ Margine operativo migliorato di {diff} punti percentuali ({q1_nums['margine']}% → {q2_nums['margine']}%)")
    
    if 'rischio' in q1_nums and 'rischio' in q2_nums:
        diff = ((q2_nums['rischio'] - q1_nums['rischio']) / q1_nums['rischio']) * 100
        if diff > 10:
            summary.append(f"🔴 Esposizione al rischio aumentata significativamente del {diff:.1f}% (Q1: {q1_nums['rischio']}M → Q2: {q2_nums['rischio']}M)")
        elif diff > 0:
            summary.append(f"⚠️ Esposizione al rischio aumentata del {diff:.1f}%")
    
    # Analisi qualitativa
    negative_keywords = ["riduzione", "calo", "diminuzione", "criticità", "volatil", "rischio"]
    q2_negative_count = sum(1 for chunk in chunks_q2 for kw in negative_keywords if kw in chunk.lower())
    q1_negative_count = sum(1 for chunk in chunks_q1 for kw in negative_keywords if kw in chunk.lower())
    
    if q2_negative_count > q1_negative_count:
        summary.append(f"⚠️ Sentiment negativo aumentato in Q2 ({q2_negative_count} vs {q1_negative_count} segnali negativi)")
    
    if not summary:
        return "➡️ Nessuna differenza significativa rilevata tra i periodi."
    
    return "\n".join(summary)


def audit_compliance(text_chunks):
    """
    Valuta possibili problemi di compliance e completezza documentale.
    """
    compliance_flags = ["deroga", "eccezione", "non conforme", "violazione", "mancato rispetto"]
    issues = []
    
    for chunk in text_chunks:
        # Flag di compliance
        for flag in compliance_flags:
            if flag in chunk.lower():
                issues.append(f"🚨 Possibile problema: '{flag}' → {chunk[:150]}...")
        
        # Verifica presenza sezioni obbligatorie
        required_sections = ["rischi", "liquidità", "ricavi", "compliance"]
        
    # Verifica completezza
    all_text = " ".join(text_chunks).lower()
    missing_sections = [sec for sec in required_sections if sec not in all_text]
    
    if missing_sections:
        issues.append(f"⚠️ Sezioni potenzialmente mancanti: {', '.join(missing_sections)}")
    
    # Verifica presenza disclaimer legali
    if "disclaimer" not in all_text and "limitazione" not in all_text:
        issues.append("⚠️ Disclaimer legale potenzialmente assente")
    
    if not issues:
        return "✅ Nessun problema di compliance evidente."
    
    return "\n".join(issues)
