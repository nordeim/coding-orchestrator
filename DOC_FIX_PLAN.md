# Documentation Fix Plan
**Created:** 2026-03-17 05:30 SGT
**Status:** READY FOR EXECUTION

---

## Executive Summary

After re-validation against source code, the findings are:

1. **DEFAULT_RULES in decomposition.py** — 4 rules (microservice, crud, ui_component, security) — THIS IS WHAT THE DOCS DESCRIBE ✅
2. **templates.py (Phase 7)** — 5 templates (microservice, crud, ui_component, api, refactor) — NOT INTEGRATED, NOT DOCUMENTED ⚠️
3. **State machine claims** — 8 states, 3 terminal — CORRECT ✅
4. **Phase 7 status** — Needs updating from 🔄 to ✅

**The docs are mostly correct**, but need:
- Phase 7 status update
- templates.py integration decision
- Architecture diagram update

---

## Detailed Findings

### 1. Template System Analysis

#### System A: decomposition.py DEFAULT_RULES (ACTIVE)

| Rule | Subtasks | Source |
|------|----------|--------|
| microservice | 8 | `_decompose_microservice()` |
| crud | 8 | `_decompose_crud()` |
| ui_component | 7 | `_decompose_ui()` |
| security | 7 | `_decompose_security()` |

**Status:** ✅ Used by TaskDecompositionService.decompose()

#### System B: templates.py TemplateRegistry (INACTIVE)

| Template | Subtasks | Status |
|----------|----------|--------|
| microservice | 5 | Duplicate of System A (different count!) |
| crud | 7 | Duplicate of System A (different count!) |
| ui_component | 6 | Duplicate of System A (different count!) |
| api | 6 | NEW — not in DEFAULT_RULES |
| refactor | 6 | NEW — not in DEFAULT_RULES |

**Status:** ⚠️ Created in Phase 7, but NOT integrated with decomposition service

**Problem:** Two systems for the same task, with different subtask counts for overlapping templates!

---

### 2. Documentation Accuracy

| Claim | Source | Accuracy |
|-------|--------|----------|
| 4 templates: microservice/crud/ui_component/security | README.md, AGENT_BRIEF.md, Usage_Guide.md | ✅ CORRECT (matches DEFAULT_RULES) |
| Subtask counts: 8, 8, 7, 7 | All three docs | ✅ CORRECT (matches DEFAULT_RULES) |
| 8 task states | AGENT_BRIEF.md | ✅ CORRECT |
| Terminal: completed/failed/cancelled | AGENT_BRIEF.md | ✅ CORRECT |
| Phase 7 incomplete (🔄) | AGENT_BRIEF.md line 355 | ⚠️ OUTDATED (should be ✅) |

---

### 3. Architecture Diagram

**Current (README.md):**
```
orchestrator/
├── domain/
│   ├── states.py
│   ├── events.py
│   └── exceptions.py
├── tasks/
│   ├── entity.py
│   ├── complexity.py
│   └── decomposition.py  ← Missing templates.py!
```

**Should include:** `tasks/templates.py`

---

## Fix Plan

### Option A: Integrate templates.py (Recommended)

**Pros:**
- Preserves Phase 7 work
- Adds valuable templates (api, refactor)
- Provides cleaner TemplateRegistry API

**Cons:**
- Requires code changes to decomposition.py
- Need to reconcile subtask count differences

**Changes Required:**

#### 1. Update decomposition.py to use TemplateRegistry

```python
# In decomposition.py, add:
from tasks.templates import TemplateRegistry

# Modify decompose() to check TemplateRegistry first:
def decompose(self, task: TaskEntity, max_depth: int = 3) -> DecompositionResult:
    # ... existing code ...
    
    # Check TemplateRegistry first
    template = TemplateRegistry.get_template(matched_rule.name)
    if template:
        # Use template function
        subtasks = template(task)
        # ... create TaskEntity from subtasks ...
    else:
        # Fall back to DEFAULT_RULES decompose_fn
        specs = matched_rule.decompose_fn(task.title, task.description)
```

#### 2. Reconcile subtask counts

Either:
- Update templates.py to match DEFAULT_RULES counts
- OR: Update DEFAULT_RULES to match templates.py counts
- OR: Keep both, document differences

#### 3. Add missing templates to TemplateRegistry

```python
# In templates.py, add:
def security_template(task: TaskEntity) -> List[TaskEntity]:
    # Match _decompose_security from decomposition.py
    ...
```

---

### Option B: Document Separation (Minimal)

**Pros:**
- No code changes
- Docs remain mostly correct

**Cons:**
- Confusion about which system to use
- templates.py remains unused

**Changes Required:**

#### 1. Add note to README.md

```markdown
## Templates

### Built-in Rules (DEFAULT_RULES)
Used by TaskDecompositionService:
- microservice (8 subtasks)
- crud (8 subtasks)
- ui_component (7 subtasks)
- security (7 subtasks)

### TemplateRegistry (tasks/templates.py)
Standalone template system for manual decomposition:
- microservice (5 subtasks)
- crud (7 subtasks)
- ui_component (6 subtasks)
- api (6 subtasks)
- refactor (6 subtasks)

> **Note:** TemplateRegistry is not integrated with TaskDecompositionService.
```

---

### Option C: Remove templates.py (Not Recommended)

**Pros:**
- Eliminates confusion

**Cons:**
- Loses Phase 7 work
- Loses valuable templates (api, refactor)

---

## Recommended Path

**Execute Option A** — Integrate templates.py:

1. Add security_template to templates.py
2. Update decomposition.py to use TemplateRegistry
3. Reconcile subtask counts (use templates.py counts as they're cleaner)
4. Update all docs to reflect unified template system
5. Update Phase 7 status to ✅

---

## Immediate Fixes (Phase 7 Status)

Regardless of Option chosen, update AGENT_BRIEF.md:

**Current:**
```markdown
| 7 | Examples & Documentation | 🔄 | — |
```

**Fixed:**
```markdown
| 7 | Examples & Documentation | ✅ | 3 examples + SKILL.md |
```

---

## Execution Checklist

- [ ] Decision: Option A, B, or C?
- [ ] If A: Modify decomposition.py
- [ ] If A: Add security_template to templates.py
- [ ] If A: Reconcile subtask counts
- [ ] Update README.md architecture diagram
- [ ] Update AGENT_BRIEF.md Phase 7 status
- [ ] Update template documentation in all three docs
- [ ] Run tests to verify nothing breaks
- [ ] Commit changes

---

*Plan created by trusty-pal — awaiting user decision*
