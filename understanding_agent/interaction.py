import sys

class Interaction:
    def ask(self, context: dict, questions: list) -> list:
        print("\n" + "="*50)
        print("          CODE UNDERSTANDING CHECK")
        print("="*50 + "\n")
        
        # 2. Print Diff and Context
        for f in context.get("structured_changes", []):
            print(f"--- FILE: {f['file']} | FUNCTION: {f['function']}() ---")
            
            # Print Summary for this change
            summary = f.get('summary', {})
            print("\n[SUMMARY]")
            print(f"What Changed: {summary.get('what_changed', 'N/A')}")
            print(f"Impact: {summary.get('impact', 'N/A')}")
            print(f"Why it matters: {summary.get('why_it_matters', 'N/A')}")
            
            print("\n[DIFF]")
            diff_lines = f['diff'].split('\n')
            # Truncate diff if it's too long to avoid spamming the terminal
            if len(diff_lines) > 20:
                print("\n".join(diff_lines[:20]))
                print("... (diff truncated)")
            else:
                print(f['diff'])
                
            print("\n[CONTEXT / DEPENDENCIES]")
            print(f['dependency_summary'])
            print("-" * 50 + "\n")
        
        # 3. Ask Questions
        print("--- QUESTIONS ---\n")
        answers = []
        for i, q in enumerate(questions, 1):
            print(f"Q{i}: {q}")
            
            # Using sys.stdin for simple CLI interaction
            if sys.stdin.isatty():
                ans = input("Your answer: ")
            else:
                ans = "Non-interactive mock answer"
                print(f"Your answer: {ans}")
            
            answers.append({
                "question": q,
                "answer": ans
            })
            print("")
            
        print("="*50)
        print("Thank you! Proceeding with commit...")
        print("="*50 + "\n")
        
        return answers
