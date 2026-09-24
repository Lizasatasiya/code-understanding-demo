import os
import stat
from pathlib import Path

def install_hook():
    repo_root = Path(__file__).parent.parent
    hook_dir = repo_root / ".git" / "hooks"
    
    if not hook_dir.exists():
        print("Error: .git/hooks directory not found. Are you in a git repository?")
        return
        
    hook_path = hook_dir / "pre-commit"
    
    hook_content = """#!/bin/sh
# Code Understanding Demo - pre-commit hook

# Run the understanding agent CLI
# Redirect stdin to /dev/tty so input() works in pre-commit
exec < /dev/tty

echo "[HOOK] Starting Code Understanding..."
python -m understanding_agent.cli

# If the agent exited with an error, prevent commit
if [ $? -ne 0 ]; then
    echo "[HOOK] Understanding check failed. Commit aborted."
    exit 1
fi

exit 0
"""
    
    with open(hook_path, "w") as f:
        f.write(hook_content)
        
    # Make it executable
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)
    
    print(f"Pre-commit hook installed successfully at {hook_path}")

if __name__ == "__main__":
    install_hook()
