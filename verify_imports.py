import sys
import os
import asyncio

# Fix path
sys.path.insert(0, os.path.abspath("."))

# Mock missing runtime libs
from unittest.mock import MagicMock
sys.modules["oracledb"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["sentence_transformers"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["fastapi"] = MagicMock()
sys.modules["fastapi.concurrency"] = MagicMock()
sys.modules["pydantic"] = MagicMock()

print("1. Testing Imports...")
try:
    from src.llm_engine import LLMEngine
    print("✅ src.llm_engine imported")
    
    from dependencies import set_llm, get_llm
    # Mock LLM for safety
    set_llm(LLMEngine(provider="ollama")) 
    print("✅ dependencies imported and initialized")

    from src.anomaly_detector import detect_anomalies
    print("✅ src.anomaly_detector imported")

    from src.backup_recommender import recommend_backup
    print("✅ src.backup_recommender imported")

    from src.query_optimizer import optimize_query
    print("✅ src.query_optimizer imported")

    from routers import performance, anomaly, backup
    print("✅ routers imported")

    print("\n🎉 ALL MODULES IMPORTED SUCCESSFULLY")

except Exception as e:
    print(f"\n❌ IMPORT ERROR: {e}")
    sys.exit(1)
