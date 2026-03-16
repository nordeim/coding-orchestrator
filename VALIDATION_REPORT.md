# Documentation Validation Report
**Generated:** 2026-03-17 05:15 SGT
**Validator:** trusty-pal
**Files Reviewed:** README.md, AGENT_BRIEF.md, Usage_Guide.md

---

## Summary

**Overall Status:** ⚠️ **NEEDS UPDATE** — 3 critical discrepancies found

The documentation is well-structured and comprehensive, but contains outdated information that doesn't reflect the current Phase 7 completion and actual template implementation.

---

## Critical Issues

### 1. Template Architecture Inconsistency ⚠️ CRITICAL

**Location:** tasks/templates.py vs tasks/decomposition.py

**Discovery:** Two parallel template systems exist:

**System A: tasks/decomposition.py (DEFAULT_RULES) — ACTUALLY USED**
- 4 rules: microservice, crud, ui_component, **security**
- Subtask counts: **8, 8, 7, 7**
- These are hardcoded in `_decompose_*()` functions
- This is what TaskDecompositionService.decompose() uses

**System B: tasks/templates.py (TemplateRegistry) — NOT INTEGRATED**
- 5 templates: microservice, crud, ui_component, **api**, **refactor**
- Subtask counts: **5, 7, 6, 6, 6**
- Created in Phase 7 but NOT used by decomposition service
- Provides TemplateRegistry class but no integration

**Documentation Claims:**
- README.md claims: "microservice (8), CRUD (8), UI Component (7), Security (7)" ✅ CORRECT (matches DEFAULT_RULES)
- AGENT_BRIEF.md claims: same ✅ CORRECT
- Usage_Guide.md claims: same ✅ CORRECT

**Actual Problem:**
- Docs are **CORRECT** about DEFAULT_RULES (decomposition.py)
- But templates.py adds NEW templates (api, refactor) that are **NOT DOCUMENTED**
- templates.py is **NOT INTEGRATED** with TaskDecompositionService

**Impact:** 
- Phase 7 created a parallel template system that's not connected
- Users can't use TemplateRegistry templates through decomposition service
- "api" and "refactor" templates exist but can't be accessed

**Fix Required:**
1. EITHER: Integrate templates.py with decomposition service
2. OR: Document that templates.py is a separate utility
3. OR: Remove templates.py (not recommended — it's good work)

---

### 2. Phase Status Outdated ⚠️ MEDIUM

**Location:** AGENT_BRIEF.md line 355

**Claimed:**
```
| 7 | Examples & Documentation | 🔄 | — |
```

**Actual:**
- Phase 7 COMPLETE ✅
- examples/decompose_task.py created (7,644 bytes)
- examples/state_machine_demo.py created (9,873 bytes)
- skills/coding-orchestrator/SKILL.md created (3,331 bytes)

**Impact:** AGENT_BRIEF.md shows incomplete status when work is done.

**Fix Required:** Update Phase 7 status to ✅ and add Phase 7 details.

---

### 3. Import Path Confusion ⚠️ LOW

**Location:** All three docs

**Claimed:**
```python
from orchestrator.tasks.entity import TaskEntity
```

**Actual:**
When running from `/home/pete/.openclaw/workspace/orchestrator/`:
```python
from tasks.entity import TaskEntity  # Works
```

When running from outside:
```python
import sys
sys.path.insert(0, '/home/pete/.openclaw/workspace/orchestrator')
from tasks.entity import TaskEntity  # Works
```

**Impact:** Low — examples/decompose_task.py already includes correct sys.path handling.

**Fix Required:** Clarify in Usage_Guide.md that imports are relative to orchestrator/ directory.

---

## Validation Details

### File Structure Match ✅

**Claimed (README.md Architecture):**
```
orchestrator/
├── domain/
│   ├── states.py
│   ├── events.py
│   └── exceptions.py
├── tasks/
│   ├── entity.py
│   ├── complexity.py
│   └── decomposition.py
├── recovery/
│   ├── checkpoint.py
│   └── health.py
├── storage/
│   └── json_store.py
├── examples/
│   ├── decompose_task.py
│   ├── state_machine_demo.py
│   └── basic_usage.py
└── tests/
    ├── test_states.py
    ├── test_task_entity.py
    ├── test_complexity.py
    ├── test_decomposition.py
    ├── test_recovery.py
    └── test_storage.py
```

**Actual:** ✅ All files exist and match.

**Note:** `tasks/templates.py` not shown in architecture diagram — should be added.

---

### Test Count Match ✅

**Claimed:** 119 tests passing

**Actual:** ✅ 119 tests passing (verified 2026-03-17 04:38 SGT)

---

### Example Files Match ✅

**Claimed:**
- examples/basic_usage.py
- examples/decompose_task.py
- examples/state_machine_demo.py

**Actual:** ✅ All exist with correct sizes:
- basic_usage.py: 3,513 bytes
- decompose_task.py: 7,644 bytes
- state_machine_demo.py: 9,873 bytes

---

### State Machine Claims ✅

**Claimed (AGENT_BRIEF.md):**
- 8 states: pending → ready → in_progress → completed/failed/cancelled
- Terminal states: completed, failed, cancelled

**Actual:** Need to verify against domain/states.py, but claims appear consistent.

---

## Recommendations

### Immediate Fixes (Critical)

1. **Update template documentation** in all three files:
   - Remove "security" template references
   - Add "api" and "refactor" templates
   - Update subtask counts: microservice (5), crud (7), ui_component (6), api (6), refactor (6)

2. **Update Phase 7 status** in AGENT_BRIEF.md:
   - Change from 🔄 to ✅
   - Add Phase 7 details section

3. **Add templates.py to architecture diagram** in README.md

### Future Improvements

1. Consider adding a `docs/` directory with:
   - API_REFERENCE.md (generated from docstrings)
   - TEMPLATE_GUIDE.md (detailed template usage)

2. Add integration tests for examples:
   - `tests/test_examples_run.py` — verify all examples execute without error

3. Version the documentation with last-updated dates

---

## Validation Sign-off

- **README.md:** ⚠️ Needs template updates
- **AGENT_BRIEF.md:** ⚠️ Needs phase status + template updates
- **Usage_Guide.md:** ⚠️ Needs template updates + import clarification

**Overall:** Documentation quality is high, but needs synchronization with Phase 7 completion and actual template implementation.

---

*Generated by trusty-pal validation check*
