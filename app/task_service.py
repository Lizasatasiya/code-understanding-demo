from app.task_utils import generate_task_id
# We will add task_validator import during the demo change
# from app.task_validator import validate_title

def add_task(tasks: list, title: str) -> list:
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
