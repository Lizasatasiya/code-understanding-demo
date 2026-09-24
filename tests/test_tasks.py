import pytest
from app.task_service import add_task, complete_task
from app.task_validator import validate_title

def test_add_task():
    tasks = []
    add_task(tasks, "Buy milk")
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Buy milk"

def test_complete_task():
    tasks = [{"id": 1, "title": "Buy milk", "completed": False}]
    complete_task(tasks, 1)
    assert tasks[0]["completed"] is True
