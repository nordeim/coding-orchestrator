# Orchestrator Toolkit

A pure-Python orchestration toolkit built from patterns extracted from the OpenCode Industrial Orchestrator.

This toolkit provides:

- **Task Management**: Hierarchical tasks with state machines, dependencies, and progress tracking
- **Complexity Analysis**: Heuristic-based task complexity scoring and capability inference
- **Task Decomposition**: Automatic breakdown of complex tasks into manageable subtasks
- **Persistence**: JSON-based storage for lightweight task persistence
- **Recovery & Health**: Checkpointing, health scoring, and failure recovery mechanisms

## Status

**119 tests passing** | **Zero external dependencies** | **Pure Python 3.12+**

## Documentation

| Document | Purpose |
|----------|---------|
| **[Usage_Guide.md](Usage_Guide.md)** | Comprehensive guide with examples and workflows |
| **[AGENT_BRIEF.md](AGENT_BRIEF.md)** | Single-source-of-truth for AI coding agents |
| [PLAN.md](PLAN.md) | Original extraction plan and design decisions |
| [TODO.md](TODO.md) | Progress tracker |

## Quick Start

```bash
# Run tests
source /opt/venv/bin/activate
python3 -m pytest orchestrator/tests/ -v

# Run examples
python3 orchestrator/examples/decompose_task.py
python3 orchestrator/examples/state_machine_demo.py
python3 orchestrator/examples/basic_usage.py
```

## Usage

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority, TaskEstimate
from orchestrator.tasks.decomposition import TaskDecompositionService

# Create a complex task
task = TaskEntity(
    title="Build user authentication microservice",
    description="Create a standalone microservice with REST API, JWT authentication",
    priority=TaskPriority.HIGH,
    estimate=TaskEstimate(optimistic_hours=8, likely_hours=20, pessimistic_hours=40),
)

# Decompose into subtasks
decomposer = TaskDecompositionService()
result = decomposer.decompose(task)
print(f"Decomposed into {result.subtask_count} subtasks:")
for child in task.children:
    print(f" - {child.title}")
```

## Architecture

```
orchestrator/
├── domain/           # Pure domain logic (zero deps)
│   ├── states.py     # Generic StateMachine with validated transitions
│   ├── events.py     # Domain events (TaskCreated, TaskDecomposed, etc.)
│   └── exceptions.py # Domain-specific error types
│
├── tasks/            # Task management
│   ├── entity.py     # TaskEntity (hierarchy, DAG deps, progress)
│   ├── complexity.py # ComplexityAnalyzer (keyword-based heuristics)
│   ├── decomposition.py # TaskDecompositionService (pattern-based)
│   └── templates.py  # TemplateRegistry (6 templates: microservice, crud, ui_component, security, api, refactor)
│
├── recovery/         # Recovery mechanisms
│   ├── checkpoint.py # CheckpointMixin for resume-from-failure
│   └── health.py     # HealthScorer for task/system health
│
├── storage/          # Persistence
│   └── json_store.py # JsonStore for file-based task storage
│
├── examples/         # Usage demos
│   ├── decompose_task.py
│   ├── state_machine_demo.py
│   └── basic_usage.py
│
└── tests/            # Test suite (119 tests)
```

## Key Features

### State Machine

Generic state machine with validated transitions:

```python
from orchestrator.domain.states import task_state_machine

sm = task_state_machine("task-001")
sm.transition_to("in_progress")
sm.transition_to("completed")
assert sm.is_terminal
```

### Task Entity

Hierarchical tasks with dependencies:

```python
from orchestrator.tasks.entity import TaskEntity

task = TaskEntity(title="Build API")
task.add_dependency(other_task.id)
task.start()
task.complete(result={"endpoints": 5})
```

### Decomposition

Pattern-based task breakdown via integrated TemplateRegistry:

| Template | Subtasks | Description |
|----------|----------|-------------|
| **Microservice** | 8 | API contract → data model → business logic → endpoints → auth → tests → observability |
| **CRUD** | 8 | schema → repository → CRUD endpoints → validation → tests |
| **UI Component** | 7 | design → structure → styling → state → interactions → tests → accessibility |
| **Security** | 7 | threat model → auth flow → implementation → RBAC → protection → audit → tests |
| **API** | 6 | specification → validation → business logic → error handling → tests → documentation |
| **Refactor** | 6 | analysis → tests → extract interfaces → migrate → validate → documentation |

```python
from orchestrator.tasks.decomposition import TaskDecompositionService

decomposer = TaskDecompositionService()
print(decomposer.available_templates())  # ['microservice', 'crud', 'ui_component', 'security', 'api', 'refactor']
```

### Health Scoring

Multi-dimensional health evaluation:

```python
from orchestrator.recovery.health import HealthScorer

scorer = HealthScorer()
report = scorer.score_task(task)
print(report.status)  # "healthy", "warning", or "critical"
```

## Testing

```bash
# Run all tests
python3 -m pytest orchestrator/tests/ -v

# Run specific test file
python3 -m pytest orchestrator/tests/test_decomposition.py -v
```

## Design Philosophy

- **Pure Python**: Zero external dependencies beyond standard library
- **Event-Driven**: Domain events for decoupled communication
- **Type Hints**: Full type hinting for IDE support
- **Composable**: Each module works standalone
- **Tested**: Comprehensive test suite (119 tests)

## Origin

Extracted from `/home/project/opencode-industrial-orchestrator/` — a production-grade enterprise system. This toolkit contains the core patterns without the infrastructure (multi-tenancy, PostgreSQL, Redis, FastAPI, etc.).

## License

MIT License
