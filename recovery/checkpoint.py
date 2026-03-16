"""
Checkpoint-based task recovery.

Tracks execution checkpoints so failed tasks can resume
from the last successful step instead of starting over.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from orchestrator.domain.exceptions import CheckpointError


@dataclass
class Checkpoint:
    """A saved execution checkpoint."""
    step: str                              # Human-readable step name
    step_index: int                        # Numeric step index
    data: Dict[str, Any] = field(default_factory=dict)  # Serialized state
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "step_index": self.step_index,
            "data": self.data,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Checkpoint":
        return cls(
            step=d["step"],
            step_index=d["step_index"],
            data=d.get("data", {}),
            timestamp=d.get("timestamp", ""),
        )


class CheckpointMixin:
    """
    Mixin that adds checkpoint-based recovery to any class with an `id` attribute.

    Tracks execution progress via named checkpoints, enabling
    recovery from the last successful step after failures.

    Usage:
        class MyTask(CheckpointMixin):
            def __init__(self, id):
                self.id = id
                super().__init__()

            def run(self):
                self.checkpoint("initialized")
                load_config()
                self.checkpoint("config_loaded", {"path": "/etc/app.json"})
                connect_db()
                self.checkpoint("db_connected")
                process()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._checkpoints: List[Checkpoint] = []
        self._checkpoint_data: Dict[str, Any] = {}

    def checkpoint(self, step: str, data: Dict[str, Any] = None) -> Checkpoint:
        """Save a checkpoint at the current step."""
        cp = Checkpoint(
            step=step,
            step_index=len(self._checkpoints),
            data=data or {},
        )
        self._checkpoints.append(cp)
        if data:
            self._checkpoint_data.update(data)
        return cp

    @property
    def current_step(self) -> Optional[str]:
        """Get the name of the last checkpoint."""
        if not self._checkpoints:
            return None
        return self._checkpoints[-1].step

    @property
    def current_step_index(self) -> int:
        """Get the index of the last checkpoint."""
        return len(self._checkpoints) - 1

    def get_checkpoint_history(self) -> List[Checkpoint]:
        """Get all checkpoints."""
        return list(self._checkpoints)

    def get_checkpoint_data(self) -> Dict[str, Any]:
        """Get accumulated checkpoint data."""
        return dict(self._checkpoint_data)

    def clear_checkpoints(self) -> None:
        """Clear all checkpoints."""
        self._checkpoints.clear()
        self._checkpoint_data.clear()

    def restore_from_checkpoint(self, step_index: int = -1) -> Dict[str, Any]:
        """
        Get state to resume from a specific checkpoint.

        Args:
            step_index: Index of checkpoint to restore from (-1 = last)

        Returns:
            Dict with checkpoint info and accumulated data

        Raises:
            CheckpointError: If no checkpoints exist or index out of range
        """
        if not self._checkpoints:
            raise CheckpointError(
                "Cannot restore: no checkpoints exist (entity: {})".format(
                    str(getattr(self, "id", "unknown"))
                )
            )

        if step_index < 0:
            step_index = len(self._checkpoints) + step_index

        if step_index < 0 or step_index >= len(self._checkpoints):
            raise CheckpointError(
                "Checkpoint index {} out of range (0-{}) (entity: {})".format(
                    step_index, len(self._checkpoints)-1, str(getattr(self, "id", "unknown"))
                )
            )

        # Collect data from checkpoints up to and including the target
        accumulated = {}
        for cp in self._checkpoints[:step_index + 1]:
            accumulated.update(cp.data)

        return {
            "step": self._checkpoints[step_index].step,
            "step_index": step_index,
            "data": accumulated,
            "total_steps": len(self._checkpoints),
        }

    def serialize_checkpoints(self) -> str:
        """Serialize checkpoints to JSON."""
        return json.dumps([cp.to_dict() for cp in self._checkpoints])

    def deserialize_checkpoints(self, json_str: str) -> None:
        """Restore checkpoints from JSON."""
        data = json.loads(json_str)
        self._checkpoints = [Checkpoint.from_dict(d) for d in data]
        self._checkpoint_data = {}
        for cp in self._checkpoints:
            self._checkpoint_data.update(cp.data)
