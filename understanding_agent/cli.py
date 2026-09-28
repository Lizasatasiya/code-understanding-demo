import sys
import time
from .environment_detector import EnvironmentDetector
from .change_detector import ChangeDetector
from .code_graph import CodeGraph
from .context_builder import ContextBuilder
from .change_summary import ChangeSummary
from .question_generator import QuestionGenerator
from .interaction import Interaction
from .server_client import ServerClient
from .answer_evaluator import AnswerEvaluator
from .followup_generator import FollowUpGenerator

def main():
    print("\n[HOOK] Code Understanding Check")
    
    # 1. Environment Detection
    env_detector = EnvironmentDetector()
    env = env_detector.detect()
    
    # 2. Change Detection
    change_detector = ChangeDetector()
    changes = change_detector.detect()
    
    if not changes.get("files"):
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
    print("\n[QUESTIONS] Generating questions...")
    question_generator = QuestionGenerator()
    questions = question_generator.generate(context, summary)
    
    # 7. Question Validation
    valid_questions = question_generator.validate(questions)
    
    # 8. Developer Interaction & Evaluation
    print("\n[INTERACTION] Asking developer...")
    interaction = Interaction()
    evaluator = AnswerEvaluator()
    followup_gen = FollowUpGenerator()
    
    interaction.print_context(context)
    
    final_results = []
    
    for i, q in enumerate(valid_questions, 1):
        q_id = q.get("question_id", f"q{i}")
        q_text = q.get("question", "")
        q_type = q.get("type", "Reasoning")
        time_limit = q.get("time_limit", 60)
        
        print(f"\nQuestion {i}/{len(valid_questions)}")
        print(f"Time: {time_limit} seconds\n")
        print(f"{q_text}\n")
        
        start_time = time.time()
        ans_text = interaction.timed_input("> ", time_limit)
        
        if ans_text is None:
            ans_text = ""
            status = "timeout"
            response_time = time_limit
            print("\n[ANSWER] Timeout reached")
        else:
            status = "answered"
            response_time = int(time.time() - start_time)
            print(f"\n[ANSWER] Received in {response_time} seconds")
            
        print("\n[EVALUATION] Evaluating answer...")
        
        ans_obj = {
            "answer": ans_text,
            "response_time_seconds": response_time,
            "status": status
        }
        
        eval_res = evaluator.evaluate(q, ans_obj, context, summary)
        print(f"[EVALUATION] Score: {eval_res.score}/100")
        
        follow_up_data = None
        final_score = eval_res.score
        
        if eval_res.follow_up_required:
            print("[EVALUATION] Answer requires clarification")
            print("\n[FOLLOW-UP] Asking targeted follow-up...\n")
            follow_up_q = followup_gen.generate(q, ans_obj, eval_res.to_dict())
            print(f"{follow_up_q}\n")
            
            f_start = time.time()
            f_ans = interaction.timed_input("> ", time_limit)
            
            f_status = "answered" if f_ans is not None else "timeout"
            f_resp_time = int(time.time() - f_start) if f_ans is not None else time_limit
            f_ans_text = f_ans or ""
            
            print("\n[FOLLOW-UP EVALUATION] Evaluating...")
            f_ans_obj = {
                "answer": f_ans_text,
                "response_time_seconds": f_resp_time,
                "status": f_status
            }
            
            # evaluate follow up by combining context or treating it as new answer
            f_eval_res = evaluator.evaluate(
                {"question": follow_up_q, "expected_concepts": eval_res.missing_concepts, "evaluation_criteria": q.get("evaluation_criteria", [])},
                f_ans_obj,
                context,
                summary
            )
            
            # combine scores
            final_score = min(100, int(eval_res.score * 0.5 + f_eval_res.score * 0.5))
            if f_eval_res.score > 70:
                print("[FOLLOW-UP EVALUATION] Understanding demonstrated")
            else:
                print("[FOLLOW-UP EVALUATION] Understanding still missing")
                
            follow_up_data = {
                "question": follow_up_q,
                "answer": f_ans_text,
                "score": f_eval_res.score
            }
            
        print(f"\n[FINAL] Question Score: {final_score}/100")
        
        result_entry = {
            "question_id": q_id,
            "question": q_text,
            "type": q_type,
            "time_limit_seconds": time_limit,
            "answer": ans_text,
            "response_time_seconds": response_time,
            "status": status,
            "evaluation": eval_res.to_dict()
        }
        if follow_up_data:
            result_entry["follow_up"] = follow_up_data
            
        final_results.append(result_entry)

    # 9. Server Client
    client = ServerClient()
    session_data = {
        "repository": env.get("repository", "unknown"),
        "branch": env.get("branch", "unknown"),
        "changed_files": changes.get("files", []),
        "change_summary": summary,
        "questions": final_results
    }
    client.send(session_data)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
