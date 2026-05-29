# ======================================================
# IMPORTS
# ======================================================
import os
import operator
from pathlib import Path
from typing import TypedDict, Annotated, Literal

import psycopg
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import ToolNode

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from router import general_chat_agent, route_initial_query
from critic import critic_agent, route_critic
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from tools.memory_tool import save_user_preference, get_relevant_memories

# ======================================================
# LOAD ENV VARIABLES
# ======================================================
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# ======================================================
# LLM
# ======================================================
llm = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    api_key=GROQ_API_KEY,
    temperature=0
)

# ======================================================
# DEFINING THE TOOLBELT WITH PYDANTIC
# ======================================================
class HotelSearchInput(BaseModel):
    query: str = Field(description="The hotel search query")

class FlightSearchInput(BaseModel):
    origin: str = Field(default="New York", description="Starting city")
    destination: str = Field(description="Destination city")
    departure_date: str = Field(default="", description="Departure date")
    return_date: str = Field(default="", description="Return date")
    adults: str = Field(default="1", description="Number of adults")

@tool(args_schema=FlightSearchInput)
def fetch_flights(
    destination: str, 
    origin: str = "New York", 
    departure_date: str = "", 
    return_date: str = "",
    adults: str = "1",
) -> str:
    """Search for live flights, airlines, and flight prices."""
    query_string = f"flights from {origin} to {destination} from {departure_date} to {return_date} for {adults} adults"
    return search_flights(query_string)

@tool(args_schema=HotelSearchInput)
def fetch_hotels(query: str) -> str:
    """Search the web for the best hotels, resorts, and accommodations."""
    return tavily_search(query)

tools = [fetch_flights, fetch_hotels, save_user_preference]
llm_with_tools = llm.bind_tools(tools)

# ======================================================
# ADVANCED STATE
# ======================================================
class TravelState(MessagesState):
    summary: str          
    llm_calls: int        
    user_query: str       
    final_response: str   

# ======================================================
# CORE AGENT NODES
# ======================================================
def planner_agent(state: TravelState):
    latest_message = state["messages"][-1].content
    past_memories = get_relevant_memories(latest_message)

    sys_msg_content = (
        "You are an elite AI travel planner. Use your tools to fetch flight and hotel data.\n"
        "CRITICAL RULES:\n"
        "1. If the user does not provide an origin city, use generic flight data or assume 'New York'.\n"
        "2. DO NOT call the same tool more than once. If a tool returns mock data, errors, or vague results, ACCEPT IT and do not retry.\n"
        "3. Once you have attempted to gather flight and hotel info, immediately generate the final travel itinerary.\n"
        "4. If the user tells you about their preferences, immediately use the save_user_preference tool."
    )
    
    if state.get("summary"):
        sys_msg_content += f"\n\nContext from previous chats: {state['summary']}"
        
    if past_memories:
        sys_msg_content += past_memories
        
    messages = [SystemMessage(content=sys_msg_content)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response], "llm_calls": state.get("llm_calls", 0) + 1}

def summarize_conversation(state: TravelState):
    summary = state.get("summary", "")
    if summary:
        summary_prompt = f"Previous summary: {summary}\n\nUpdate the summary using the new messages."
    else:
        summary_prompt = "Summarize the key travel preferences and findings from the conversation above."
        
    messages_to_summarize = state["messages"][:-2] 
    prompt = messages_to_summarize + [HumanMessage(content=summary_prompt)]
    response = llm.invoke(prompt)
    
    return {"summary": response.content, "llm_calls": state.get("llm_calls", 0) + 1}

def human_approval(state: TravelState):
    # This node acts as an empty placeholder. The real action happens in the terminal 
    # where we manually inject the human's response using update_state().
    return {}

# ======================================================
# ROUTING LOGIC
# ======================================================
def should_continue(state: TravelState) -> Literal["tools", "human_approval"]:
    """Decides the next step in the ReAct loop."""
    last_message = state["messages"][-1]
    
    # 1. Did the LLM request a tool?
    if last_message.tool_calls:
        return "tools"
        
    # 2. If it didn't request a tool, it means it finished writing the itinerary!
    # Send it straight to the human, bypassing the summarization trap.
    return "human_approval"

