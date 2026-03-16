"""
Tests for JSON storage.
"""

import json
import pytest
import tempfile
import os
from pathlib import Path

from orchestrator.storage.json_store import JsonStore
from orchestrator.tasks.entity import TaskEntity, TaskEstimate, TaskPriority


@pytest.fixture
def tmp_path():
    """Create a temporary file path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def store(tmp_path):
    return JsonStore(tmp_path)


class TestJsonStore:

    def test_save_and_load(self, store):
        task = TaskEntity(title="Build API", description="REST endpoints")
        task_id = store.save(task)

        loaded = store.load(task_id)
        assert loaded is not None
        assert loaded.title == "Build API"
        assert loaded.description == "REST endpoints"

    def test_load_nonexistent(self, store):
        assert store.load("nonexistent-id") is None

    def test_save_with_estimate(self, store):
        task = TaskEntity(
            title="Complex task",
            estimate=TaskEstimate(optimistic_hours=2, likely_hours=5, pessimistic_hours=10, confidence=0.7),
        )
        task_id = store.save(task)
        loaded = store.load(task_id)
        assert loaded is not None
        assert loaded.estimate.likely_hours == 5

    def test_save_with_tags_and_metadata(self, store):
        task = TaskEntity(
            title="Tagged task",
            tags=["backend", "api"],
            metadata={"sprint": "3", "team": "platform"},
        )
        task_id = store.save(task)
        loaded = store.load(task_id)
        assert loaded is not None
        assert "backend" in loaded.tags
        assert loaded.metadata["sprint"] == "3"

    def test_save_many(self, store):
        tasks = [TaskEntity(title=f"Task {i}") for i in range(5)]
        ids = store.save_many(tasks)
        assert len(ids) == 5
        assert store.count == 5

    def test_list_all(self, store):
        store.save(TaskEntity(title="A"))
        store.save(TaskEntity(title="B"))
        store.save(TaskEntity(title="C"))
        all_tasks = store.list_all()
        assert len(all_tasks) == 3

    def test_list_by_status(self, store):
        t1 = TaskEntity(title="Pending task")
        t2 = TaskEntity(title="Started task")
        t2.start()
        store.save(t1)
        store.save(t2)

        # JSON preserves status in the file
        import json
        with open(store.path, "r") as f:
            data = json.load(f)
        statuses = {v["status"] for v in data["tasks"].values()}
        assert "pending" in statuses
        assert "in_progress" in statuses

    def test_delete(self, store):
        task = TaskEntity(title="Delete me")
        task_id = store.save(task)
        assert store.count == 1
        assert store.delete(task_id)
        assert store.count == 0

    def test_delete_nonexistent(self, store):
        assert not store.delete("no-such-id")

    def test_clear(self, store):
        store.save(TaskEntity(title="A"))
        store.save(TaskEntity(title="B"))
        store.clear()
        assert store.count == 0

    def test_count(self, store):
        assert store.count == 0
        store.save(TaskEntity(title="One"))
        assert store.count == 1

    def test_persistence_across_instances(self, tmp_path):
        store1 = JsonStore(tmp_path)
        store1.save(TaskEntity(title="Persistent task"))
        task_id = store1.save(TaskEntity(title="Another task"))

        # New instance reads same file
        store2 = JsonStore(tmp_path)
        assert store2.count == 2
        loaded = store2.load(task_id)
        assert loaded.title == "Another task"

    def test_overwrite_on_save(self, store):
        task = TaskEntity(title="Original title")
        task_id = store.save(task)

        task.title = "Updated title"
        store.save(task)

        loaded = store.load(task_id)
        assert loaded.title == "Updated title"

    def test_json_file_structure(self, tmp_path):
        store = JsonStore(tmp_path)
        store.save(TaskEntity(title="Test task"))

        with open(tmp_path, "r") as f:
            data = json.load(f)

        assert "version" in data
        assert "updated_at" in data
        assert "tasks" in data
        assert "task_count" in data
        assert data["task_count"] == 1

    def test_corrupt_file_handled(self, tmp_path):
        with open(tmp_path, "w") as f:
            f.write("NOT VALID JSON{{{")
        store = JsonStore(tmp_path)
        assert store.count == 0
        assert store.list_all() == []

    def test_parent_child_ids_stored(self, store):
        parent = TaskEntity(title="Parent")
        child = TaskEntity(title="Child")
        parent.add_child(child)
        store.save(parent)

        # Verify child relationship is persisted in JSON
        import json
        with open(store.path, "r") as f:
            data = json.load(f)
        parent_data = data["tasks"][str(parent.id)]
        assert str(child.id) in parent_data["children_ids"]