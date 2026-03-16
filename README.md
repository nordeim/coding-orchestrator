# Orchestrator Toolkit

A pure-Python orchestration toolkit built from patterns extracted from the OpenCode Industrial Orchestrator. This toolkit provides:

- **Task Management**: Hierarchical tasks with state machines, dependencies, and progress tracking
- **Complexity Analysis**: Heuristic-based task complexity scoring and capability inference
- **Task Decomposition**: Automatic breakdown of complex tasks into manageable subtasks
- **Persistence**: JSON-based storage for lightweight task persistence
- **Recovery & Health**: Checkpointing, health scoring, and failure recovery mechanisms
- **Examples**: Practical usage examples

## Features

### Task Entity (`orchestrator/tasks/entity`)
- Hierarchical task structure with parent/child relationships
- Dependency management (DAG-based)
- State machine with 10 states (pending → ready → in_progress → blocked → completed/failed/cancelled)
- Progress tracking and health scoring
- Event emission for state changes

### Complexity Analysis (`orchestrator/tasks/complexity`)
- Keyword-based complexity detection
- Capability inference from task descriptions
- PERT-based estimation (optimistic/likely/pessimistic)
- Risk factor identification

### Task Decomposition (`orchestrator/tasks/decomposition`)
- Template-based decomposition (microservices, CRUD, UI, security patterns)
- Rule-based decomposition with regex patterns
- Configurable complexity thresholds

### Storage (`orchestrator/storage`)
- JSON file persistence
- Lazy loading for performance
- Atomic writes to prevent corruption
- Backup and recovery mechanisms

### Recovery & Health (`orchestrator/recovery`)
- Checkpoint-based recovery with state serialization
- Health scoring based on progress, blockers, and dependencies
- Circuit breaker patterns for failure handling

## Usage

See the examples directory for practical usage patterns:

```bash
python3 examples/basic_usage.py
```

## Design Philosophy

- **Pure Python**: Zero external dependencies beyond Python standard library
- **Event-Driven**: Domain events for decoupled communication
- **Type Hints**: Full type hinting for IDE support and correctness
- **Tested**: Comprehensive test suite (>100 tests)
- **Extensible**: Clean interfaces for customization

## Phases of Development

This toolkit was built incrementally following a meticulous approach:

1. **Foundation**: Domain layer (states, events, exceptions)
2. **Task Entity**: Core task functionality with state machine
3. **Complexity Analyzer**: Heuristic-based complexity assessment
4. **Decomposition**: Task breakdown capabilities
5. **Recovery & Health**: Checkpointing and health monitoring
6. **Storage**: JSON persistence layer
7. **Examples & Documentation**: Usage examples and API docs

## Testing

Run the full test suite:

```bash
python3 -m pytest orchestrator/tests/ -v
```

## License

MIT License - see LICENSE file for details.