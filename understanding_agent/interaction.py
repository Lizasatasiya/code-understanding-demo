import sys
import select
import time
import tty
import termios

class Interaction:
    def _timed_input(self, prompt: str, timeout: int) -> str:
        """Read a line from stdin with a live countdown timer.
        
        Uses a single-threaded non-blocking input loop to handle the timer
        and backspace correctly without threading race conditions.
        """
        if not sys.stdin.isatty():
            ans = "Non-interactive mock answer"
            print(f"{prompt}{ans}")
            return ans

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        start_time = time.time()
        user_input = []
        
        try:
            tty.setcbreak(fd)
            while True:
                remaining = int(timeout - (time.time() - start_time))
                if remaining <= 0:
                    sys.stdout.write(f"\r\033[2K⏰ Time's up! ({timeout}s limit reached)\n")
                    sys.stdout.flush()
                    return None
                    
                # Redraw the line
                timer_str = f"⏱  {remaining:2d}s"
                current_str = "".join(user_input)
                sys.stdout.write(f"\r\033[2K{timer_str} | {prompt}{current_str}")
                sys.stdout.flush()
                
                # Wait for keypress
                ready, _, _ = select.select([sys.stdin], [], [], 0.2)
                if ready:
                    ch = sys.stdin.read(1)
                    if ch in ('\n', '\r'):
                        sys.stdout.write("\n")
                        return "".join(user_input)
                    elif ch in ('\x08', '\x7f'):  # Backspace
                        if user_input:
                            user_input.pop()
                    elif ch == '\x03':  # Ctrl+C
                        raise KeyboardInterrupt()
                    elif ch == '\x04':  # Ctrl+D
                        sys.stdout.write("\n")
                        return "".join(user_input)
                    elif ch == '\x1b':  # Escape sequences (arrow keys)
                        # Consume the rest of the escape sequence so it doesn't print garbage
                        r, _, _ = select.select([sys.stdin], [], [], 0.05)
                        if r:
                            sys.stdin.read(1)
                            r2, _, _ = select.select([sys.stdin], [], [], 0.05)
                            if r2:
                                sys.stdin.read(1)
                    elif ch.isprintable():
                        user_input.append(ch)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

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
        any_timeout = False
        
        for i, q in enumerate(questions, 1):
            question_text = q["question"]
            q_type       = q.get("type", "Reasoning")
            time_limit   = q.get("time_limit", 60)

            print(f"Q{i}: {question_text}")
            ans = self._timed_input("Your answer: ", time_limit)
            
            if ans is None:
                any_timeout = True
                ans = "[No answer — timed out]"

            answers.append({
                "question":   question_text,
                "type":       q_type,
                "time_limit": time_limit,
                "answer":     ans
            })
            print("")
            
        if any_timeout:
            print("⛔ Commit aborted: all questions must be answered within the time limit.")
            print("   Please review your changes and try again.\n")
            sys.exit(1)
            
        print("Thank you! Proceeding with commit...")
        print("\n")
        
        return answers
