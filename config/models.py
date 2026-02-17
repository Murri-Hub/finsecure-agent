# models.py
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.huggingface import HuggingFaceLLM
from transformers import BitsAndBytesConfig
import torch

def setup_models():
    """Configura embed_model e LLM"""
    
    # Embeddings
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )
    
    # LLM con quantizzazione 4-bit
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    Settings.llm = HuggingFaceLLM(
        model_name="mistralai/Mistral-7B-Instruct-v0.2",
        tokenizer_name="mistralai/Mistral-7B-Instruct-v0.2",
        context_window=2048,
        max_new_tokens=500,
        generate_kwargs={
            "do_sample": True,
            "temperature": 0.4,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
        },
        model_kwargs={
            "quantization_config": bnb_config,
        },
        device_map="auto",
    )
