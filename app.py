"""
app.py
Entry point per FinSecure AI Audit Agent
"""
import sys
import os
from utils.color import B, X

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from config.models import setup_models
from ingestion.parse_docs import parse_and_index
from ui.gradio_interface import create_interface

def main():
    print("Caricamento modelli...")
    setup_models()
    print(f"\n{B}Modelli caricati!{X}\n")

    print("Indicizzazione...")
    parse_and_index()
    print(f"\n{B}Fatto!{X}\n")

    print(f"{B}Lancio interfaccia...{X}\n")
    demo = create_interface()
    demo.queue().launch(
        share=True,
        inline=False,
        debug=False
    )

if __name__ == "__main__":
    main()
