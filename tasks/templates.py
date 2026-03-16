"""Decomposition Templates for Task Patterns.

Provides pre-built decomposition strategies for common software development tasks.
"""
from typing import List, Dict, Callable, Optional
from tasks.entity import TaskEntity, TaskComplexityLevel


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


def microservice_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for implementing a microservice."""
    base_title = task.title.replace("Implement ", "").replace("Create ", "")
    return [
        TaskEntity(title=f"Design API for {base_title}", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Implement service layer for {base_title}", complexity=TaskComplexityLevel.HIGH),
        TaskEntity(title=f"Set up database for {base_title}", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Write tests for {base_title}", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Create deployment config for {base_title}", complexity=TaskComplexityLevel.LOW),
    ]


def crud_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for CRUD feature implementation."""
    base_title = task.title.replace("Implement ", "").replace("Create ", "").replace("CRUD for ", "")
    return [
        TaskEntity(title=f"Define data model for {base_title}", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Create {base_title} (POST endpoint)", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Read {base_title} (GET endpoints)", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Update {base_title} (PUT/PATCH)", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Delete {base_title} (DELETE)", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Add validation for {base_title}", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Write tests for {base_title} CRUD", complexity=TaskComplexityLevel.MEDIUM),
    ]


def ui_component_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for UI component development."""
    base_title = task.title.replace("Build ", "").replace("Create ", "UI ")
    return [
        TaskEntity(title=f"Design {base_title} component structure", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Implement {base_title} core logic", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Add styles/theme for {base_title}", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Implement {base_title} event handlers", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Add {base_title} accessibility features", complexity=TaskComplexityLevel.LOW),
        TaskEntity(title=f"Write {base_title} tests", complexity=TaskComplexityLevel.MEDIUM),
    ]


def api_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for API endpoint implementation."""
    base_title = task.title.replace("Build ", "").replace("Create ", "").replace("API for ", "")
    return [
        TaskEntity(title=f"Design {base_title} API specification", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Implement {base_title} request validation", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Implement {base_title} business logic", complexity=TaskComplexityLevel.HIGH),
        TaskEntity(title=f"Add {base_title} error handling", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Write {base_title} integration tests", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Document {base_title} API", complexity=TaskComplexityLevel.LOW),
    ]


def refactor_template(task: TaskEntity) -> List[TaskEntity]:
    """Template for code refactoring."""
    base_title = task.title.replace("Refactor ", "").replace("Restructure ", "")
    return [
        TaskEntity(title=f"Analyze {base_title} before refactor", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Write tests for {base_title}", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Extract interfaces from {base_title}", complexity=TaskComplexityLevel.HIGH),
        TaskEntity(title=f"Migrate {base_title} to new structure", complexity=TaskComplexityLevel.HIGH),
        TaskEntity(title=f"Validate {base_title} after refactor", complexity=TaskComplexityLevel.MEDIUM),
        TaskEntity(title=f"Update documentation for {base_title}", complexity=TaskComplexityLevel.LOW),
    ]


# Register templates
TemplateRegistry.register("microservice", microservice_template)
TemplateRegistry.register("crud", crud_template)
TemplateRegistry.register("ui_component", ui_component_template)
TemplateRegistry.register("api", api_template)
TemplateRegistry.register("refactor", refactor_template)
