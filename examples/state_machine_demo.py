#!/usr/bin/env python3
"""
Focused demo: State machine transitions.

Demonstrates the generic StateMachine with validated transitions,
history tracking, and pre-built task/session state machines.

Run: source /opt/venv/bin/activate && python3 examples/state_machine_demo.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from orchestrator.domain.states import (
    StateMachine,
    TransitionError,
    task_state_machine,
    session_state_machine,
)


def demo_basic_transitions():
    """Demo: Basic state machine transitions."""
    print("\n" + "=" * 60)
    print("🔄 BASIC STATE MACHINE")
    print("=" * 60)

    sm = StateMachine(
        initial="pending",
        transitions={
            "pending": {"running", "cancelled"},
            "running": {"completed", "failed", "paused"},
            "paused": {"running", "cancelled"},
            "completed": set(),
            "failed": set(),
            "cancelled": set(),
        },
        entity_id="task-001",
    )

    print(f"\n📋 Initial state: {sm.current}")
    print(f"   Allowed transitions: {sm.allowed_transitions()}")
    print(f"   Is terminal: {sm.is_terminal}")

    print("\n➡️ Transitioning: pending → running")
    t = sm.transition_to("running", reason="started execution")
    print(f"   Current state: {sm.current}")
    print(f"   Transition timestamp: {t.timestamp.isoformat()}")

    print("\n➡️ Transitioning: running → paused")
    sm.transition_to("paused", reason="user requested pause")
    print(f"   Current state: {sm.current}")

    print("\n➡️ Transitioning: paused → running")
    sm.transition_to("running", reason="resumed")
    print(f"   Current state: {sm.current}")

    print("\n➡️ Transitioning: running → completed")
    sm.transition_to("completed", reason="all work done")
    print(f"   Current state: {sm.current}")
    print(f"   Is terminal: {sm.is_terminal}")

    print("\n📜 Transition history:")
    for i, t in enumerate(sm.history, 1):
        print(f"   {i}. {t.from_state} → {t.to_state} ({t.reason})")

    return sm


def demo_invalid_transition():
    """Demo: Invalid transition handling."""
    print("\n" + "=" * 60)
    print("⚠️ INVALID TRANSITION HANDLING")
    print("=" * 60)

    sm = task_state_machine("task-002")
    print(f"\n📋 Initial state: {sm.current}")
    print(f"   Allowed: {sm.allowed_transitions()}")

    print("\n❌ Attempting invalid transition: pending → completed")
    print("   (direct transition not allowed)")

    try:
        sm.transition_to("completed")
    except TransitionError as e:
        print(f"   ✅ Caught TransitionError: {e}")

    print("\n✓ Correct path: pending → in_progress → completed")
    sm.transition_to("in_progress")
    sm.transition_to("completed")
    print(f"   Current state: {sm.current}")


def demo_task_state_machine():
    """Demo: Full task lifecycle."""
    print("\n" + "=" * 60)
    print("📋 TASK STATE MACHINE (8 states)")
    print("=" * 60)

    sm = task_state_machine("task-003")

    print("\n📊 States and transitions:")
    states = [
        "pending",
        "ready",
        "in_progress",
        "blocked",
        "paused",
        "completed",
        "failed",
        "cancelled",
    ]

    for state in states:
        sm._current = state
        allowed = sm.allowed_transitions()
        terminal = (
            " (terminal)" if state in {"completed", "failed", "cancelled"} else ""
        )
        print(f"   {state}: {allowed or 'none'}{terminal}")

    sm._current = "pending"
    print("\n🎬 Full lifecycle demo:")

    print(f"   Starting: {sm.current}")
    sm.transition_to("ready", reason="dependencies satisfied")
    print(f"   → {sm.current} (dependencies satisfied)")
    sm.transition_to("in_progress", reason="started")
    print(f"   → {sm.current} (started)")
    sm.transition_to("paused", reason="user pause")
    print(f"   → {sm.current} (paused)")
    sm.transition_to("in_progress", reason="resumed")
    print(f"   → {sm.current} (resumed)")
    sm.transition_to("completed", reason="done")
    print(f"   → {sm.current} (completed)")
    print(f"   Terminal: {sm.is_terminal}")


def demo_session_state_machine():
    """Demo: Session lifecycle with retry support."""
    print("\n" + "=" * 60)
    print("🖥️ SESSION STATE MACHINE (12 states)")
    print("=" * 60)

    sm = session_state_machine("session-001")

    print("\n📊 All states:")
    states = [
        "pending",
        "queued",
        "running",
        "paused",
        "degraded",
        "failed",
        "timeout",
        "completed",
        "partially_completed",
        "stopped",
        "cancelled",
        "orphaned",
    ]

    terminal_states = {
        "completed",
        "partially_completed",
        "stopped",
        "cancelled",
        "orphaned",
    }

    for state in states:
        sm._current = state
        allowed = sm.allowed_transitions()
        marker = " [terminal]" if state in terminal_states else ""
        print(f"   {state}:{marker}")
        if allowed:
            print(f"      → {allowed}")

    print("\n🎬 Lifecycle with failure and retry:")
    sm._current = "pending"

    print(f"   Starting: {sm.current}")
    sm.transition_to("queued", reason="added to queue")
    print(f"   → {sm.current}")
    sm.transition_to("running", reason="dequeued")
    print(f"   → {sm.current}")
    sm.transition_to("failed", reason="connection lost")
    print(f"   → {sm.current} (FAILED)")

    print("\n   🔄 Retry support (failed → pending):")
    sm.transition_to("pending", reason="retry requested")
    print(f"   → {sm.current} (back to pending)")
    sm.transition_to("running", reason="retry started")
    print(f"   → {sm.current}")
    sm.transition_to("completed", reason="success on retry")
    print(f"   → {sm.current} (COMPLETED)")


def demo_timeout_recovery():
    """Demo: Timeout recovery flow."""
    print("\n" + "=" * 60)
    print("⏱️ TIMEOUT RECOVERY")
    print("=" * 60)

    sm = session_state_machine("session-002")

    print("\n🎬 Timeout recovery demo:")
    print(f"   Starting: {sm.current}")
    sm.transition_to("running", reason="started")
    print(f"   → {sm.current}")
    sm.transition_to("timeout", reason="no heartbeat for 30s")
    print(f"   → {sm.current} (TIMEOUT)")

    print("\n   🔄 Retry from timeout:")
    sm.transition_to("pending", reason="automatic retry")
    print(f"   → {sm.current} (back to pending)")
    sm.transition_to("running", reason="restarted")
    print(f"   → {sm.current}")


def demo_can_transition():
    """Demo: Pre-checking transitions."""
    print("\n" + "=" * 60)
    print("✅ PRE-CHECKING TRANSITIONS")
    print("=" * 60)

    sm = task_state_machine("task-004")

    print(f"\n📋 Current state: {sm.current}")

    transitions = ["ready", "in_progress", "completed", "cancelled"]
    print("\n   Checking transitions:")
    for target in transitions:
        can = sm.can_transition_to(target)
        symbol = "✓" if can else "✗"
        print(f"   {symbol} {sm.current} → {target}: {can}")


def demo_custom_state_machine():
    """Demo: Custom state machine configuration."""
    print("\n" + "=" * 60)
    print("⚙️ CUSTOM STATE MACHINE")
    print("=" * 60)

    print("\n📚 Content publishing workflow:")

    sm = StateMachine(
        initial="draft",
        transitions={
            "draft": {"review", "cancelled"},
            "review": {"approved", "rejected", "cancelled"},
            "rejected": {"draft", "cancelled"},
            "approved": {"published"},
            "published": {"archived"},
            "archived": set(),
            "cancelled": set(),
        },
        entity_id="article-001",
    )

    states = [
        "draft",
        "review",
        "rejected",
        "approved",
        "published",
        "archived",
        "cancelled",
    ]

    print("\n   States:")
    for state in states:
        sm._current = state
        allowed = sm.allowed_transitions()
        terminal = " [terminal]" if not allowed else ""
        print(f"   {state}: {allowed or 'none'}{terminal}")

    print("\n🎬 Publishing flow:")
    sm._current = "draft"
    print(f"   {sm.current}")
    sm.transition_to("review", reason="submitted for review")
    print(f"   → {sm.current}")
    sm.transition_to("rejected", reason="needs revision")
    print(f"   → {sm.current}")
    sm.transition_to("draft", reason="back to drafting")
    print(f"   → {sm.current}")
    sm.transition_to("review", reason="resubmitted")
    print(f"   → {sm.current}")
    sm.transition_to("approved", reason="approved by editor")
    print(f"   → {sm.current}")
    sm.transition_to("published", reason="published to production")
    print(f"   → {sm.current}")
    sm.transition_to("archived", reason="archived")
    print(f"   → {sm.current} [terminal]")


def main():
    print("🔧 ORCHESTRATOR TOOLKIT — State Machine Demo")
    print("=" * 60)

    demo_basic_transitions()
    demo_invalid_transition()
    demo_task_state_machine()
    demo_session_state_machine()
    demo_timeout_recovery()
    demo_can_transition()
    demo_custom_state_machine()

    print("\n" + "=" * 60)
    print("✨ Demo complete!")
    print("=" * 60)
    print("\n💡 Key takeaways:")
    print("   - StateMachine enforces valid transitions")
    print("   - Terminal states have no outgoing transitions")
    print("   - History tracks all transitions with timestamps")
    print("   - Retry support: failed → pending, timeout → pending")
    print("   - Pre-built machines for tasks (8 states) and sessions (12 states)")
    print("\n📚 See AGENT_BRIEF.md for full documentation")


if __name__ == "__main__":
    main()
