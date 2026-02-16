"""
app.py
Entry point per FinSecure AI Audit Agent
"""
import sys
import os

# 1️⃣ PRIMA DI TUTTO: Sopprimi warning
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

# 2️⃣ Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 3️⃣ SOLO ORA importa moduli
from ingestion.parse_docs import parse_and_index
from ui.gradio_interface import create_interface


def initialize():
    """Inizializza il sistema (indicizzazione documenti)"""
    
    print("=" * 60)
    print("🚀 FinSecure AI Audit Agent - Inizializzazione")
    print("=" * 60)
    
    print("\n📚 Indicizzazione documenti in corso...")
    try:
        parse_and_index()
        print("✅ Documenti indicizzati con successo!")
    except Exception as e:
        print(f"⚠️ Errore durante l'indicizzazione: {e}")
        print("Continuando comunque...")
    
    print("\n✅ Sistema inizializzato!")


def launch_interface():
    """Crea e lancia l'interfaccia Gradio"""
    
    print("\n🎨 Creazione interfaccia Gradio...")
    demo = create_interface()
    print("✅ Interfaccia creata!")
    
    print("\n🚀 Lancio interfaccia...")
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
