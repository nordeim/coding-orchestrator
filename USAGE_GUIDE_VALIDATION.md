# Usage_Guide.md Validation Report

**Generated:** 2026-03-17 10:52 SGT
**Validator:** trusty-pal

---

## Summary

**Overall Status:** ✅ **VALID** — Usage Guide accurately reflects codebase API with minor clarifications needed.

---

## Validation Results

### Imports ✅
All imports in Usage Guide work correctly:
- `TaskEntity, TaskPriority, TaskEstimate` ✓
- `ComplexityAnalyzer` ✓
- `TaskDecompositionService` ✓
- `TemplateRegistry` ✓
- `JsonStore` ✓
- `HealthScorer` ✓
- `CheckpointMixin` ✓
- `StateMachine, task_state_machine` ✓
- `EventCollector` ✓

### Methods ✅
All documented methods exist:
- TaskEntity: start(), complete(), fail(), pause(), resume(), block(), unblock(), cancel(), mark_ready(), add_child(), find_child(), flatten(), add_dependency(), validate_dag(), get_execution_order(), get_critical_path(), get_progress(), health_score(), drain_events()
- HealthScorer: score_task(), score_system()
- ComplexityAnalyzer: analyze(), batch_analyze()
- TaskDecompositionService: decompose(), available_templates(), available_rules(), add_rule()
- StateMachine: transition_to(), allowed_transitions(), can_transition_to()

### Enums ✅
- TaskPriority: BLOCKER, CRITICAL, HIGH, NORMAL, LOW, BACKGROUND
- TaskComplexity: TRIVIAL, SIMPLE, MODERATE, COMPLEX, EXPERT
- TaskStatus: pending, ready, in_progress, blocked, paused, completed, failed, cancelled

### Templates ✅
All 6 templates verified:
- microservice (8 subtasks)
- crud (8 subtasks)
- ui_component (7 subtasks)
- security (7 subtasks)
- api (6 subtasks)
- refactor (6 subtasks)

### Examples ✅
All example files run correctly after fixing basic_usage.py:
- `examples/decompose_task.py` — Works
- `examples/state_machine_demo.py` — Works
- `examples/basic_usage.py` — Fixed (API mismatches corrected)

---

## Issues Found & Fixed

### 1. basic_usage.py API Mismatches ✅ FIXED
**Issue:** Example used wrong attribute names:
- `complexity.estimated_hours` → should be `complexity.estimate.expected_hours`
- `health.score` → should be `health.overall_score`
- `task.progress` → should be `task.get_progress()['progress_pct']`
- `store.path` → attribute doesn't exist

**Fix:** Rewrote basic_usage.py with correct API calls.

### 2. JsonStore Hierarchy Limitation ⚠️ DOCUMENTED
**Finding:** JsonStore saves `children_ids` but does NOT restore child objects automatically. Loaded tasks have 0 children.

**Root Cause:** `_dict_to_task()` stores `_stored_children_ids` but doesn't reconstruct hierarchy. This is intentional design (commented in code).

**Recommendation:** Update Usage Guide Section 7 "Save and Restore" to clarify this limitation and show correct pattern:

```python
# Save parent and all children separately
store.save(task)
for child in task.children:
    store.save(child)

# Restore requires manual reconstruction
loaded = store.load(str(task.id))
for child_id in loaded._stored_children_ids:
    child = store.load(child_id)
    if child:
        loaded.add_child(child)
```

---

## Clarifications Needed in Usage Guide

### Section: "Save and Restore"
Current text:
> "Save and restore task state to JSON files"

Should clarify:
- Only flat tasks are fully restored
- Hierarchical tasks require manual reconstruction
- Task status is NOT restored (deserialized tasks start in "pending" state)

### Section: "Typical Coding Workflow"
Step 7 code example should note:
- Loaded tasks need status restoration via state machine API if resuming work

---

## Validation Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Imports | ✅ | All work correctly |
| Methods | ✅ | All documented methods exist |
| Enums | ✅ | Values match documentation |
| Templates | ✅ | 6 templates, counts accurate |
| Examples | ✅ | All run after fix |
| State Machine | ✅ | Transitions accurate |
| Complexity Analyzer | ✅ | Works as documented |
| Health Scorer | ✅ | Works as documented |
| JsonStore | ⚠️ | Hierarchy limitation needs documentation |
| Decomposition | ✅ | Works as documented |

---

## Recommendations

1. ✅ DONE: Fixed basic_usage.py API mismatches
2. ⚠️ TODO: Update Usage Guide "Save and Restore" section to clarify hierarchy limitation
3. ⚠️ TODO: Add note about status not being restored from JSON

---

**Conclusion:** Usage Guide is **substantially accurate and useful** for sub-agents. The main gap is JsonStore hierarchy handling which needs explicit documentation.
