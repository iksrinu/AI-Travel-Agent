import os
import requests

def search_flights(query: str) -> str:
    """
    Phase 2: Real-world API Integration.
    Fetches live flight data using AviationStack.
    """
    print(f"[Tool] Searching live flights for: {query}...")
    
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    
    # Fallback to mock data if no key is provided, preventing the app from crashing in production
    if not api_key or api_key == "your_aviationstack_key":
        return f"Mock Flight Data: Found available round-trip flights based on '{query}' starting at $450 with Delta Airlines."

    # Example integration using AviationStack API
    url = "http://api.aviationstack.com/v1/flights"
    #url = "http://api.aviationstack.com/v1/FAKE_ENDPOINT"
    
    # In a fully Tool-Calling system (Phase 5), the LLM will extract exact IATA codes. 
    # For now, we query general active flights as a proof of concept.
    params = {
        'access_key': api_key,
        'limit': 5
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status() # Raise exception for bad HTTP status codes
        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            flights = []
            for f in data["data"]:
                airline = f.get("airline", {}).get("name", "Unknown Airline")
                flight_num = f.get("flight", {}).get("iata", "Unknown")
                status = f.get("flight_status", "unknown")
                departure = f.get("departure", {}).get("airport", "Unknown Origin")
                arrival = f.get("arrival", {}).get("airport", "Unknown Destination")
                
                flights.append(f"{airline} ({flight_num}): {departure} -> {arrival} (Status: {status})")
                
            return "Live Flights Found:\n" + "\n".join(flights)
        else:
            return "No live flights found for these parameters right now."
            
    except requests.exceptions.RequestException as e:
        # AGENTIC ERROR RECOVERY: We talk directly to the LLM here.
        return f"TOOL ERROR: The AviationStack API failed or timed out. Do not crash. Politely inform the user that live flight data is temporarily unavailable, and seamlessly continue formulating the rest of the travel plan. System details: {str(e)}"