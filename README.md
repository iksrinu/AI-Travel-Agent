
```markdown
# 🌍 AI Autonomous Travel Planner

An enterprise-grade, multi-agent AI travel booking system built with **LangGraph**. This application utilizes a ReAct (Reason + Act) architecture to autonomously research flights, find hotels, and draft itineraries, while featuring a **Human-in-the-Loop (HITL)** interrupt system for manual review and approval.

## ✨ Key Features

* **🧠 Autonomous ReAct Agent:** The core planner dynamically decides which tools to call, parses the data, and formulates a complete travel plan without hardcoded chains.
* **⏸️ Human-in-the-Loop (HITL):** The workflow explicitly pauses execution before finalizing the itinerary, allowing the user to approve the plan or submit feedback to force the agent to rethink and re-execute.
* **💾 Long-Term Semantic Memory:** Integrates **ChromaDB** as a vector database to silently save and recall user travel preferences (e.g., budget constraints, dietary needs) across entirely different sessions.
* **🛠️ Live Tool Execution:** * **AviationStack API:** Fetches real-time flight schedules and airline data.
  * **Tavily Search:** Scours the web for up-to-date hotel ratings, sightseeing, and local transport.
* **🎨 Streamlit Frontend:** A sleek, dark-mode ChatGPT-style web interface that tracks the agent's live execution state and renders the final plan with a downloadable Markdown export.

## 🧰 Tech Stack

* **Framework:** LangGraph, LangChain
* **LLM / Inference:** Groq (LLaMA 3.1 / Gemma 2 / Mixtral)
* **Frontend:** Streamlit
* **Databases:** PostgreSQL (Short-term thread memory), ChromaDB (Long-term vector memory)
* **Tools/APIs:** AviationStack, Tavily

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/iksrinu/AI-Travel-Agent.git](https://github.com/iksrinu/AI-Travel-Agent.git)
cd AI-Travel-Agent

```

### 2. Install Dependencies

Make sure you have a Python virtual environment activated, then install the required packages:

```bash
pip install langgraph langchain-core langchain-groq streamlit psycopg chromadb pydantic python-dotenv

```

*(Note: You will also need to install the specific packages for your tools, such as `tavily-python` and `requests`)*

### 3. Environment Variables

Create a `.env` file in the root directory and add your API keys:

```env
GROQ_API_KEY="your_groq_key"
DATABASE_URL="your_postgresql_connection_string"
# Add your Tavily and AviationStack keys if applicable in your tool files

```

### 4. Run the Application

Start the Streamlit server:

```bash
streamlit run frontend.py

```

## 🏗️ Architecture Flow

1. **User Input:** The user provides a travel destination and parameters.
2. **Memory Retrieval:** The system queries ChromaDB for past preferences.
3. **Planner Agent:** Analyzes the prompt and dynamically routes to necessary tools.
4. **Tool Execution:** Fetches live flight and hotel data.
5. **Summarizer:** Compresses thread history if the context window gets too large.
6. **Interrupt Barrier:** The graph freezes and displays the drafted itinerary to the user.
7. **Resolution:** The user approves (ending the graph) or provides feedback (routing back to the Planner Agent).

---

*Created by Srinivas Kaluvala*

```

