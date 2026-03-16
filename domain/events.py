"""
Domain events for audit trail.

Lightweight event models for tracking what happened, when, and why.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
from uuid import UUID
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DomainEvent:
    """Base domain event."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = ""

    def __post_init__(self):
        if not self.event_type:
            object.__setattr__(self, 'event_type', self.__class__.__name__)


# --- Task events ---

@dataclass(frozen=True)
class TaskCreated(DomainEvent):
    task_id: UUID = None
    title: str = ""
    priority: str = ""
    event_type: str = "TaskCreated"


@dataclass(frozen=True)
class TaskStatusChanged(DomainEvent):
    task_id: UUID = None
    old_status: str = ""
    new_status: str = ""
    reason: str = ""
    event_type: str = "TaskStatusChanged"


@dataclass(frozen=True)
class TaskDecomposed(DomainEvent):
    task_id: UUID = None
    subtask_count: int = 0
    strategy: str = ""
    event_type: str = "TaskDecomposed"


@dataclass(frozen=True)
class TaskCompleted(DomainEvent):
    task_id: UUID = None
    duration_seconds: float = 0.0
    result_summary: str = ""
    event_type: str = "TaskCompleted"


@dataclass(frozen=True)
class TaskFailed(DomainEvent):
    task_id: UUID = None
    error_type: str = ""
    error_message: str = ""
    retryable: bool = False
    event_type: str = "TaskFailed"


# --- Checkpoint events ---

@dataclass(frozen=True)
class CheckpointSaved(DomainEvent):
    task_id: UUID = None
    sequence: int = 0
    data_keys: List[str] = field(default_factory=list)
    event_type: str = "CheckpointSaved"


@dataclass(frozen=True)
class CheckpointRestored(DomainEvent):
    task_id: UUID = None
    sequence: int = 0
    event_type: str = "CheckpointRestored"


# --- Event collector ---

class EventCollector:
    """
    Collects domain events for later processing.

    Usage:
        collector = EventCollector()
        collector.emit(TaskCreated(task_id=uuid, title="Build feature"))
        collector.emit(TaskCompleted(task_id=uuid, duration_seconds=3600))
        events = collector.drain()  # Get and clear
    """

    def __init__(self):
        self._events: List[DomainEvent] = []

    def emit(self, event: DomainEvent) -> None:
        """Emit a domain event."""
        self._events.append(event)

    def drain(self) -> List[DomainEvent]:
        """Get all events and clear the collector."""
        events = list(self._events)
        self._events.clear()
        return events

    def peek(self) -> List[DomainEvent]:
        """Get events without clearing."""
        return list(self._events)

    @property
    def count(self) -> int:
        return len(self._events)

    def clear(self) -> None:
        self._events.clear()