def check_human_feedback(state: TravelState) -> Literal["planner_agent", END]:
    """Routes the graph based on the human's manual input."""
    last_message = state["messages"][-1].content
    
    # If the human approved it, end the graph.
    if last_message == "APPROVED":
        return END
        
    # If the human provided feedback (e.g., "Find a cheaper hotel"), route back to the brain!
    return "planner_agent"

# ======================================================
# GRAPH SETUP
# ======================================================
graph = StateGraph(TravelState)

# 1. Add all nodes
graph.add_node("planner_agent", planner_agent)
graph.add_node("general_chat_agent", general_chat_agent) 
graph.add_node("critic_agent", critic_agent) # NEW
graph.add_node("tools", ToolNode(tools)) 
graph.add_node("summarize_conversation", summarize_conversation)
graph.add_node("human_approval", human_approval)

# 2. Start at the conditional router
graph.add_conditional_edges(
    START, 
    route_initial_query,
    {
        "planner_agent": "planner_agent",
        "general_chat_agent": "general_chat_agent"
    }
)

# 3. Standard Planner Edges (Intercepted!)
graph.add_conditional_edges(
    "planner_agent", 
    should_continue,
    {
        "tools": "tools",
        # We intercept the flow here so the Critic reviews the plan first
        "human_approval": "critic_agent" 
    }
)
graph.add_edge("tools", "planner_agent")
graph.add_edge("summarize_conversation", "planner_agent")

# 4. Critic Routing (Pass or Fail)
graph.add_conditional_edges(
    "critic_agent",
    route_critic,
    {
        "human_approval": "human_approval", # Passed QA, show the user
        "planner_agent": "planner_agent"    # Failed QA, rewrite it
    }
)

# 5. Human Feedback Loop
graph.add_conditional_edges("human_approval", check_human_feedback)
graph.add_edge("general_chat_agent", END)

# ======================================================
# COMPILE APP WITH INTERRUPT
# ======================================================
_conn = psycopg.connect(DATABASE_URL, autocommit=True)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()

# PHASE 8 MAGIC: We explicitly tell the graph to freeze before this node
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_approval"]
)

# ======================================================
# TERMINAL TESTING (Phase 8 UI)
# ======================================================
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "canda"}}
    
    user_input = input("\nEnter travel request:\n\n")
    print("\n[System] Invoking Autonomous Agent Loop...\n")
    
    # 1. Start the initial execution
    for chunk in app.stream(
        {"messages": [HumanMessage(content=user_input)], "user_query": user_input, "llm_calls": 0, "summary": ""},
        config=config,
        stream_mode="updates"
    ):
        for node_name, state_update in chunk.items():
            print(f"✅ Agent completed: {node_name}")
            
    # 2. Check if the graph is paused waiting for a human
    state = app.get_state(config)
    
    if state.next and state.next[0] == "human_approval":
        print("\n===================================")
        print("⏸️ GRAPH PAUSED: AWAITING HUMAN REVIEW")
        print("===================================\n")
        
        # Display the itinerary for the user to read
        print(state.values["messages"][-1].content)
        
        # Ask for manual input
        print("\n-----------------------------------")
        feedback = input("Do you approve this itinerary? (Type 'yes' to approve, or type requested changes): ")
        
        if feedback.lower() in ["yes", "y", "approve"]:
            print("\n[System] Approval confirmed. Finalizing workflow...\n")
            # Inject the approval token into the state as if the human_approval node generated it
            app.update_state(config, {"messages": [HumanMessage(content="APPROVED")]}, as_node="human_approval")
        else:
            print("\n[System] Feedback received. Routing back to the AI Planner...\n")
            # Inject the human's custom feedback into the state
            app.update_state(config, {"messages": [HumanMessage(content=f"Human requested changes: {feedback}")]}, as_node="human_approval")
            
        # 3. Resume the graph by passing 'None' to the stream
        for chunk in app.stream(None, config=config, stream_mode="updates"):
            for node_name, state_update in chunk.items():
                print(f"✅ Agent completed: {node_name}")
                
        print("\n===================================")
        print("FINAL RESPONSE")
        print("===================================\n")
        
        final_state = app.get_state(config).values
        
        # The AI's response is now the second to last message, because the last message is our manual "APPROVED" token
        if final_state["messages"][-1].content == "APPROVED":
            print(final_state["messages"][-2].content)
        else:
            print(final_state["messages"][-1].content)