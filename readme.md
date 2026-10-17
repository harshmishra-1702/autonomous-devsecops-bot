# Autonomous DevSecOps Code Review & Self-Healing Bot

An event-driven, self-healing code review and refactoring pipeline built using **CrewAI Flows**, **CrewAI Custom Tools**, **Pydantic Data Contracts**, and high-speed **Groq LLM inference**.

This system moves beyond traditional chat-based code reviews by pairing autonomous AI reasoning agents with deterministic Python AST verification and an automated self-healing retry loop.

## Architecture & Design Highlights

* **Agent Tools vs. Task Tools (Least Privilege):** Read-only AST code exploration tools (`inspect_code_structure`) are assigned globally at the Agent level, while strict static security analyzers (`run_static_security_scanner`) and compiler gatekeepers (`verify_patched_code`) are locked exclusively to individual Tasks. This prevents tool-calling drift and hallucinations.

* **Deterministic Validation Loop:** Rewritten code is automatically parsed via Python's native `ast` compiler and re-scanned rule-by-rule before commit approval. If any vulnerability or syntax error remains, the code is rejected.

* **Self-Healing State Machine:** Powered by **CrewAI Flows** (`@router`, `@listen`), the system automatically routes broken or unverified patches back into a self-healing retry loop (with configurable retry limits).

* **Multi-Model Tiering:** Routes fast static-analysis triage to lightweight models and complex code refactoring to high-capacity reasoning models via Groq's high-speed inference engine.

## Tech Stack

* **Orchestration:** CrewAI & CrewAI Flows

* **Validation Contracts:** Pydantic (`BaseModel`)

* **Inference Engine:** Groq API (OpenAI-compatible endpoints)

* **Static Analysis & Compilation:** Python native `ast` and `re` modules

* **User Interface:** Streamlit

## Project File Structure

```
code_review_bot/
│
├── llm_config.py           # Groq multi-model LLM configuration
├── secops_tools.py         # Custom deterministic AST and security scanner tools
├── secops_crew.py          # Agent definitions, task mappings, and Pydantic schemas
├── self_healing_flow.py    # Stateful CrewAI Flow with self-healing retry loop
├── app.py                  # Interactive Streamlit web interface
└── .gitignore              # Ignores venv, .env, and local traces

```

## Setup & Installation

### 1. Clone the Repository & Setup Virtual Environment

```
git clone https://github.com/YOUR_USERNAME/autonomous-devsecops-bot.git
cd autonomous-devsecops-bot
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

### 2. Install Dependencies

```
pip install crewai litellm pydantic python-dotenv streamlit

```

### 3. Configure Environment Variables

Create a `.env` file in the root directory and add your Groq API key:

```
GROQ_API_KEY=gsk_your_actual_groq_api_key_here

```

## Usage

### Run the Interactive Streamlit Web App

To launch the user interface where you can paste vulnerable code and watch the self-healing agentic flow run in real time:

```
streamlit run app.py
