# GEMINI.md — High-Fidelity Agent /init Briefing

> **Project:** Orchestrator Toolkit
> **Mode:** Elite / Meticulous / Avant-Garde
> **System:** Pure-Python 3.12+ (Zero External Dependencies)
> **Baseline:** 119/119 Tests Passing ✅

---

## ✦ The Meticulous Approach

As an elite coding agent, you operate under the **Standard Operating Procedure (SOP)**. Every directive must pass through these phases:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ANALYZE         Deep, multi-dimensional requirement mining   │
│        ↓          — never surface-level assumptions            │
│                                                                 │
│   PLAN            Structured execution roadmap presented       │
│        ↓          — with phases, checklists, decision points   │
│                                                                 │
│   VALIDATE        Explicit confirmation checkpoint             │
│        ↓          — before a single line of code is written    │
│                                                                 │
│   IMPLEMENT       Modular, tested, documented builds           │
│        ↓          — library-first, bespoke styling             │
│                                                                 │
│   VERIFY          Rigorous QA against success criteria         │
│        ↓          — edge cases, accessibility, performance     │
│                                                                 │
│   DELIVER         Complete handoff with knowledge transfer     │
│                   — nothing left ambiguous                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Project Soul & Architecture

The Orchestrator Toolkit is a lightweight extraction of the core orchestration patterns from the OpenCode Industrial Orchestrator. It is a single-user, zero-dependency toolkit for managing complex hierarchical workflows.

### 🏗️ File Structure
```
orchestrator/
├── domain/           # 🧠 Pure Domain Logic
│   ├── states.py     # Generic StateMachine (Validated Transitions)
│   ├── events.py     # Event-Driven Audit Trail
│   └── exceptions.py # Centralized Domain Errors
├── tasks/            # 📋 Task Management
│   ├── entity.py     # TaskEntity (Hierarchy, DAG Deps, PERT)
│   ├── complexity.py # ComplexityAnalyzer (Keyword Heuristics)
│   ├── decomposition.py # TaskDecompositionService (Pattern-based)
│   └── templates.py  # TemplateRegistry (6 Pre-built Templates)
├── recovery/         # 🔄 Reliability
│   ├── checkpoint.py # CheckpointMixin (Resume-from-failure)
│   └── health.py     # HealthScorer (Vitality Monitoring)
└── storage/          # 💾 Persistence
    └── json_store.py # JsonStore (Atomic File Storage)
```

---

## 🛠️ Technical Truths & Guardrails (CRITICAL)

You must strictly adhere to the following implementation details validated against the codebase:

### 1. Task Decomposition Logic
*   **Skip Guard**: `TaskDecompositionService` **skips** any task with an estimate of `TRIVIAL` (< 0.25h) or `SIMPLE` (< 1h). 
*   **Init Requirement**: You MUST run the `ComplexityAnalyzer` OR manually set a non-trivial `TaskEstimate` before calling `decompose()`, otherwise it will return 0 subtasks.
*   **Templates (6)**: Aligned with `TemplateRegistry`:
    | Pattern | Subtasks | Focus |
    | :--- | :--- | :--- |
    | `microservice` | 8 | API, Data Model, Service Layer, Auth, Tests |
    | `crud` | 8 | Schema, Repository, POST/GET/PUT/DELETE, Tests |
    | `ui_component` | 7 | Design, Structure, Styling, State, Interaction, Tests |
    | `security` | 7 | Threat Model, Auth Flow, RBAC, Sanitization, Audit |
    | `api` | 6 | Specification, Validation, Logic, Errors, Tests, Docs |
    | `refactor` | 6 | Analysis, Safety Tests, Extraction, Migration, Validation |

### 2. State Machine Integrity
*   **Validated Transitions Only**: You cannot skip states (e.g., `pending` -> `completed` is forbidden).
*   **Task Path**: `pending` -> `ready` -> `in_progress` -> `completed`/`failed`/`cancelled`.
*   **Terminality**: Once in a terminal state, the machine is locked.

### 3. Storage & Persistence Constraints
*   **Status Reset**: `JsonStore` does **NOT** restore task status. Every loaded task starts as `"pending"`.
*   **Flat Reconstruction**: `JsonStore` performs a shallow load. It populates `_stored_children_ids` but does not re-hydrate the `children` object list automatically. You must manually reconstruct hierarchies if needed.

---

## 🚀 Validated "/init" Quick Start

```python
from orchestrator.tasks.entity import TaskEntity, TaskPriority
from orchestrator.tasks.complexity import ComplexityAnalyzer
from orchestrator.tasks.decomposition import TaskDecompositionService

# 1. Initialize
task = TaskEntity(
    title="Build user authentication microservice",
    description="OAuth2 + JWT with PostgreSQL",
    priority=TaskPriority.HIGH
)

# 2. Analyze (MANDATORY for decomposition)
analyzer = ComplexityAnalyzer()
task.estimate = analyzer.analyze(task.description, task.title).estimate

# 3. Decompose
decomposer = TaskDecompositionService()
result = decomposer.decompose(task)

# 4. Verify
print(f"Subtasks: {result.subtask_count}") # Returns 8 for microservice
```

---

## ✅ Quality Assurance Checklist

- [ ] All code changes are verified with `python3 -m pytest orchestrator/tests/`.
- [ ] No external libraries (e.g., Pydantic, NetworkX) are introduced.
- [ ] Type hints are strictly applied to all method signatures.
- [ ] Hierarchy reconstruction is handled manually after `JsonStore.load()`.
- [ ] State transitions are checked via `sm.can_transition_to()` before execution.

**Mode:** Elite / Meticulous. Proceed with precision.
