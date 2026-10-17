import ast
import re
from crewai.tools import tool

@tool("inspect_code_structure")
def inspect_code_structure(source_code :str)->str:
    """Parses Python source code into an Abstract Syntax Tree (AST) to list all defined functions and imported modules. Safe for general agent exploration."""
    clean_code = re.sub(r"^```(?:python)?\n|\n```$", "",source_code.strip())
    try:
        tree = ast.parse(clean_code)
        functions = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        ]
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        return f"AST_VALID | Functions: {functions} | Imports: {list(set(imports))}"
    except SyntaxError as e:
        return f"AST_SYNTAX_ERROR: Line {e.lineno}: {e.msg}"



def _scan_source_lines(source_code: str) -> list[str]:
    """Internal helper function so both tools can share the exact same scan logic."""
    clean_code = re.sub(r"^```(?:python)?\n|\n```$", "", source_code.strip())
    findings = []
    for idx, line in enumerate(clean_code.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        if re.search(r"(api_key|secret|password|token)\s*=\s*['\"][^'\"]+['\"]", line, re.I):
            findings.append(
                f"Line {idx} | Rule: SEC-SECRET | Severity: HIGH | Hardcoded credential string detected."
            )
        if re.search(r"(?<!literal_)\b(eval|exec)\s*\(", line):
            findings.append(
                f"Line {idx} | Rule: SEC-EVAL | Severity: HIGH | Dangerous eval() or exec() call."
            )
        if "shell=True" in line:
            findings.append(
                f"Line {idx} | Rule: SEC-CMD | Severity: HIGH | Subprocess invoked with shell=True."
            )
        if re.search(r"SELECT\s+.*(\%|f['\"]|\.format\()", line, re.I) or (
            re.search(r"f['\"]SELECT\s+", line, re.I)
        ):
            findings.append(
                f"Line {idx} | Rule: SEC-SQLI | Severity: HIGH | Unparameterized SQL query string."
            )
    return findings


@tool("run_static_security_scanner")
def run_static_security_scanner(source_code: str) -> str:
    """Scans Python code for security vulnerabilities (hardcoded secrets, eval/exec, 
    shell=True, and SQL injection). Assigned strictly to the Security Audit Task."""
    findings = _scan_source_lines(source_code)
    if not findings:
        return "SCAN_PASSED: 0 vulnerabilities detected."
    return f"SCAN_FAILED ({len(findings)} issues found):\n" + "\n".join(findings)



@tool("verify_patched_code")
def verify_patched_code(patched_code: str) -> str:
    """Verifies that refactored Python code compiles without SyntaxErrors and 
    passes all static security checks. Assigned strictly to the Verification Task."""
    clean_code = re.sub(r"^```(?:python)?\n|\n```$", "", patched_code.strip())

    try:
        ast.parse(clean_code)
    except SyntaxError as e:
        return f"VERIFICATION_FAILED: SyntaxError on line {e.lineno}: {e.msg}"

    remaining_issues = _scan_source_lines(clean_code)
    if remaining_issues:
        return (
            f"VERIFICATION_FAILED: {len(remaining_issues)} security flaw(s) remain:\n"
            + "\n".join(remaining_issues)
        )

    return "VERIFICATION_PASSED: Code compiles cleanly and contains 0 vulnerabilities."



if __name__ == "__main__":
    sample_bad_code = '''
import sqlite3

STRIPE_API_KEY = "sk_live_99887766"

def get_user(conn, user_input, raw_data):
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    parsed = eval(raw_data)
    return cursor.fetchall(), parsed
'''

    print("1. Testing Agent-Level Tool (inspect_code_structure):")
    print(inspect_code_structure.run(sample_bad_code))

    print("\n2. Testing Task-1 Tool (run_static_security_scanner):")
    print(run_static_security_scanner.run(sample_bad_code))

    print("\n3. Testing Task-3 Tool (verify_patched_code on BAD code):")
    print(verify_patched_code.run(sample_bad_code))

