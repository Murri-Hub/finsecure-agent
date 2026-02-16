"""
launch_gradio.py
Launcher leggero per interfaccia Gradio (evita import pesanti all'avvio)
"""
import sys
import os

# Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

def main():
    """Lancia solo l'interfaccia (assumendo che i modelli siano già caricati)"""
    
    print("=" * 60)
    print("🚀 FinSecure AI Audit - Gradio Interface")
    print("=" * 60)
    
    print("✅ Moduli importati!")
    
    # Crea interfaccia
    print("\n🔨 Creazione interfaccia...")
    demo = create_interface()
    print("✅ Interfaccia pronta!")
    
    # Lancio
    print("\n🌐 Avvio server Gradio...")
    print("=" * 60 + "\n")
    
    demo.queue()  # Abilita queue per Colab
    
    demo.launch(
        share=False,
        debug=True,
        inline=True,
        height=800
    )


if __name__ == "__main__":
    # Sopprimi warning TensorFlow
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    main()
