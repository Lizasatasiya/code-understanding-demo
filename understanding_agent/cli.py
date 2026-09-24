import sys
from .environment_detector import EnvironmentDetector
from .change_detector import ChangeDetector
from .code_graph import CodeGraph
from .context_builder import ContextBuilder
from .change_summary import ChangeSummary
from .question_generator import QuestionGenerator
from .interaction import Interaction
from .server_client import ServerClient

def main():
    print("\n[HOOK] Code Understanding Check")
    
    # 1. Environment Detection
    env_detector = EnvironmentDetector()
    env = env_detector.detect()
    print(f"[ENV] {env['language'].capitalize()} project detected");
    
    # 2. Change Detection
    change_detector = ChangeDetector()
    changes = change_detector.detect()
    
    if not changes.get("files"):
        print("[HOOK] No supported staged changes found. Proceeding.")
        sys.exit(0)
        
    # 3. Code Graph
    graph = CodeGraph()
    graph.build(changes.get("files"))
    
    # 4. Context Builder
    context_builder = ContextBuilder()
    context = context_builder.build(changes, graph)
    
    # 5. Change Summary
    summary_generator = ChangeSummary()
    summary = summary_generator.generate(context)
    
    # 6. Question Generator
    question_generator = QuestionGenerator()
    questions = question_generator.generate(context, summary)
    
    # 7. Question Validation
    valid_questions = question_generator.validate(questions)
    
    # 8. Developer Interaction
    interaction = Interaction()
    answers = interaction.ask(context, valid_questions)
    
    # 9. Server Client
    client = ServerClient()
    session_data = {
        "repository": env.get("repository", "unknown"),
        "branch": env.get("branch", "unknown"),
        "changed_files": changes.get("files", []),
        "change_summary": summary,
        "questions": answers
    }
    client.send(session_data)
    
    print("[HOOK] Understanding session completed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
