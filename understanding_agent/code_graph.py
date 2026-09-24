class CodeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        
    def build(self, changed_files: list):
        print("[GRAPH] Building code relationship graph...")
        # Very simple in-memory graph prototype
        relationships = 0
        for f in changed_files:
            file_node = f"file:{f['path']}"
            self.nodes[file_node] = {"type": "file", "name": f['path']}
            
            for func in f.get('changed_functions', []):
                func_node = f"func:{func['name']}"
                self.nodes[func_node] = {"type": "function", "name": func['name']}
                
                self.edges.append({"source": file_node, "target": func_node, "relation": "contains"})
                self.edges.append({"source": func_node, "target": file_node, "relation": "defined_in"})
                relationships += 2
                
                for call in func.get('added_calls', []):
                    call_node = f"func:{call}"
                    if call_node not in self.nodes:
                        self.nodes[call_node] = {"type": "function", "name": call}
                    self.edges.append({"source": func_node, "target": call_node, "relation": "calls"})
                    relationships += 1
                    
        print(f"[GRAPH] Found {relationships} code relationships")
        
    def get_related_functions(self, func_name: str):
        related = []
        for edge in self.edges:
            if edge["source"] == f"func:{func_name}" and edge["relation"] == "calls":
                related.append(edge["target"].split(":", 1)[1])
        return related
