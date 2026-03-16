#!/usr/bin/env python3
"""
Basic usage example for the orchestrator toolkit.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate
from orchestrator.tasks.complexity import ComplexityAnalyzer
from orchestrator.tasks.decomposition import TaskDecompositionService
from orchestrator.storage.json_store import JsonStore
from orchestrator.recovery.health import HealthScorer
from orchestrator.recovery.checkpoint import CheckpointMixin

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
        )
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
    print(f"   Estimated hours: {complexity.estimated_hours:.1f}")
    print(f"   Risk factors: {', '.join(complexity.risk_factors) or 'None'}")
    print()
    
    # Decompose the task
    decomposer = TaskDecompositionService()
    subtasks = decomposer.decompose(task)
    print(f"🔨 Decomposed into {len(subtasks)} subtasks:")
    for i, subtask in enumerate(subtasks, 1):
        print(f"   {i}. {subtask.title} ({subtask.priority.value})")
    print()
    
    # Add subtasks as children
    for subtask in subtasks:
        task.add_child(subtask)
    
    print(f"👨‍👩‍👧‍👦 Task now has {len(task.children)} children")
    print()
    
    # Start working on the task
    task.start()
    print("▶️  Task started!")
    print(f"   Status: {task.status}")
    print()
    
    # Simulate some work
    print("⚙️  Simulating work progress...")
    import time
    time.sleep(1)
    
    # Complete some subtasks
    for i, subtask in enumerate(subtasks[:2]):  # Complete first 2 subtasks
        subtask.complete()
        print(f"   ✅ Completed: {subtask.title}")
    
    # Calculate progress
    progress = task.progress
    print(f"📈 Progress: {progress:.1%}")
    print()
    
    # Health check
    health_scorer = HealthScorer()
    health = health_scorer.score(task)
    print("❤️  Health Check:")
    print(f"   Score: {health.score:.2f}")
    print(f"   Status: {health.status}")
    print(f"   Issues: {', '.join(health.issues) or 'None'}")
    print()
    
    # Save to storage
    store = JsonStore("./example_tasks.json")
    store.save(task)
    print(f"💾 Saved task to {store.path}")
    
    # Load it back
    loaded = store.load(task.id)
    if loaded:
        print(f"📥 Loaded task: {loaded.title}")
        print(f"   Progress: {loaded.progress:.1%}")
        print(f"   Children: {len(loaded.children)}")
    
    print()
    print("✨ Example completed successfully!")
    print("💡 Try modifying the example to explore more features!")

if __name__ == "__main__":
    main()