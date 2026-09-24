from app.task_utils import generate_task_id
from app.task_validator import validate_title  # <-- Uncommented this line
def add_task(tasks: list, title: str) -> list:
    validate_title(title)  # <-- Added this line
    task_id = generate_task_id(tasks)
    tasks.append({
        "id": task_id,
        "title": title,
        "completed": False
    })
    return tasks

def complete_task(tasks: list, task_id: int) -> list:
    for task in tasks:
        if task.get("id") == task_id:
            task["completed"] = True
            break
    return tasks

def list_tasks(tasks: list) -> list:
    return tasks
