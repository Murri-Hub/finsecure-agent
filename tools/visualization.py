"""
visualization.py
Dashboard e visualizzazioni
"""
from config.settings import OUTPUT_DIR

def generate_dashboard(q1_data, q2_data, output_dir=None):
    if output_dir is None:
        output_dir = OUTPUT_DIR
    """
    Genera visualizzazioni comparative tra Q1 e Q2

    Args:
        q1_data: dict con metriche Q1 {'ricavi': 11.8, 'margine': 39.8, 'rischio': 2.4}
        q2_data: dict con metriche Q2
        output_dir: directory di output (default per Colab)

    Returns:
        str: path del file immagine generato
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os

    # Assicurati che la directory esista
    os.makedirs(output_dir, exist_ok=True)

    # Configura stile
    sns.set_style("whitegrid")
    plt.rcParams['figure.facecolor'] = 'white'

    # Crea figura
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('FinSecure Analytics - Dashboard Comparativa Q1 vs Q2 2024',
                 fontsize=16, fontweight='bold')

    # GRAFICO 1: RICAVI
    if 'ricavi' in q1_data and 'ricavi' in q2_data:
        ricavi_vals = [q1_data['ricavi'], q2_data['ricavi']]
        bars = axes[0, 0].bar(['Q1', 'Q2'], ricavi_vals, color=['#3498db', '#2ecc71'])
        axes[0, 0].set_title('Ricavi (M€)', fontweight='bold')
        axes[0, 0].set_ylabel('Milioni €')

        # Aggiunge valori sopra le barre
        for i, (bar, val) in enumerate(zip(bars, ricavi_vals)):
            axes[0, 0].text(bar.get_x() + bar.get_width() / 2, val + 0.2,
                            f'{val:.1f}M', ha='center', va='bottom', fontweight='bold')

        # Calcola variazione
        diff = ((ricavi_vals[1] - ricavi_vals[0]) / ricavi_vals[0]) * 100
        axes[0, 0].text(0.5, 0.95, f'Variazione: {diff:+.1f}%',
                        transform=axes[0, 0].transAxes, ha='center',
                        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    else:
        axes[0, 0].text(0.5, 0.5, 'Dati ricavi non disponibili',
                        ha='center', va='center', transform=axes[0, 0].transAxes)

    # GRAFICO 2: MARGINE OPERATIVO
    if 'margine' in q1_data and 'margine' in q2_data:
        margine_vals = [q1_data['margine'], q2_data['margine']]
        axes[0, 1].plot(['Q1', 'Q2'], margine_vals, marker='o', linewidth=2,
                        markersize=10, color='#e74c3c')
        axes[0, 1].set_title('Margine Operativo (%)', fontweight='bold')
        axes[0, 1].set_ylabel('Percentuale %')
        axes[0, 1].grid(True, alpha=0.3)

        # Evidenzia punti
        for i, val in enumerate(margine_vals):
            axes[0, 1].annotate(f'{val:.1f}%',
                                xy=(i, val),
                                xytext=(0, 10),
                                textcoords='offset points',
                                ha='center',
                                fontweight='bold')

        # Alert se calo significativo
        diff = margine_vals[1] - margine_vals[0]
        if diff < -5:
            axes[0, 1].axhline(y=30, color='red', linestyle='--', alpha=0.5, label='Soglia critica')
            axes[0, 1].legend()
    else:
        axes[0, 1].text(0.5, 0.5, 'Dati margine non disponibili',
                        ha='center', va='center', transform=axes[0, 1].transAxes)

    # GRAFICO 3: ESPOSIZIONE AL RISCHIO
    if 'rischio' in q1_data and 'rischio' in q2_data:
        rischio_vals = [q1_data['rischio'], q2_data['rischio']]
        colors = ['#f39c12' if rischio_vals[0] < 3 else '#e74c3c',
                  '#f39c12' if rischio_vals[1] < 3 else '#e74c3c']
        bars = axes[1, 0].bar(['Q1', 'Q2'], rischio_vals, color=colors)
        axes[1, 0].set_title('Esposizione al Rischio (M€)', fontweight='bold')
        axes[1, 0].set_ylabel('Milioni €')

        # Valori sopra le barre
        for bar, val in zip(bars, rischio_vals):
            axes[1, 0].text(bar.get_x() + bar.get_width() / 2, val + 0.1,
                            f'{val:.1f}M', ha='center', va='bottom', fontweight='bold')

        # Soglia di rischio critico
        axes[1, 0].axhline(y=3.0, color='red', linestyle='--', alpha=0.5, label='Soglia critica (3M)')
        axes[1, 0].legend()

        diff_pct = ((rischio_vals[1] - rischio_vals[0]) / rischio_vals[0]) * 100
        axes[1, 0].text(0.5, 0.95, f'Variazione: {diff_pct:+.1f}%',
                        transform=axes[1, 0].transAxes, ha='center',
                        bbox=dict(boxstyle='round', facecolor='salmon' if diff_pct > 20 else 'lightgray', alpha=0.5))
    else:
        axes[1, 0].text(0.5, 0.5, 'Dati rischio non disponibili',
                        ha='center', va='center', transform=axes[1, 0].transAxes)

    # GRAFICO 4: RIEPILOGO KPI
    # Crea un heatmap con tutti i KPI
    metrics_names = []
    q1_values = []
    q2_values = []

    for metric in ['ricavi', 'margine', 'rischio']:
        if metric in q1_data and metric in q2_data:
            metrics_names.append(metric.capitalize())
            # Normalizza per confronto
            q1_val = q1_data[metric]
            q2_val = q2_data[metric]
            change_pct = ((q2_val - q1_val) / q1_val * 100) if q1_val != 0 else 0
            q1_values.append(0)  # baseline
            q2_values.append(change_pct)

    if metrics_names:
        x_pos = range(len(metrics_names))
        width = 0.35

        bars1 = axes[1, 1].bar([p - width / 2 for p in x_pos], q1_values, width,
                               label='Q1 (baseline)', color='#95a5a6', alpha=0.7)
        bars2 = axes[1, 1].bar([p + width / 2 for p in x_pos], q2_values, width,
                               label='Q2 (variazione %)',
                               color=['#2ecc71' if v > 0 else '#e74c3c' for v in q2_values])

        axes[1, 1].set_title('Variazioni % Q1→Q2', fontweight='bold')
        axes[1, 1].set_ylabel('Variazione %')
        axes[1, 1].set_xticks(x_pos)
        axes[1, 1].set_xticklabels(metrics_names)
        axes[1, 1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        # Valori sopra le barre
        for bar in bars2:
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width() / 2., height,
                            f'{height:+.1f}%', ha='center',
                            va='bottom' if height > 0 else 'top',
                            fontweight='bold')
    else:
        axes[1, 1].text(0.5, 0.5, 'Dati KPI non disponibili',
                        ha='center', va='center', transform=axes[1, 1].transAxes)

    # Layout ottimizzato
    plt.tight_layout()

    # Salva figura
    output_path = os.path.join(output_dir, 'dashboard_comparativa.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

    # Chiusura figura per liberare memoria
    plt.close(fig)

    return output_path



