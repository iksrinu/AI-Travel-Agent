import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from main import GROQ_API_KEY

# Load your .env
load_dotenv()

# Print debug info to your terminal
print(f"--- DEBUGGING ---")
print(f"LANGCHAIN_API_KEY loaded: {bool(os.getenv('LANGCHAIN_API_KEY'))}")
print(f"LANGCHAIN_PROJECT: '{os.getenv('LANGCHAIN_PROJECT')}'")
print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")

# Run a dummy trace
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0
)
try:
    llm.invoke("Hello, are you connected?")
    print("\n--- SUCCESS: If you see this, the connection worked! ---")
except Exception as e:
    print(f"\n--- ERROR: {e} ---")