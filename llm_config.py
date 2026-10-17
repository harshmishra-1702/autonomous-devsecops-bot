import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    raise ValueError("GROQ_API_KEY not found in .env file!")


fast_scanner_llm = LLM(
    model="openai/gpt-oss-20b",
    provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_key,
    temperature=0.0
)

reasoning_coder_llm = LLM(
    model="openai/gpt-oss-120b",
    provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_key,
    temperature=0.1
)

if __name__ == "__main__":
    print("Testing Native OpenAI-Compatible Groq connection...")

    response = fast_scanner_llm.call("Reply with the exact word: READY")
    print(f"Fast Scanner Model Response: {response}")

    response_coder = reasoning_coder_llm.call("Reply with the exact word: ONLINE")
    print(f"Reasoning Coder Model Response: {response_coder}")