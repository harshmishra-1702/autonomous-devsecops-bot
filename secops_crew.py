from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process


from llm_config import fast_scanner_llm, reasoning_coder_llm
from secops_tools import (
    inspect_code_structure,
    run_static_security_scanner,
    verify_patched_code,
)


class VulnerabilityItem(BaseModel):
    line_number: int = Field(description="Line number where the issue was found")
    rule_id: str = Field(description="Rule ID such as SEC-SECRET, SEC-SQLI, SEC-EVAL, SEC-CMD")
    severity: str = Field(description="Severity level, e.g., HIGH")
    description: str = Field(description="Description of the security issue")


class SecurityAuditReport(BaseModel):
    total_issues: int = Field(description="Total count of vulnerabilities detected")
    is_secure: bool = Field(description="True if 0 issues found, False otherwise")
    vulnerabilities: List[VulnerabilityItem] = Field(description="List of detected vulnerabilities")



def build_secops_crew():
    auditor_agent = Agent(
        role="Lead Application Security Auditor",
        goal="Run static security scans on Python code and output an exact structured vulnerability report.",
        backstory=(
            "You are a deterministic security auditor. You never guess vulnerabilities. "
            "You always execute your assigned task scanner tool on the exact code snippet "
            "and convert its findings into the required structured report."
        ),
        tools=[inspect_code_structure],  
        llm=fast_scanner_llm,
        verbose=True,
        allow_delegation=False,
    )

    remediation_agent = Agent(
        role="Principal Secure Code Refactoring Engineer",
        goal="Refactor vulnerable Python code to eliminate all security flaws while keeping original functionality intact.",
        backstory=(
            "You are a senior Python security engineer. You fix hardcoded secrets using "
            "os.getenv(), fix SQL injection using parameterized '?' tuples, and replace "
            "eval() with ast.literal_eval()."
        ),
        tools=[inspect_code_structure],  
        llm=reasoning_coder_llm,
        verbose=True,
        allow_delegation=False,
    )

   
    audit_task = Task(
        description=(
            "Scan the following Python code for security vulnerabilities using the "
            "`run_static_security_scanner` tool:\n\n"
            "{code_snippet}\n\n"
            "Pass the raw code directly to the tool and populate the SecurityAuditReport."
        ),
        expected_output="A structured SecurityAuditReport matching the exact findings of the scanner tool.",
        agent=auditor_agent,
        tools=[run_static_security_scanner], 
        output_pydantic=SecurityAuditReport,
    )

    
    refactor_task = Task(
        description=(
            "Review the original vulnerable code:\n\n"
            "{code_snippet}\n\n"
            "And review the structured vulnerability report from the previous task. "
            "First, use your `inspect_code_structure` tool to inspect the code's AST. "
            "Then rewrite the Python code to fix every single reported vulnerability:\n"
            "1. Replace hardcoded secrets with `os.getenv('VAR_NAME')` (and add `import os`).\n"
            "2. Replace formatted SQL strings with parameterized queries using `?` placeholders, "
            "e.g., `cursor.execute('SELECT * FROM users WHERE name = ?', (user_input,))`.\n"
            "3. Replace `eval(...)` with `ast.literal_eval(...)` (and add `import ast`).\n"
            "Output ONLY the raw, valid refactored Python code without markdown code fences."
        ),
        expected_output="Raw, valid refactored Python code with all vulnerabilities fixed and no markdown fences.",
        agent=remediation_agent,
        context=[audit_task],
    )

    verify_task = Task(
        description=(
            "Take the refactored Python code from the previous task and pass it into the "
            "`verify_patched_code` tool to confirm it compiles and has 0 remaining vulnerabilities. "
            "Return the exact verification status string from the tool."
        ),
        expected_output="The exact string returned by verify_patched_code (starting with VERIFICATION_PASSED or VERIFICATION_FAILED).",
        agent=remediation_agent,
        tools=[verify_patched_code], 
        context=[refactor_task],
    )

    crew = Crew(
        agents=[auditor_agent, remediation_agent],
        tasks=[audit_task, refactor_task, verify_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew, audit_task, refactor_task, verify_task



if __name__ == "__main__":
    sample_vulnerable_code = '''import sqlite3

STRIPE_API_KEY = "sk_live_99887766"

def get_user(conn, user_input, raw_data):
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    parsed = eval(raw_data)
    return cursor.fetchall(), parsed
'''

    crew, audit_task, refactor_task, verify_task = build_secops_crew()
    crew.kickoff(inputs={"code_snippet": sample_vulnerable_code})

    print("\n" + "=" * 60)
    print("1. PYDANTIC AUDIT REPORT (From Task 1):")
    print(audit_task.output.pydantic.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("2. REFACTORED SECURE CODE (From Task 2):")
    print(refactor_task.output.raw)

    print("\n" + "=" * 60)
    print("3. GATEKEEPER VERIFICATION (From Task 3):")
    print(verify_task.output.raw)