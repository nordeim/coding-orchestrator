"""
Tests for TaskEntity.
"""

import pytest
from uuid import uuid4
from orchestrator.tasks.entity import (
    TaskEntity, TaskEstimate, TaskPriority, TaskComplexity,
    TaskDependency, DependencyType,
)


class TestTaskEstimate:
    """Tests for PERT estimation."""

    def test_expected_hours_pert(self):
        est = TaskEstimate(optimistic_hours=1, likely_hours=3, pessimistic_hours=8)
        # (1 + 4*3 + 8) / 6 = 21/6 = 3.5
        assert est.expected_hours == pytest.approx(3.5)

    def test_standard_deviation(self):
        est = TaskEstimate(optimistic_hours=1, likely_hours=3, pessimistic_hours=8)
        assert est.standard_deviation == pytest.approx(7 / 6)

    def test_zero_estimate(self):
        est = TaskEstimate()
        assert est.expected_hours == 0.0
        assert est.complexity == TaskComplexity.TRIVIAL

    def test_complexity_levels(self):
        assert TaskEstimate(likely_hours=0.1).complexity == TaskComplexity.TRIVIAL
        assert TaskEstimate(likely_hours=0.5).complexity == TaskComplexity.SIMPLE
        assert TaskEstimate(likely_hours=2.0).complexity == TaskComplexity.MODERATE
        assert TaskEstimate(likely_hours=6.0).complexity == TaskComplexity.COMPLEX
        # PERT expected: (8 + 4*10 + 12) / 6 = 60/6 = 10.0 → EXPERT
        assert TaskEstimate(optimistic_hours=8, likely_hours=10, pessimistic_hours=12).complexity == TaskComplexity.EXPERT


class TestTaskEntity:
    """Tests for TaskEntity."""

    def test_create_task(self):
        task = TaskEntity(title="Implement login feature")
        assert task.title == "Implement login feature"
        assert task.status == "pending"
        assert task.is_root
        assert task.is_leaf

    def test_empty_title_raises(self):
        with pytest.raises(ValueError):
            TaskEntity(title="")

    def test_full_lifecycle(self):
        task = TaskEntity(title="Build API endpoint", estimate=TaskEstimate(likely_hours=2))
        assert task.status == "pending"

        task.mark_ready()
        assert task.status == "ready"

        task.start()
        assert task.status == "in_progress"
        assert task.started_at is not None

        task.complete({"files_changed": 3})
        assert task.status == "completed"
        assert task.completed_at is not None
        assert task.result == {"files_changed": 3}
        assert task.is_terminal

    def test_failure(self):
        task = TaskEntity(title="Risky deployment")
        task.start()
        task.fail(RuntimeError("Connection timeout"), {"host": "prod-1"})
        assert task.status == "failed"
        assert task.error["type"] == "RuntimeError"
        assert task.error["context"]["host"] == "prod-1"

    def test_pause_resume(self):
        task = TaskEntity(title="Long compilation")
        task.start()
        task.pause()
        assert task.status == "paused"
        task.resume()
        assert task.status == "in_progress"

    def test_block_unblock(self):
        task = TaskEntity(title="Waiting for API key")
        task.start()
        task.block("Need credentials from DevOps")
        assert task.status == "blocked"
        task.unblock()
        assert task.status == "in_progress"

    def test_cancel(self):
        task = TaskEntity(title="Deprecated feature")
        task.cancel("No longer needed")
        assert task.status == "cancelled"
        assert task.is_terminal


class TestTaskHierarchy:
    """Tests for task decomposition and hierarchy."""

    def test_add_children(self):
        parent = TaskEntity(title="Build auth system")
        child1 = TaskEntity(title="Implement login")
        child2 = TaskEntity(title="Implement logout")

        parent.add_child(child1)
        parent.add_child(child2)

        assert len(parent.children) == 2
        assert child1.parent_id == parent.id
        assert child2.parent_id == parent.id
        assert not parent.is_leaf
        assert child1.is_leaf

    def test_flatten_hierarchy(self):
        root = TaskEntity(title="Build app")
        child1 = TaskEntity(title="Frontend")
        child2 = TaskEntity(title="Backend")
        grandchild = TaskEntity(title="Database schema")

        child2.add_child(grandchild)
        root.add_child(child1)
        root.add_child(child2)

        flat = root.flatten()
        assert len(flat) == 4  # root + 2 children + 1 grandchild

    def test_find_child(self):
        root = TaskEntity(title="Root")
        child = TaskEntity(title="Child")
        root.add_child(child)

        found = root.find_child(child.id)
        assert found is not None
        assert found.title == "Child"

        not_found = root.find_child(uuid4())
        assert not_found is None

    def test_count_descendants(self):
        root = TaskEntity(title="Root")
        c1 = TaskEntity(title="C1")
        c2 = TaskEntity(title="C2")
        c1.start()
        c1.complete()

        root.add_child(c1)
        root.add_child(c2)

        assert root.count_descendants() == 2
        assert root.count_descendants("completed") == 1


