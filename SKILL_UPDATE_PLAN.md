# SKILL.md Update Plan

## Current State
Two SKILL.md files exist:
1. `/home/pete/.openclaw/workspace/skills/orchestrator-toolkit/SKILL.md` (5,557 bytes, Mar 16)
2. `/home/pete/.openclaw/workspace/orchestrator/skills/coding-orchestrator/SKILL.md` (3,361 bytes, Mar 17)

## Recommended Action
**Consolidate into single authoritative SKILL.md in the expected skills path.**

Target: `/home/pete/.openclaw/workspace/skills/orchestrator-toolkit/SKILL.md`

## Required Updates (from codebase verification)

### 1. Templates (6 total)
| Template | Subtasks | File line refs |
|----------|----------|----------------|
| microservice | 8 | templates.py:190 |
| crud | 8 | templates.py:191 |
| ui_component | 7 | templates.py:192 |
| security | 7 | templates.py:193 |
| api | 6 | templates.py:194 |
| refactor | 6 | templates.py:195 |

### 2. State Machine (task_state_machine)
States: `pending` → `ready` → `in_progress` → `completed/failed/cancelled`
- Also: `blocked`, `paused`
- Terminal: `completed`, `failed`, `cancelled`
- Source: domain/states.py:45-58

### 3. Correct Enum Names
- `TaskComplexity` (not TaskComplexityLevel)
- Values: TRIVIAL, SIMPLE, MODERATE, COMPLEX, EXPERT
- Source: tasks/entity.py:22

### 4. Import Paths
All imports should use `orchestrator.` prefix:
```python
from orchestrator.tasks.entity import TaskEntity, TaskComplexity
from orchestrator.tasks.decomposition import TaskDecompositionService
from orchestrator.tasks.templates import TemplateRegistry
```

### 5. Test Count
119 tests passing (verified 2026-03-17 09:45)

## Action Items
1. [x] Verify actual codebase state
2. [ ] Update skills/orchestrator-toolkit/SKILL.md with correct info
3. [ ] Remove redundant orchestrator/skills/coding-orchestrator/SKILL.md
4. [ ] Verify update reflects current code
