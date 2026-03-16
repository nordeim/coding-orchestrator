"""
Tests for checkpoint and health modules.
"""

import pytest
import json
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from orchestrator.recovery.checkpoint import CheckpointMixin, Checkpoint
from orchestrator.recovery.health import HealthScorer, HealthReport, HealthIndicator
from orchestrator.tasks.entity import TaskEntity, TaskEstimate
from orchestrator.domain.exceptions import CheckpointError


# --- Checkpoint tests ---

class SampleCheckpointable(CheckpointMixin):
    def __init__(self, entity_id=None):
        self.id = entity_id or str(uuid4())
        super().__init__()


class TestCheckpoint:

    def test_checkpoint_creation(self):
        obj = SampleCheckpointable()
        cp = obj.checkpoint("initialized")
        assert cp.step == "initialized"
        assert cp.step_index == 0

    def test_multiple_checkpoints(self):
        obj = SampleCheckpointable()
        obj.checkpoint("step_1")
        obj.checkpoint("step_2")
        obj.checkpoint("step_3")
        assert obj.current_step == "step_3"
        assert obj.current_step_index == 2

    def test_checkpoint_with_data(self):
        obj = SampleCheckpointable()
        obj.checkpoint("loaded", {"config_path": "/etc/app.json", "port": 8080})
        data = obj.get_checkpoint_data()
        assert data["config_path"] == "/etc/app.json"
        assert data["port"] == 8080

    def test_checkpoint_data_accumulates(self):
        obj = SampleCheckpointable()
        obj.checkpoint("step_1", {"a": 1})
        obj.checkpoint("step_2", {"b": 2})
        data = obj.get_checkpoint_data()
        assert data == {"a": 1, "b": 2}

    def test_checkpoint_history(self):
        obj = SampleCheckpointable()
        obj.checkpoint("a")
        obj.checkpoint("b")
        obj.checkpoint("c")
        history = obj.get_checkpoint_history()
        assert len(history) == 3
        assert [h.step for h in history] == ["a", "b", "c"]

    def test_clear_checkpoints(self):
        obj = SampleCheckpointable()
        obj.checkpoint("a")
        obj.checkpoint("b", {"x": 1})
        obj.clear_checkpoints()
        assert obj.current_step is None
        assert obj.get_checkpoint_data() == {}

    def test_restore_from_checkpoint(self):
        obj = SampleCheckpointable()
        obj.checkpoint("init")
        obj.checkpoint("loaded", {"path": "/config.json"})
        obj.checkpoint("connected")

        result = obj.restore_from_checkpoint(1)
        assert result["step"] == "loaded"
        assert result["data"]["path"] == "/config.json"

    def test_restore_last_checkpoint(self):
        obj = SampleCheckpointable()
        obj.checkpoint("a")
        obj.checkpoint("b")
        result = obj.restore_from_checkpoint(-1)
        assert result["step"] == "b"

    def test_restore_no_checkpoints_raises(self):
        obj = SampleCheckpointable()
        with pytest.raises(CheckpointError):
            obj.restore_from_checkpoint()

    def test_restore_out_of_range_raises(self):
        obj = SampleCheckpointable()
        obj.checkpoint("a")
        with pytest.raises(CheckpointError):
            obj.restore_from_checkpoint(5)

    def test_serialize_deserialize(self):
        obj = SampleCheckpointable()
        obj.checkpoint("step_1", {"key": "value"})
        obj.checkpoint("step_2")

        json_str = obj.serialize_checkpoints()
        assert isinstance(json_str, str)

        obj2 = SampleCheckpointable()
        obj2.deserialize_checkpoints(json_str)
        assert obj2.current_step == "step_2"
        assert obj2.get_checkpoint_data()["key"] == "value"


class TestCheckpointDataModel:

    def test_to_dict(self):
        cp = Checkpoint(step="test", step_index=0, data={"x": 1})
        d = cp.to_dict()
        assert d["step"] == "test"
        assert d["data"]["x"] == 1

    def test_from_dict(self):
        d = {"step": "test", "step_index": 2, "data": {"y": 2}, "timestamp": "2026-03-16T00:00:00Z"}
        cp = Checkpoint.from_dict(d)
        assert cp.step == "test"
        assert cp.step_index == 2
        assert cp.data["y"] == 2


# --- Health Scorer tests ---

class TestHealthScorer:

    def test_healthy_task(self):
        scorer = HealthScorer()
        task = TaskEntity(title="Quick task", estimate=TaskEstimate(likely_hours=1))
        task.start()
        report = scorer.score_task(task)
        assert report.overall_score > 0.5
        assert report.status in ("healthy", "warning")

    def test_completed_task(self):
        scorer = HealthScorer()
        task = TaskEntity(title="Done task")
        task.start()
        task.complete()
        report = scorer.score_task(task)
        assert report.overall_score >= 0.9
        assert report.status == "healthy"

    def test_failed_task(self):
        scorer = HealthScorer()
        task = TaskEntity(title="Failing task")
        task.start()
        task.fail(RuntimeError("boom"))
        report = scorer.score_task(task)
        assert report.overall_score < 0.5
        assert report.status == "critical"

    def test_blocked_task(self):
        scorer = HealthScorer()
        task = TaskEntity(title="Blocked task")
        task.start()
        task.block("waiting on API key")
        report = scorer.score_task(task)
        assert report.overall_score < 0.6

    def test_report_structure(self):
        scorer = HealthScorer()
        task = TaskEntity(title="Test task")
        report = scorer.score_task(task)
        assert isinstance(report, HealthReport)
        assert 0.0 <= report.overall_score <= 1.0
        assert report.timestamp
        d = report.to_dict()
        assert "status" in d
        assert "indicators" in d

    def test_system_health(self):
        scorer = HealthScorer()
        tasks = []
        for i in range(5):
            t = TaskEntity(title=f"Task {i}")
            t.start()
            if i < 3:
                t.complete()
            elif i == 3:
                t.fail(RuntimeError("test"))
            tasks.append(t)

        report = scorer.score_system(tasks)
        assert report.overall_score < 1.0  # some failures
        assert report.status in ("warning", "critical")

    def test_empty_system(self):
        scorer = HealthScorer()
        report = scorer.score_system([])
        assert report.overall_score == 1.0

    def test_all_healthy_system(self):
        scorer = HealthScorer()
        tasks = []
        for i in range(3):
            t = TaskEntity(title=f"Task {i}")
            t.start()
            t.complete()
            tasks.append(t)

        report = scorer.score_system(tasks)
        assert report.overall_score > 0.8
        assert report.status == "healthy"


class TestHealthIndicator:

    def test_indicator_creation(self):
        indicator = HealthIndicator("time", 0.7, "At risk", "warning")
        assert indicator.name == "time"
        assert indicator.score == 0.7
        assert indicator.severity == "warning"

    def test_report_status_levels(self):
        assert HealthReport(overall_score=0.9).status == "healthy"
        assert HealthReport(overall_score=0.6).status == "warning"
        assert HealthReport(overall_score=0.3).status == "critical"
