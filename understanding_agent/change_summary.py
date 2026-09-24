class ChangeSummary:
    def generate(self, context: dict) -> dict:
        print("[SUMMARY] Generating change summary...")
        # In a real system, we would use an LLM here
        # For the prototype, we provide a hardcoded summary based on our specific demo
        # Or a rudimentary deterministic summary
        
        return {
            "what_changed": "Added fraud detection to the checkout flow.",
            "why_it_matters": "Suspicious transactions over $1000 or by blacklisted IDs are rejected.",
            "impact": "Checkout will now throw PermissionError for fraudulent transactions."
        }
