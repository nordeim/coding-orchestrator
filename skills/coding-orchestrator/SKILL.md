# SKILL.md - Coding Orchestrator

## Overview

The Coding Orchestrator provides intelligent task decomposition and workflow management for software development projects. It extracts patterns from OpenCode's Industrial Orchestrator without infrastructure dependencies (PostgreSQL/Redis/K8s).

## What It Does

- **Task Decomposition**: Breaks complex tasks into manageable subtasks using templates
- **State Management**: Manages task lifecycle with formal state machines
- **Complexity Analysis**: Automatically assesses task complexity
- **Dependency Management**: Handles task dependencies and scheduling
- **Recovery**: Provides checkpoint and health monitoring for failed tasks

## Core Components

### Domain Layer (`domain/`)
- `state_machine.py` — Task state transitions and lifecycle
- `events.py` — Task event definitions
- `exceptions.py` — Custom exceptions for illegal transitions

### Tasks Layer (`tasks/`)
- `entity.py` — TaskEntity with PERT estimates and hierarchy
- `complexity.py` — ComplexityAnalyzer with keyword/capability detection
- `decomposition.py` — TaskDecompositionService with strategies
- `templates.py` — Pre-built templates (microservice, CRUD, UI, API, refactor)

### Recovery Layer (`recovery/`)
- `checkpoint.py` — TaskCheckpoint for state serialization
- `health.py` — HealthScorer for task vitality assessment

### Storage Layer (`storage/`)
- `json_store.py` — JSON storage with UUID string keys

## Installation

```bash
cd /home/pete/.openclaw/workspace/orchestrator
python3 -m pytest tests/ -v  # 119 tests should pass
```

## Quick Start

```python
from tasks.entity import TaskEntity, TaskComplexityLevel
from tasks.decomposition import TaskDecompositionService
from tasks.templates import TemplateRegistry
from tasks.complexity import ComplexityAnalyzer

# Initialize
analyzer = ComplexityAnalyzer()
service = TaskDecompositionService(analyzer, TemplateRegistry)

# Decompose using template
task = TaskEntity(
    title="Create API for user management",
    complexity=TaskComplexityLevel.MEDIUM
)
subtasks = service.decompose(task, strategy="template", template_name="crud")
```

## Available Templates

| Template | Description | Generated Tasks |
|----------|-------------|-----------------|
| `crud` | CRUD feature | 7 subtasks (model, POST, GET, PUT/PATCH, DELETE, validation, tests) |
| `microservice` | Microservice | 5 subtasks (API design, service, database, tests, deployment) |
| `ui_component` | UI component | 6 subtasks (design, logic, styles, events, accessibility, tests) |
| `api` | API endpoint | 6 subtasks (spec, validation, logic, errors, tests, docs) |
| `refactor` | Code refactor | 6 subtasks (analyze, tests, extract interfaces, migrate, validate, docs) |

## Task State Machine

States: `queued` → `accepted` → `executing` → `checkpoint_created` → `awaiting_review` → `completed`
- Recovery from `failed` requires creating a new task
- Invalid transitions raise `IllegalStateTransitionError`

## Examples

Run the examples:

```bash
cd /home/pete/.openclaw/workspace/orchestrator
python3 examples/decompose_task.py
python3 examples/state_machine_demo.py
```

## API Reference

See inline docstrings in each module for full API documentation.

## Success Criteria

- 119/119 tests passing
- All 5 templates functional
- Examples executable
- SKILL.md complete
