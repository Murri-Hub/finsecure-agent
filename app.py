"""
app.py
Entry point per FinSecure AI Audit Agent
"""
import sys
import os
from utils.colors import B, X        # Per print in grassetto

# Soppressione warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

# Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Import moduli
from ingestion.parse_docs import parse_and_index
from ui.gradio_interface import create_interface

def initialize():
    """Inizializza il sistema (indicizzazione documenti)"""
    
    print("\n" + "=" * 60)
    print("🚀 FinSecure AI Audit Agent - Inizializzazione")
    print("=" * 60)
    
    print("\nIndicizzazione documenti in corso...")
    try:
        parse_and_index()
        print(f"{B}Documenti indicizzati con successo!{X}")
    except Exception as e:
        print(f"Errore durante l'indicizzazione: {e}")
        print("Continuando comunque...")
    
    print(f"{B}\nSistema inizializzato!{X}")
    
def launch_interface():
    """Crea e lancia l'interfaccia Gradio"""
    
    print("\nCreazione interfaccia Gradio...")
    demo = create_interface()
    print(f"{B}Interfaccia creata!{X}")
    
    print("\nLancio interfaccia...")
    demo.queue().launch(
        share=True,
        inline=False,
        debug=False
    )


def main():
    """Workflow completo: inizializza + lancia interfaccia"""
    initialize()
    launch_interface()

if __name__ == "__main__":
    main()
