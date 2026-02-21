# FinSecure AI Audit Agent

Agente AI per l'analisi automatica di report finanziari trimestrali.
Utilizza LlamaIndex ReActAgent per ragionamento agentico su documenti reali.

## Funzionalità

- Identificazione di omissioni e dati mancanti nei report
- Confronto metriche finanziarie tra Q1 e Q2 2024
- Verifica conformità normativa (compliance)
- Predizione trend rischio Q3 tramite regressione lineare
- Simulazione scenari what-if (crisi, crescita, rialzo tassi)
- Generazione report PDF con dashboard comparativa

## Architettura
```
app.py                  # Entry point
config/
  models.py             # Setup Mistral-7B + embeddings
  settings.py           # Path configurabili via env
agent/
  agent.py              # ReActAgent + indice vettoriale cachato
tools/
  tools.py              # Tool agentici + wrapper per ReActAgent
  simulation.py         # Simulazione scenari di rischio
  visualization.py      # Dashboard matplotlib
ingestion/
  parse_docs.py         # Parsing e indicizzazione documenti
reports/
  report_generator.py   # Generazione PDF
ui/
  gradio_interface.py   # Interfaccia Gradio
```

## Avvio (Google Colab)
```bash
pip install -r requirements.txt
python app.py
```

Per eseguire fuori da Colab, imposta la variabile d'ambiente:
```bash
export FINSECURE_BASE_DIR=/path/to/finsecure-agent
python app.py
```

## Tecnologie

- LlamaIndex ReActAgent + RAG con filtri su metadata
- Mistral-7B-Instruct-v0.2 (quantizzazione 4-bit con BitsAndBytes)
- scikit-learn per predizione trend
- Matplotlib/Seaborn per visualizzazioni
- FPDF per report PDF
- Gradio per interfaccia web
