# Coding Orchestration Scaffold — Extraction Plan

> **Source:** `/home/project/opencode-industrial-orchestrator/`
> **Target:** `/home/pete/.openclaw/workspace/orchestrator/`
> **Date:** 2026-03-16
> **Philosophy:** Extract the brains, dump the infrastructure. Pure Python, no external services.

---

## What We're Extracting (and Why)

### 1. State Machine (`SessionStatus`)
**Source:** `domain/value_objects/session_status.py`
**Why:** Clean validated transitions with 12 states, terminal/active/error categorization, retry support (`FAILED → PENDING`, `TIMEOUT → PENDING`), visual properties (emoji, color codes).
**Adaptation:** Strip `str` enum, keep transition map. Make generic for any entity.

### 2. Task Entity + Decomposition
**Source:** `domain/entities/task.py`, `application/services/task_decomposition_service.py`
**Why:** This is the real value. Hierarchical task decomposition with:
- Complexity analysis (word count, technical terms, capability inference)
- Dependency DAG with cycle detection (NetworkX)
- Critical path calculation
- Multiple decomposition strategies (functional, temporal, capability)
- Template-based decomposition (microservice, CRUD, UI, security patterns)
- Progress tracking with PERT estimates
**Adaptation:** Drop `tenant_id`, drop `session_id` coupling. Make standalone. Replace Pydantic with dataclasses (or keep Pydantic v2 — it's fine). Drop NetworkX dependency for lighter impl.

### 3. Checkpoint Recovery
**Source:** `domain/entities/session.py` (add_checkpoint, get_latest_checkpoint, is_recoverable)
**Why:** Essential for long-running coding tasks that survive interruptions.
**Adaptation:** Extract into a mixin or standalone class.

### 4. Health Scoring
**Source:** `domain/entities/session.py` (calculate_health_score)
**Why:** Simple but effective elapsed-vs-limit monitoring.
**Adaptation:** Generalize for any timed task.

### 5. Domain Events
**Source:** `domain/events/session_events.py`
**Why:** Lightweight event system for audit trail. Simple Pydantic models.
**Adaptation:** Generalize to generic `TaskEvent` base.

### 6. Complexity Analyzer
**Source:** `application/services/task_decomposition_service.py` (ComplexityAnalyzer)
**Why:** Heuristic analysis of task descriptions — word count, technical term detection, capability inference, PERT estimation. This is useful standalone.
**Adaptation:** Extract as standalone class, keep the keyword-to-capability map.

---

## What We're NOT Extracting

| Dropped | Reason |
|---------|--------|
| Multi-tenancy (`tenant_id`, `Tenant`, RBAC) | Single-user. No teams. |
| EAP (External Agent Protocol) | No external agents to connect |
| Fine-tuning pipeline | Was simulated anyway |
| PostgreSQL repositories | SQLite or JSON files |
| Redis distributed locking | File-based locks or simplified mutex |
| K8s deployment | Docker Compose at most |
| FastAPI presentation layer | CLI or internal API, not web server |
| WebSocket handlers | Not needed for CLI usage |
| OpenCode client adapter | OpenClaw already has session management |
| Dashboard (Next.js) | Terminal-first, not web UI |

---

## Target Structure

```
orchestrator/
├── __init__.py
├── README.md                    # What this is, how to use it
│
├── domain/
│   ├── __init__.py
│   ├── states.py                # Generic state machine (from SessionStatus)
│   ├── events.py                # Domain events (from session_events.py)
│   └── exceptions.py            # Domain exceptions
│
├── tasks/
│   ├── __init__.py
│   ├── entity.py                # TaskEntity (simplified, no tenant_id)
│   ├── complexity.py            # ComplexityAnalyzer (extracted)
│   ├── decomposition.py         # TaskDecompositionService (simplified)
│   └── templates.py             # Decomposition templates
│
├── recovery/
│   ├── __init__.py
│   ├── checkpoint.py            # Checkpoint mixin/manager
│   └── health.py                # Health scoring
│
├── storage/
│   ├── __init__.py
│   └── json_store.py            # Simple JSON file persistence
│
├── examples/
│   ├── decompose_task.py        # Demo: decompose a complex task
│   └── state_machine_demo.py    # Demo: state transitions
│
└── tests/
    ├── __init__.py
    ├── test_states.py
    ├── test_task_entity.py
    ├── test_complexity.py
    ├── test_decomposition.py
    ├── test_checkpoint.py
    └── test_health.py
```

---

## Implementation Order

### Phase 1: Foundation (states + events + exceptions)
1. `domain/states.py` — Generic `StateMachine` with validated transitions
2. `domain/events.py` — Base `DomainEvent` + task-specific events
3. `domain/exceptions.py` — Domain error types
4. `tests/test_states.py` — Test state transitions

### Phase 2: Task Entity
5. `tasks/entity.py` — Core `TaskEntity` with status, priority, complexity, dependencies
6. `tests/test_task_entity.py` — Test entity lifecycle

### Phase 3: Complexity Analysis
7. `tasks/complexity.py` — `ComplexityAnalyzer` (keyword detection, PERT, capability inference)
8. `tests/test_complexity.py` — Test analysis heuristics

### Phase 4: Decomposition
9. `tasks/decomposition.py` — `TaskDecompositionService` with strategies
10. `tasks/templates.py` — Pre-built templates (web service, CRUD, refactoring, security)
11. `tests/test_decomposition.py` — Test decomposition strategies

### Phase 5: Recovery & Health
12. `recovery/checkpoint.py` — `CheckpointMixin` with sequence tracking, recovery logic
13. `recovery/health.py` — `HealthScorer` with elapsed-vs-limit scoring
14. `tests/test_checkpoint.py` — Test checkpoint save/load/recover
15. `tests/test_health.py` — Test health score calculation

### Phase 6: Storage
16. `storage/json_store.py` — Simple JSON file persistence for tasks
17. `README.md` — Documentation

### Phase 7: Examples & Polish
18. `examples/decompose_task.py` — Working demo
19. `examples/state_machine_demo.py` — Working demo
20. Final review and cleanup

---

## Key Design Decisions

1. **Pure Python, minimal deps.** Only `pydantic` v2 (for validation). No NetworkX — implement simple DAG check ourselves.
2. **Dataclass-like entities.** Pydantic `BaseModel` for validation but kept lightweight.
3. **No async.** The original was async for Redis/Postgres. We're file-based, so sync is fine.
4. **Composable.** Each module works standalone. State machine doesn't need tasks. Tasks don't need storage. Storage doesn't need decomposition.
5. **Test-first where possible.** Write test alongside implementation.

---

## Validation Checkpoint

Before implementation, review this plan for:
- [ ] Structure makes sense for single-user CLI tool?
- [ ] Dropped enough fluff?
- [ ] Missing anything critical?
- [ ] File naming clear?
- [ ] Implementation order logical?
