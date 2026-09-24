def generate_task_id(tasks: list) -> int:
    if not tasks:
        return 1
    return max(t.get("id", 0) for t in tasks) + 1
