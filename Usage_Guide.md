# Orchestrator Toolkit — Comprehensive Usage Guide

> **A practical guide for managing coding tasks with hierarchical decomposition, state machines, and progress tracking.**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Core Concepts](#core-concepts)
4. [Getting Started](#getting-started)
5. [Typical Coding Workflow](#typical-coding-workflow)
6. [Component Deep Dives](#component-deep-dives)
7. [Advanced Usage](#advanced-usage)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Reference](#reference)

---

## Introduction

### What is the Orchestrator Toolkit?

The Orchestrator Toolkit is a **pure-Python library** for managing complex coding tasks. It provides:

- **Task Hierarchy** — Break down large projects into manageable subtasks
- **State Machines** — Track task lifecycle with validated transitions
- **Dependency Management** — Define which tasks must complete before others
- **Complexity Analysis** — Automatically estimate effort based on task descriptions
- **Progress Tracking** — Monitor completion across entire task trees
- **Health Scoring** — Identify at-risk tasks before they fail
- **Persistence** — Save and restore task state to JSON files

### Why Use It?

**Problem:** Coding projects often start simple but grow complex. Without structure, you face:
- Lost context when switching tasks
- Unclear progress status
- Forgotten dependencies
- No recovery from interruptions

**Solution:** The Orchestrator provides a structured approach to task management that:
- Keeps you organized across sessions
- Shows clear progress at any moment
- Automatically decomposes complex tasks
- Enables recovery from failures

### Design Philosophy

**"Extract the brains, dump the infrastructure."**

This toolkit is a lightweight extraction from a production enterprise system. It contains only the core orchestration logic — no databases, no external services, no multi-tenancy. Just pure Python that works anywhere.

---

## Installation & Setup

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Setup

```bash
# Activate your virtual environment
source /opt/venv/bin/activate

# Navigate to the project directory
cd /path/to/orchestrator

# Verify tests pass
python3 -m pytest orchestrator/tests/ -v
```

### Running Examples

```bash
# Run the decomposition demo
python3 orchestrator/examples/decompose_task.py

# Run the state machine demo
python3 orchestrator/examples/state_machine_demo.py

# Run the basic usage example
python3 orchestrator/examples/basic_usage.py
```

---

## Core Concepts

### 1. Task Entity

The **TaskEntity** is the fundamental unit of work. It represents anything you need to build, fix, or implement.

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate

task = TaskEntity(
    title="Build REST API",
    description="Create a REST API with authentication",
    priority=TaskPriority.HIGH,
    estimate=TaskEstimate(
        optimistic_hours=2,
        likely_hours=4,
        pessimistic_hours=8,
        confidence=0.7
    )
)
```

**Key attributes:**
- `id` — Unique identifier (UUID)
- `title` — Human-readable task name
- `description` — Detailed task description
- `priority` — BLOCKER, CRITICAL, HIGH, NORMAL, LOW, BACKGROUND
- `estimate` — PERT-style time estimate
- `status` — Current state (pending, in_progress, completed, etc.)
- `children` — Subtasks for hierarchical decomposition
- `dependencies` — Tasks that must complete first

### 2. State Machine

Every task has a **state machine** that enforces valid transitions.

```
pending → ready → in_progress → completed
                   ↓
                 blocked
                   ↓
                paused
                   ↓
              failed / cancelled
```

**Valid transitions:**
- `pending` → `ready`, `in_progress`, `cancelled`
- `ready` → `in_progress`, `cancelled`
- `in_progress` → `completed`, `failed`, `blocked`, `paused`
- `blocked` → `in_progress`, `cancelled`
- `paused` → `in_progress`, `cancelled`

### 3. Decomposition

**Decomposition** breaks complex tasks into subtasks using pattern matching.

**Available templates:**
| Pattern | Subtasks | Example Match |
|---------|----------|---------------|
| Microservice | 8 | "Build user authentication microservice" |
| CRUD | 8 | "Create product management CRUD" |
| UI Component | 7 | "Build user profile page component" |
| Security | 7 | "Implement OAuth2 authentication" |
| API | 6 | "Create REST API for user management" |
| Refactor | 6 | "Refactor authentication module" |

### 4. Complexity Analysis

The **ComplexityAnalyzer** examines task descriptions to estimate effort.

**Factors analyzed:**
- Word count
- Technical keyword density (API, database, auth, etc.)
- Capability breadth (backend, frontend, devops, etc.)
- Complexity signals (refactor, migrate, distributed, etc.)

**Complexity levels:**
| Level | Hours Range | Description |
|-------|-------------|-------------|
| TRIVIAL | < 0.25h | Quick fixes, typo corrections |
| SIMPLE | 0.25-1h | Single function, minor feature |
| MODERATE | 1-4h | Component, API endpoint |
| COMPLEX | 4-8h | Service, feature module |
| EXPERT | 8+h | System, distributed architecture |

### 5. Health Scoring

The **HealthScorer** evaluates task health across multiple dimensions.

**Dimensions:**
- **State health** — Is the task in a good state?
- **Time health** — Elapsed vs. estimated time
- **Dependency health** — Are dependencies satisfied?
- **Hierarchy health** — Subtask completion rate

**Health status:**
| Score | Status | Meaning |
|-------|--------|---------|
| ≥ 0.8 | healthy | On track |
| 0.5-0.8 | warning | Needs attention |
| < 0.5 | critical | At risk of failure |

---

## Getting Started

### Your First Task

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority

# Create a simple task
task = TaskEntity(
    title="Fix login button styling",
    description="The login button needs proper padding and hover state"
)

# Check initial state
print(f"Status: {task.status}")  # "pending"
print(f"Priority: {task.priority.value}")  # "normal"

# Start working
task.start()
print(f"Status: {task.status}")  # "in_progress"

# Complete the task
task.complete(result={"files_changed": ["login.css"]})
print(f"Status: {task.status}")  # "completed"
```

### Adding Estimates

```python
from orchestrator.tasks.entity import TaskEntity, TaskEstimate

task = TaskEntity(
    title="Implement password reset",
    description="Add password reset flow with email verification",
    estimate=TaskEstimate(
        optimistic_hours=2,   # Best case
        likely_hours=4,       # Most likely
        pessimistic_hours=8,  # Worst case
        confidence=0.6        # How confident (0-1)
    )
)

# Access PERT-calculated expected hours
print(f"Expected: {task.estimate.expected_hours:.1f}h")  # (2 + 4*4 + 8) / 6 = 4.33h
print(f"Complexity: {task.estimate.complexity.value}")  # "moderate"
```

### Creating a Task Hierarchy

```python
from orchestrator.tasks.entity import TaskEntity

# Parent task
project = TaskEntity(
    title="E-commerce Platform",
    description="Full-stack e-commerce with React and Node.js"
)

# Child tasks
frontend = TaskEntity(title="Build Frontend", parent_id=project.id)
backend = TaskEntity(title="Build Backend", parent_id=project.id)
database = TaskEntity(title="Design Database", parent_id=project.id)

# Add to parent
project.add_child(frontend)
project.add_child(backend)
project.add_child(database)

# Query hierarchy
print(f"Total tasks: {len(project.flatten())}")  # 4 (parent + 3 children)
print(f"Is leaf: {frontend.is_leaf}")  # True
print(f"Is root: {project.is_root}")  # True
```

---

## Typical Coding Workflow

This section walks through a complete workflow from receiving a task to completion.

### Step 1: Analyze the Task

```python
from orchestrator.tasks.complexity import ComplexityAnalyzer
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate

# You receive a task
task = TaskEntity(
    title="Build user authentication microservice",
    description="""
    Create a standalone microservice with:
    - REST API for user registration and login
    - JWT authentication with refresh tokens
    - PostgreSQL database for user storage
    - Rate limiting and brute-force protection
    """,
    priority=TaskPriority.HIGH
)

# Analyze complexity
analyzer = ComplexityAnalyzer()
result = analyzer.analyze(task.description, task.title)

print(f"Complexity: {result.complexity_level.name}")
# Output: COMPLEX

print(f"Estimated hours: {result.estimate.expected_hours:.1f}h")
# Output: 8.5h

print(f"Capabilities: {', '.join(result.capabilities_required)}")
# Output: backend_api, authentication, database, security
```

### Step 2: Decompose the Task

```python
from orchestrator.tasks.decomposition import TaskDecompositionService

# Create decomposition service
decomposer = TaskDecompositionService()

# Add estimate to task (required for decomposition)
task.estimate = result.estimate

# Decompose
decomposition = decomposer.decompose(task)

print(f"Pattern matched: {decomposition.rule_used.name}")
# Output: microservice

print(f"Subtasks created: {decomposition.subtask_count}")
# Output: 8

print(f"Confidence: {decomposition.confidence:.0%}")
# Output: 85%

# View subtasks
for i, child in enumerate(task.children, 1):
    print(f"{i}. {child.title}")
# Output:
# 1. Design API contract (endpoints, request/response schemas)
# 2. Define data model and database schema
# 3. Implement core business logic / service layer
# 4. Implement API endpoints with validation
# 5. Add authentication and authorization
# 6. Write unit tests for service layer
# 7. Write integration tests for API endpoints
# 8. Add logging, metrics, and health checks
```

### Step 3: Set Up Dependencies

```python
# Dependencies are automatically set by decomposition
# But you can modify them:

# Get the execution order
order = task.get_execution_order()
print("Execution order:")
for task_id in order:
    child = task.find_child(task_id)
    if child:
        print(f"  - {child.title}")

# Validate no cycles
assert task.validate_dag(), "Dependency graph has cycles!"

# Get critical path (longest path)
critical = task.get_critical_path()
print(f"Critical path has {len(critical)} tasks")
```

### Step 4: Start Execution

```python
# Start the parent task
task.start()
print(f"Project status: {task.status}")  # "in_progress"

# Start first subtask
first_subtask = task.children[0]
first_subtask.start()
print(f"Working on: {first_subtask.title}")
```

### Step 5: Track Progress

```python
# Complete subtasks as you work
first_subtask.complete(result={
    "endpoints": [
        {"method": "POST", "path": "/auth/register"},
        {"method": "POST", "path": "/auth/login"},
        {"method": "POST", "path": "/auth/refresh"},
    ]
})

# Get progress
progress = task.get_progress()
print(f"Progress: {progress['progress_pct']:.1f}%")
print(f"Completed: {progress['completed']}/{progress['total_subtasks']}")

# Check health
from orchestrator.recovery.health import HealthScorer

scorer = HealthScorer()
health = scorer.score_task(task)

print(f"Health: {health.status}")  # "healthy", "warning", "critical"
print(f"Score: {health.overall_score:.2f}")

if health.recommendations:
    print("Recommendations:")
    for rec in health.recommendations:
        print(f"  - {rec}")
```

### Step 6: Handle Interruptions

```python
from orchestrator.recovery.checkpoint import CheckpointMixin

# Define a recoverable workflow
class AuthMicroserviceWorkflow(CheckpointMixin):
    def __init__(self, task):
        self.task = task
        self.id = str(task.id)
        super().__init__()
    
    def run(self):
        # Save checkpoints at key points
        self.checkpoint("initialized", {"task_id": str(self.task.id)})
        
        self.setup_database()
        self.checkpoint("database_ready", {"tables": ["users", "tokens"]})
        
        self.implement_auth()
        self.checkpoint("auth_implemented")
        
        self.write_tests()
        self.checkpoint("tests_written")
        
        self.deploy()
        self.checkpoint("deployed")
    
    def resume_from_last(self):
        # Restore from last checkpoint after failure
        state = self.restore_from_checkpoint()
        print(f"Resuming from: {state['step']}")
        # Continue from where you left off...

# Use it
workflow = AuthMicroserviceWorkflow(task)
try:
    workflow.run()
except Exception as e:
    print(f"Failed at: {workflow.current_step}")
    # Later, you can resume:
    # workflow.resume_from_last()
```

### Step 7: Save and Restore

```python
from orchestrator.storage.json_store import JsonStore

# Save progress
store = JsonStore("/path/to/project/tasks.json")
store.save(task)

# Later, restore
loaded = store.load(str(task.id))
if loaded:
    print(f"Restored: {loaded.title}")
    print(f"Status: {loaded.status}")
    print(f"Children: {len(loaded.children)}")
```

---

## Component Deep Dives

### State Machine

The state machine enforces valid transitions and tracks history.

```python
from orchestrator.domain.states import StateMachine, task_state_machine

# Use pre-built task state machine
sm = task_state_machine("my-task-001")

# Check current state
print(sm.current)  # "pending"

# Check allowed transitions
print(sm.allowed_transitions())  # {'in_progress', 'ready', 'cancelled'}

# Pre-check if transition is valid
if sm.can_transition_to("in_progress"):
    sm.transition_to("in_progress", reason="Started coding")

# Transition history
for t in sm.history:
    print(f"{t.from_state} → {t.to_state} at {t.timestamp}")

# Terminal states
sm.transition_to("completed")
print(sm.is_terminal)  # True
# sm.transition_to("in_progress")  # Raises TransitionError!
```

#### Custom State Machine

```python
# Create a custom state machine for content publishing
publishing_sm = StateMachine(
    initial="draft",
    transitions={
        "draft": {"review", "cancelled"},
        "review": {"approved", "rejected", "cancelled"},
        "rejected": {"draft", "cancelled"},
        "approved": {"published"},
        "published": {"archived"},
        "archived": set(),  # terminal
        "cancelled": set(),  # terminal
    },
    entity_id="article-123",
    terminal_states={"archived", "cancelled"}
)
```

### Complexity Analyzer

```python
from orchestrator.tasks.complexity import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()

# Analyze task descriptions
descriptions = [
    "Fix typo in README",
    "Add pagination to user list",
    "Build distributed caching layer with Redis",
    "Design microservices architecture for e-commerce platform",
]

for desc in descriptions:
    result = analyzer.analyze(desc)
    print(f"{desc[:40]}...")
    print(f"  Complexity: {result.complexity_level.name}")
    print(f"  Estimate: {result.estimate.expected_hours:.1f}h")
    print(f"  Keywords: {result.technical_terms_found[:3]}")
    print()
```

#### Custom Keywords

```python
# Add custom technical keywords
analyzer = ComplexityAnalyzer(
    technical_keywords={"graphql", "websocket", "grpc", "kafka", "rabbitmq"},
    capability_map={
        "graphql": "backend_api",
        "websocket": "realtime",
        "kafka": "messaging",
    },
    complexity_signals={
        "scale": 2,
        "distributed": 3,
        "quick": -1,
    }
)
```

### Task Decomposition

```python
from orchestrator.tasks.decomposition import (
    TaskDecompositionService,
    DecompositionRule,
    SubtaskSpec,
)
from orchestrator.tasks.entity import TaskEntity, TaskEstimate

# Built-in rules
decomposer = TaskDecompositionService()
print(decomposer.available_rules())
# ['microservice', 'crud', 'ui_component', 'security']

# Create a custom rule
def _decompose_ml_pipeline(title, description):
    return [
        SubtaskSpec("Data collection and exploration", priority="high"),
        SubtaskSpec("Data preprocessing and feature engineering"),
        SubtaskSpec("Model selection and baseline training"),
        SubtaskSpec("Hyperparameter tuning"),
        SubtaskSpec("Model evaluation and validation"),
        SubtaskSpec("Deployment and monitoring setup"),
    ]

ml_rule = DecompositionRule(
    name="ml_pipeline",
    pattern=r"machine learning|ml model|predict|train model|classifier",
    description="ML pipeline from data to deployment",
    decompose_fn=_decompose_ml_pipeline,
    confidence=0.75,
)

# Add custom rule
decomposer.add_rule(ml_rule)

# Decompose matching task
task = TaskEntity(
    title="Build churn prediction model",
    description="Create ML model to predict customer churn",
    estimate=TaskEstimate(optimistic_hours=8, likely_hours=16, pessimistic_hours=32)
)

result = decomposer.decompose(task)
print(f"Matched: {result.rule_used.name}")  # "ml_pipeline"
```

### Health Scoring

```python
from orchestrator.recovery.health import HealthScorer
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate

# Create a task tree
task = TaskEntity(
    title="Feature Project",
    estimate=TaskEstimate(optimistic_hours=4, likely_hours=8, pessimistic_hours=16)
)

task.add_child(TaskEntity(title="Subtask 1"))
task.add_child(TaskEntity(title="Subtask 2"))
task.add_child(TaskEntity(title="Subtask 3"))

# Start and partially complete
task.start()
task.children[0].start()
task.children[0].complete()

# Score health
scorer = HealthScorer()
report = scorer.score_task(task)

print(f"Overall: {report.overall_score:.2f}")  # 0.85
print(f"Status: {report.status}")  # "healthy"

for indicator in report.indicators:
    print(f"  {indicator.name}: {indicator.score:.2f} - {indicator.reason}")
# Output:
#   state: 0.90 - Actively executing
#   time: 0.95 - Ahead of schedule (10% of estimate)
#   hierarchy: 0.70 - 1/3 subtasks complete

if report.recommendations:
    for rec in report.recommendations:
        print(f"  Recommend: {rec}")
```

#### System Health

```python
# Score multiple tasks as a system
tasks = [
    TaskEntity(title="Task A"),
    TaskEntity(title="Task B"),
    TaskEntity(title="Task C"),
]

# Mark some as failed/blocked
tasks[0].start()
tasks[0].complete()

tasks[1].start()
tasks[1].fail(Exception("Connection timeout"))

tasks[2].block("Waiting for Task B")

# Score the system
scorer = HealthScorer()
system_health = scorer.score_system(tasks)

print(f"System health: {system_health.overall_score:.2f}")
print(f"Status: {system_health.status}")
# Output:
#   System health: 0.45
#   Status: warning
#   Recommendations: High failure rate (33%). Review error patterns.
```

### JSON Storage

```python
from orchestrator.storage.json_store import JsonStore
from orchestrator.tasks.entity import TaskEntity, TaskEstimate

# Create store
store = JsonStore("./my_project/tasks.json")

# Create and save task
task = TaskEntity(
    title="Important Feature",
    estimate=TaskEstimate(optimistic_hours=2, likely_hours=4, pessimistic_hours=8)
)
store.save(task)

# Query tasks
all_tasks = store.list_all()
print(f"Total tasks: {store.count}")

pending = store.list_by_status("pending")
in_progress = store.list_by_status("in_progress")

# Load specific task
loaded = store.load(str(task.id))

# Delete task
store.delete(task.id)

# Clear all
store.clear()
```

#### Persistence Format

```json
{
  "version": "1.0",
  "updated_at": "2026-03-17T12:00:00+00:00",
  "task_count": 1,
  "tasks": {
    "550e8400-e29b-41d4-a716-446655440000": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Important Feature",
      "description": "",
      "status": "pending",
      "priority": "normal",
      "estimate": {
        "optimistic_hours": 2.0,
        "likely_hours": 4.0,
        "pessimistic_hours": 8.0,
        "confidence": 0.5
      },
      "tags": [],
      "metadata": {},
      "parent_id": null,
      "children_ids": [],
      "dependency_ids": [],
      "created_at": "2026-03-17T12:00:00+00:00"
    }
  }
}
```

---

## Advanced Usage

### Event-Driven Audit Trail

```python
from orchestrator.tasks.entity import TaskEntity
from orchestrator.domain.events import EventCollector

# All task operations emit events
task = TaskEntity(title="Eventful Task")

task.start()  # Emits TaskStatusChanged
task.add_child(TaskEntity(title="Subtask"))  # Emits TaskDecomposed
task.complete()  # Emits TaskCompleted

# Drain events for audit log
events = task.drain_events()

for event in events:
    print(f"{event.event_type} at {event.timestamp.isoformat()}")
    if hasattr(event, 'task_id'):
        print(f"  Task: {event.task_id}")
    if hasattr(event, 'old_status'):
        print(f"  {event.old_status} → {event.new_status}")
```

### Dependency Graph Analysis

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority
import uuid

# Create tasks
task_a = TaskEntity(title="Setup Database")
task_b = TaskEntity(title="Create Models")
task_c = TaskEntity(title="Build API")
task_d = TaskEntity(title="Write Tests")

# Create parent with children
project = TaskEntity(title="Backend Project")
project.add_child(task_a)
project.add_child(task_b)
project.add_child(task_c)
project.add_child(task_d)

# Set dependencies (DAG)
task_b.add_dependency(task_a.id)  # Models need database
task_c.add_dependency(task_b.id)  # API needs models
task_d.add_dependency(task_c.id)  # Tests need API

# Analyze
print(f"Valid DAG: {project.validate_dag()}")  # True

# Get execution order
order = project.get_execution_order()
print("Optimal execution order:")
for task_id in order:
    t = project.find_child(task_id)
    print(f"  {t.title}")

# Get critical path
critical = project.get_critical_path()
print(f"Critical path: {len(critical)} tasks")
```

### Batch Analysis

```python
from orchestrator.tasks.complexity import ComplexityAnalyzer

# Analyze multiple task descriptions
analyzer = ComplexityAnalyzer()

tasks_descriptions = [
    ("Fix button color", "Change the submit button to blue"),
    ("Add search", "Implement full-text search with Elasticsearch"),
    ("Migrate database", "Migrate from MySQL to PostgreSQL"),
    ("Build dashboard", "Create admin dashboard with charts and filters"),
]

results = analyzer.batch_analyze([d[1] for d in tasks_descriptions])

for (title, _), result in zip(tasks_descriptions, results):
    print(f"{title}: {result.complexity_level.name} ({result.estimate.expected_hours:.1f}h)")
```

### Custom Task Types

```python
from orchestrator.tasks.entity import TaskEntity
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CodeReviewTask(TaskEntity):
    """Task specifically for code reviews."""
    task_type: str = "code_review"
    files_to_review: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    approval_count: int = 0
    required_approvals: int = 2
    
    def approve(self, reviewer: str):
        if reviewer not in self.reviewers:
            self.reviewers.append(reviewer)
            self.approval_count += 1
            
        if self.approval_count >= self.required_approvals:
            self.complete(result={"approved_by": self.reviewers})
    
    def reject(self, reviewer: str, feedback: str):
        self.fail(Exception(f"Rejected by {reviewer}: {feedback}"))

# Usage
review = CodeReviewTask(
    title="Review Authentication PR",
    files_to_review=["auth.py", "test_auth.py"],
    required_approvals=2
)

review.start()
review.approve("alice")
review.approve("bob")
# Automatically completes when approval_count >= required_approvals
```

---

## Best Practices

### 1. Always Set Estimates

```python
# Good: Task with estimate
task = TaskEntity(
    title="Build feature",
    estimate=TaskEstimate(optimistic_hours=2, likely_hours=4, pessimistic_hours=8)
)

# Avoid: Task without estimate
# decomposition will skip trivial tasks
task = TaskEntity(title="Build feature")  # No estimate
```

### 2. Use Meaningful Descriptions

```python
# Good: Detailed description
task = TaskEntity(
    title="Implement caching",
    description="""
    Add Redis caching layer for user sessions:
    - Cache session data with TTL of 24 hours
    - Implement cache invalidation on logout
    - Add fallback to database on cache miss
    - Include metrics for cache hit/miss ratio
    """
)

# Avoid: Vague description
task = TaskEntity(title="Implement caching", description="Add caching")
```

### 3. Decompose Before Starting

```python
# Good: Decompose first, then work
task = TaskEntity(title="Build microservice", estimate=...)
decomposer.decompose(task)  # Creates children
task.start()  # Now start the parent

# Work on children in order
for child in task.children:
    if child.status == "pending":
        child.start()
        # ... do work ...
        child.complete()
```

### 4. Check Health Regularly

```python
from orchestrator.recovery.health import HealthScorer

scorer = HealthScorer()

# Check before each work session
health = scorer.score_task(task)

if health.status == "critical":
    print("⚠️ Task at risk!")
    for rec in health.recommendations:
        print(f"  Action: {rec}")
elif health.status == "warning":
    print("⚡ Task needs attention")
```

### 5. Save Progress Frequently

```python
from orchestrator.storage.json_store import JsonStore

store = JsonStore("tasks.json")

# Save after each significant change
task.start()
store.save(task)

task.children[0].complete()
store.save(task)

# Use checkpoint for long operations
from orchestrator.recovery.checkpoint import CheckpointMixin
```

### 6. Validate Dependencies

```python
# Always validate before execution
task.add_dependency(other_task.id)

if not task.validate_dag():
    print("⚠️ Circular dependency detected!")
    # Fix the issue...

order = task.get_execution_order()  # Raises if cycles exist
```

---

## Troubleshooting

### Issue: Decomposition Returns 0 Subtasks

**Cause:** Task complexity is "trivial" or "simple", or no estimate is set.

**Solution:**
```python
# Add an estimate with higher hours
task.estimate = TaskEstimate(optimistic_hours=4, likely_hours=8, pessimistic_hours=16)

# Then decompose
result = decomposer.decompose(task)
```

### Issue: Invalid State Transition

**Cause:** Attempting transition that's not allowed.

**Solution:**
```python
from orchestrator.domain.states import TransitionError

try:
    task.complete()  # Can't complete from "pending"
except TransitionError as e:
    print(f"Error: {e}")
    print(f"Allowed: {task._state.allowed_transitions()}")
    # Correct path: pending → in_progress → completed
```

### Issue: Circular Dependency

**Cause:** Task dependencies form a cycle.

**Solution:**
```python
# Validate before adding dependencies
task_a.add_dependency(task_b.id)
task_b.add_dependency(task_a.id)  # Creates cycle!

if not project.validate_dag():
    # Find and remove cycle
    for child in project.children:
        if child.id in child.get_dependency_ids():
            # Self-reference found
            pass
```

### Issue: Module Not Found

**Cause:** Python path not set correctly.

**Solution:**
```python
# In scripts, add parent directory to path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from orchestrator.tasks.entity import TaskEntity
```

### Issue: Task Not Loading from Storage

**Cause:** Task starts in "pending" state after load (by design).

**Solution:**
```python
# Loaded tasks start in "pending" regardless of saved state
# Use the stored status to restore manually:
loaded = store.load(task_id)
# If you need to restore state, use checkpoints or custom logic
```

---

## Reference

### TaskEntity Methods

| Method | Description |
|--------|-------------|
| `start()` | Transition to `in_progress` |
| `complete(result)` | Transition to `completed` |
| `fail(error)` | Transition to `failed` |
| `pause()` | Transition to `paused` |
| `resume()` | Transition from `paused` to `in_progress` |
| `block(reason)` | Transition to `blocked` |
| `unblock()` | Transition from `blocked` to `in_progress` |
| `cancel(reason)` | Transition to `cancelled` |
| `mark_ready()` | Transition from `pending` to `ready` |
| `add_child(task)` | Add subtask |
| `find_child(id)` | Find subtask by ID (recursive) |
| `flatten()` | Get all tasks in hierarchy |
| `add_dependency(id)` | Add dependency |
| `validate_dag()` | Check for cycles |
| `get_execution_order()` | Topological sort |
| `get_critical_path()` | Longest path |
| `get_progress()` | Progress summary |
| `health_score()` | Task health (0-1) |
| `drain_events()` | Get and clear events |

### TaskEstimate Properties

| Property | Formula | Description |
|----------|---------|-------------|
| `expected_hours` | (O + 4L + P) / 6 | PERT expected value |
| `standard_deviation` | (P - O) / 6 | PERT standard deviation |
| `complexity` | Based on hours | TRIVIAL to EXPERT |

### TaskPriority Values

| Value | Use Case |
|-------|----------|
| `BLOCKER` | Must fix now, blocks everything |
| `CRITICAL` | Must complete this sprint |
| `HIGH` | Important, should do soon |
| `NORMAL` | Regular priority |
| `LOW` | Nice to have |
| `BACKGROUND` | Do when free |

### TaskStatus Values

| Status | Terminal | Description |
|--------|----------|-------------|
| `pending` | No | Not started |
| `ready` | No | Dependencies satisfied |
| `in_progress` | No | Currently working |
| `blocked` | No | Waiting on something |
| `paused` | No | Temporarily stopped |
| `completed` | Yes | Successfully finished |
| `failed` | Yes | Did not complete |
| `cancelled` | Yes | Abandoned |

### ComplexityAnalyzer Results

| Field | Type | Description |
|-------|------|-------------|
| `word_count` | int | Words in description |
| `technical_term_count` | int | Technical keywords found |
| `technical_terms_found` | List[str] | Which keywords |
| `capabilities_required` | List[str] | Inferred capabilities |
| `complexity_score` | float | Numeric score |
| `complexity_level` | TaskComplexity | TRIVIAL to EXPERT |
| `estimate` | TaskEstimate | PERT estimate |
| `signals` | List[str] | Complexity modifiers found |
| `risk_factors` | List[str] | Potential issues |

### HealthScorer Results

| Field | Type | Description |
|-------|------|-------------|
| `overall_score` | float | 0.0 to 1.0 |
| `status` | str | "healthy", "warning", "critical" |
| `indicators` | List[HealthIndicator] | Per-dimension scores |
| `recommendations` | List[str] | Actionable suggestions |
| `timestamp` | str | ISO 8601 timestamp |

---

## Quick Reference Card

```python
# Create task
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate

task = TaskEntity(
    title="Build Feature",
    priority=TaskPriority.HIGH,
    estimate=TaskEstimate(2, 4, 8)
)

# Decompose
from orchestrator.tasks.decomposition import TaskDecompositionService

decomposer = TaskDecompositionService()
result = decomposer.decompose(task)

# Start work
task.start()

# Track progress
progress = task.get_progress()
health = HealthScorer().score_task(task)

# Save
from orchestrator.storage.json_store import JsonStore
store = JsonStore("tasks.json")
store.save(task)
```

---

**End of Usage Guide**
