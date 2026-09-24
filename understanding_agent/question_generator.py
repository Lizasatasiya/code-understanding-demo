class QuestionGenerator:
    def generate(self, context: dict, summary: dict) -> list:
        print("[QUESTIONS] Generating questions...")
        
        # In a real system, we would use an LLM here to generate specific questions based on context
        questions = [
            "What behavior did your change introduce?",
            "Why is validate_title() called before adding the task?",
            "What should happen when the title is invalid?"
        ]
        
        print(f"[QUESTIONS] Generated {len(questions)} questions")
        return questions
        
    def validate(self, questions: list) -> list:
        # Simple validation
        return [q for q in questions if len(q) > 10]
