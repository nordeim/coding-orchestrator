# AGENT_BRIEF.md — Single Source of Truth for Coding Agents

> **Project:** Orchestrator Toolkit  
> **Type:** Pure-Python Orchestration Library (Distillation)  
> **Origin:** Extracted from `/home/project/opencode-industrial-orchestrator/`  
> **Last Updated:** 2026-03-17  
> **Test Status:** 119 tests passing ✅

---

## 🎯 Project Purpose

This project is a **lightweight extraction** of the core orchestration patterns from the OpenCode Industrial Orchestrator. The goal is to provide a **zero-dependency, single-user toolkit** for:

1. **Task Management** — Hierarchical tasks with state machines, dependencies, and progress tracking
2. **Complexity Analysis** — Heuristic-based task complexity scoring and capability inference
3. **Task Decomposition** — Automatic breakdown of complex tasks into manageable subtasks
4. **Persistence** — JSON-based storage for lightweight task persistence
5. **Recovery & Health** — Checkpointing, health scoring, and failure recovery mechanisms

**Design Philosophy:** "Extract the brains, dump the infrastructure" — Pure Python, no external services, no multi-tenancy, no databases, no Redis.

---

## 🏗️ Architecture

```
orchestrator/
├── domain/           # 🧠 Pure domain logic (zero external deps)
│   ├── states.py     # Generic StateMachine with validated transitions
│   ├── events.py     # Domain events (TaskCreated, TaskDecomposed, etc.)
│   └── exceptions.py # Domain-specific error types
│
├── tasks/            # 📋 Task management
│   ├── entity.py     # TaskEntity (hierarchy, DAG deps, progress)
│   ├── complexity.py # ComplexityAnalyzer (keyword-based heuristics)
│   └── decomposition.py # TaskDecompositionService (pattern-based)
│
├── recovery/         # 🔄 Recovery mechanisms
│   ├── checkpoint.py # CheckpointMixin for resume-from-failure
│   └── health.py     # HealthScorer for task/system health
│
├── storage/          # 💾 Persistence
│   └── json_store.py # JsonStore for file-based task storage
│
├── examples/         # 📚 Usage demos
│   └── basic_usage.py
│
└── tests/            # ✅ Test suite (119 tests)
    ├── test_states.py
    ├── test_task_entity.py
    ├── test_complexity.py
    ├── test_decomposition.py
    ├── test_recovery.py
    └── test_storage.py
```

---

## 📦 Key Components

### 1. State Machine (`domain/states.py`)

Generic state machine extracted from `SessionStatus`. Supports:

- **Validated transitions** — Only allowed state changes permitted
- **Terminal states** — States with no outgoing transitions
- **History tracking** — Full audit trail of transitions
- **Retry support** — `failed → pending`, `timeout → pending` for recovery

**Pre-built machines:**
- `task_state_machine()` — 8 states (pending → ready → in_progress → completed/failed/cancelled)
- `session_state_machine()` — 12 states (from industrial orchestrator)

```python
from orchestrator.domain.states import StateMachine, task_state_machine

sm = task_state_machine("task-123")
sm.transition_to("in_progress")
sm.transition_to("completed")
assert sm.is_terminal
```

### 2. Task Entity (`tasks/entity.py`)

Core unit of work with:

- **Hierarchy** — Parent/child relationships via `add_child()`, `flatten()`
- **Dependencies** — DAG-based with cycle detection (`validate_dag()`, `get_execution_order()`, `get_critical_path()`)
- **State tracking** — Via embedded StateMachine (`start()`, `complete()`, `fail()`, `pause()`, `block()`)
- **PERT estimates** — `TaskEstimate` with optimistic/likely/pessimistic hours
- **Event emission** — Audit trail via `drain_events()`
- **Health scoring** — `health_score()` method

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate

task = TaskEntity(
    title="Build REST API",
    description="Create a REST API with authentication",
    priority=TaskPriority.HIGH,
    estimate=TaskEstimate(optimistic_hours=2, likely_hours=4, pessimistic_hours=8)
)

task.start()
task.complete(result={"endpoints": 5})
```

### 3. Complexity Analyzer (`tasks/complexity.py`)

Heuristic analysis of task descriptions:

- **Technical keyword detection** — Identifies API, database, auth, etc.
- **Capability inference** — Maps keywords to required skills (backend, frontend, devops)
- **PERT estimation** — Generates time estimates based on complexity
- **Risk factors** — Identifies potential issues

```python
from orchestrator.tasks.complexity import ComplexityAnalyzer

