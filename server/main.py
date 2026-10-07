import os
import sys

# Auto-resolve understanding-agent-hook directory if not already in python path
hook_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "understanding-agent-hook"))
if os.path.exists(hook_path) and hook_path not in sys.path:
    sys.path.insert(0, hook_path)

import uvicorn
from understanding_agent.server import create_app

# Repository root for code-understanding-demo
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = create_app(repo_root=REPO_ROOT)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
