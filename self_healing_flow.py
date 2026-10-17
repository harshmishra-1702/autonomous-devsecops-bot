from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router


from secops_crew import build_secops_crew



class SecOpsFlowState(BaseModel):
    target_code: str = ""
    patched_code: str = ""
    verification_status: str = "PENDING"
    retry_count: int = 0
    max_retries: int = 2



class AutonomousSecOpsFlow(Flow[SecOpsFlowState]):

    @start()
    def ingest_code(self):
        print(f"\n[Flow Step 1] Ingesting target code into DevSecOps Pipeline...")
        return self.state.target_code

    @listen(ingest_code)
    def run_crew_pipeline(self, _):
        attempt_num = self.state.retry_count + 1
        print(f"\n[Flow Step 2] Running SecOps Crew (Attempt #{attempt_num})...")

        crew, audit_task, refactor_task, verify_task = build_secops_crew()

        crew.kickoff(inputs={"code_snippet": self.state.target_code})

        self.state.patched_code = refactor_task.output.raw
        self.state.verification_status = verify_task.output.raw

    @router(run_crew_pipeline)
    def evaluate_gatekeeper(self):
        """Router: Decides whether to approve commit or trigger self-healing retry."""
        if "VERIFICATION_PASSED" in self.state.verification_status:
            return "commit_approved"
        elif self.state.retry_count < self.state.max_retries:
            self.state.retry_count += 1
            print(f"\n⚠️ [Self-Healing Router] Verification failed! Retrying with failed patch as new input (Retry {self.state.retry_count})...")
            self.state.target_code = self.state.patched_code
            return "retry_pipeline"
        else:
            return "max_retries_exceeded"

    @listen("retry_pipeline")
    def trigger_retry(self):
        """Listens to the 'retry_pipeline' route and loops back to run the crew again."""
        self.run_crew_pipeline(None)

    @listen("commit_approved")
    def finalize_success(self):
        print("\n" + "=" * 60)
        print("✅ [Flow Complete: COMMIT APPROVED]")
        print("Final Verified Secure Code:")
        print("=" * 60)
        print(self.state.patched_code)

    @listen("max_retries_exceeded")
    def finalize_failure(self):
        print("\n" + "=" * 60)
        print("❌ [Flow Halted: HUMAN REVIEW REQUIRED]")
        print("Pipeline reached max retries without passing gatekeeper verification.")
        print("Last generated code:")
        print(self.state.patched_code)



if __name__ == "__main__":
    vulnerable_sample = '''import sqlite3

STRIPE_API_KEY = "sk_live_99887766"

def get_user(conn, user_input, raw_data):
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    cursor.execute(query)
    parsed = eval(raw_data)
    return cursor.fetchall(), parsed
'''

    flow = AutonomousSecOpsFlow()
    flow.state.target_code = vulnerable_sample
    flow.kickoff()