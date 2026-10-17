Autonomous Agentic DevSecOps Code Review & Self-Healing BotAn event-driven, multi-agent DevSecOps code review and automated refactoring pipeline built using CrewAI Flows, CrewAI Custom Tools, Pydantic Data Contracts, Groq LLM Inference, and Streamlit.🚀 OverviewStandard Large Language Models often hallucinate security fixes, introduce syntax errors, or fail to catch subtle vulnerabilities when asked to review code. This project solves that problem by combining AI reasoning with deterministic Python tooling inside a closed, self-healing feedback loop.The system ingests vulnerable Python code, audits it using static rules, refactors it securely, and validates the patch using an abstract syntax tree (AST) compiler gatekeeper before approving a commit.🛡️ Architecture & Key HighlightsAgent Tools vs. Task Tools (Principle of Least Privilege):Read-only AST code exploration tools (inspect_code_structure) are assigned globally at the Agent level.Strict security scanners (run_static_security_scanner) and compiler gatekeepers (verify_patched_code) are enforced strictly at the Task level, preventing LLM tool-calling drift and hallucinations.Stateful Self-Healing Loop: Powered by CrewAI Flows (@start, @listen, @router), if a generated patch fails compilation or leaves security flaws behind, the state machine automatically loops back to retry remediation.Structured Pydantic Inter-Task Communication: Eliminates fragile regex parsing by forcing auditors to emit validated SecurityAuditReport Pydantic models.Lightning-Fast Groq Inference: Leverages Groq’s high-speed LPU infrastructure (gpt-oss-20b for fast triage and gpt-oss-120b for complex code refactoring).Interactive Streamlit Web UI: Provides a live user interface to paste code, execute the pipeline, and view audit metrics in real-time.🛠️ Tech StackOrchestration: crewai, crewai-flowData Contracts & Validation: pydanticInference Engine: groq (OpenAI-compatible endpoints)Static Analysis & Compiling: Python Built-in ast & re modulesWeb Frontend: streamlitEnvironment Management: python-dotenv📁 Project Structurecode_review_bot/
│
├── llm_config.py          # Groq model configurations (Fast & Reasoning tiers)
├── secops_tools.py        # Deterministic Python AST & static analysis tools
├── secops_crew.py         # CrewAI Agents, Tasks, and Pydantic schemas
├── self_healing_flow.py   # Stateful CrewAI Flow with retry loop (@router)
├── app.py                 # Streamlit web interface
├── test_secops.py         # Automated test suite
├── .env                   # Environment variables (API keys - gitignored)
├── .gitignore             # Excluded files and directories
└── README.md              # Project documentation
⚙️ Installation & Setup1. Clone the Repositorygit clone https://github.com/YOUR_USERNAME/autonomous-devsecops-bot.git
cd autonomous-devsecops-bot
2. Create and Activate a Virtual Environmentpython -m venv venv
# On Windows (PowerShell):
.\venv\Scripts\Activate
# On macOS/Linux:
source venv/bin/activate
3. Install Dependenciespip install crewai litellm pydantic python-dotenv streamlit
4. Configure Environment VariablesCreate a .env file in the root directory and add your Groq API key:GROQ_API_KEY=gsk_your_actual_groq_api_key_here
🖥️ Running the ApplicationOption A: Launch the Streamlit Web Interfacestreamlit run app.py
Open your browser at http://localhost:8501, paste any vulnerable Python snippet, and click Run Security Audit & Refactor.Option B: Run via CLI & Test Suitepython self_healing_flow.py
python test_secops.py
🔍 Example Vulnerability Detection & ResolutionVulnerable PatternDetected RuleSecure Refactored OutputSTRIPE_API_KEY = "sk_live_..."SEC-SECRETSTRIPE_API_KEY = os.getenv("STRIPE_API_KEY")f"SELECT * FROM users WHERE name = '{input}'"SEC-SQLIcursor.execute("SELECT * FROM users WHERE name = ?", (input,))eval(raw_data)SEC-EVALast.literal_eval(raw_data)
