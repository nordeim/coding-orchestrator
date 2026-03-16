"""
Domain exceptions for the orchestrator.

All domain-specific errors live here. No infrastructure errors leak into domain.
"""


class DomainError(Exception):
    """Base for all domain errors."""
    pass


# --- Task errors ---

class TaskError(DomainError):
    """Base for task-related errors."""
    pass


class TaskNotFoundError(TaskError):
    """Task with given ID doesn't exist."""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class TaskDependencyCycleError(TaskError):
    """Task dependency graph contains a cycle."""
    pass


class TaskDecompositionError(TaskError):
    """Task decomposition failed."""
    pass


class TaskComplexityOverflowError(TaskError):
    """Task complexity exceeds safety limits."""
    pass


# --- State machine errors ---

class InvalidStateTransition(DomainError):
    """Attempted an invalid state transition."""
    def __init__(self, current: str, target: str, entity_id: str = ""):
        self.current = current
        self.target = target
        self.entity_id = entity_id
        msg = f"Invalid transition: {current} -> {target}"
        if entity_id:
            msg += f" (entity: {entity_id})"
        super().__init__(msg)


# --- Checkpoint errors ---

class CheckpointError(DomainError):
    """Checkpoint operation failed."""
    pass


class NoCheckpointError(CheckpointError):
    """No checkpoints exist for recovery."""
    pass


# --- Storage errors ---

class StorageError(DomainError):
    """Storage operation failed."""
    pass


class SerializationError(StorageError):
    """Failed to serialize/deserialize data."""
    pass
