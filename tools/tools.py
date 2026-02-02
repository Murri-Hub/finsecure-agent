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
    
    # Funzione helper per estrarre TUTTI i numeri da ogni chunk
    def extract_all_numbers(chunks):
        all_numbers = []
        for chunk in chunks:
            # Ricavi
            for match in re.finditer(r'ricavi.*?(\d+[,.]?\d*)\s*milioni', chunk.lower()):
                val = float(match.group(1).replace(',', '.'))
                all_numbers.append(('ricavi', val))
            # Margine
            for match in re.finditer(r'margine.*?(\d+[,.]?\d*)%', chunk.lower()):
                val = float(match.group(1).replace(',', '.'))
                all_numbers.append(('margine', val))
            # Rischio
            for match in re.finditer(r'rischio.*?(\d+[,.]?\d*)\s*milioni', chunk.lower()):
                val = float(match.group(1).replace(',', '.'))
                all_numbers.append(('rischio', val))
        return all_numbers
    
    q1_all = extract_all_numbers(chunks_q1)
    q2_all = extract_all_numbers(chunks_q2)
    
    # Prendi i valori massimi per ogni metrica (assumendo siano i più aggiornati)
    def get_metrics(numbers_list):
        metrics = {}
        for metric, value in numbers_list:
            if metric not in metrics or value > metrics[metric]:
                metrics[metric] = value
        return metrics
    
    q1_nums = get_metrics(q1_all)
    q2_nums = get_metrics(q2_all)
    
    # Confronta ricavi
    if 'ricavi' in q1_nums and 'ricavi' in q2_nums:
        diff = ((q2_nums['ricavi'] - q1_nums['ricavi']) / q1_nums['ricavi']) * 100
        if diff > 0:
            summary.append(f"📈 Ricavi aumentati del {diff:.1f}% (Q1: {q1_nums['ricavi']}M → Q2: {q2_nums['ricavi']}M)")
        elif diff < 0:
            summary.append(f"📉 Ricavi diminuiti del {abs(diff):.1f}% (Q1: {q1_nums['ricavi']}M → Q2: {q2_nums['ricavi']}M)")
        else:
            summary.append(f"➡️ Ricavi stabili a {q1_nums['ricavi']}M")
    
    # Confronta margine
    if 'margine' in q1_nums and 'margine' in q2_nums:
        diff = q2_nums['margine'] - q1_nums['margine']
        if diff < -2:
            summary.append(f"🔴 Margine operativo calato significativamente di {abs(diff):.1f} punti percentuali ({q1_nums['margine']}% → {q2_nums['margine']}%)")
        elif diff < 0:
            summary.append(f"⚠️ Margine operativo calato di {abs(diff):.1f} punti percentuali ({q1_nums['margine']}% → {q2_nums['margine']}%)")
        elif diff > 2:
            summary.append(f"✅ Margine operativo migliorato significativamente di {diff:.1f} punti percentuali ({q1_nums['margine']}% → {q2_nums['margine']}%)")
    
    # Confronta rischio
    if 'rischio' in q1_nums and 'rischio' in q2_nums:
        diff = ((q2_nums['rischio'] - q1_nums['rischio']) / q1_nums['rischio']) * 100
        if diff > 20:
            summary.append(f"🔴 Esposizione al rischio aumentata in modo critico del {diff:.1f}% (Q1: {q1_nums['rischio']}M → Q2: {q2_nums['rischio']}M)")
        elif diff > 10:
            summary.append(f"⚠️ Esposizione al rischio aumentata significativamente del {diff:.1f}% (Q1: {q1_nums['rischio']}M → Q2: {q2_nums['rischio']}M)")
        elif diff > 0:
            summary.append(f"📊 Esposizione al rischio aumentata del {diff:.1f}%")
    
    # Alert combinato critico
    if q2_nums.get('margine', 0) < q1_nums.get('margine', 0) and q2_nums.get('rischio', 0) > q1_nums.get('rischio', 0):
        summary.append("⚠️ ALERT: Combinazione critica di margine in calo e rischio in aumento")
    
    # Analisi qualitativa
    if len(chunks_q2) > len(chunks_q1) * 1.2:
        summary.append("📄 Q2 mostra documentazione più complessa (+20% dettagli)")
    
    negative_keywords = ["riduzione", "calo", "diminuzione", "criticità", "volatile", "incerto"]
    q2_neg = sum(1 for c in chunks_q2 for kw in negative_keywords if kw in c.lower())
    q1_neg = sum(1 for c in chunks_q1 for kw in negative_keywords if kw in c.lower())
    
    if q2_neg > q1_neg + 2:
        summary.append(f"⚠️ Sentiment più negativo in Q2 ({q2_neg} vs {q1_neg} segnali di rischio)")
    
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
        for flag in compliance_flags:
            if flag in chunk.lower():
                issues.append(f"🚨 Possibile problema: '{flag}' → {chunk[:150]}...")
    
    # Verifica completezza con pattern più flessibili
    all_text = " ".join(text_chunks).lower()
    
    # Verifica solo sezioni rilevanti per compliance
    checks = {
        "rischi": ["rischi", "risk", "esposizione"],
        "compliance": ["compliance", "conforme", "normativ"]
    }
    
    missing_sections = []
    for section, keywords in checks.items():
        if not any(kw in all_text for kw in keywords):
            missing_sections.append(section)
    
    if missing_sections:
        issues.append(f"⚠️ Sezioni potenzialmente mancanti: {', '.join(missing_sections)}")
    
    # Verifica presenza disclaimer legali
    if "disclaimer" not in all_text and "limitazione" not in all_text:
        issues.append("⚠️ Disclaimer legale potenzialmente assente")
    
    if not issues:
        return "✅ Nessun problema di compliance evidente."
    
    return "\n".join(issues)
