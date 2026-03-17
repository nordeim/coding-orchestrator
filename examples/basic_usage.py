#!/usr/bin/env python3
"""
Basic usage example for the orchestrator toolkit.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate
from orchestrator.tasks.complexity import ComplexityAnalyzer
from orchestrator.tasks.decomposition import TaskDecompositionService
from orchestrator.storage.json_store import JsonStore
from orchestrator.recovery.health import HealthScorer

def main():
    print("🔧 Orchestrator Toolkit Basic Usage Example")
    print("=" * 50)

    # Create a complex task
    task = TaskEntity(
        title="Build E-commerce Website",
        description="Create a full-stack e-commerce platform with React and Node.js",
        priority=TaskPriority.HIGH,
        estimate=TaskEstimate(
            optimistic_hours=20,
            likely_hours=40,
            pessimistic_hours=80,
            confidence=0.8
        ),
    )

    print(f"📋 Created task: {task.title}")
    print(f"   ID: {task.id}")
    print(f"   Priority: {task.priority.value}")
    print(f"   Estimate: {task.estimate.likely_hours}h (likelihood)")
    print(f"   Status: {task.status}")
    print()

    # Analyze complexity
    analyzer = ComplexityAnalyzer()
    complexity = analyzer.analyze(task)

    print("📊 Complexity Analysis:")
    print(f"   Score: {complexity.complexity_score:.2f}")
    print(f"   Level: {complexity.complexity_level.name}")
    print(f"   Estimated hours: {complexity.estimate.expected_hours:.1f}")
    print(f"   Risk factors: {', '.join(complexity.risk_factors) or 'None'}")
    print()

    # Decompose the task
    decomposer = TaskDecompositionService()
    result = decomposer.decompose(task)

    print(f"🔨 Decomposed into {result.subtask_count} subtasks:")
    print(f"   Pattern: {result.rule_used.name if result.rule_used else 'generic'}")
    print(f"   Confidence: {result.confidence:.0%}")
    for i, child in enumerate(task.children, 1):
        print(f"   {i}. {child.title}")
    print()

    # Start working on the task
    task.start()
    print("▶️ Task started!")
    print(f"   Status: {task.status}")
    print()

    # Simulate some work
    print("⚙️ Simulating work progress...")

    # Complete some subtasks
    for i, child in enumerate(task.children[:2]):
        child.start()
        child.complete()
        print(f"   ✅ Completed: {child.title}")

    # Calculate progress
    progress = task.get_progress()
    print(f"\n📈 Progress: {progress['progress_pct']:.1%}")
    print(f"   Completed: {progress['completed']}/{progress['total_subtasks']}")
    print()

    # Health check
    health_scorer = HealthScorer()
    health = health_scorer.score_task(task)

    print("❤️ Health Check:")
    print(f"   Score: {health.overall_score:.2f}")
    print(f"   Status: {health.status}")
    if health.recommendations:
        print(f"   Recommendations: {', '.join(health.recommendations)}")
    print()

    # Save to storage
    import tempfile
    temp_dir = tempfile.mkdtemp()
    store_path = os.path.join(temp_dir, "example_tasks.json")
    store = JsonStore(store_path)
    store.save(task)
    print(f"💾 Saved task ({store.count} task(s))")

    # Load it back
    loaded = store.load(str(task.id))
    if loaded:
        print(f"📥 Loaded task: {loaded.title}")
        progress = loaded.get_progress()
        print(f"   Progress: {progress['progress_pct']:.1%}")
        print(f"   Children: {len(loaded.children)}")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

    print()
    print("✨ Example completed successfully!")
    print("💡 Try modifying the example to explore more features!")

if __name__ == "__main__":
    main()