class TestTaskDependencies:
    """Tests for dependency management and DAG operations."""

    def test_add_dependency(self):
        task_a = TaskEntity(title="Task A")
        task_b = TaskEntity(title="Task B")

        task_b.add_dependency(task_a.id, DependencyType.FINISH_TO_START)
        assert len(task_b.dependencies) == 1
        assert task_b.dependencies[0].target_task_id == task_a.id

    def test_self_dependency_raises(self):
        task = TaskEntity(title="Task")
        with pytest.raises(ValueError, match="cannot depend on itself"):
            task.add_dependency(task.id)

    def test_duplicate_dependency_raises(self):
        task_a = TaskEntity(title="Task A")
        task_b = TaskEntity(title="Task B")

        task_b.add_dependency(task_a.id)
        with pytest.raises(ValueError, match="already exists"):
            task_b.add_dependency(task_a.id)

    def test_get_dependency_ids(self):
        a = TaskEntity(title="A")
        b = TaskEntity(title="B")
        c = TaskEntity(title="C")

        c.add_dependency(a.id)
        c.add_dependency(b.id)

        assert c.get_dependency_ids() == {a.id, b.id}

    def test_validate_dag_no_cycle(self):
        root = TaskEntity(title="Root")
        a = TaskEntity(title="A")
        b = TaskEntity(title="B")

        root.add_child(a)
        root.add_child(b)
        b.add_dependency(a.id, required=False)  # b depends on a

        assert root.validate_dag()

    def test_execution_order(self):
        root = TaskEntity(title="Root")
        a = TaskEntity(title="A")
        b = TaskEntity(title="B")
        c = TaskEntity(title="C")

        root.add_child(a)
        root.add_child(b)
        root.add_child(c)

        # C depends on B, B depends on A
        b.add_dependency(a.id)
        c.add_dependency(b.id)

        order = root.get_execution_order()
        order_ids = [str(tid) for tid in order]

        # A must come before B, B before C
        assert order_ids.index(str(a.id)) < order_ids.index(str(b.id))
        assert order_ids.index(str(b.id)) < order_ids.index(str(c.id))

    def test_critical_path(self):
        root = TaskEntity(title="Root")
        a = TaskEntity(title="A", estimate=TaskEstimate(likely_hours=1))
        b = TaskEntity(title="B", estimate=TaskEstimate(likely_hours=4))  # longest
        c = TaskEntity(title="C", estimate=TaskEstimate(likely_hours=2))

        root.add_child(a)
        root.add_child(b)
        root.add_child(c)

        c.add_dependency(b.id)
        b.add_dependency(a.id)

        path = root.get_critical_path()
        assert len(path) == 3
        assert path[0] == a.id
        assert path[-1] == c.id


class TestTaskProgress:
    """Tests for progress tracking."""

    def test_progress_empty(self):
        task = TaskEntity(title="Solo task")
        progress = task.get_progress()
        assert progress["total_subtasks"] == 0
        assert progress["progress_pct"] == 0

    def test_progress_with_children(self):
        root = TaskEntity(title="Project")
        t1 = TaskEntity(title="Task 1")
        t2 = TaskEntity(title="Task 2")
        t3 = TaskEntity(title="Task 3")

        root.add_child(t1)
        root.add_child(t2)
        root.add_child(t3)

        t1.start()
        t1.complete()
        t2.start()

        progress = root.get_progress()
        assert progress["total_subtasks"] == 3
        assert progress["completed"] == 1
        assert progress["in_progress"] == 1
        assert progress["progress_pct"] == pytest.approx(33.33, rel=0.01)

    def test_health_score(self):
        task = TaskEntity(
            title="Quick task",
            estimate=TaskEstimate(likely_hours=1),
        )
        assert task.health_score() == 0.8  # default for pending

        task.start()
        assert task.health_score() > 0.5  # healthy initially

        task.complete()
        assert task.health_score() == 1.0

    def test_health_score_failure(self):
        task = TaskEntity(title="Failing task")
        task.start()
        task.fail(RuntimeError("boom"))
        assert task.health_score() == 0.0

    def test_events(self):
        task = TaskEntity(title="Eventful task")
        assert task._events.count == 0  # no events on init
        task.start()
        events = task.drain_events()
        assert any(e.event_type == "TaskStatusChanged" for e in events)
        assert task._events.count == 0  # drained