analyzer = ComplexityAnalyzer()
result = analyzer.analyze("Build a real-time chat API with WebSocket support")
print(result.complexity_level)  # TaskComplexity.COMPLEX
print(result.capabilities_required)  # ['backend_api', 'caching']
```

### 4. Task Decomposition (`tasks/decomposition.py`)

Pattern-based task breakdown:

- **Rule matching** — Regex patterns to identify task types
- **Template decomposition** — Pre-built templates for:
  - Microservice (8 subtasks: API contract → data model → business logic → endpoints → auth → tests → observability)
  - CRUD (8 subtasks: schema → repository → CRUD endpoints → validation → tests)
  - UI Component (7 subtasks: design → structure → styling → state → interactions → tests → accessibility)
  - Security (7 subtasks: threat model → auth flow → implementation → RBAC → protection → audit → tests)
- **Dependency resolution** — Automatically sets up subtask dependencies

```python
from orchestrator.tasks.decomposition import TaskDecompositionService

decomposer = TaskDecompositionService()
task = TaskEntity(title="Build user management microservice")
result = decomposer.decompose(task)
print(f"Created {result.subtask_count} subtasks")
```

### 5. Checkpoint Recovery (`recovery/checkpoint.py`)

Mixin for resume-from-failure:

- **Named checkpoints** — `checkpoint("step_name", data)`
- **History tracking** — `get_checkpoint_history()`
- **Restore** — `restore_from_checkpoint(step_index)`
- **Serialization** — `serialize_checkpoints()` / `deserialize_checkpoints()`

```python
from orchestrator.recovery.checkpoint import CheckpointMixin

class MyTask(CheckpointMixin):
    def run(self):
        self.checkpoint("initialized")
        load_config()
        self.checkpoint("config_loaded", {"path": "/etc/app.json"})
        # ... on failure, can restore from last checkpoint
```

### 6. Health Scorer (`recovery/health.py`)

Multi-dimensional health evaluation:

- **State health** — Based on task status
- **Time health** — Elapsed vs estimated time
- **Dependency health** — Are dependencies satisfied?
- **Hierarchy health** — Subtask completion rates

```python
from orchestrator.recovery.health import HealthScorer

scorer = HealthScorer()
report = scorer.score_task(task)
print(report.status)  # "healthy", "warning", or "critical"
print(report.overall_score)  # 0.0 to 1.0
```

### 7. JSON Storage (`storage/json_store.py`)

File-based task persistence:

- **Lazy loading** — Loads from disk on first access
- **Atomic writes** — Safe persistence
- **Hierarchical support** — Stores parent/child relationships
- **Query methods** — `list_all()`, `list_by_status()`

```python
from orchestrator.storage.json_store import JsonStore

store = JsonStore("/tmp/tasks.json")
store.save(task)
loaded = store.load(task.id)
```

---

## 🧪 Testing

**Run all tests:**
```bash
source /opt/venv/bin/activate
python3 -m pytest tests/ -v
```

**Test coverage:**
| Module | Tests | Focus |
|--------|-------|-------|
| `test_states.py` | 19 | State transitions, history, retry |
| `test_task_entity.py` | 27 | Entity lifecycle, hierarchy, DAG, progress |
| `test_complexity.py` | 14 | Keyword detection, capability inference |
| `test_decomposition.py` | 21 | Rule matching, template decomposition |
| `test_recovery.py` | 26 | Checkpoint save/restore, health scoring |
| `test_storage.py` | 12 | JSON persistence, loading, filtering |
| **Total** | **119** | All passing ✅ |

---

## 🚧 What Was Dropped (from Industrial Orchestrator)

| Dropped | Reason |
|---------|--------|
| Multi-tenancy (`tenant_id`, RBAC) | Single-user toolkit |
| EAP (External Agent Protocol) | No external agents |
| PostgreSQL repositories | JSON file storage |
| Redis distributed locking | File-based or simplified |
| FastAPI presentation layer | Library, not web server |
| WebSocket handlers | No real-time updates needed |
| Next.js Dashboard | Terminal-first, not web UI |
| NetworkX dependency | Simplified DAG implementation |

---

## 🔧 Development Conventions

### Code Style
- **Pure Python** — Zero external dependencies beyond standard library
- **Type hints** — Full type hinting for IDE support
- **Dataclasses** — Used for all entities (no Pydantic required)
- **No async** — Synchronous only (no async/await)

### Testing
- **pytest** — Test framework
- **Descriptive names** — `test_<method>_<scenario>_<expected>`
- **One assertion per test** — Clear failure identification

### Imports
```python
# Standard library first
from datetime import datetime
from typing import List, Dict
from uuid import UUID

