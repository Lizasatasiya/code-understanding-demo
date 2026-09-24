import subprocess
import ast
import os
from typing import List, Dict, Any

class ChangeDetector:
    def detect(self) -> Dict[str, Any]:
        print("[CHANGE] Reading staged diff...")
        
        try:
            diff_output = subprocess.check_output(
                ["git", "diff", "--cached", "--name-status"],
                text=True
            ).strip()
        except subprocess.CalledProcessError:
            return {"files": []}
            
        if not diff_output:
            return {"files": []}
            
        files = []
        lines = diff_output.split('\n')
        for line in lines:
            if not line:
                continue
            parts = line.split('\t')
            status = parts[0]
            path = parts[-1]
            
            if not path.endswith('.py') or status == 'D':
                continue
                
            files.append({
                "path": path,
                "status": "modified" if status == 'M' else "added",
                "language": "python",
                "changed_functions": self._analyze_ast_changes(path)
            })
            
        print(f"[CHANGE] Found {len(files)} modified python files")
        return {"files": files}
        
    def _analyze_ast_changes(self, filepath: str) -> List[Dict[str, Any]]:
        # In a real system we would compare AST of HEAD vs Staged
        # For the prototype, we simply parse the staged file and look for function definitions and their calls.
        
        print("[AST] Analyzing changed functions...")
        try:
            staged_content = subprocess.check_output(
                ["git", "show", f":{filepath}"],
                text=True
            )
            tree = ast.parse(staged_content)
            
            changed_functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    calls = [
                        n.func.id for n in ast.walk(node) 
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                    ]
                    changed_functions.append({
                        "name": node.name,
                        "change_type": "modified",
                        "added_calls": calls
                    })
            return changed_functions
        except Exception as e:
            print(f"[AST] Error parsing {filepath}: {e}")
            return []
