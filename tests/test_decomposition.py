"""
Tests for decomposition service.
"""

import pytest
from orchestrator.tasks.decomposition import (
    TaskDecompositionService, DecompositionRule, SubtaskSpec,
    _decompose_generic, _decompose_microservice, _decompose_crud,
    DEFAULT_RULES,
)
from orchestrator.tasks.entity import TaskEntity, TaskComplexity, TaskEstimate


@pytest.fixture
def service():
    return TaskDecompositionService()


class TestDecompositionRules:

    def test_microservice_matches(self):
        assert any(r.matches("build microservice API") for r in DEFAULT_RULES)

    def test_crud_matches(self):
        assert any(r.matches("implement CRUD endpoints") for r in DEFAULT_RULES)

    def test_ui_matches(self):
        assert any(r.matches("build React component with form") for r in DEFAULT_RULES)

    def test_security_matches(self):
        assert any(r.matches("implement OAuth JWT authentication") for r in DEFAULT_RULES)

    def test_no_match_returns_generic(self, service):
        task = TaskEntity(title="Random complex thing", description="doing something very complicated that takes many hours")
        # Give it a COMPLEX estimate so decomposition isn't skipped
        task.estimate = TaskEstimate(optimistic_hours=3, likely_hours=8, pessimistic_hours=16)
        result = service.decompose(task)
        assert result.rule_used is not None
        assert result.rule_used.name == "generic"


class TestGenericDecomposition:

    def test_generic_returns_five_subtasks(self):
        specs = _decompose_generic("Build feature", "complex implementation")
        assert len(specs) == 5

    def test_generic_has_dependencies(self):
        specs = _decompose_generic("Build feature", "complex")
        # Testing depends on implementation
        assert len(specs[3].dependencies) > 0


class TestMicroserviceDecomposition:

    def test_returns_eight_subtasks(self):
        specs = _decompose_microservice("Build service", "microservice API")
        assert len(specs) == 8

    def test_has_api_contract_first(self):
        specs = _decompose_microservice("Build service", "microservice API")
        assert "API" in specs[0].title or "api" in specs[0].title

    def test_has_testing_subtasks(self):
        specs = _decompose_microservice("Build service", "microservice API")
        categories = [s.metadata.get("category") for s in specs]
        assert "testing" in categories


class TestTaskDecompositionService:

    def test_decompose_microservice(self, service):
        task = TaskEntity(
            title="Build user management microservice",
            description="Full microservice with REST API and database",
        )
        task.estimate = TaskEstimate(optimistic_hours=3, likely_hours=8, pessimistic_hours=16)

        result = service.decompose(task)
        assert result.subtask_count >= 5
        assert len(task.children) >= 5
        assert task.children[0].parent_id == task.id

    def test_decompose_crud(self, service):
        task = TaskEntity(
            title="Build CRUD API endpoints for products",
            description="Create, read, update, delete product entities",
        )
        task.estimate = TaskEstimate(optimistic_hours=2, likely_hours=5, pessimistic_hours=10)

        result = service.decompose(task)
        assert result.subtask_count >= 5
        assert result.rule_used is not None
        assert result.rule_used.name == "crud"

    def test_decompose_ui(self, service):
        task = TaskEntity(
            title="Build React dashboard component",
            description="Frontend page with charts and data display",
        )
        task.estimate = TaskEstimate(optimistic_hours=2, likely_hours=5, pessimistic_hours=10)

        result = service.decompose(task)
        assert result.subtask_count >= 5
        categories = [c.metadata.get("category") for c in task.children]
        assert "frontend" in categories or "design" in categories

    def test_decompose_security(self, service):
        task = TaskEntity(
            title="Implement OAuth authentication system",
            description="JWT-based auth with RBAC permissions",
        )
        task.estimate = TaskEstimate(optimistic_hours=3, likely_hours=8, pessimistic_hours=16)

        result = service.decompose(task)
        assert result.subtask_count >= 5
        assert result.rule_used.name == "security"

    def test_skips_trivial_tasks(self, service):
        task = TaskEntity(title="Fix typo in docs")
        # Estimate is TRIVIAL by default (0 hours)
        result = service.decompose(task)
        assert result.subtask_count == 0

    def test_subtask_dependencies_resolved(self, service):
        task = TaskEntity(
            title="Build user microservice with database",
            description="Microservice implementation",
        )
        task.estimate = TaskEstimate(optimistic_hours=3, likely_hours=8, pessimistic_hours=16)

        result = service.decompose(task)
        # Some children should have dependencies on sibling tasks
        deps_count = sum(1 for c in task.children if c.dependencies)
        assert deps_count > 0

    def test_confidence_score(self, service):
        task = TaskEntity(
            title="Build CRUD API endpoints",
            description="Standard CRUD operations",
        )
        task.estimate = TaskEstimate(optimistic_hours=2, likely_hours=5, pessimistic_hours=10)

        result = service.decompose(task)
        assert 0.0 < result.confidence <= 1.0

    def test_available_rules(self, service):
        rules = service.available_rules()
        assert "microservice" in rules
        assert "crud" in rules
        assert "ui_component" in rules
        assert "security" in rules

    def test_custom_rule(self, service):
        def custom_decompose(title, desc):
            return [SubtaskSpec("Custom step 1"), SubtaskSpec("Custom step 2")]

        service.add_rule(DecompositionRule(
            name="custom_pattern",
            pattern=r"custom\s+task",
            description="My custom decomposition",
            decompose_fn=custom_decompose,
        ))

        task = TaskEntity(
            title="Custom task implementation",
            description="Something special",
        )
        task.estimate = TaskEstimate(optimistic_hours=1, likely_hours=3, pessimistic_hours=6)

        result = service.decompose(task)
        assert result.rule_used.name == "custom_pattern"
        assert result.subtask_count == 2

    def test_decomposition_event_emitted(self, service):
        task = TaskEntity(
            title="Build CRUD endpoints for users",
            description="Full CRUD API",
        )
        task.estimate = TaskEstimate(optimistic_hours=2, likely_hours=5, pessimistic_hours=10)

        service.decompose(task)
        events = service._events.drain()
        assert len(events) >= 1
        assert events[0].event_type == "TaskDecomposed"
