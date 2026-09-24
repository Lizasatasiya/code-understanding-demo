class ChangeSummary:
    def generate(self, context: dict) -> dict:
        print("[SUMMARY] Generating change summary...")
        # In a real system, we would use an LLM here
        # For the prototype, we provide a hardcoded summary based on our specific demo
        # Or a rudimentary deterministic summary
        
        return {
            "what_changed": "Added title validation before creating a task.",
            "why_it_matters": "Invalid task titles are now rejected.",
            "impact": "Task creation behavior has changed."
        }
