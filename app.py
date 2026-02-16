"""
app.py
Entry point per FinSecure AI Audit Agent
"""
import sys
import os

# Aggiungi path per import
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from ingestion.parse_docs import parse_and_index
from ui.gradio_interface import create_interface

def main():
    """Inizializza e avvia l'applicazione"""
    
    print("=" * 60)
    print("🚀 FinSecure AI Audit Agent")
    print("=" * 60)
    
    # Indicizzazione documenti
    print("\n📚 Indicizzazione documenti in corso...")
    try:
        parse_and_index()
        print("✅ Documenti indicizzati con successo!")
    except Exception as e:
        print(f"⚠️ Errore durante l'indicizzazione: {e}")
        print("Continuando comunque...")
    
    # Crea interfaccia
    print("\n🎨 Creazione interfaccia Gradio...")
    demo = create_interface()
    print("✅ Interfaccia pronta!")
    
    # Lancio
    print("\n🌐 Avvio server Gradio...")
    print("=" * 60)
    
    demo.launch(
        share=True,      # Link pubblico temporaneo (72h)
        debug=True,      # Modalità debug
        server_name="0.0.0.0",
        server_port=7860
    )


if __name__ == "__main__":
    main()
