import sys
import select
import time
import threading

class Interaction:
    def _timed_input(self, prompt: str, timeout: int) -> str:
        """Read a line from stdin with a live countdown timer.
        Falls back to untimed input when stdin is not a TTY.
        """
        if not sys.stdin.isatty():
            ans = "Non-interactive mock answer"
            print(f"Your answer: {ans}")
            return ans

        # ── Countdown thread ──────────────────────────────────────────
        stop_event = threading.Event()

        def _countdown():
            remaining = timeout
            while remaining > 0 and not stop_event.is_set():
                # Overwrite the timer portion after the prompt on the same line
                sys.stdout.write(f"\r{prompt}  ⏱ {remaining:2d}s remaining  \r{prompt}")
                sys.stdout.flush()
                time.sleep(1)
                remaining -= 1

        timer_thread = threading.Thread(target=_countdown, daemon=True)
        timer_thread.start()

        # ── Wait for input or timeout ─────────────────────────────────
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        stop_event.set()
        timer_thread.join(timeout=1)

        if ready:
            answer = sys.stdin.readline().rstrip("\n")
            # Clear the timer artifact from the line
            sys.stdout.write("\r" + " " * 60 + "\r")
            sys.stdout.flush()
            return answer
        else:
            sys.stdout.write(f"\n⏰ Time's up! ({timeout}s limit reached)\n")
            sys.stdout.flush()
            return "[No answer — timed out]"

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
