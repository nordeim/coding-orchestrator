"""Decomposition Templates for Task Patterns.

Provides pre-built decomposition strategies for common software development tasks.
Integrated with TaskDecompositionService via TemplateRegistry.

Template counts (aligned with decomposition.py DEFAULT_RULES):
- microservice: 8 subtasks
- crud: 8 subtasks
- ui_component: 7 subtasks
- security: 7 subtasks
- api: 6 subtasks (new)
- refactor: 6 subtasks (new)
"""

from typing import List, Dict, Callable, Optional
from orchestrator.tasks.entity import TaskEntity


class TemplateRegistry:
    """Registry of pre-built decomposition templates."""
    
    _templates: Dict[str, Callable[[TaskEntity], List[TaskEntity]]] = {}
    
    @classmethod
    def register(cls, name: str, template_func: Callable[[TaskEntity], List[TaskEntity]]):
        """Register a template function."""
        cls._templates[name] = template_func
    
    @classmethod
    def get_template(cls, name: str) -> Optional[Callable[[TaskEntity], List[TaskEntity]]]:
        """Get a template by name."""
        return cls._templates.get(name)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List all available template names."""
        return list(cls._templates.keys())
    
    @classmethod
    def has_template(cls, name: str) -> bool:
        """Check if a template exists."""
        return name in cls._templates


def microservice_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for implementing a microservice (8 subtasks).
    
    Aligned with decomposition.py _decompose_microservice.
    """
    base_title = task.title.replace("Implement ", "").replace("Create ", "")
    return [
        TaskEntity(title=f"Design API contract for {base_title} (endpoints, request/response schemas)", 
                   metadata={"complexity": "moderate", "category": "design"}),
        TaskEntity(title=f"Define data model and database schema for {base_title}",
                   metadata={"complexity": "moderate", "category": "database"}),
        TaskEntity(title=f"Implement core business logic / service layer for {base_title}",
                   metadata={"complexity": "complex", "category": "backend"}),
        TaskEntity(title=f"Implement API endpoints with validation for {base_title}",
                   metadata={"complexity": "moderate", "category": "backend"}),
        TaskEntity(title=f"Add authentication and authorization to {base_title}",
                   metadata={"complexity": "complex", "category": "security"}),
        TaskEntity(title=f"Write unit tests for {base_title} service layer",
                   metadata={"complexity": "moderate", "category": "testing"}),
        TaskEntity(title=f"Write integration tests for {base_title} API endpoints",
                   metadata={"complexity": "moderate", "category": "testing"}),
        TaskEntity(title=f"Add logging, metrics, and health checks for {base_title}",
                   metadata={"complexity": "simple", "category": "observability"}),
    ]


def crud_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for CRUD feature implementation (8 subtasks).
    
    Aligned with decomposition.py _decompose_crud.
    """
    base_title = task.title.replace("Implement ", "").replace("Create ", "").replace("CRUD for ", "")
    return [
        TaskEntity(title=f"Define entity schema and validation rules for {base_title}",
                   metadata={"complexity": "simple", "category": "schema"}),
        TaskEntity(title=f"Implement repository/data access layer for {base_title}",
                   metadata={"complexity": "moderate", "category": "data"}),
        TaskEntity(title=f"Create {base_title} POST endpoint (create)",
                   metadata={"complexity": "simple", "category": "api"}),
        TaskEntity(title=f"Create {base_title} GET endpoints (read/list)",
                   metadata={"complexity": "simple", "category": "api"}),
        TaskEntity(title=f"Create {base_title} PUT/PATCH endpoint (update)",
                   metadata={"complexity": "simple", "category": "api"}),
        TaskEntity(title=f"Create {base_title} DELETE endpoint",
                   metadata={"complexity": "simple", "category": "api"}),
        TaskEntity(title=f"Add input validation and error handling for {base_title}",
                   metadata={"complexity": "moderate", "category": "validation"}),
        TaskEntity(title=f"Write tests for all {base_title} CRUD operations",
                   metadata={"complexity": "moderate", "category": "testing"}),
    ]


def ui_component_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for UI component development (7 subtasks).
    
    Aligned with decomposition.py _decompose_ui.
    """
    base_title = task.title.replace("Build ", "").replace("Create ", "")
    return [
        TaskEntity(title=f"Design {base_title} component hierarchy and props interface",
                   metadata={"complexity": "simple", "category": "design"}),
        TaskEntity(title=f"Implement {base_title} component structure and layout",
                   metadata={"complexity": "moderate", "category": "frontend"}),
        TaskEntity(title=f"Add styling for {base_title} (responsive + accessible)",
                   metadata={"complexity": "simple", "category": "frontend"}),
        TaskEntity(title=f"Implement state management and data flow for {base_title}",
                   metadata={"complexity": "moderate", "category": "frontend"}),
        TaskEntity(title=f"Add user interactions and event handlers for {base_title}",
                   metadata={"complexity": "moderate", "category": "frontend"}),
        TaskEntity(title=f"Write component tests for {base_title}",
                   metadata={"complexity": "moderate", "category": "testing"}),
        TaskEntity(title=f"Accessibility review and fixes for {base_title}",
                   metadata={"complexity": "simple", "category": "accessibility"}),
    ]


