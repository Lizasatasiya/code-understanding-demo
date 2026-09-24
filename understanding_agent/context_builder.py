import subprocess
class ContextBuilder:
    def build(self, changes: dict, graph) -> dict:
        print("[DEPENDENCY] Finding relevant dependencies...")
        print("[CONTEXT] Building code understanding context...")
        
        changed_code = changes.get("files", [])
        dependencies = []
        
        # Prototype: naive dependency finding
        # Find which file defines the added calls
        for f in changed_code:
            for func in f.get("changed_functions", []):
                calls = func.get("added_calls", [])
                for call in calls:
                    # Let's find definition in app directory using git grep
                    try:
                        grep_out = subprocess.check_output(
                            ["git", "grep", "-n", f"def {call}"],
                            text=True, stderr=subprocess.DEVNULL
                        )
                        if grep_out:
                            file_path = grep_out.split(':')[0]
                            dependencies.append({
                                "function": call,
                                "defined_in": file_path
                            })
                    except subprocess.CalledProcessError:
                        pass
        
        context = {
            "changed_code": changed_code,
            "dependencies": dependencies,
            "tests": [], # Skipping tests for this small prototype
            "documentation": [],
            "graph_relationships": graph.edges
        }
        
        entities = len(changed_code) + len(dependencies)
        print(f"[CONTEXT] Selected {entities} relevant code entities")
        return context
