import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

# 1. Initialize the Critic LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant", 
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# 2. Define the QA Output Schema
class CriticReview(BaseModel):
    passed: str = Field(description="Strictly output the string 'true' if the itinerary strictly meets ALL user constraints. Output 'false' if it violates any constraints or hallucinated information.")
    feedback: str = Field(description="If passed is 'false', provide specific, harsh instructions to the planner on what to fix. If 'true', leave empty.")

# 3. Create the Critic Agent
def critic_agent(state):
    """Audits the drafted plan against the original user query."""
    user_query = state.get("user_query", "")
    latest_plan = state["messages"][-1].content
    
    sys_msg = SystemMessage(
            content="""You are a pragmatic Quality Assurance Reviewer for a travel agency. Compare the proposed itinerary against the user's original request. 
            CRITICAL RULES:
            1. Only fail the plan if it actively VIOLATES a constraint (e.g., includes a location the user explicitly wanted to avoid).
            2. If the user asked to avoid a location, and that location is simply NOT in the itinerary, that is a PASS. Do NOT demand the planner add explicit notes stating they avoided it.
            3. Do not be pedantic about formatting. If the core travel requests are met, you must pass it."""
        )
    
    eval_prompt = f"User Request: {user_query}\n\nProposed Plan:\n{latest_plan}"
    
    # Force the LLM to output our structured Pass/Fail JSON
    classifier_llm = llm.with_structured_output(CriticReview)
    review = classifier_llm.invoke([sys_msg, HumanMessage(content=eval_prompt)])
    
# Safely extract values whether LangChain returns a dict or a Pydantic object
    passed_status = review.get("passed", "false") if isinstance(review, dict) else review.passed
    feedback_text = review.get("feedback", "No feedback provided.") if isinstance(review, dict) else review.feedback

    # Evaluate the string value
    if passed_status.lower() == 'true':
        # If it passes, return no new messages so the graph flows normally
        return state 
    else:
        # If it fails, append the feedback to the thread as a rejection notice
        return {
            "messages": [HumanMessage(content=f"QA REJECTION: The plan failed validation. You must fix these issues and generate a new plan: {feedback_text}")]
        }
# 4. Create the Routing Logic
def route_critic(state) -> Literal["human_approval", "planner_agent"]:
    """Reads the state to see if the QA check passed or failed, with a Circuit Breaker."""
    messages = state.get("messages", [])
    latest_msg = messages[-1].content
    
    if "QA REJECTION:" in latest_msg:
        # CIRCUIT BREAKER: Count how many times we've rejected the plan in this thread
        rejection_count = sum(1 for msg in messages if hasattr(msg, 'content') and "QA REJECTION:" in msg.content)
        
        if rejection_count >= 2:
            print("⚡ CIRCUIT BREAKER TRIPPED: Max QA retries reached. Forcing human review.")
            # We override the rejection and force the graph to the user
            return "human_approval"
            
        # If under the limit, send it back to the drawing board
        return "planner_agent"
    
    # Send it to the user for final approval if it passed
    return "human_approval"