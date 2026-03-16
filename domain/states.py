"""
Generic state machine with validated transitions.

Extracted from SessionStatus, generalized for any entity.
No dependencies on infrastructure, storage, or external services.
"""

from enum import Enum
from typing import Set, Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timezone


class TransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    def __init__(self, current: str, target: str, entity_id: str = "", reason: str = ""):
        self.current = current
        self.target = target
        self.entity_id = entity_id
        self.reason = reason
        msg = f"Cannot transition from '{current}' to '{target}'"
        if entity_id:
            msg += f" (entity: {entity_id})"
        if reason:
            msg += f". {reason}"
        super().__init__(msg)


@dataclass(frozen=True)
class Transition:
    """A recorded state transition."""
    from_state: str
    to_state: str
    timestamp: datetime
    entity_id: str = ""
    reason: str = ""


class StateMachine:
    """
    Generic state machine with validated transitions.

    Usage:
        sm = StateMachine(
            initial="pending",
            transitions={
                "pending": {"running", "cancelled"},
                "running": {"completed", "failed", "paused"},
                "paused": {"running", "cancelled"},
                "failed": {"pending"},  # retry
                "completed": set(),     # terminal
                "cancelled": set(),     # terminal
            }
        )
        sm.transition_to("running")
        sm.transition_to("completed")
    """

    def __init__(
        self,
        initial: str,
        transitions: Dict[str, Set[str]],
        terminal_states: Optional[Set[str]] = None,
        entity_id: str = "",
    ):
        self._current = initial
        self._transitions = transitions
        self._entity_id = entity_id
        self._history: List[Transition] = []

        # Derive terminal states if not provided
        if terminal_states is not None:
            self._terminal = terminal_states
        else:
            self._terminal = {s for s, targets in transitions.items() if not targets}

    @property
    def current(self) -> str:
        return self._current

    @property
    def is_terminal(self) -> bool:
        return self._current in self._terminal

    @property
    def history(self) -> List[Transition]:
        return list(self._history)

    def can_transition_to(self, target: str) -> bool:
        """Check if transition to target state is valid."""
        allowed = self._transitions.get(self._current, set())
        return target in allowed

    def allowed_transitions(self) -> Set[str]:
        """Get set of states reachable from current state."""
        return self._transitions.get(self._current, set()).copy()

    def transition_to(self, target: str, reason: str = "") -> Transition:
        """
        Transition to target state with validation.

        Returns the Transition record.
        Raises TransitionError if invalid.
        """
        if self.is_terminal:
            raise TransitionError(
                self._current, target, self._entity_id,
                f"Cannot transition from terminal state '{self._current}'"
            )

        if not self.can_transition_to(target):
            allowed = self.allowed_transitions()
            raise TransitionError(
                self._current, target, self._entity_id,
                f"Allowed transitions: {allowed or 'none'}"
            )

        old_state = self._current
        self._current = target

        transition = Transition(
            from_state=old_state,
            to_state=target,
            timestamp=datetime.now(timezone.utc),
            entity_id=self._entity_id,
            reason=reason,
        )
        self._history.append(transition)
        return transition

    def reset(self, to_state: str = None, reason: str = "") -> Transition:
        """Reset state machine (typically for retry scenarios)."""
        target = to_state or self._initial_state()
        if target not in self._transitions:
            raise ValueError(f"Unknown reset target state: {target}")

        old = self._current
        self._current = target
        transition = Transition(
            from_state=old,
            to_state=target,
            timestamp=datetime.now(timezone.utc),
            entity_id=self._entity_id,
            reason=reason or "reset",
        )
        self._history.append(transition)
        return transition

    def _initial_state(self) -> str:
        """Find the initial state (state with no incoming transitions)."""
        all_targets = set()
        for targets in self._transitions.values():
            all_targets.update(targets)
        roots = set(self._transitions.keys()) - all_targets
        if roots:
            return next(iter(roots))
        # Fallback: first key
        return next(iter(self._transitions.keys())) if self._transitions else ""

    def __repr__(self) -> str:
        return f"StateMachine(current='{self._current}', terminal={self.is_terminal})"


# --- Pre-built state machines for common use cases ---

def task_state_machine(entity_id: str = "") -> StateMachine:
    """State machine for task lifecycle. Allows direct start from pending."""
    return StateMachine(
        initial="pending",
        transitions={
            "pending": {"ready", "in_progress", "cancelled"},
            "ready": {"in_progress", "cancelled"},
            "in_progress": {"completed", "failed", "blocked", "paused"},
            "blocked": {"in_progress", "cancelled"},
            "paused": {"in_progress", "cancelled"},
            "completed": set(),
            "failed": set(),
            "cancelled": set(),
        },
        terminal_states={"completed", "failed", "cancelled"},
        entity_id=entity_id,
    )


def session_state_machine(entity_id: str = "") -> StateMachine:
    """State machine for session lifecycle (12 states from industrial orchestrator)."""
    return StateMachine(
        initial="pending",
        transitions={
            "pending": {"queued", "running", "cancelled", "failed"},
            "queued": {"running", "cancelled", "failed"},
            "running": {
                "completed", "partially_completed", "failed",
                "timeout", "paused", "stopped", "degraded",
            },
            "paused": {"running", "stopped", "cancelled"},
            "degraded": {"running", "failed", "completed", "stopped"},
            "failed": {"pending"},  # retry
            "timeout": {"pending"},  # retry
            "completed": set(),
            "partially_completed": set(),
            "stopped": set(),
            "cancelled": set(),
            "orphaned": set(),
        },
        terminal_states={
            "completed", "partially_completed", "stopped",
            "cancelled", "orphaned",
        },
        entity_id=entity_id,
    )
