from src.llm_engine import LLMEngine
from src.rag_setup import retrieve_context
from src.data_extractor import extract_data


_llm_instance = LLMEngine()

def get_llm():
    return _llm_instance

def set_llm(new_engine: LLMEngine):
    global _llm_instance
    _llm_instance = new_engine

def get_rag_context(query: str):
    return '\n'.join(retrieve_context(query))
