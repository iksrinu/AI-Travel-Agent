import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

# 1. Initialize a lightweight LLM specifically for routing
llm = ChatGroq(
    model="llama-3.3-70b-versatile", # Feel free to match whatever model you are using in main.py
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# 2. Define the Classification Schema
class RouteClassification(BaseModel):
    intent: Literal["travel_planning", "general_query"] = Field(
        description="Classify the user's query. If they want to plan a trip, book flights, or find hotels, choose 'travel_planning'. For all other casual questions, greetings, or off-topic queries, choose 'general_query'."
    )

# 3. Create the General Chat Agent (for non-travel queries)
def general_chat_agent(state):
    """Handles basic greetings and non-travel questions quickly and cheaply."""
    sys_msg = SystemMessage(
        content="You are a helpful AI Travel Agent. The user just asked a general question or said hello. Answer politely and concisely, but remind them that your primary job is to book flights and plan travel itineraries."
    )
    
    messages = [sys_msg] + state["messages"]
    response = llm.invoke(messages)
    
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# 4. Create the Routing Logic (The Traffic Cop)
def route_initial_query(state) -> Literal["planner_agent", "general_chat_agent"]:
    """Acts as the traffic cop for the very first user message."""
    latest_message = state["messages"][-1].content
    
    # Force the LLM to ignore all tools and focus only on the classification schema
    classifier_llm = llm.with_structured_output(RouteClassification)
    
    # We pass 'tools=[]' to ensure it has no capability to call anything else
    decision = classifier_llm.invoke([
        SystemMessage(content="You are a routing classification system. Do not use tools."), 
        HumanMessage(content=latest_message)
    ])
    
    if decision.intent == "travel_planning":
        return "planner_agent"
    
    return "general_chat_agent"