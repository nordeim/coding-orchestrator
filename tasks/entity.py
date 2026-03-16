"""
Task entity — a unit of work with decomposition, dependencies, and progress tracking.

Extracted and simplified from industrial orchestrator's TaskEntity.
No tenant_id, no session_id coupling, no NetworkX dependency.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime, timezone
from dataclasses import dataclass, field

from orchestrator.domain.states import StateMachine, task_state_machine
from orchestrator.domain.events import (
    EventCollector, TaskCreated, TaskStatusChanged,
    TaskCompleted, TaskFailed, TaskDecomposed,
)
from orchestrator.domain.exceptions import TaskDependencyCycleError


class TaskComplexity(str, Enum):
    TRIVIAL = "trivial"      # < 15 min
    SIMPLE = "simple"        # 15-60 min
    MODERATE = "moderate"    # 1-4 hours
    COMPLEX = "complex"      # 4-8 hours
    EXPERT = "expert"        # 8+ hours


class TaskPriority(str, Enum):
    BLOCKER = "blocker"
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# --- Dependency types ---

class DependencyType(str, Enum):
    FINISH_TO_START = "finish_to_start"    # B waits for A to finish
    START_TO_START = "start_to_start"      # B waits for A to start
    FINISH_TO_FINISH = "finish_to_finish"  # B waits for A to finish before B finishes


@dataclass
class TaskDependency:
    """A dependency relationship between tasks."""
    target_task_id: UUID           # The task we depend ON
    dependency_type: DependencyType = DependencyType.FINISH_TO_START
    is_required: bool = True
    description: str = ""


@dataclass
class TaskEstimate:
    """PERT-style time estimate."""
    optimistic_hours: float = 0.0
    likely_hours: float = 0.0
    pessimistic_hours: float = 0.0
    confidence: float = 0.5        # 0.0 to 1.0
    required_capabilities: List[str] = field(default_factory=list)

    @property
    def expected_hours(self) -> float:
        """PERT expected value: (O + 4L + P) / 6"""
        if self.optimistic_hours == 0 and self.likely_hours == 0 and self.pessimistic_hours == 0:
            return 0.0
        return (self.optimistic_hours + 4 * self.likely_hours + self.pessimistic_hours) / 6

    @property
    def standard_deviation(self) -> float:
        """PERT standard deviation: (P - O) / 6"""
        if self.pessimistic_hours <= self.optimistic_hours:
            return 0.0
        return (self.pessimistic_hours - self.optimistic_hours) / 6

    @property
    def complexity(self) -> TaskComplexity:
        hours = self.expected_hours
        if hours < 0.25:
            return TaskComplexity.TRIVIAL
        elif hours < 1.0:
            return TaskComplexity.SIMPLE
        elif hours < 4.0:
            return TaskComplexity.MODERATE
        elif hours < 8.0:
            return TaskComplexity.COMPLEX
        return TaskComplexity.EXPERT


@dataclass
class TaskEntity:
    """
    A unit of work with decomposition, dependencies, and progress tracking.

    Core design:
    - Hierarchical (parent/child decomposition)
    - Dependency-aware (DAG with cycle detection)
    - State-tracked (via StateMachine)
    - Event-emitting (audit trail)
    - Health-monitored (elapsed vs estimate)
    """

    title: str
    description: str = ""
    task_type: str = "implementation"
    priority: TaskPriority = TaskPriority.NORMAL
    estimate: TaskEstimate = field(default_factory=TaskEstimate)

    # Identity
    id: UUID = field(default_factory=uuid4)
    parent_id: Optional[UUID] = None

    # Hierarchy
    children: List["TaskEntity"] = field(default_factory=list)

    # Dependencies
    dependencies: List[TaskDependency] = field(default_factory=list)

    # Execution tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    artifacts: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Internal
    _state: Optional[StateMachine] = field(default=None, repr=False)
    _events: EventCollector = field(default_factory=EventCollector, repr=False)

    def __post_init__(self):
        if self._state is None:
            self._state = task_state_machine(str(self.id))
        if not self.title.strip():
            raise ValueError("Task title cannot be empty")

    # --- State properties ---

    @property
    def status(self) -> str:
        return self._state.current

    @property
    def is_terminal(self) -> bool:
        return self._state.is_terminal

    @property
    def is_leaf(self) -> bool:
        return len(self.children) == 0

    @property
    def is_root(self) -> bool:
        return self.parent_id is None

    @property
    def elapsed_hours(self) -> Optional[float]:
        if self.started_at and not self.completed_at and not self.failed_at:
            return (datetime.now(timezone.utc) - self.started_at).total_seconds() / 3600
        return None

    @property
    def duration_hours(self) -> Optional[float]:
        end = self.completed_at or self.failed_at
        if self.started_at and end:
            return (end - self.started_at).total_seconds() / 3600
        return None

    # --- State transitions ---

    def start(self) -> None:
        """Start task execution."""
        self._state.transition_to("in_progress", reason="started")
        self.started_at = datetime.now(timezone.utc)
        self._events.emit(TaskStatusChanged(
            task_id=self.id, old_status="pending", new_status="in_progress"
        ))

    def complete(self, result: Dict[str, Any] = None) -> None:
        """Mark task as completed."""
        self._state.transition_to("completed", reason="done")
        self.completed_at = datetime.now(timezone.utc)
        self.result = result or {}
        self._events.emit(TaskCompleted(
            task_id=self.id,
            duration_seconds=self.duration_hours * 3600 if self.duration_hours else 0,
        ))

    def fail(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Mark task as failed."""
        self._state.transition_to("failed", reason=str(error))
        self.failed_at = datetime.now(timezone.utc)
        self.error = {
            "type": error.__class__.__name__,
            "message": str(error),
            "context": context or {},
        }
        self._events.emit(TaskFailed(
            task_id=self.id,
            error_type=error.__class__.__name__,
            error_message=str(error),
        ))

    def pause(self) -> None:
        """Pause task execution."""
        self._state.transition_to("paused", reason="paused")

    def resume(self) -> None:
        """Resume paused task."""
        self._state.transition_to("in_progress", reason="resumed")

    def block(self, reason: str = "") -> None:
        """Mark task as blocked."""
        self._state.transition_to("blocked", reason=reason)

    def unblock(self) -> None:
        """Remove blocked status."""
        self._state.transition_to("in_progress", reason="unblocked")

    def cancel(self, reason: str = "") -> None:
        """Cancel task."""
        self._state.transition_to("cancelled", reason=reason)

    def mark_ready(self) -> None:
        """Mark task as ready (dependencies satisfied)."""
        self._state.transition_to("ready", reason="dependencies satisfied")

    # --- Hierarchy ---

    def add_child(self, child: "TaskEntity") -> None:
        """Add a child task (decomposition)."""
        child.parent_id = self.id
        self.children.append(child)
        self._events.emit(TaskDecomposed(
            task_id=self.id,
            subtask_count=len(self.children),
        ))

    def find_child(self, task_id: UUID) -> Optional["TaskEntity"]:
        """Find child task by ID (recursive)."""
        if self.id == task_id:
            return self
        for child in self.children:
            found = child.find_child(task_id)
            if found:
                return found
        return None

    def flatten(self) -> List["TaskEntity"]:
        """Flatten hierarchy into list."""
        tasks = [self]
        for child in self.children:
            tasks.extend(child.flatten())
        return tasks

    def count_descendants(self, status_filter: Optional[str] = None) -> int:
        """Count descendant tasks, optionally filtered by status."""
        count = 0
        for child in self.children:
            if status_filter is None or child.status == status_filter:
                count += 1
            count += child.count_descendants(status_filter)
        return count

    # --- Dependencies ---

    def add_dependency(
        self,
        target_task_id: UUID,
        dep_type: DependencyType = DependencyType.FINISH_TO_START,
        required: bool = True,
        description: str = "",
    ) -> None:
        """Add a dependency on another task."""
        if target_task_id == self.id:
            raise ValueError("Task cannot depend on itself")
        if any(d.target_task_id == target_task_id for d in self.dependencies):
            raise ValueError(f"Dependency on {target_task_id} already exists")
        self.dependencies.append(TaskDependency(
            target_task_id=target_task_id,
            dependency_type=dep_type,
            is_required=required,
            description=description,
        ))

    def get_dependency_ids(self) -> Set[UUID]:
        """Get set of task IDs this task depends on."""
        return {d.target_task_id for d in self.dependencies if d.is_required}

    # --- Dependency DAG (no NetworkX) ---

    def _collect_all_tasks(self) -> Dict[UUID, "TaskEntity"]:
        """Collect all tasks in the hierarchy by ID."""
        tasks = {}
        for t in self.flatten():
            tasks[t.id] = t
        return tasks

    def validate_dag(self) -> bool:
        """Validate that dependency graph has no cycles. Returns True if valid."""
        tasks = self._collect_all_tasks()
        # Build adjacency list: task -> tasks it depends on
        adj = {tid: t.get_dependency_ids() & tasks.keys() for tid, t in tasks.items()}

        # DFS-based cycle detection
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {tid: WHITE for tid in tasks}

        def dfs(node):
            if color[node] == GRAY:
                return False  # cycle found
            if color[node] == BLACK:
                return True
            color[node] = GRAY
            for dep in adj.get(node, set()):
                if not dfs(dep):
                    return False
            color[node] = BLACK
            return True

        return all(dfs(tid) for tid in tasks if color[tid] == WHITE)

    def get_execution_order(self) -> List[UUID]:
        """Topological sort of all tasks based on dependencies."""
        tasks = self._collect_all_tasks()
        adj = {tid: t.get_dependency_ids() & tasks.keys() for tid, t in tasks.items()}

        # Kahn's algorithm
        in_degree = {tid: 0 for tid in tasks}
        for tid, deps in adj.items():
            for dep in deps:
                in_degree[tid] = in_degree.get(tid, 0) + 1

        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)
            # Reduce in-degree of tasks that depend on this node
            for tid, deps in adj.items():
                if node in deps:
                    in_degree[tid] -= 1
                    if in_degree[tid] == 0:
                        queue.append(tid)

        if len(result) != len(tasks):
            raise TaskDependencyCycleError(
                f"Cycle detected: only {len(result)}/{len(tasks)} tasks resolved"
            )
        return result

    def get_critical_path(self) -> List[UUID]:
        """Calculate critical path (longest path by expected hours)."""
        order = self.get_execution_order()
        tasks = self._collect_all_tasks()
        adj = {tid: t.get_dependency_ids() & tasks.keys() for tid, t in tasks.items()}

        # Forward pass: earliest finish times
        earliest = {}
        for tid in order:
            task = tasks[tid]
            deps = adj.get(tid, set())
            if not deps:
                earliest[tid] = task.estimate.expected_hours
            else:
                earliest[tid] = max(earliest.get(d, 0) for d in deps) + task.estimate.expected_hours

        # Critical path = longest path
        # Trace back from the task with max earliest finish time
        if not order:
            return []

        end_task = max(earliest, key=earliest.get)
        path = [end_task]

        # Backtrack through dependencies
        current = end_task
        while adj.get(current, set()):
            deps = adj[current]
            # Find the dependency with the max earliest finish time
            critical_dep = max(deps, key=lambda d: earliest.get(d, 0))
            path.append(critical_dep)
            current = critical_dep

        path.reverse()
        return path

    # --- Progress ---

    def get_progress(self) -> Dict[str, Any]:
        """Get progress summary for entire task tree."""
        all_tasks = self.flatten()
        total = len(all_tasks) - 1  # exclude self
        if total <= 0:
            total = 0

        by_status = {}
        for t in all_tasks[1:]:  # skip self
            s = t.status
            by_status[s] = by_status.get(s, 0) + 1

        completed = by_status.get("completed", 0)
        in_progress = by_status.get("in_progress", 0)
        failed = by_status.get("failed", 0)
        blocked = by_status.get("blocked", 0)

        return {
            "task_id": str(self.id),
            "title": self.title,
            "status": self.status,
            "progress_pct": (completed / total * 100) if total > 0 else 0,
            "total_subtasks": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "blocked": blocked,
            "elapsed_hours": self.elapsed_hours,
            "complexity": self.estimate.complexity.value,
            "priority": self.priority.value,
        }

    # --- Events ---

    def drain_events(self) -> list:
        """Get and clear all events."""
        return self._events.drain()

    def health_score(self) -> float:
        """Calculate health score (0.0 to 1.0)."""
        if self.status == "completed":
            return 1.0
        if self.status == "failed" or self.status == "cancelled":
            return 0.0
        if self.status == "in_progress" and self.started_at:
            elapsed = (datetime.now(timezone.utc) - self.started_at).total_seconds()
            limit = self.estimate.expected_hours * 3600
            if limit <= 0:
                return 0.8
            ratio = elapsed / limit
            if ratio > 0.9:
                return 0.3  # at risk
            elif ratio > 0.7:
                return 0.7  # warning
            return 0.9  # healthy
        return 0.8  # default for pending/ready/etc
