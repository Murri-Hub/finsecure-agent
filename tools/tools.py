"""
tools.py
Tool agentici per audit finanziari e gestione del rischio
"""

def find_omissions(text_chunks):
    """
    Analizza i chunk recuperati e cerca segnali di omissioni o vaghezza.
    """
    signals = ["non specificato", "non dettagliato", "stimato", "potrebbe", "in fase di valutazione"]
    findings = []

    for chunk in text_chunks:
        for signal in signals:
            if signal in chunk.lower():
                findings.append(f"Omissione potenziale: '{signal}' → {chunk[:120]}...")

    if not findings:
        return "Nessuna omissione evidente rilevata."

    return "\n".join(findings)


def compare_periods(chunks_q1, chunks_q2):
    """
    Confronta due periodi e segnala differenze qualitative.
    """
    summary = []

    if len(chunks_q2) > len(chunks_q1):
        summary.append("Q2 mostra maggiore complessità e potenziali rischi rispetto a Q1.")

    if any("riduzione" in c.lower() for c in chunks_q2):
        summary.append("In Q2 emergono segnali di riduzione delle performance.")

    if not summary:
        return "Nessuna differenza rilevante tra i periodi."

    return "\n".join(summary)


def audit_compliance(text_chunks):
    """
    Valuta possibili problemi di compliance.
    """
    compliance_flags = ["deroga", "eccezione", "non conforme", "violazione"]
    issues = []

    for chunk in text_chunks:
        for flag in compliance_flags:
            if flag in chunk.lower():
                issues.append(f"Possibile problema di compliance: '{flag}' → {chunk[:120]}...")

    if not issues:
        return "Nessun problema di compliance evidente."

    return "\n".join(issues)
