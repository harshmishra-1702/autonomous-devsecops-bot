import streamlit as st
import os
from dotenv import load_dotenv

from self_healing_flow import AutonomousSecOpsFlow

load_dotenv()

st.st_set_page_config = getattr(st, "set_page_config", lambda **kwargs: None)
st.set_page_config(
    page_title="AI DevSecOps Code Review Bot",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Autonomous DevSecOps Code Review & Self-Healing Bot")
st.markdown(
    "Powered by **CrewAI Flows**, **Groq LLMs (`gpt-oss-20b` & `gpt-oss-120b`)**, "
    "and **Deterministic Python AST Tools**."
)

with st.sidebar:
    st.header("Pipeline Architecture")
    st.markdown("- **Agent Tools:** Read-only AST inspector (`inspect_code_structure`)")
    st.markdown("- **Task Tools:** Static security scanner & compiler gatekeeper")
    st.markdown("- **State Machine:** Autonomous self-healing retry loop via CrewAI Flows")
    st.markdown("---")
    api_key_status = "✅ Loaded" if os.getenv("GROQ_API_KEY") else "❌ Missing (.env)"
    st.markdown(f"**Groq API Key Status:** {api_key_status}")

default_sample = '''import sqlite3

STRIPE_API_KEY = "sk_live_99887766"

def get_user(conn, user_input, raw_data):
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    
    parsed = eval(raw_data)
    return cursor.fetchall(), parsed
'''

col1, col2 = st.columns(2)

with col1:
    st.subheader("📥 Vulnerable Input Code")
    user_code_input = st.text_area(
        "Paste Python code to review and refactor:",
        value=default_sample,
        height=320
    )
    run_button = st.button("🚀 Run Security Audit & Refactor", type="primary")

with col2:
    st.subheader("📤 Secure Refactored Output")
    output_container = st.container()

if run_button:
    if not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY not found! Please ensure your .env file is configured.")
    elif not user_code_input.strip():
        st.warning("Please provide a valid Python code snippet.")
    else:
        with st.spinner("🤖 CrewAI Agents & Self-Healing Flow running... Please wait (~5-10s)..."):
            try:
                flow = AutonomousSecOpsFlow()
                flow.state.target_code = user_code_input
                flow.kickoff()

                with col2:
                    st.success(f"Verification Status: {flow.state.verification_status}")
                    st.metric(label="Retry Attempts Used", value=flow.state.retry_count)
                    
                    st.markdown("**Final Secure Code:**")
                    st.code(flow.state.patched_code, language="python")

            except Exception as e:
                with col2:
                    st.error(f"Pipeline Execution Failed: {e}")