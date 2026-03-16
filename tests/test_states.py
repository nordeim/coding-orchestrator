"""
Tests for state machine module.
"""

import pytest
from orchestrator.domain.states import (
    StateMachine, TransitionError,
    task_state_machine, session_state_machine,
)


class TestStateMachine:
    """Tests for generic StateMachine."""

    def test_initial_state(self):
        sm = StateMachine("pending", {"pending": {"running"}, "running": set()})
        assert sm.current == "pending"

    def test_valid_transition(self):
        sm = StateMachine("pending", {"pending": {"running"}, "running": set()})
        t = sm.transition_to("running")
        assert sm.current == "running"
        assert t.from_state == "pending"
        assert t.to_state == "running"

    def test_invalid_transition_raises(self):
        sm = StateMachine("pending", {"pending": {"running"}, "running": set()})
        with pytest.raises(TransitionError) as exc_info:
            sm.transition_to("completed")
        assert "Cannot transition" in str(exc_info.value)

    def test_terminal_state_no_transitions(self):
        sm = StateMachine("pending", {"pending": {"completed"}, "completed": set()})
        sm.transition_to("completed")
        assert sm.is_terminal
        with pytest.raises(TransitionError):
            sm.transition_to("pending")

    def test_can_transition_to(self):
        sm = StateMachine("pending", {"pending": {"running", "cancelled"}, "running": set(), "cancelled": set()})
        assert sm.can_transition_to("running")
        assert sm.can_transition_to("cancelled")
        assert not sm.can_transition_to("completed")

    def test_allowed_transitions(self):
        sm = StateMachine("pending", {"pending": {"running", "cancelled"}, "running": set(), "cancelled": set()})
        assert sm.allowed_transitions() == {"running", "cancelled"}

    def test_history_tracking(self):
        sm = StateMachine("pending", {"pending": {"running"}, "running": {"completed"}, "completed": set()})
        sm.transition_to("running", reason="start")
        sm.transition_to("completed", reason="done")
        assert len(sm.history) == 2
        assert sm.history[0].from_state == "pending"
        assert sm.history[0].to_state == "running"
        assert sm.history[0].reason == "start"

    def test_retry_from_failed(self):
        """Test the retry pattern: failed -> pending."""
        sm = StateMachine(
            "pending",
            {
                "pending": {"running"},
                "running": {"completed", "failed"},
                "failed": {"pending"},  # retry
                "completed": set(),
            },
        )
        sm.transition_to("running")
        sm.transition_to("failed")
        assert sm.current == "failed"
        # Retry
        sm.transition_to("pending")
        assert sm.current == "pending"
        sm.transition_to("running")
        sm.transition_to("completed")
        assert sm.is_terminal

    def test_entity_id_in_error(self):
        sm = StateMachine("pending", {"pending": set()}, entity_id="task-123")
        with pytest.raises(TransitionError) as exc_info:
            sm.transition_to("running")
        assert "task-123" in str(exc_info.value)


class TestTaskStateMachine:
    """Tests for pre-built task state machine."""

    def test_full_lifecycle(self):
        sm = task_state_machine("task-1")
        assert sm.current == "pending"
        sm.transition_to("ready")
        sm.transition_to("in_progress")
        sm.transition_to("completed")
        assert sm.is_terminal

    def test_failure_with_retry(self):
        sm = task_state_machine("task-2")
        sm.transition_to("ready")
        sm.transition_to("in_progress")
        sm.transition_to("failed")
        assert sm.is_terminal

    def test_pause_resume(self):
        sm = task_state_machine("task-3")
        sm.transition_to("ready")
        sm.transition_to("in_progress")
        sm.transition_to("paused")
        assert sm.current == "paused"
        sm.transition_to("in_progress")
        assert sm.current == "in_progress"

    def test_blocked_then_resumed(self):
        sm = task_state_machine("task-4")
        sm.transition_to("ready")
        sm.transition_to("in_progress")
        sm.transition_to("blocked")
        sm.transition_to("in_progress")
        sm.transition_to("completed")
        assert sm.is_terminal


class TestSessionStateMachine:
    """Tests for pre-built session state machine (12 states)."""

    def test_standard_flow(self):
        sm = session_state_machine("sess-1")
        sm.transition_to("running")  # start_execution: pending -> running
        sm.transition_to("completed")
        assert sm.is_terminal

    def test_queued_then_running(self):
        sm = session_state_machine("sess-1b")
        sm.transition_to("queued")
        sm.transition_to("running")
        sm.transition_to("completed")
        assert sm.is_terminal

    def test_degraded_recovery(self):
        sm = session_state_machine("sess-2")
        sm.transition_to("queued")
        sm.transition_to("running")
        sm.transition_to("degraded")
        assert sm.current == "degraded"
        sm.transition_to("running")
        assert sm.current == "running"

    def test_retry_from_failed(self):
        sm = session_state_machine("sess-3")
        sm.transition_to("queued")
        sm.transition_to("running")
        sm.transition_to("failed")
        assert not sm.is_terminal  # failed has retry path to pending
        sm.transition_to("pending")  # retry
        assert sm.current == "pending"

    def test_timeout_retry(self):
        sm = session_state_machine("sess-4")
        sm.transition_to("running")
        sm.transition_to("timeout")
        assert not sm.is_terminal  # timeout has retry path
        sm.transition_to("pending")  # retry

    def test_completed_is_terminal(self):
        sm = session_state_machine("sess-5")
        sm.transition_to("running")
        sm.transition_to("completed")
        assert sm.is_terminal
        with pytest.raises(TransitionError):
            sm.transition_to("pending")
