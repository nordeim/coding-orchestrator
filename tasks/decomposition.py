"""
Decomposition service — breaks complex tasks into executable subtasks.

Extracted from TaskDecompositionService. Uses heuristics + templates
to decompose tasks by pattern (microservice, CRUD, UI, security, etc.)
No external dependencies.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from uuid import uuid4

from orchestrator.tasks.entity import TaskEntity, TaskEstimate, TaskPriority
from orchestrator.tasks.complexity import ComplexityAnalyzer, AnalysisResult
from orchestrator.domain.events import EventCollector, TaskDecomposed


# --- Decomposition rules ---

@dataclass
class DecompositionRule:
    """Rule for matching tasks and suggesting decompositions."""
    name: str
    pattern: str               # regex pattern
    description: str
    decompose_fn: Callable     # takes (title, description) → List[dict]
    confidence: float = 0.7

    def matches(self, text: str) -> bool:
        return bool(re.search(self.pattern, text, re.IGNORECASE))


@dataclass
class SubtaskSpec:
    """Specification for a subtask (not yet a TaskEntity)."""
    title: str
    description: str = ""
    priority: str = "normal"
    estimate: Optional[TaskEstimate] = None
    dependencies: List[str] = field(default_factory=list)  # indices of parent subtasks
    metadata: Dict[str, str] = field(default_factory=dict)


def _decompose_microservice(title: str, description: str) -> List[SubtaskSpec]:
    return [
        SubtaskSpec("Design API contract (endpoints, request/response schemas)",
                    priority="high", metadata={"category": "design"}),
        SubtaskSpec("Define data model and database schema",
                    priority="high", metadata={"category": "database"}),
        SubtaskSpec("Implement core business logic / service layer",
                    priority="high", dependencies=["0", "1"], metadata={"category": "backend"}),
        SubtaskSpec("Implement API endpoints with validation",
                    dependencies=["0", "2"], metadata={"category": "backend"}),
        SubtaskSpec("Add authentication and authorization",
                    dependencies=["0"], metadata={"category": "security"}),
        SubtaskSpec("Write unit tests for service layer",
                    dependencies=["2"], metadata={"category": "testing"}),
        SubtaskSpec("Write integration tests for API endpoints",
                    dependencies=["3", "4"], metadata={"category": "testing"}),
        SubtaskSpec("Add logging, metrics, and health checks",
                    dependencies=["3"], metadata={"category": "observability"}),
    ]


def _decompose_crud(title: str, description: str) -> List[SubtaskSpec]:
    return [
        SubtaskSpec("Define entity schema and validation rules",
                    priority="high", metadata={"category": "schema"}),
        SubtaskSpec("Implement repository/data access layer",
                    dependencies=["0"], metadata={"category": "data"}),
        SubtaskSpec("Create endpoint: POST (create)",
                    dependencies=["0", "1"], metadata={"category": "api"}),
        SubtaskSpec("Create endpoint: GET (read/list)",
                    dependencies=["1"], metadata={"category": "api"}),
        SubtaskSpec("Create endpoint: PUT/PATCH (update)",
                    dependencies=["0", "1"], metadata={"category": "api"}),
        SubtaskSpec("Create endpoint: DELETE",
                    dependencies=["1"], metadata={"category": "api"}),
        SubtaskSpec("Add input validation and error handling",
                    dependencies=["2", "3", "4", "5"], metadata={"category": "validation"}),
        SubtaskSpec("Write tests for all CRUD operations",
                    dependencies=["6"], metadata={"category": "testing"}),
    ]


def _decompose_ui(title: str, description: str) -> List[SubtaskSpec]:
    return [
        SubtaskSpec("Design component hierarchy and props interface",
                    priority="high", metadata={"category": "design"}),
        SubtaskSpec("Implement component structure and layout",
                    dependencies=["0"], metadata={"category": "frontend"}),
        SubtaskSpec("Add styling (responsive + accessible)",
                    dependencies=["1"], metadata={"category": "frontend"}),
        SubtaskSpec("Implement state management and data flow",
                    dependencies=["0", "1"], metadata={"category": "frontend"}),
        SubtaskSpec("Add user interactions and event handlers",
                    dependencies=["1", "3"], metadata={"category": "frontend"}),
        SubtaskSpec("Write component tests",
                    dependencies=["2", "4"], metadata={"category": "testing"}),
        SubtaskSpec("Accessibility review and fixes",
                    dependencies=["2", "4"], metadata={"category": "accessibility"}),
    ]


def _decompose_security(title: str, description: str) -> List[SubtaskSpec]:
    return [
        SubtaskSpec("Threat model and requirements analysis",
                    priority="high", metadata={"category": "security"}),
        SubtaskSpec("Design authentication flow",
                    dependencies=["0"], metadata={"category": "security"}),
        SubtaskSpec("Implement authentication (login/register/token)",
                    dependencies=["1"], metadata={"category": "security"}),
        SubtaskSpec("Implement authorization and RBAC",
                    dependencies=["2"], metadata={"category": "security"}),
        SubtaskSpec("Add input sanitization and CSRF/XSS protection",
                    dependencies=["2"], metadata={"category": "security"}),
        SubtaskSpec("Security audit and penetration testing",
                    dependencies=["3", "4"], metadata={"category": "security"}),
        SubtaskSpec("Write security-focused tests",
                    dependencies=["3", "4"], metadata={"category": "testing"}),
    ]


def _decompose_generic(title: str, description: str) -> List[SubtaskSpec]:
    """Generic decomposition for unrecognized patterns."""
    return [
        SubtaskSpec("Requirements analysis and design",
                    priority="high", metadata={"category": "design"}),
        SubtaskSpec("Core implementation",
                    dependencies=["0"], metadata={"category": "implementation"}),
        SubtaskSpec("Edge cases and error handling",
                    dependencies=["1"], metadata={"category": "implementation"}),
        SubtaskSpec("Testing and validation",
                    dependencies=["1", "2"], metadata={"category": "testing"}),
        SubtaskSpec("Documentation",
                    dependencies=["3"], metadata={"category": "docs"}),
    ]


# --- Default rules ---

DEFAULT_RULES: List[DecompositionRule] = [
    DecompositionRule(
        name="microservice",
        pattern=r"microservice|service\s+api|standalone\s+service",
        description="Full microservice with API, data layer, and tests",
        decompose_fn=_decompose_microservice,
        confidence=0.85,
    ),
    DecompositionRule(
        name="crud",
        pattern=r"\bcrud\b|create.*read.*update.*delete|api\s+endpoint",
        description="CRUD operations with data layer",
        decompose_fn=_decompose_crud,
        confidence=0.8,
    ),
    DecompositionRule(
        name="ui_component",
        pattern=r"\bui\b|component|frontend|react|vue|angular|page|screen|form",
        description="UI component with state and styling",
        decompose_fn=_decompose_ui,
        confidence=0.75,
    ),
    DecompositionRule(
        name="security",
        pattern=r"auth|login|security|rbac|permission|oauth|jwt",
        description="Security implementation with auth and protection",
        decompose_fn=_decompose_security,
        confidence=0.8,
    ),
]


# --- Decomposition service ---

@dataclass
class DecompositionResult:
    """Result of task decomposition."""
    parent_task: TaskEntity
    subtask_specs: List[SubtaskSpec]
    rule_used: Optional[DecompositionRule]
    analysis: Optional[AnalysisResult] = None
    confidence: float = 0.0

    @property
    def subtask_count(self) -> int:
        return len(self.subtask_specs)


class TaskDecompositionService:
    """
    Decomposes complex tasks into executable subtask hierarchies.

    Uses pattern matching to select decomposition strategy,
    then creates TaskEntity objects from templates.

    Usage:
        svc = TaskDecompositionService()
        task = TaskEntity(title="Build user management microservice")
        result = svc.decompose(task)
        print(f"Created {result.subtask_count} subtasks")  # 8
        for child in task.children:
            print(f"  - {child.title}")
    """

    def __init__(
        self,
        rules: List[DecompositionRule] = None,
        analyzer: ComplexityAnalyzer = None,
    ):
        self.rules = rules or DEFAULT_RULES
        self.analyzer = analyzer or ComplexityAnalyzer()
        self._events = EventCollector()

    def decompose(self, task: TaskEntity, max_depth: int = 3) -> DecompositionResult:
        """
        Decompose a task into subtasks.

        Args:
            task: The TaskEntity to decompose
            max_depth: Maximum decomposition depth (prevents infinite recursion)

        Returns:
            DecompositionResult with specs and the rule used
        """
        if task.estimate.complexity.value in ("trivial", "simple"):
            return DecompositionResult(
                parent_task=task,
                subtask_specs=[],
                rule_used=None,
                confidence=1.0,
            )

        # Analyze the task
        analysis = self.analyzer.analyze(task.description, task.title)

        # Find matching rule
        text = f"{task.title} {task.description}".lower()
        matched_rule = None
        for rule in self.rules:
            if rule.matches(text):
                matched_rule = rule
                break

        if not matched_rule:
            # Use generic decomposition
            matched_rule = DecompositionRule(
                name="generic",
                pattern="",
                description="Generic task breakdown",
                decompose_fn=_decompose_generic,
                confidence=0.5,
            )

        # Generate subtask specs
        specs = matched_rule.decompose_fn(task.title, task.description)

        # Create TaskEntity children
        spec_to_task: Dict[int, TaskEntity] = {}
        for i, spec in enumerate(specs):
            child = TaskEntity(
                title=spec.title,
                description=spec.description,
                priority=TaskPriority(spec.priority) if spec.priority in [p.value for p in TaskPriority] else TaskPriority.NORMAL,
                estimate=spec.estimate or analysis.estimate if analysis else TaskEstimate(),
                parent_id=task.id,
                tags=[spec.metadata.get("category", "")] if spec.metadata else [],
                metadata=spec.metadata or {},
            )
            spec_to_task[i] = child
            task.add_child(child)

        # Resolve dependency references
        for i, spec in enumerate(specs):
            if spec.dependencies:
                child = spec_to_task[i]
                for dep_idx in spec.dependencies:
                    try:
                        dep_child = spec_to_task.get(int(dep_idx))
                        if dep_child:
                            child.add_dependency(dep_child.id, required=False)
                    except (ValueError, KeyError):
                        pass

        self._events.emit(TaskDecomposed(
            task_id=task.id,
            subtask_count=len(specs),
        ))

        return DecompositionResult(
            parent_task=task,
            subtask_specs=specs,
            rule_used=matched_rule,
            analysis=analysis,
            confidence=matched_rule.confidence,
        )

    def available_rules(self) -> List[str]:
        """List available decomposition rule names."""
        return [r.name for r in self.rules]

    def add_rule(self, rule: DecompositionRule) -> None:
        """Add a custom decomposition rule."""
        self.rules.append(rule)
