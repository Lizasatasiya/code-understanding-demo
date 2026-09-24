# Code Understanding Demo

This is a proof-of-concept IDE-independent code understanding system that runs on `git commit`.

## How the Code Graph works
The system uses the Python `ast` module to detect function definitions and calls in staged files. A simple in-memory graph is constructed using nodes (files and functions) and edges (contains, defined_in, calls). The `ContextBuilder` uses this graph to find relevant dependencies for the modified code.

## How it remains IDE-independent
The system integrates via a Git `pre-commit` hook. Since Git works exactly the same whether you use VS Code, PyCharm, Neovim, or the terminal, the hook runs reliably regardless of your editor, prompting for understanding before allowing the commit.

## Setup Instructions

1. **Initialize the repository:**
   ```bash
   cd code-understanding-demo
   git init
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the FastAPI Server:**
   Open a new terminal and run:
   ```bash
   cd code-understanding-demo
   source venv/bin/activate
   python -m server.main
   ```

4. **Install the Git Hook:**
   In your main terminal, run:
   ```bash
   python -m scripts.install_hook
   ```
   Add initial files:
   ```bash
   git add .
   git commit -m "Initial commit" --no-verify
   ```

## Make a Demo Change

Modify `app/task_service.py` to add `validate_title`:

```python
from app.task_utils import generate_task_id
from app.task_validator import validate_title

def add_task(tasks: list, title: str) -> list:
    validate_title(title) # <--- ADD THIS
    task_id = generate_task_id(tasks)
    tasks.append({
        "id": task_id,
        "title": title,
        "completed": False
    })
    return tasks
```

Run the commit flow:
```bash
git add app/task_service.py
git commit -m "add task validation"
```

## Example Terminal Output
```
$ git commit -m "add task validation"

[HOOK] Code Understanding Check
[ENV] Python project detected
[CHANGE] Reading staged diff...
[CHANGE] Found 1 modified python files
[AST] Analyzing changed functions...
[GRAPH] Building code relationship graph...
[GRAPH] Found 3 code relationships
[DEPENDENCY] Finding relevant dependencies...
[CONTEXT] Building code understanding context...
[CONTEXT] Selected 2 relevant code entities
[SUMMARY] Generating change summary...
[QUESTIONS] Generating questions...
[QUESTIONS] Generated 3 questions

[INTERACTION] Asking developer...

========================================
Code Understanding Check

Changed:
app/task_service.py

Function:
add_task()

Question 1/3

What behavior did your change introduce?

Your answer:
> Added title validation to the task creation.

...

[SERVER] Sending understanding session...
[SERVER] Session received successfully.
[HOOK] Understanding session completed.
```
