import os
import subprocess
from pathlib import Path

class EnvironmentDetector:
    def detect(self) -> dict:
        print("[ENV] Detecting environment...")
        
        try:
            repo_root = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], 
                text=True
            ).strip()
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
                text=True
            ).strip()
        except subprocess.CalledProcessError:
            repo_root = str(Path.cwd())
            branch = "unknown"
            
        return {
            "language": "python",
            "repository": os.path.basename(repo_root),
            "branch": branch,
            "project_root": repo_root,
            "framework": "unknown"
        }
