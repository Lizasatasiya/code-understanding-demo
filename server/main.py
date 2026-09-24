from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

class QuestionAnswer(BaseModel):
    question: str
    answer: str

class UnderstandingSession(BaseModel):
    repository: str
    branch: str
    changed_files: List[Dict[str, Any]]
    change_summary: Dict[str, str]
    questions: List[QuestionAnswer]

@app.post("/understanding-session")
def receive_session(session: UnderstandingSession):
    print("\n" + "="*50)
    print("NEW UNDERSTANDING SESSION RECEIVED")
    print("="*50)
    print(f"Repository: {session.repository}")
    print(f"Branch: {session.branch}")
    print(f"Changed Files: {len(session.changed_files)}")
    print(f"Change Summary:\n  What changed: {session.change_summary.get('what_changed')}")
    print("Questions and Answers:")
    for i, qa in enumerate(session.questions, 1):
        print(f"\nQ{i}: {qa.question}")
        print(f"A{i}: {qa.answer}")
    print("="*50 + "\n")
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
