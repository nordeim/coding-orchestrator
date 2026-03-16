#!/usr/bin/env python3
"""
Focused demo: Task decomposition patterns.

Demonstrates how the TaskDecompositionService breaks down
complex tasks using pattern-matching rules and templates.

Run: source /opt/venv/bin/activate && python3 examples/decompose_task.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate
from orchestrator.tasks.complexity import ComplexityAnalyzer
from orchestrator.tasks.decomposition import TaskDecompositionService


def demo_microservice():
    """Demo: Microservice decomposition."""
    print("\n" + "=" * 60)
    print("📦 MICROSERVICE DECOMPOSITION")
    print("=" * 60)

    task = TaskEntity(
        title="Build user authentication microservice",
        description="Create a standalone microservice with REST API, JWT authentication, and PostgreSQL database",
        priority=TaskPriority.HIGH,
    )

    print(f"\n📋 Original Task: {task.title}")
    print(f"   Complexity: {task.estimate.complexity.value}")

    decomposer = TaskDecompositionService()
    result = decomposer.decompose(task)

    print(f"\n✅ Decomposed into {result.subtask_count} subtasks")
    print(
        f"   Rule matched: {result.rule_used.name if result.rule_used else 'generic'}"
    )
    print(f"   Confidence: {result.confidence:.0%}")

    print("\n📝 Subtasks:")
    for i, child in enumerate(task.children, 1):
        deps = (
            ", ".join(str(d.target_task_id)[:8] for d in child.dependencies) or "none"
        )
        print(f"   {i}. {child.title}")
        print(f"      Priority: {child.priority.value} | Dependencies: {deps}")

    return task, result


def demo_crud():
    """Demo: CRUD operations decomposition."""
    print("\n" + "=" * 60)
    print("🗄️ CRUD DECOMPOSITION")
    print("=" * 60)

    task = TaskEntity(
        title="Create product management CRUD",
        description="Build CRUD API endpoints for product management with create, read, update, delete operations",
    )

    print(f"\n📋 Original Task: {task.title}")

    decomposer = TaskDecompositionService()
    result = decomposer.decompose(task)

    print(f"\n✅ Decomposed into {result.subtask_count} subtasks")
    print(
        f"   Rule matched: {result.rule_used.name if result.rule_used else 'generic'}"
    )

    print("\n📝 Subtasks:")
    for i, child in enumerate(task.children, 1):
        category = child.metadata.get("category", "general")
        print(f"   {i}. [{category}] {child.title}")

    return task, result


def demo_ui_component():
    """Demo: UI component decomposition."""
    print("\n" + "=" * 60)
    print("🎨 UI COMPONENT DECOMPOSITION")
    print("=" * 60)

    task = TaskEntity(
        title="Build user profile page component",
        description="Create a React component for user profile with avatar, settings form, and activity feed",
    )

    print(f"\n📋 Original Task: {task.title}")

    decomposer = TaskDecompositionService()
    result = decomposer.decompose(task)

    print(f"\n✅ Decomposed into {result.subtask_count} subtasks")
    print(
        f"   Rule matched: {result.rule_used.name if result.rule_used else 'generic'}"
    )

    print("\n📝 Subtasks:")
    for i, child in enumerate(task.children, 1):
        category = child.metadata.get("category", "general")
        print(f"   {i}. [{category}] {child.title}")

    return task, result


def demo_security():
    """Demo: Security implementation decomposition."""
    print("\n" + "=" * 60)
    print("🔒 SECURITY DECOMPOSITION")
    print("=" * 60)

    task = TaskEntity(
        title="Implement OAuth2 authentication",
        description="Add OAuth2 login with Google and GitHub providers, JWT tokens, and RBAC authorization",
    )

    print(f"\n📋 Original Task: {task.title}")

    decomposer = TaskDecompositionService()
    result = decomposer.decompose(task)

    print(f"\n✅ Decomposed into {result.subtask_count} subtasks")
    print(
        f"   Rule matched: {result.rule_used.name if result.rule_used else 'generic'}"
    )

    print("\n📝 Subtasks:")
    for i, child in enumerate(task.children, 1):
        category = child.metadata.get("category", "general")
        print(f"   {i}. [{category}] {child.title}")

    return task, result


def demo_complexity_analysis():
    """Demo: Complexity analysis before decomposition."""
    print("\n" + "=" * 60)
    print("📊 COMPLEXITY ANALYSIS")
    print("=" * 60)

    analyzer = ComplexityAnalyzer()

    examples = [
        ("Simple fix", "Fix the button color"),
        (
            "Moderate feature",
            "Add pagination to the user list with server-side filtering",
        ),
        (
            "Complex system",
            "Build a distributed real-time notification system with WebSocket support, Redis pub/sub, and rate limiting",
        ),
        (
            "Expert challenge",
            "Design and implement a multi-region microservices architecture with event sourcing, CQRS, and automated failover",
        ),
    ]

    for title, desc in examples:
        result = analyzer.analyze(desc, title)
        print(f'\n📝 {title}: "{desc[:50]}..."')
        print(f"   Complexity: {result.complexity_level.name}")
        print(f"   Score: {result.complexity_score:.1f}")
        print(f"   Estimate: {result.estimate.expected_hours:.1f}h (PERT)")
        caps = result.capabilities_required
        if caps:
            print(f"   Capabilities: {', '.join(caps)}")


def demo_execution_order():
    """Demo: Task execution order with dependencies."""
    print("\n" + "=" * 60)
    print("⏱️ EXECUTION ORDER (Topological Sort)")
    print("=" * 60)

    task = TaskEntity(
        title="Build API with database",
        description="API with database backend",
    )

    decomposer = TaskDecompositionService()
    decomposer.decompose(task)

    if task.children:
        print(f"\n📋 Task: {task.title}")
        print(f"   Subtasks: {len(task.children)}")

        try:
            order = task.get_execution_order()
            print("\n   Execution order (topological):")
            for i, tid in enumerate(order, 1):
                child = task.find_child(tid)
                if child:
                    print(f"   {i}. {child.title}")
        except Exception as e:
            print(f"\n   ⚠️ Could not compute order: {e}")


def main():
    print("🔧 ORCHESTRATOR TOOLKIT — Decomposition Demo")
    print("=" * 60)

    demo_complexity_analysis()
    demo_microservice()
    demo_crud()
    demo_ui_component()
    demo_security()
    demo_execution_order()

    print("\n" + "=" * 60)
    print("✨ Demo complete!")
    print("=" * 60)
    print("\n💡 Key takeaways:")
    print("   - Pattern matching selects appropriate decomposition template")
    print("   - Each template produces subtasks with dependencies")
    print("   - Complexity analysis provides effort estimates")
    print("   - Topological sort determines execution order")
    print("\n📚 See AGENT_BRIEF.md for full documentation")


if __name__ == "__main__":
    main()