def security_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for security implementation (7 subtasks).
    
    Aligned with decomposition.py _decompose_security.
    """
    base_title = task.title.replace("Implement ", "").replace("Add ", "").replace("Create ", "")
    return [
        TaskEntity(title=f"Threat model and requirements analysis for {base_title}",
                   metadata={"complexity": "complex", "category": "security"}),
        TaskEntity(title=f"Design authentication flow for {base_title}",
                   metadata={"complexity": "moderate", "category": "security"}),
        TaskEntity(title=f"Implement authentication for {base_title} (login/register/token)",
                   metadata={"complexity": "complex", "category": "security"}),
        TaskEntity(title=f"Implement authorization and RBAC for {base_title}",
                   metadata={"complexity": "complex", "category": "security"}),
        TaskEntity(title=f"Add input sanitization and CSRF/XSS protection for {base_title}",
                   metadata={"complexity": "moderate", "category": "security"}),
        TaskEntity(title=f"Security audit and penetration testing for {base_title}",
                   metadata={"complexity": "complex", "category": "security"}),
        TaskEntity(title=f"Write security-focused tests for {base_title}",
                   metadata={"complexity": "moderate", "category": "testing"}),
    ]


def api_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for API endpoint implementation (6 subtasks).
    
    New template not in DEFAULT_RULES.
    """
    base_title = task.title.replace("Build ", "").replace("Create ", "").replace("API for ", "")
    return [
        TaskEntity(title=f"Design {base_title} API specification",
                   metadata={"complexity": "moderate", "category": "design"}),
        TaskEntity(title=f"Implement {base_title} request validation",
                   metadata={"complexity": "moderate", "category": "backend"}),
        TaskEntity(title=f"Implement {base_title} business logic",
                   metadata={"complexity": "complex", "category": "backend"}),
        TaskEntity(title=f"Add {base_title} error handling",
                   metadata={"complexity": "moderate", "category": "backend"}),
        TaskEntity(title=f"Write {base_title} integration tests",
                   metadata={"complexity": "moderate", "category": "testing"}),
        TaskEntity(title=f"Document {base_title} API",
                   metadata={"complexity": "simple", "category": "docs"}),
    ]


def refactor_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for code refactoring (6 subtasks).
    
    New template not in DEFAULT_RULES.
    """
    base_title = task.title.replace("Refactor ", "").replace("Restructure ", "")
    return [
        TaskEntity(title=f"Analyze {base_title} before refactor",
                   metadata={"complexity": "moderate", "category": "analysis"}),
        TaskEntity(title=f"Write tests for {base_title} (safety net)",
                   metadata={"complexity": "moderate", "category": "testing"}),
        TaskEntity(title=f"Extract interfaces from {base_title}",
                   metadata={"complexity": "complex", "category": "refactoring"}),
        TaskEntity(title=f"Migrate {base_title} to new structure",
                   metadata={"complexity": "complex", "category": "refactoring"}),
        TaskEntity(title=f"Validate {base_title} after refactor",
                   metadata={"complexity": "moderate", "category": "validation"}),
        TaskEntity(title=f"Update documentation for {base_title}",
                   metadata={"complexity": "simple", "category": "docs"}),
    ]


# Register all templates
TemplateRegistry.register("microservice", microservice_template)
TemplateRegistry.register("crud", crud_template)
TemplateRegistry.register("ui_component", ui_component_template)
TemplateRegistry.register("security", security_template)
TemplateRegistry.register("api", api_template)
TemplateRegistry.register("refactor", refactor_template)
