import sys
import signal

class Interaction:
    def _timed_input(self, prompt: str, timeout: int) -> str:
        """Read a line from stdin with a hard timeout using SIGALRM.

        Uses plain input() so the terminal's line editing (backspace, cursor
        movement, etc.) works correctly. Falls back to untimed input when
        stdin is not a TTY.
        """
        if not sys.stdin.isatty():
            ans = "Non-interactive mock answer"
            print(f"Your answer: {ans}")
            return ans

        def _timeout_handler(signum, frame):
            raise TimeoutError()

        # Show the time budget once — no background thread touches stdout
        sys.stdout.write(f"⏱  You have {timeout}s to answer.\n")
        sys.stdout.flush()

        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)
        try:
            ans = input(prompt)
            return ans
        except TimeoutError:
            print(f"\n⏰ Time's up! ({timeout}s limit reached)")
            return None
        finally:
            signal.alarm(0)                          # cancel any pending alarm
            signal.signal(signal.SIGALRM, old_handler)  # restore previous handler

    def ask(self, context: dict, questions: list) -> list:
        print("\n")
        print("          CODE UNDERSTANDING CHECK")
        print("\n")
        
        # 2. Print Diff and Context
        for f in context.get("structured_changes", []):
            print(f"FILE: {f['file']} | FUNCTION: {f['function']}() ")
            
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
            print("\n")
        
        # 3. Ask Questions
        print(" QUESTIONS \n")
        answers = []
        for i, q in enumerate(questions, 1):
            question_text = q["question"]
            q_type       = q.get("type", "Reasoning")
            time_limit   = q.get("time_limit", 60)

            print(f"Q{i}: {question_text}")
            ans = self._timed_input("Your answer: ", time_limit)
            
            if ans is None:
                print("\n⛔ Commit aborted: all questions must be answered within the time limit.")
                print("   Please review your changes and try again.\n")
                sys.exit(1)

            answers.append({
                "question":   question_text,
                "type":       q_type,
                "time_limit": time_limit,
                "answer":     ans
            })
            print("")
            
       
        print("Thank you! Proceeding with commit...")
        print("\n")
        
        return answers