# Local imports last
from orchestrator.domain.states import StateMachine
```

### File Structure
- Each module has a `__init__.py` for package exports
- Tests mirror source structure in `tests/` directory
- Examples in `examples/` directory

---

## 📝 Common Tasks

### Add a New Decomposition Rule
```python
from orchestrator.tasks.decomposition import DecompositionRule, SubtaskSpec

def _decompose_ml_pipeline(title: str, description: str) -> List[SubtaskSpec]:
    return [
        SubtaskSpec("Data collection and preprocessing"),
        SubtaskSpec("Feature engineering"),
        SubtaskSpec("Model selection and training"),
        SubtaskSpec("Evaluation and validation"),
        SubtaskSpec("Deployment pipeline"),
    ]

rule = DecompositionRule(
    name="ml_pipeline",
    pattern=r"ml|machine learning|model training|pipeline",
    description="ML pipeline with data prep and training",
    decompose_fn=_decompose_ml_pipeline,
    confidence=0.75,
)
```

### Add a New State Machine
```python
from orchestrator.domain.states import StateMachine

def custom_state_machine(entity_id: str = "") -> StateMachine:
    return StateMachine(
        initial="draft",
        transitions={
            "draft": {"review", "cancelled"},
            "review": {"approved", "rejected", "draft"},
            "approved": {"published"},
            "rejected": {"draft", "cancelled"},
            "published": set(),  # terminal
            "cancelled": set(),  # terminal
        },
        entity_id=entity_id,
    )
```

### Add a New Domain Event
```python
# In domain/events.py
@dataclass(frozen=True)
class TaskPaused(DomainEvent):
    task_id: UUID = None
    reason: str = ""
    event_type: str = "TaskPaused"
```

---

## ⚠️ Known Limitations

1. **No concurrent access** — JsonStore is not thread-safe
2. **No state restoration on load** — Deserialized tasks start in "pending" state
3. **Simplified DAG** — Custom implementation, not NetworkX
4. **No distributed locking** — Single-process only

---

## 🔗 Relationship to Parent Project

This toolkit is a **distillation** of `/home/project/opencode-industrial-orchestrator/`. Key extracts:

| Source | Extracted As |
|--------|--------------|
| `domain/value_objects/session_status.py` | `domain/states.py` |
| `domain/entities/task.py` | `tasks/entity.py` |
| `application/services/task_decomposition_service.py` | `tasks/decomposition.py` + `tasks/complexity.py` |
| `domain/entities/session.py` (checkpoints) | `recovery/checkpoint.py` |
| `domain/entities/session.py` (health) | `recovery/health.py` |
| `domain/events/session_events.py` | `domain/events.py` |

---

## 📋 Current Status

**Phase 6 COMPLETE ✅** — All planned phases implemented and tested.

| Phase | Description | Status | Tests |
|-------|-------------|--------|-------|
| 1 | Foundation (states, events, exceptions) | ✅ | 19 |
| 2 | Task Entity | ✅ | 27 |
| 3 | Complexity Analysis | ✅ | 14 |
| 4 | Decomposition | ✅ | 21 |
| 5 | Recovery & Health | ✅ | 26 |
| 6 | Storage | ✅ | 12 |
| 7 | Examples & Documentation | 🔄 | — |

**Next Steps:**
- Complete Phase 7: Documentation polish, more examples
- Consider: Add skill file for AI agent integration

---

## 🚀 Quick Start

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate
from orchestrator.tasks.decomposition import TaskDecompositionService
from orchestrator.storage.json_store import JsonStore

# Create and decompose a complex task
task = TaskEntity(
    title="Build user authentication microservice",
    description="OAuth2 + JWT authentication with refresh tokens",
    priority=TaskPriority.HIGH,
)

decomposer = TaskDecompositionService()
result = decomposer.decompose(task)

print(f"Decomposed into {result.subtask_count} subtasks")
for child in task.children:
    print(f"  - {child.title}")

# Persist
store = JsonStore("tasks.json")
store.save(task)
```

---

> **Remember:** This is a lightweight extraction. The parent project at `/home/project/opencode-industrial-orchestrator/` contains the full enterprise implementation with multi-tenancy, EAP, fine-tuning pipeline, and more.
