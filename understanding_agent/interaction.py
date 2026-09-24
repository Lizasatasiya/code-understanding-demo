import sys

class Interaction:
    def ask(self, context: dict, questions: list) -> list:
        print("\n[INTERACTION] Asking developer...")
        print("\n" + "="*40)
        print("Code Understanding Check\n")
        
        for f in context.get("structured_changes", []):
            print(f"Changed:\n{f['file']}\n")
            print(f"Function:\n{f['function']}()\n")
        
        answers = []
        for i, q in enumerate(questions, 1):
            print(f"Question {i}/{len(questions)}\n")
            print(q)
            print("\nYour answer:")
            
            # Using sys.stdin for simple CLI interaction
            # If not in an interactive terminal, we just skip or provide mock answers
            if sys.stdin.isatty():
                ans = input("> ")
            else:
                ans = "Non-interactive mock answer"
                print("> " + ans)
            
            answers.append({
                "question": q,
                "answer": ans
            })
            print("")
            
        return answers
