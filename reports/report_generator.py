"""
Generazione report PDF
"""
def generate_audit_report(analysis_results, output_dir="/mnt/user-data/outputs", dashboard_path=None):
    """
    Genera report PDF professionale con analisi finanziarie

    Args:
        analysis_results: dict con chiavi:
            - 'omissions': str (risultato tool omissioni)
            - 'comparison': str (risultato tool confronto)
            - 'compliance': str (risultato tool compliance)
            - 'simulation': str (opzionale, risultato simulazione)
            - 'metadata': dict (es. {'period': 'Q2 2024', 'analyst': 'AI Agent'})
        output_dir: directory di output
        dashboard_path: path opzionale dell'immagine dashboard da includere

    Returns:
        str: path del PDF generato
    """

    from fpdf import FPDF
    from datetime import datetime
    import os

    # Assicurati che la directory esista
    os.makedirs(output_dir, exist_ok=True)

    # Crea PDF
    pdf = FPDF()
    pdf.add_page()

    # --- INTESTAZIONE ---
    pdf.set_font("Arial", 'B', size=18)
    pdf.cell(0, 15, txt="FinSecure Analytics", ln=True, align='C')

    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(0, 10, txt="Report di Audit Finanziario", ln=True, align='C')

    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, txt=f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')

    # Metadata opzionali
    metadata = analysis_results.get('metadata', {})
    if 'period' in metadata:
        pdf.cell(0, 6, txt=f"Periodo: {metadata['period']}", ln=True, align='C')

    pdf.ln(10)  # Spazio

    # Linea separatrice
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    # --- FUNZIONE HELPER PER SEZIONI ---
    def add_section(title, content, icon=""):
        """Aggiunge una sezione formattata"""
        # Titolo sezione
        pdf.set_font("Arial", 'B', size=13)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, txt=f"{icon} {title}", ln=True, fill=True)
        pdf.ln(3)

        # Contenuto
        pdf.set_font("Arial", size=10)

        # Gestisci encoding per caratteri speciali
        if content:
            # Sostituisci emoji con testo (FPDF non supporta emoji)
            content_cleaned = (content
                               .replace('✅', '[OK]')
                               .replace('❌', '[X]')
                               .replace('⚠️', '[!]')
                               .replace('🔴', '[CRITICO]')
                               .replace('📈', '[+]')
                               .replace('📉', '[-]')
                               .replace('📊', '[DATO]')
                               .replace('🚨', '[ALERT]')
                               .replace('€', 'EUR')
                               )

            # Rimuovi caratteri non ASCII rimanenti
            content_cleaned = content_cleaned.encode('latin-1', 'ignore').decode('latin-1')

            pdf.multi_cell(0, 6, txt=content_cleaned)
        else:
            pdf.set_text_color(150, 150, 150)
            pdf.multi_cell(0, 6, txt="Nessun dato disponibile per questa sezione")
            pdf.set_text_color(0, 0, 0)

        pdf.ln(5)

    # --- SEZIONE 1: ANALISI OMISSIONI ---
    if 'omissions' in analysis_results:
        add_section("1. Analisi Omissioni e Completezza Dati",
                    analysis_results['omissions'],
                    icon="[1]")

    # --- SEZIONE 2: CONFRONTO PERIODI ---
    if 'comparison' in analysis_results:
        add_section("2. Confronto Periodi Q1 vs Q2",
                    analysis_results['comparison'],
                    icon="[2]")

    # --- SEZIONE 3: COMPLIANCE ---
    if 'compliance' in analysis_results:
        add_section("3. Audit di Compliance Normativa",
                    analysis_results['compliance'],
                    icon="[3]")
    
    # 🆕 AGGIUNGI DASHBOARD SE DISPONIBILE
    if dashboard_path and os.path.exists(dashboard_path):
        pdf.ln(10)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)
        
        pdf.set_font("Arial", 'B', size=13)
        pdf.cell(0, 10, txt="4. Dashboard Comparativa Q1 vs Q2", ln=True)
        pdf.ln(5)
        
        # Calcola dimensioni per centrare l'immagine
        page_width = 210  # A4 width in mm
        margin = 10
        img_width = page_width - 2 * margin
        
        # Aggiungi immagine
        try:
            pdf.image(dashboard_path, x=margin, w=img_width)
            pdf.ln(10)
        except Exception as e:
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(0, 6, txt=f"[Errore nel caricamento dashboard: {str(e)}]")
    

    # --- SEZIONE 4: SIMULAZIONE (opzionale) ---
    if 'simulation' in analysis_results and analysis_results['simulation']:
        section_num = "5" if dashboard_path else "4"  # Aggiusta numerazione
        add_section(f"{section_num}. Simulazione Scenari di Rischio",
                    analysis_results['simulation'],
                    icon=f"[{section_num}]")

    # --- SEZIONE CONCLUSIONI ---
    pdf.ln(5)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 8, txt="Conclusioni e Raccomandazioni", ln=True)
    pdf.set_font("Arial", size=10)

    # Genera raccomandazioni automatiche basate sui risultati
    recommendations = []

    if 'omissions' in analysis_results and 'MANCANTE' in analysis_results['omissions']:
        recommendations.append("- Integrare i dati mancanti identificati nelle sezioni incomplete")

    if 'comparison' in analysis_results and 'CRITICO' in analysis_results['comparison']:
        recommendations.append("- Monitorare attentamente le metriche critiche evidenziate")
        recommendations.append("- Implementare azioni correttive per ridurre l'esposizione al rischio")

    if 'compliance' in analysis_results and 'Disclaimer' in analysis_results['compliance']:
        recommendations.append("- Aggiungere disclaimer legale alla documentazione finanziaria")

    if not recommendations:
        recommendations.append("- Continuare il monitoraggio periodico delle metriche finanziarie")

    for rec in recommendations:
        pdf.multi_cell(0, 6, txt=rec)

    # --- FOOTER ---
    pdf.ln(10)
    pdf.set_font("Arial", 'I', size=8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, txt="Report generato automaticamente da FinSecure AI Agent", ln=True, align='C')
    pdf.cell(0, 5, txt="Questo documento e' riservato e confidenziale", ln=True, align='C')

    # Salva PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'audit_report_{timestamp}.pdf')

    pdf.output(output_path)

    return output_path
