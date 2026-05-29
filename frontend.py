import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage

# Import the Phase 8 LangGraph app
from main import app

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide"
)

# ======================================================
# CSS & STYLING (Kept exactly as you designed it!)
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp { font-family: 'Inter', sans-serif; background-color: #080d14; }

/* ── Hero ── */
.hero-wrapper { position: relative; border-radius: 20px; overflow: hidden; margin-bottom: 2rem; height: 280px; }
.hero-bg { width: 100%; height: 100%; object-fit: cover; display: block; filter: brightness(0.35); position: absolute; top: 0; left: 0; }
.hero-content { position: relative; z-index: 2; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 2rem; }
.hero-badge { background: rgba(58,123,213,0.25); border: 1px solid rgba(58,123,213,0.5); color: #7ab8f5 !important; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.3rem 0.9rem; border-radius: 20px; margin-bottom: 0.9rem; display: inline-block; }
.hero-title { font-size: 2.6rem; font-weight: 700; color: #ffffff; margin: 0 0 0.6rem; line-height: 1.2; }
.hero-sub { color: #94adc8; font-size: 1rem; max-width: 560px; }

/* ── Input card ── */
.input-card { background: #0e1623; border: 1px solid #1e2e44; border-radius: 16px; padding: 1.6rem 1.8rem; margin-bottom: 1.5rem; }
.input-label { color: #7ab8f5; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem; }

/* ── Quick destinations ── */
.dest-row { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.8rem 0 1.2rem; }
.dest-chip { background: #111b2b; border: 1px solid #1e3050; color: #f7fdf4; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.82rem; cursor: pointer; transition: all 0.2s; }
.dest-chip:hover { background: #1a2e47; border-color: #3a7bd5; color: #fff; }

/* ── Generate button ── */
div[data-testid="stButton"] > button { background: linear-gradient(135deg, #1a6bbf 0%, #0d4a8a 50%, #0a3d75 100%) !important; color: #ffffff !important; border: none !important; border-radius: 12px !important; padding: 0.85rem 2.5rem !important; font-size: 1.05rem !important; font-weight: 700 !important; letter-spacing: 0.03em !important; width: 100% !important; box-shadow: 0 0 24px rgba(26,107,191,0.35), 0 4px 15px rgba(0,0,0,0.4) !important; transition: all 0.3s ease !important; }
div[data-testid="stButton"] > button:hover { box-shadow: 0 0 40px rgba(26,107,191,0.6), 0 6px 20px rgba(0,0,0,0.5) !important; transform: translateY(-2px) !important; background: linear-gradient(135deg, #2278d4 0%, #1057a0 50%, #0d4a8a 100%) !important; }
div[data-testid="stButton"] > button:active { transform: translateY(0px) !important; }

/* ── Agent status cards ── */
[data-testid="stStatusWidget"] { background: #0e1a2e !important; border: 1px solid #1e3050 !important; border-radius: 12px !important; }
[data-testid="stStatusWidget"] > div:first-child { background: #0e1a2e !important; border-radius: 12px 12px 0 0 !important; }
[data-testid="stStatusWidget"] details, [data-testid="stStatusWidget"] details > div, [data-testid="stStatusWidget"] [data-testid="stVerticalBlock"] { background: #0a1520 !important; color: #ffffff !important; padding: 0.25rem 0.5rem !important; }
[data-testid="stStatusWidget"] * { color: #ffffff !important; }
[data-testid="stStatusWidget"] a { color: #4ea8f0 !important; }
[data-testid="stStatusWidget"] hr { border-color: #1e3050 !important; }

/* ── Section headers ── */
.sec-head { display: flex; align-items: center; gap: 0.6rem; margin: 2rem 0 0.75rem; padding-bottom: 0.5rem; border-bottom: 1px solid #1e2e44; }
.sec-head span { font-size: 1.15rem; font-weight: 600; color: #e0edf8; }

/* ── Metric bar ── */
.metric-row { display: flex; gap: 1rem; margin: 1.5rem 0; }
.metric-box { flex: 1; background: #0e1623; border: 1px solid #1e2e44; border-radius: 12px; padding: 1rem 1.2rem; text-align: center; }
.metric-val { font-size: 1.8rem; font-weight: 700; color: #4ea8f0; }
.metric-lbl { font-size: 0.78rem; color: #7aa8cc !important; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* ── Final plan ── */
.final-card { background: linear-gradient(160deg, #0c1a2e 0%, #0a1520 100%); border: 1px solid #1e3a5c; border-left: 4px solid #3a7bd5; border-radius: 14px; padding: 1.8rem; line-height: 1.8; color: #cce0f5; font-size: 0.95rem; }

/* ── Save bar ── */
.save-bar { background: #0e1623; border: 1px solid #1e2e44; border-radius: 10px; padding: 0.85rem 1.2rem; color: #8ab8d8 !important; font-size: 0.88rem; margin-top: 0.5rem; }
.save-bar code { color: #7ab8f5 !important; background: #0a1520 !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] { background: #090e18 !important; border-right: 1px solid #141f30 !important; }
.sidebar-chip { background: #0e1a2b; border: 1px solid #1a2e44; border-radius: 8px; padding: 0.45rem 0.75rem; margin-bottom: 0.4rem; font-size: 0.83rem; color: #7aa8cc; }
.sidebar-title { color: #e0edf8; font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem; }
#MainMenu, footer, header { visibility: hidden; }

/* Form overrides */
.stTextArea textarea { background: #0a1520 !important; border: 1px solid #1e2e44 !important; border-radius: 10px !important; color: #e8f4ff !important; font-size: 0.95rem !important; resize: none !important; }
.stTextArea textarea:focus { border-color: #3a7bd5 !important; box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important; }
.stTextArea textarea::placeholder { color: #4a6a85 !important; }
input[type="text"], .stTextInput input { background: #0e1a2b !important; border: 1px solid #1a2e44 !important; border-radius: 8px !important; color: #e0edf8 !important; }
input[type="text"]:focus, .stTextInput input:focus { border-color: #3a7bd5 !important; box-shadow: 0 0 0 2px rgba(58,123,213,0.2) !important; }
.stTextInput label, .stTextArea label { color: #7ab8f5 !important; font-size: 0.82rem !important; font-weight: 600 !important; letter-spacing: 0.08em !important; }
.stMarkdown p, .stMarkdown li { color: #cce0f5 !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #e8f4ff !important; }
.stAlert { background: #0e1a2b !important; border-radius: 10px !important; }
.stAlert p, .stAlert div { color: #e0edf8 !important; }
div[data-testid="stDownloadButton"] > button { background: #1a3a5c !important; color: #e8f4ff !important; border: 1px solid #2a5080 !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🌍 AI Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")
    thread_id = st.text_input("👤 User ID", value="aarohi_user", help="Your session ID — keeps travel history across queries")

    st.markdown("<div class='sidebar-title'>Powered by</div>", unsafe_allow_html=True)
    for tech in ["🔗 LangGraph", "🧠 Groq · LLaMA 3.1 8B", "🐘 PostgreSQL", "💾 ChromaDB", "🔍 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

    # UPDATED: The new ReAct pipeline nodes!
    st.markdown("<div class='sidebar-title'>Agent Pipeline</div>", unsafe_allow_html=True)
    for step in ["① Planner Agent (Brain)", "② Tool Execution (Hands)", "③ Memory Summarizer", "④ Human Approval"]:
        st.markdown(f"<div class='sidebar-chip'>{step}</div>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg" src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80" alt="airplane above clouds"/>
    <div class="hero-content">
        <div class="hero-badge">✦ Autonomous ReAct Agent</div>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">An enterprise-grade AI that actively researches flights, hotels, and awaits your approval before finalizing the perfect trip.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Destination image strip ───────────────────────────────────────────────────
DESTINATIONS = [
    ("🇯🇵 Tokyo",     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("🇫🇷 Paris",     "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("🇹🇭 Bangkok",   "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("🇮🇹 Rome",      "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("🇦🇪 Dubai",     "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

cols = st.columns(5)
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div style="border-radius:10px;overflow:hidden;position:relative;height:90px;cursor:pointer;">
            <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;filter:brightness(0.55);" />
            <div style="position:absolute;bottom:8px;left:0;right:0;text-align:center;
                        color:#fff;font-size:0.8rem;font-weight:600;">{name}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ======================================================
# BACKEND INTEGRATION & STATE MANAGEMENT
# ======================================================
config = {"configurable": {"thread_id": thread_id}}
current_state = app.get_state(config)
is_paused = current_state.next and current_state.next[0] == "human_approval"

# ── NEW: Human-in-the-Loop Review Screen ──────────────────────────────────────
if is_paused:
    st.markdown("<div class='sec-head'><span>⏸️ Review Draft Itinerary</span></div>", unsafe_allow_html=True)
    st.warning("The Autonomous Agent has researched your trip and drafted a plan. It is waiting for your approval to finalize.")
    
    # Extract the AI's drafted response
    draft = current_state.values["messages"][-1].content
    st.markdown(f"<div class='final-card'>{draft}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve Itinerary", use_container_width=True):
            app.update_state(config, {"messages": [HumanMessage(content="APPROVED")]}, as_node="human_approval")
            for _ in app.stream(None, config=config): pass # Finish execution
            st.rerun()
            
    with col2:
        feedback = st.text_input("Or request changes:", placeholder="e.g. Find a cheaper hotel...")
        if st.button("🔄 Rethink Itinerary", use_container_width=True) and feedback:
            app.update_state(config, {"messages": [HumanMessage(content=f"Human requested changes: {feedback}")]}, as_node="human_approval")
            with st.spinner("Agent is rethinking the plan based on your feedback..."):
                for _ in app.stream(None, config=config): pass # Rerun planner
            st.rerun()

# ── Default Input Screen (When Not Paused) ────────────────────────────────────
else:
    st.markdown("<div class='input-label'>🗺️ Describe your trip</div>", unsafe_allow_html=True)

    QUICK = ["7-day Japan under ₹2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
    qcols = st.columns(len(QUICK))
    quick_fill = ""
    for qc, label in zip(qcols, QUICK):
        if qc.button(label, key=f"q_{label}"):
            quick_fill = label

    user_query = st.text_area(
        "",
        value=quick_fill,
        placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
        height=100,
        label_visibility="collapsed",
    )

    generate = st.button("🚀  Research & Plan My Trip", use_container_width=True)

    # UPDATED AGENT META FOR THE NEW ARCHITECTURE
    AGENT_META = {
        "planner_agent": ("🧠", "Planner Agent"),
        "tools": ("🔧", "Web & API Tools"),
        "summarize_conversation": ("🗜️", "Memory Summarizer"),
    }

    if generate:
        if not user_query.strip():
            st.warning("Please describe your trip first.")
        else:
            st.markdown("---")
            st.markdown("<div class='sec-head'><span>🤖 Agent Execution Logs</span></div>", unsafe_allow_html=True)

            for chunk in app.stream(
                {
                    "messages": [HumanMessage(content=user_query)],
                    "user_query": user_query,
                    "llm_calls": 0,
                    "summary": ""
                },
                config=config,
                stream_mode="updates",
            ):
                for node_name, state_update in chunk.items():
                    
                    # 🔴 ADD THIS SAFETY CHECK 🔴
                    # Ignore the interrupt tuple and any non-dictionary updates
                    if node_name == "__interrupt__" or not isinstance(state_update, dict):
                        continue

                    icon, label = AGENT_META.get(node_name, ("⚡", node_name))

                    with st.status(f"{icon}  {label} completed.", state="complete"):
                        # We pull the latest messages dynamically since there are no hardcoded variables anymore
                        msgs = state_update.get("messages", [])
                        if msgs:
                            latest = msgs[-1].content
                            st.markdown(latest if latest else "_Action completed silently._")
                            
            # Check if paused after running and reload UI
            st.rerun()

# ── Final Output & File Saving ────────────────────────────────────────────────
# Only show the final output if we aren't paused and there is actual data
if not is_paused and current_state.values.get("messages") and len(current_state.values["messages"]) > 1:
    
    msgs = current_state.values["messages"]
    # If the last message was our manual "APPROVED" signal, the actual itinerary is the second to last message
    if msgs[-1].content == "APPROVED":
        final_response = msgs[-2].content
    else:
        final_response = msgs[-1].content
        
    llm_calls = current_state.values.get("llm_calls", 0)

    # Metrics
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box"><div class="metric-val">ReAct</div><div class="metric-lbl">Architecture</div></div>
        <div class="metric-box"><div class="metric-val">{llm_calls}</div><div class="metric-lbl">LLM Calls</div></div>
        <div class="metric-box"><div class="metric-val">✅</div><div class="metric-lbl">Approved</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Final plan card
    st.markdown("<div class='sec-head'><span>✅ Final Approved Travel Plan</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='final-card'>{final_response}</div>", unsafe_allow_html=True)

    # UPDATED: Save functionality (extracts the whole chat log)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"travel_plan_{timestamp}.md"
    save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
    os.makedirs(save_dir, exist_ok=True)

    # Compile the full conversation history for the download file
    chat_log = "\n\n".join([f"**{msg.type.upper()}:**\n{msg.content}" for msg in msgs if msg.content])

    file_content = f"""# Final Travel Plan
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---
## 🧠 Final Itinerary
{final_response}

---
## 📜 Detailed Execution Log
{chat_log}

---
*Total LLM Calls: {llm_calls}*
"""
    with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
        f.write(file_content)

    dl_col, info_col = st.columns([1, 3])
    with dl_col:
        st.download_button("⬇️ Download Plan", data=file_content, file_name=filename, mime="text/markdown", use_container_width=True)
    with info_col:
        st.markdown(f"<div class='save-bar'>📁 Auto-saved → <code>travel_plans/{filename}</code></div>", unsafe_allow_html=True)