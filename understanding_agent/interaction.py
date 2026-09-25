import sys
import select
import time
import threading

class Interaction:
    def _timed_input(self, prompt: str, timeout: int) -> str:
        """Read a line from stdin with a live countdown timer on its own line.
        Falls back to untimed input when stdin is not a TTY.
        """
        if not sys.stdin.isatty():
            ans = "Non-interactive mock answer"
            print(f"Your answer: {ans}")
            return ans

        # Print the timer on a dedicated line, then the input prompt below it.
        # The background thread rewrites only the timer line using ANSI cursor
        # save/restore so the user's typing line is never disturbed.
        sys.stdout.write(f"⏱  {timeout:2d}s remaining\n{prompt}")
        sys.stdout.flush()

        # ── Countdown thread ──────────────────────────────────────────
        stop_event = threading.Event()

        def _countdown():
            remaining = timeout - 1
            while remaining >= 0 and not stop_event.is_set():
                time.sleep(1)
                if stop_event.is_set():
                    break
                # \033[s  save cursor position (on the input line)
                # \033[1A move up one line  (to the timer line)
                # \033[2K erase the entire timer line
                # \r      go to column 0
                # write new timer text
                # \033[u  restore cursor back to input line
                sys.stdout.write(
                    f"\033[s\033[1A\033[2K\r⏱  {remaining:2d}s remaining\033[u"
                )
                sys.stdout.flush()
                remaining -= 1

        timer_thread = threading.Thread(target=_countdown, daemon=True)
        timer_thread.start()

        # ── Wait for input or timeout ─────────────────────────────────
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        stop_event.set()
        timer_thread.join(timeout=1)

        if ready:
            answer = sys.stdin.readline().rstrip("\n")
            # Erase the timer line that sits above
            sys.stdout.write("\033[1A\033[2K\r")
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
