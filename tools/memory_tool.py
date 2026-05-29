# tools/memory_tool.py
import chromadb
from langchain_core.tools import tool

# 1. Initialize the local Vector Database
# This creates a hidden folder (.chroma_db) in your project to store memories permanently
chroma_client = chromadb.PersistentClient(path="./.chroma_db")

# Create or load a "collection" (like a table in SQL) for user preferences
collection = chroma_client.get_or_create_collection(name="user_preferences")

# 2. The Tool for the LLM to SAVE memories
@tool
def save_user_preference(preference: str) -> str:
    """
    Use this tool to save important details about the user's travel style, 
    dietary restrictions, budget, or future trip plans.
    Example: save_user_preference("User prefers local transport and budget hostels")
    """
    # We use the count as a simple unique ID for each memory
    memory_id = f"mem_{collection.count() + 1}"
    
    collection.add(
        documents=[preference],
        ids=[memory_id]
    )
    return f"Successfully remembered: {preference}"

# 3. The Function for the Backend to RETRIEVE memories
def get_relevant_memories(query: str) -> str:
    """Searches the vector database for memories related to the current query."""
    if collection.count() == 0:
        return ""
        
    results = collection.query(
        query_texts=[query],
        n_results=2 # Fetch the top 2 most relevant past memories
    )
    
    if results['documents'] and results['documents'][0]:
        memories = "\n- ".join(results['documents'][0])
        return f"\n\nRELEVANT LONG-TERM MEMORIES:\n- {memories}"
    
    return ""