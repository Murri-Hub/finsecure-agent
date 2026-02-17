"""
simulation.py
Simulazione scenari di rischio
"""
import re


def simulate_risk_scenario(chunks, scenario_type="crisis"):
    """
    Simula scenari di rischio (es. recessione, aumento tassi, default cliente)
    """

    # --- ESTRAI METRICHE ATTUALI ---
    def extract_metrics(chunks):
        """Estrae le metriche numeriche dai chunk"""
        metrics = {}
        all_text = " ".join(chunks)

        # Ricavi
        match = re.search(r'ricavi.*?(\d+[,.]?\d*)\s*milioni', all_text.lower())
        if match:
            metrics['ricavi'] = float(match.group(1).replace(',', '.'))

        # Margine
        match = re.search(r'margine.*?(\d+[,.]?\d*)%', all_text.lower())
        if match:
            metrics['margine'] = float(match.group(1).replace(',', '.'))

        # Rischio
        match = re.search(r'rischio.*?(\d+[,.]?\d*)\s*milioni', all_text.lower())
        if match:
            metrics['rischio'] = float(match.group(1).replace(',', '.'))

        # Liquidità
        match = re.search(r'liquidità.*?(\d+[,.]?\d*)\s*milioni', all_text.lower())
        if match:
            metrics['liquidità'] = float(match.group(1).replace(',', '.'))

        # Costi
        match = re.search(r'costi.*?(\d+[,.]?\d*)\s*milioni', all_text.lower())
        if match:
            metrics['costi'] = float(match.group(1).replace(',', '.'))

        return metrics

    # DEFINIZIONE SCENARI
    scenarios = {
        "crisis": {
            "ricavi": -0.20,  # -20%
            "rischio": +0.50,  # +50%
            "liquidità": -0.30,  # -30%
            "margine": -5.0  # -5 punti percentuali
        },
        "growth": {
            "ricavi": +0.15,  # +15%
            "rischio": -0.10,  # -10%
            "liquidità": +0.20,  # +20%
            "margine": +3.0  # +3 punti percentuali
        },
        "interest_hike": {
            "costi": +0.10,  # +10%
            "rischio": +0.25,  # +25%
            "margine": -4.0  # -4 punti percentuali
        }
    }

    if scenario_type not in scenarios:
        return f"Scenario '{scenario_type}' non riconosciuto. Usa: crisis, growth, interest_hike"

    # ESTRAE METRICHE CORRENTI
    current_metrics = extract_metrics(chunks)

    if not current_metrics:
        return "Impossibile estrarre metriche dai documenti forniti"

    # APPLICA SCENARIO
    scenario_changes = scenarios[scenario_type]
    projected_metrics = {}

    for metric, current_value in current_metrics.items():
        if metric in scenario_changes:
            change = scenario_changes[metric]
            if metric == "margine":
                # Per margine, somma diretta (punti percentuali)
                projected_metrics[metric] = current_value + change
            else:
                # Per altre metriche, applica variazione percentuale
                projected_metrics[metric] = current_value * (1 + change)
        else:
            projected_metrics[metric] = current_value

    # FORMATTA RISULTATI
    scenario_names = {
        "crisis": "Scenario di Crisi",
        "growth": "Scenario di Crescita",
        "interest_hike": "Scenario Rialzo Tassi"
    }

    results = [f"\n{scenario_names.get(scenario_type, scenario_type)}\n{'=' * 50}"]
    results.append("\nMETRICHE ATTUALI vs PROIETTATE:\n")

    for metric in current_metrics.keys():
        current = current_metrics[metric]
        projected = projected_metrics[metric]
        diff = projected - current
        diff_pct = (diff / current * 100) if current != 0 else 0

        if metric == "margine":
            results.append(
                f"• {metric.capitalize()}: {current:.1f}% → {projected:.1f}% "
                f"({diff:+.1f} punti)"
            )
        else:
            results.append(
                f"• {metric.capitalize()}: {current:.1f}M → {projected:.1f}M "
                f"({diff:+.1f}M, {diff_pct:+.1f}%)"
            )

    # ALERT SE CRITICO
    results.append("\nALERT:")

    if projected_metrics.get('rischio', 0) > current_metrics.get('rischio', 0) * 1.3:
        results.append("Rischio aumenta oltre il 30% - Situazione critica!")

    if projected_metrics.get('margine', 100) < 20:
        results.append("Margine scende sotto il 20% - Soglia critica!")

    if projected_metrics.get('liquidità', 100) < 2:
        results.append("Liquidità critica sotto i 2M€ - Rischio default!")


    return "\n".join(results)

