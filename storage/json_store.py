"""
Simple JSON file persistence for tasks and sessions.

Zero-dependency storage layer. Reads/writes task trees
to JSON files for lightweight persistence without databases.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from orchestrator.tasks.entity import TaskEntity, TaskEstimate, TaskStatus, TaskPriority
from orchestrator.domain.events import DomainEvent


class JsonStore:
    """
    Simple JSON file-based task store.

    Persists task hierarchies to a JSON file on disk.
    Suitable for single-process, single-file workloads.

    Usage:
        store = JsonStore("/tmp/tasks.json")
        task = TaskEntity(title="Build API")
        store.save(task)
        
        loaded = store.load(task.id)
        assert loaded.title == "Build API"
        
        all_tasks = store.list_all()
    """

    def __init__(self, path: str = "tasks.json"):
        self.path = Path(path)
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy-load from disk."""
        if self._loaded:
            return
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    data = json.load(f)
                self._tasks = data.get("tasks", {})
            except (json.JSONDecodeError, IOError):
                self._tasks = {}
        self._loaded = True

    def _persist(self) -> None:
        """Write to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(
                {
                    "version": "1.0",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "task_count": len(self._tasks),
                    "tasks": self._tasks,
                },
                f,
                indent=2,
                default=str,
            )

    def save(self, task: TaskEntity) -> str:
        """
        Save a task (and all its children) to the store.

        Returns:
            The task ID string.
        """
        self._ensure_loaded()
        self._tasks[str(task.id)] = self._task_to_dict(task)
        self._persist()
        return str(task.id)

    def save_many(self, tasks: List[TaskEntity]) -> List[str]:
        """Save multiple tasks."""
        self._ensure_loaded()
        ids = []
        for task in tasks:
            self._tasks[str(task.id)] = self._task_to_dict(task)
            ids.append(str(task.id))
        self._persist()
        return ids

    def load(self, task_id: str) -> Optional[TaskEntity]:
        """Load a single task by ID."""
        self._ensure_loaded()
        data = self._tasks.get(task_id)
        if not data:
            return None
        return self._dict_to_task(data)

    def list_all(self) -> List[TaskEntity]:
        """Load all tasks."""
        self._ensure_loaded()
        return [self._dict_to_task(d) for d in self._tasks.values()]

    def list_by_status(self, status: str) -> List[TaskEntity]:
        """Filter tasks by status."""
        return [t for t in self.list_all() if t.status == status]

    def delete(self, task_id: Union[str, UUID]) -> bool:
        """Delete a task. Returns True if it existed."""
        self._ensure_loaded()
        task_id_str = str(task_id)
        if task_id_str in self._tasks:
            del self._tasks[task_id_str]
            self._persist()
            return True
        return False

    def clear(self) -> None:
        """Remove all tasks."""
        self._tasks.clear()
        self._persist()

    @property
    def count(self) -> int:
        """Number of stored tasks."""
        self._ensure_loaded()
        return len(self._tasks)

    # --- Serialization helpers ---

    def _task_to_dict(self, task: TaskEntity) -> Dict[str, Any]:
        return {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority.value,
            "estimate": {
                "optimistic_hours": task.estimate.optimistic_hours,
                "likely_hours": task.estimate.likely_hours,
                "pessimistic_hours": task.estimate.pessimistic_hours,
                "confidence": task.estimate.confidence,
            },
            "tags": list(task.tags),
            "metadata": dict(task.metadata),
            "parent_id": str(task.parent_id) if task.parent_id else None,
            "children_ids": [str(c.id) for c in task.children],
            "dependency_ids": [str(d.task_id) for d in task.dependencies],
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "events_count": task._events.count,
        }

    def _dict_to_task(self, data: Dict[str, Any]) -> TaskEntity:
        from uuid import UUID as _UUID
        est = data.get("estimate", {})
        task = TaskEntity(
            title=data["title"],
            description=data.get("description", ""),
            priority=TaskPriority(data.get("priority", "normal")),
            estimate=TaskEstimate(
                optimistic_hours=est.get("optimistic_hours", 0),
                likely_hours=est.get("likely_hours", 0),
                pessimistic_hours=est.get("pessimistic_hours", 0),
                confidence=est.get("confidence", 0.5),
            ),
            parent_id=_UUID(data["parent_id"]) if data.get("parent_id") else None,
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
        # Override auto-generated ID to match stored one
        task.id = _UUID(data["id"])
        # Store serialized IDs for reconstruction reference
        task._stored_children_ids = data.get("children_ids", [])  # type: ignore
        task._stored_dependency_ids = data.get("dependency_ids", [])  # type: ignore
        # Note: status is NOT restored — deserialized tasks start in "pending" state.
        # Use the state machine API (start, complete, fail, etc.) to restore status.
        return task
