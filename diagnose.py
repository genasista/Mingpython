import os
import sys

print("=== PYTHON API DIAGNOSTIK ===")
print(f"PORT: {os.getenv('PORT', 'NOT SET')}")
print(f"GROQ_API_KEY: {'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET'}")
print(f"OPENAI_API_KEY: {'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
print(f"LLM_BASE_URL: {os.getenv('LLM_BASE_URL', 'NOT SET')}")
print(f"LLM_MODEL: {os.getenv('LLM_MODEL', 'NOT SET')}")

# Test LLM service
try:
    from app.servies.llm_service import llm_service
    print(f"\nLLM Service Config:")
    print(f"  API Key: {'SET' if llm_service.config.api_key else 'NOT SET'}")
    print(f"  Base URL: {llm_service.config.base_url}")
    print(f"  Model: {llm_service.config.model}")
except Exception as e:
    print(f"\n LLM Service Error: {e}")
