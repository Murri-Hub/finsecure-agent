"""
app.py
Inizializzazione FinSecure AI Audit Agent (SOLO setup, NO interfaccia)
"""
import sys
import os
print("\n🎨 Importazione moduli UI...")
from ui.gradio_interface import create_interface

# Sopprimi warning TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Aggiungi path per import
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from ingestion.parse_docs import parse_and_index

def initialize():
    """Inizializza il sistema (indicizzazione documenti)"""
    
    print("=" * 60)
    print("🚀 FinSecure AI Audit Agent - Inizializzazione")
    print("=" * 60)
    
    # Indicizzazione documenti
    print("\n📚 Indicizzazione documenti in corso...")
    try:
        parse_and_index()
        print("✅ Documenti indicizzati con successo!")
    except Exception as e:
        print(f"⚠️ Errore durante l'indicizzazione: {e}")
        print("Continuando comunque...")
    
    print("\n✅ Sistema inizializzato!")
    print("\nPer lanciare l'interfaccia Gradio:")
    print("  python launch_gradio.py")
    print("\nOppure importa create_interface da ui.gradio_interface")
    print("=" * 60)


if __name__ == "__main__":
    initialize()
